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

"""This module contains user commands to interact with the bot. Commands starts with '/' sign.
All methods has the same arguments signature which described in start method. Not all methods
may contain the whole list of described arguments"""

from telegram.ext.dispatcher import run_async

import messages
import mongo_queries as mq
from config import base as base_config
from services.core import (
    logger,
    notify,
    exchange_convert,
    kb_main,
    MAIN_MENU,
    BLACK_HOLE,
    SETTINGS_MENU, kb_settings)


# @run_async
def start(bot, update, args, job_queue, chat_data):
    """
    Main entry point of the bot. This command starts the bot interface and checks user authorization.
    
    Args:
        :param bot: <object> bot instance 
        :param update: <dict> update object that contains updates from user chat
        :param args: arguments that user enters after command. In this case command /start receives 
                     the unique hash key for user authentication
        :param job_queue: <object> queue of jobs. The notify job automatically adds to queue after start 
        :param chat_data: <dict> stores the data for the chat. In this case a job object stores in it.
        
    Returns:
        :return: Main menu identifier
    """
    msg = update.message
    user = mq.get_user(msg.chat_id)
    if not user:
        if len(args) == 0:
            msg.reply_text(messages.ABOUT_TEXT, parse_mode=messages.MARKDOWN)
            msg.reply_text(messages.GET_REGISTRATION_TEXT, parse_mode=messages.MARKDOWN)
            return BLACK_HOLE
        else:
            key = args[0]
            email = mq.get_user_email(key)
            if not email:
                msg.reply_text(messages.AUTHORIZATION_FAIL_TEXT, parse_mode=messages.MARKDOWN)
                return BLACK_HOLE
            else:
                mq.add_user(msg, email)
                msg.reply_text(messages.AUTHORIZATION_SUCC_TEXT, parse_mode=messages.MARKDOWN)

    msg.reply_text(messages.HELLO_TEXT, reply_markup=kb_main, parse_mode=messages.MARKDOWN)

    # Add job to queue
    if 'job' not in chat_data:
        user_settings = mq.get_user_settings(msg.chat_id)
        if user_settings[base_config.NOTIFICATIONS]:
            job = job_queue.run_repeating(notify, int(user_settings[base_config.INTERVAL]), context={'chat_id': msg.chat_id})
            chat_data['job'] = job

    return MAIN_MENU


def switch_on(bot, update, job_queue, chat_data):
    """Add the job to the queue"""

    msg = update.message
    if mq.get_user_settings(msg.chat_id)[base_config.NOTIFICATIONS]:
        msg.reply_text(messages.ALREADY_ON_TEXT, reply_markup=kb_main, parse_mode=messages.MARKDOWN)
        return MAIN_MENU
    mq.update_setting(msg.chat_id, setting=base_config.NOTIFICATIONS, value=True)
    if 'job' in chat_data:
        chat_data['job'].schedule_removal()
    job = job_queue.run_repeating(notify, int(mq.get_user_settings(msg.chat_id)[base_config.INTERVAL]),
                                  context={'chat_id': msg.chat_id})
    chat_data['job'] = job
    msg.reply_text(messages.NOTIFICATIONS_ON_TEXT, parse_mode=messages.MARKDOWN)


def switch_off(bot, update, job_queue, chat_data):
    """Remove the job if the user changed their mind"""

    msg = update.message
    if not mq.get_user_settings(msg.chat_id)[base_config.NOTIFICATIONS]:
        msg.reply_text(messages.ALREADY_OFF_TEXT, reply_markup=kb_main, parse_mode=messages.MARKDOWN)
        return MAIN_MENU
    mq.update_setting(msg.chat_id, setting=base_config.NOTIFICATIONS, value=False)
    chat_data['job'].schedule_removal()
    msg.reply_text(messages.NOTIFICATIONS_OFF_TEXT, parse_mode=messages.MARKDOWN)


@run_async
def set_interval(bot, update, args, chat_data, job_queue):
    """Set interval between notifications in seconds"""

    msg = update.message
    try:
        interval = int(args[0])
        if interval <= 0:
            msg.reply_text(messages.SET_INTERVAL_BAD_VALUE_TEXT, reply_markup=kb_main, parse_mode=messages.MARKDOWN)
            return MAIN_MENU
        mq.update_setting(msg.chat_id, setting=base_config.INTERVAL, value=interval)
        if mq.get_user_settings(msg.chat_id)[base_config.NOTIFICATIONS]:
            chat_data['job'].schedule_removal()
            job = job_queue.run_repeating(notify, interval, context={'chat_id': msg.chat_id})
            chat_data['job'] = job
        msg.reply_text(messages.SET_INTERVAL_SUCC_TEXT.format(interval),
                       reply_markup=kb_main,parse_mode=messages.MARKDOWN)
        return MAIN_MENU
    except (IndexError, ValueError, IndexError):
        msg.reply_text(messages.SET_INTERVAL_HELP_TEXT, reply_markup=kb_main, parse_mode=messages.MARKDOWN)
        return MAIN_MENU
    except OverflowError:
        msg.reply_text(messages.SET_INTERVAL_BIG_VALUE_EXCEPTION, reply_markup=kb_main, parse_mode=messages.MARKDOWN)
        return MAIN_MENU


@run_async
def set_threshold(bot, update, args):
    """Set the threshold between cryptocurrencies by which the bot will notify the user"""

    msg = update.message
    try:
        threshold = float(args[0])
        if threshold <= 0:
            msg.reply_text(messages.SET_THRESHOLD_BAD_VALUE_TEXT, reply_markup=kb_main, parse_mode=messages.MARKDOWN)
            return MAIN_MENU
        if threshold > 100:
            msg.reply_text(messages.SET_THRESHOLD_BAD_VALUE_TEXT, reply_markup=kb_main, parse_mode=messages.MARKDOWN)
            return MAIN_MENU
        mq.update_setting(msg.chat_id, setting=base_config.THRESHOLD, value=threshold)
        msg.reply_text(messages.SET_THRESHOLD_SUCC_TEXT.format(threshold), reply_markup=kb_main,
                       parse_mode=messages.MARKDOWN)
        return MAIN_MENU
    except (IndexError, ValueError):
        msg.reply_text(messages.SET_THRESHOLD_HELP_TEXT, reply_markup=kb_main, parse_mode=messages.MARKDOWN)
        return MAIN_MENU
    except OverflowError:
        msg.reply_text(messages.SET_THRESHOLD_BIG_VALUE_EXCEPTION, reply_markup=kb_main, parse_mode=messages.MARKDOWN)
        return MAIN_MENU


@run_async
def add_coin(bot, update, args):
    """Add coin to coins list by which the bot will notify the user"""

    msg = update.message
    try:
        coin = args[0].upper()
        if coin not in mq.coins:
            msg.reply_text(messages.UNSUPPORTED_COIN_TEXT.format('`' + '`, `'.join(mq.coins) + '`'),
                           reply_markup=kb_main, parse_mode=messages.MARKDOWN)
            return MAIN_MENU
        user_coins = mq.get_user_settings(msg.chat_id)[base_config.COINS]
        if coin in user_coins:
            msg.reply_text(messages.ALREADY_ENABLED_COIN.format('`' + coin + '`'),
                           reply_markup=kb_main, parse_mode=messages.MARKDOWN)
            return MAIN_MENU
        mq.add_to_list(msg.chat_id, list=base_config.COINS, value=coin)
        new_user_coins = '`' + '`, `'.join(set(user_coins + [coin])) + '`'
        msg.reply_text(messages.ADD_COIN_SUCC_TEXT.format(new_user_coins),
                       reply_markup=kb_main, parse_mode=messages.MARKDOWN)
        return MAIN_MENU
    except (IndexError, ValueError):
        msg.reply_text(messages.ADD_COIN_HELP_TEXT, reply_markup=kb_main, parse_mode=messages.MARKDOWN)
        return MAIN_MENU


@run_async
def remove_coin(bot, update, args):
    """Remove coin from coins list by which the bot will notify the user"""

    msg = update.message
    try:
        coin = args[0].upper()
        user_coins = mq.get_user_settings(msg.chat_id)[base_config.COINS]
        if coin not in user_coins:
            msg.reply_text(messages.ALREADY_DISABLED_COIN.format('`' + '`, `'.join(user_coins) + '`'),
                           reply_markup=kb_main, parse_mode=messages.MARKDOWN)
            return MAIN_MENU
        mq.remove_from_list(msg.chat_id, list=base_config.COINS, value=coin)
        new_user_coins = '`' + '`, `'.join(set(user_coins) - {coin}) + '`'
        msg.reply_text(messages.REMOVE_COIN_SUCC_TEXT.format(new_user_coins),
                       reply_markup=kb_main, parse_mode=messages.MARKDOWN)
        return MAIN_MENU
    except (IndexError, ValueError):
        msg.reply_text(messages.REMOVE_COIN_HELP_TEXT, reply_markup=kb_main, parse_mode=messages.MARKDOWN)
        return MAIN_MENU


@run_async
def show_your_coins(bot, update):
    """Show the user's coins list"""

    msg = update.message
    msg.reply_text('`' + '`, `'.join(mq.get_user_settings(msg.chat_id)[base_config.COINS]) + '`',
                   reply_markup=kb_main, parse_mode=messages.MARKDOWN)
    return MAIN_MENU


@run_async
def add_exchange(bot, update, args):
    """Add exchange to exchanges list by which the bot will notify the user"""

    msg = update.message
    try:
        exchange = args[0].replace('-', '_').lower()
        if exchange not in mq.exchanges:
            exchanges = exchange_convert(mq.exchanges)
            msg.reply_text(messages.UNSUPPORTED_EXCHANGE_TEXT.format('`' + '`, `'.join(exchanges) + '`'),
                           reply_markup=kb_main, parse_mode=messages.MARKDOWN)
            return MAIN_MENU
        user_exchanges = mq.get_user_settings(msg.chat_id)[base_config.EXCHANGES]
        if exchange in user_exchanges:
            msg.reply_text(messages.ALREADY_ENABLED_EXCHANGE_TEXT.format('`' + exchange_convert(exchange) + '`'),
                           reply_markup=kb_main, parse_mode=messages.MARKDOWN)
            return MAIN_MENU
        mq.add_to_list(msg.chat_id, list=base_config.EXCHANGES, value=exchange)
        new_user_exchanges = '`' + '`, `'.join(exchange_convert(set(user_exchanges + [exchange]))) + '`'
        msg.reply_text(messages.ADD_EXCHANGE_SUCC_TEXT.format(new_user_exchanges),
                       reply_markup=kb_main, parse_mode=messages.MARKDOWN)
        return MAIN_MENU
    except (IndexError, ValueError):
        msg.reply_text(messages.ADD_EXCHANGE_HELP_TEXT, reply_markup=kb_main, parse_mode=messages.MARKDOWN)
        return MAIN_MENU


@run_async
def remove_exchange(bot, update, args):
    """Remove exchange to exchanges list by which the bot will notify the user"""

    msg = update.message
    try:
        exchange = args[0].replace('-', '_').lower()
        user_exchanges = mq.get_user_settings(msg.chat_id)[base_config.EXCHANGES]
        if exchange not in user_exchanges:
            user_exchanges = exchange_convert(user_exchanges)
            msg.reply_text(messages.ALREADY_DISABLED_EXCHANGE_TEXT.format('`' + '`, `'.join(user_exchanges) + '`'),
                           reply_markup=kb_main, parse_mode=messages.MARKDOWN)
            return MAIN_MENU
        mq.remove_from_list(msg.chat_id, list=base_config.EXCHANGES, value=exchange)
        new_user_exchanges = '`' + '`, `'.join(exchange_convert(set(user_exchanges) - {exchange})) + '`'
        msg.reply_text(messages.REMOVE_EXCHANGE_SUCC_TEXT.format(new_user_exchanges),
                       reply_markup=kb_main, parse_mode=messages.MARKDOWN)
        return MAIN_MENU
    except (IndexError, ValueError):
        msg.reply_text(messages.REMOVE_EXCHANGE_HELP_TEXT, reply_markup=kb_main, parse_mode=messages.MARKDOWN)
        return MAIN_MENU


@run_async
def show_your_exchanges(bot, update):
    """Show user's exchanges list"""

    user_exchanges = mq.get_user_settings(update.message.chat_id)[base_config.EXCHANGES]
    update.message.reply_text('`' + '`, `'.join(user_exchanges) + '`',
                              reply_markup=kb_main, parse_mode=messages.MARKDOWN)
    return MAIN_MENU


@run_async
def default_response(bot, update):
    update.message.reply_text(messages.HELLO_TEXT, reply_markup=kb_main, parse_mode=messages.MARKDOWN)
    return MAIN_MENU


@run_async
def get_registration(bot, update):
    update.message.reply_text(messages.ABOUT_TEXT, parse_mode=messages.MARKDOWN)
    update.message.reply_text(messages.GET_REGISTRATION_TEXT, parse_mode=messages.MARKDOWN)
    return BLACK_HOLE


def error(bot, update, error):
    logger.warning(messages.ERROR_TEXT.format(str(update), str(error)))
