"""
Copyright 2017 Evgeniy Koltsov, Sergey Zhirnov.

This file is part of CindicatorArbitrageBot.

CindicatorArbitrageBot is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

CindicatorArbitrageBot is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with CindicatorArbitrageBot. If not, see <http://www.gnu.org/licenses/>.
"""

"""This module contains constants (objects of all menus and keyboards), methods to get notifications, and 
restart method"""

import logging
from traceback import format_exc
from itertools import combinations

from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.error import Unauthorized, TimedOut
from telegram.ext.dispatcher import run_async

import messages
import config.base as base_config
import mongo_queries as mq

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Menus objects
MAIN_MENU, SETTINGS_MENU, ALERTS_MENU, SET_INTERVAL, SET_THRESHOLD, ADD_RM_COINS, ADD_RM_EX, BLACK_HOLE = range(8)

# Keyboards objects
kb_main = ReplyKeyboardMarkup([[KeyboardButton('🤖Settings'), KeyboardButton('🔬FAQ')],
                               [KeyboardButton('👾About'), KeyboardButton('📱Contacts')]],
                              resize_keyboard=True)

kb_settings = ReplyKeyboardMarkup([[KeyboardButton('⏱Set interval'), KeyboardButton('🎚Set threshold')],
                                   [KeyboardButton('🎛Alerts settings'), KeyboardButton('🔊Turn off/on notification')],
                                   [KeyboardButton('⬅Back')]],
                                  resize_keyboard=True)

kb_alerts = ReplyKeyboardMarkup([[KeyboardButton('💎Add/remove coins'), KeyboardButton('⚖️Add/remove exchanges')],
                                 [KeyboardButton('⚙️Show my settings'), KeyboardButton('⬅Back')]],
                                resize_keyboard=True)

kb_back = ReplyKeyboardMarkup([[KeyboardButton('⬅Back')]], resize_keyboard=True)

kb_entry_point = ReplyKeyboardMarkup([[KeyboardButton('/start')]], resize_keyboard=True)


def _price_checker(exchanges_pair, threshold, coin_name):
    """
    If bid price on one of two exchanges is bigger than ask price on another exchange,
    than return tuple with next structure: (coin name, bid exchange name, ask exchange name,
    diff in percent between bid and ask)

    Args:
        :param exchanges_pair: <list> with two <dict> with next structure:
            {'name': exchange name, 'ask': best ask price, 'bid': best bid price}
        :param threshold: <float> notification threshold
        :param coin_name: <string> coin name

    Returns:
        :return: coin_name: <string> coin name
        :return: bid_exchange: <string> exchange name
        :return: ask_exchange: <string> exchange name
        :return: delta: <float> diff in percent between bid and ask

    """
    for bid_exchange, ask_exchange in [(exchanges_pair[0], exchanges_pair[1]),
                                       (exchanges_pair[1], exchanges_pair[0])]:
        if bid_exchange['bid'] > ask_exchange['ask']:
            delta = round((bid_exchange['bid'] - ask_exchange['ask']) / ask_exchange['ask'] * 100, 2)
            if delta > threshold:
                return coin_name, bid_exchange['name'], ask_exchange['name'], delta
    return None


def _generate_string(data):
    """
    Generate notification text
    
    Args:
        :param data: <list> of lists that contains 4 items: [coin name, first exchange name,
            second exchange name, diff in percent between bid and ask coin's price on exchanges],
            bid price is higher than ask price 
        
    Returns:
        :return: <string> notification text 
         
    """
    message = ''
    for element in data:
        message += messages.ALERT_TEXT.format(element[0], element[1], element[2], element[3])
    return message


def crawl(chat_id):
    """
    Return list of lists that contains coin name, two exchanges names, and diff in percent between
    bid and ask on coin on this exchanges (diff always positive, bid bigger than ask)
    
    Args:
        :param chat_id: <int> or <string> user's chat id
         
    Returns:
        :return: <list> of lists that contains 4 items: [coin name, first exchange name,
            second exchange name, diff in percent between bid and ask coin's price on exchanges],
            bid price is higher than ask price 
     
    """
    user_settings = mq.get_user_settings(chat_id)
    threshold = user_settings[base_config.THRESHOLD]
    user_coins = user_settings[base_config.COINS]
    user_exchanges = user_settings[base_config.EXCHANGES]
    res = []
    for user_coin in user_coins:
        try:
            coin_doc = mq.get_coin(user_coin)
            exchanges_list = []
            for user_exch in user_exchanges:
                try:
                    exch_doc_list = list(filter(lambda coin_exch: coin_exch['name'] == user_exch,
                                                coin_doc['exchanges']))
                    if len(exch_doc_list) > 0:
                        exch_doc = exch_doc_list[0]
                        name = exch_doc['name']
                        ask = exch_doc['ask']
                        bid = exch_doc['bid']
                        if ask and bid:
                            exchanges_list.append({'name': name, 'ask': ask, 'bid': bid})
                except Exception as e:
                    logger.warning('chat_id: {}; error: {}\n'
                                   '{}'.format(chat_id, str(e), format_exc()))
            if len(exchanges_list) > 1:
                combined_exchanges = combinations(exchanges_list, 2)
                for exchanges_pair in combined_exchanges:
                    try:
                        check_res = _price_checker(exchanges_pair=exchanges_pair, threshold=threshold,
                                                   coin_name=coin_doc['name'].replace('/', '\_'))
                        if check_res:
                            res.append(check_res)
                    except Exception as e:
                        logger.warning('chat_id: {}; error: {}\n'
                                       '{}'.format(chat_id, str(e), format_exc()))
        except Exception as e:
            logger.warning('chat_id: {}; error: {}\n'
                           '{}'.format(chat_id, str(e), format_exc()))
    return res


def notify(bot, job):
    """
    Send notification to user
    
    Args:
        :param bot: <telegram.Bot> bot instance
        :param job: <telegram.ext.jobqueue.Job> user's job instance
         
    """
    res = crawl(job.context['chat_id'])
    if len(res) > 0:
        try:
            bot.send_message(chat_id=job.context['chat_id'], text=_generate_string(res), parse_mode=messages.MARKDOWN)
        except Unauthorized:
            job.schedule_removal()
            mq.update_setting(job.context['chat_id'], setting=base_config.NOTIFICATIONS, value=False)
        except TimedOut:
            logger.warning('chat_id: {}; error: {}'.format(job.context['chat_id'],
                                                           'Time out while sending notification'))
        except Exception as e:
            logger.warning('chat_id: {}; error: {}\n'
                           '{}'.format(job.context['chat_id'], str(e), format_exc()))


def restart_jobs(dispatcher, users):
    """
    Notify users about bot's restart and restart users notifications
    
    Args:
        :param dispatcher: <telegram.ext.dispatcher.Dispatcher> bot's dispatcher instance 
        :param users: <list> of dict with user's data
    
    """
    job_queue = dispatcher.job_queue
    chat_data = dispatcher.chat_data
    for user in users:
        try:
            if user[base_config.SETTINGS][base_config.NOTIFICATIONS]:
                job = job_queue.run_repeating(notify, user[base_config.SETTINGS][base_config.INTERVAL],
                                              context={'chat_id': user[base_config.CHAT_ID]})
                chat_data[int(user[base_config.CHAT_ID])]['job'] = job
            try:
                job_queue.bot.send_message(chat_id=int(user[base_config.CHAT_ID]), text=messages.RESTART_TEXT,
                                           reply_markup=kb_entry_point, parse_mode='Markdown')
            except Exception as e:
                if 'job' in chat_data[int(user[base_config.CHAT_ID])]:
                    chat_data[int(user[base_config.CHAT_ID])]['job'].schedule_removal()
                logger.warning('chat_id: {}; error: {}\n'
                               '{}'.format(user[base_config.CHAT_ID], str(e), format_exc()))
        except Exception as e:
            logger.critical('chat_id: {}; error: {}\n'
                            '{}'.format(user[base_config.CHAT_ID], str(e), format_exc()))


def exchange_convert(exchanges):
    """
    Convert exchange name (or list of exchanges names) to name (names) from DB
    
    Args:
        :param exchanges: <str> (or <list> of <str>'s) exchange name
        
    Returns:
        :return: <str> (or <list> of <str>'s) DB exchange name
        
    """
    if type(exchanges) == str:
        return mq.exchange_map[exchanges]
    return [mq.exchange_map[exchange] for exchange in exchanges]
