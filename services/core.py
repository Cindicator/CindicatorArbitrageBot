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
from itertools import combinations

from telegram import KeyboardButton, ReplyKeyboardMarkup

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


def _stocks_price_checker(first_broker, second_broker):
    """
    Return two exchange pairs: first pair have higher price on coin than second
    
    Args:
        :param first_broker: <pair>: (exchange name, coin's price on this exchange)
        :param second_broker: <pair>: (exchange name, coin's price on this exchange)
    
    Returns:
        :return: higher_stock: <string> exchange name
        :return: lower_stock: <string>: exchange name
        
    """
    if first_broker[1] > second_broker[1]:
        return first_broker[0], second_broker[0]
    else:
        return second_broker[0], first_broker[0]


def _generate_string(data):
    """
    Generate notification text
    
    Args:
        :param data: <list> of lists that contains 4 items: [coin name, first exchange name,
            second exchange name, diff in percent between first and second exchange price on coin],
            price on first exchange is higher than on second
        
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
    prices on coin on this exchanges (diff always positive)
    
    Args:
        :param chat_id: <int> or <string> user's chat id
         
    Returns:
        :return: <list> of lists that contains 4 items: [coin name, first exchange name,
            second exchange name, diff in percent between first and second exchange price on coin],
            price on first exchange is higher than on second
     
    """
    user_settings = mq.get_user_settings(chat_id)
    thresh = user_settings[base_config.THRESHOLD]
    user_coins = user_settings[base_config.COINS]
    user_exchanges = user_settings[base_config.EXCHANGES]
    res = []
    for user_coin in user_coins:
        try:
            coin_doc = mq.get_coin(user_coin)
            exchanges_list = []
            for user_exch in user_exchanges:
                try:
                    exch_doc_list = list(filter(lambda coin_doc: coin_doc['name'] == user_exch, coin_doc['exchanges']))
                    if len(exch_doc_list) > 0:
                        exch_doc = exch_doc_list[0]
                        name = exch_doc['name']
                        value = exch_doc['price']
                        if value:
                            exchanges_list.append((name, value))
                except Exception as e:
                    logger.warning('chat_id: {}; error: {}'.format(chat_id, str(e)))
            if len(exchanges_list) > 1:
                combined_exchanges = combinations(exchanges_list, 2)
                for exchanges_pair in combined_exchanges:
                    try:
                        stocks_delta = round(abs(exchanges_pair[0][1] - exchanges_pair[1][1])
                                             / max(exchanges_pair[0][1], exchanges_pair[1][1]) * 100, 2)
                        higher_stock, lower_stock = _stocks_price_checker(exchanges_pair[0], exchanges_pair[1])
                        if stocks_delta > thresh:
                            res.append((coin_doc['name'].replace('/', '\_'), higher_stock, lower_stock, stocks_delta))
                    except Exception as e:
                        logger.warning('chat_id: {}; error: {}'.format(chat_id, str(e)))
        except Exception as e:
            logger.warning('chat_id: {}; error: {}'.format(chat_id, str(e)))
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
        bot.send_message(chat_id=job.context['chat_id'], text=_generate_string(res), parse_mode=messages.MARKDOWN)


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
        if user[base_config.SETTINGS][base_config.NOTIFICATIONS]:
            job = job_queue.run_repeating(notify, user[base_config.SETTINGS][base_config.INTERVAL],
                                          context={'chat_id': user[base_config.CHAT_ID]})
            chat_data[int(user[base_config.CHAT_ID])]['job'] = job
        try:
            job_queue.bot.send_message(chat_id=int(user[base_config.CHAT_ID]), text=messages.RESTART_TEXT,
                                       reply_markup=kb_entry_point, parse_mode='Markdown')
        except Exception as e:
            logger.warning('chat_id: {}; error: {}'.format(user[base_config.CHAT_ID], str(e)))


def exchange_convert(exchanges):
    if type(exchanges) == str:
        return mq.exchange_map[exchanges]
    return [mq.exchange_map[exchange] for exchange in exchanges]
