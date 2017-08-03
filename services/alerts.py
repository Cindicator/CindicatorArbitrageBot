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

"""This module contains logic and interactive replies for user's bot alerts menu.
All methods has the same arguments signature which described in add_remove_coin method."""

from telegram.ext.dispatcher import run_async

import messages
import mongo_queries as mq
from config import base as base_config
from services.core import (
    exchange_convert,
    kb_back,
    kb_alerts,
    ALERTS_MENU,
    ADD_RM_COINS,
    ADD_RM_EX
)


@run_async
def add_remove_coin(bot, update):
    """
    Begin dialog for change coin's list
    
    Args:
        :param bot: <telegram.Bot> bot instance
        :param update: <telegram.update.Update> update instance 
    
    Returns:
        :return: change coin's list dialog identifier
         
    """
    msg = update.message
    user_coins = '`' + '`, `'.join(mq.get_user_settings(msg.chat_id)[base_config.COINS]) + '`'
    msg.reply_text(messages.ADD_RM_COINS_TEXT.format(user_coins), reply_markup=kb_back, parse_mode=messages.MARKDOWN)
    return ADD_RM_COINS


@run_async
def add_coin_dialog(bot, update):
    """Add coin to user's list and send message to user about operation's result"""

    msg = update.message
    coin = msg.text[4:].strip(' \t\n\r').upper()
    if coin not in mq.coins:
        msg.reply_text(messages.UNSUPPORTED_COIN_CONV_TEXT.format(coin), parse_mode=messages.MARKDOWN)
        return ADD_RM_COINS
    user_coins = mq.get_user_settings(msg.chat_id)[base_config.COINS]
    if coin in user_coins:
        msg.reply_text(messages.ALREADY_ENABLED_COIN.format(coin), parse_mode=messages.MARKDOWN)
        return ADD_RM_COINS
    mq.add_to_list(msg.chat_id, list=base_config.COINS, value=coin)
    new_user_coins = '`' + '`, `'.join(set(user_coins + [coin])) + '`'
    msg.reply_text(messages.ADD_COIN_SUCC_TEXT.format(new_user_coins), parse_mode=messages.MARKDOWN)
    return ADD_RM_COINS


@run_async
def remove_coin_dialog(bot, update):
    """Remove coin from user's list and send message to user about operation's result"""

    msg = update.message
    coin = msg.text[3:].strip(' \t\n\r').upper()
    user_coins = mq.get_user_settings(msg.chat_id)[base_config.COINS]
    if coin not in user_coins:
        msg.reply_text(messages.ALREADY_DISABLED_COIN.format('`' + '`, `'.join(user_coins) + '`'),
                       parse_mode=messages.MARKDOWN)
        return ADD_RM_COINS
    mq.remove_from_list(msg.chat_id, list=base_config.COINS, value=coin)
    new_user_coins = '`' + '`, `'.join(set(user_coins) - {coin}) + '`'
    msg.reply_text(messages.REMOVE_COIN_SUCC_TEXT.format(new_user_coins), parse_mode=messages.MARKDOWN)
    return ADD_RM_COINS


@run_async
def show_all_coins(bot, update):
    """Send message to user with all available coins"""

    update.message.reply_text('`' + '`, `'.join(mq.coins) + '`', parse_mode=messages.MARKDOWN)
    return ADD_RM_COINS


@run_async
def coins_help(bot, update):
    """Send message to user when bot gets unavailable coin"""

    update.message.reply_text(messages.ADD_REMOVE_COIN_HELP, parse_mode=messages.MARKDOWN)
    return ADD_RM_COINS


@run_async
def add_remove_exchange(bot, update):
    """
    Begin dialog for change exchange's list
    
    Returns:
        :return: change exchange's list dialog identifier
             
    """
    msg = update.message
    user_ex = '`' + '`, `'.join(exchange_convert(mq.get_user_settings(msg.chat_id)[base_config.EXCHANGES])) + '`'
    msg.reply_text(messages.ADD_RM_EX_TEXT.format(user_ex), reply_markup=kb_back, parse_mode=messages.MARKDOWN)
    return ADD_RM_EX


@run_async
def add_exchange_dialog(bot, update):
    """Add exchange to user's list and send message to user about operation's result """

    msg = update.message
    exchange = msg.text[4:].strip(' \t\n\r').replace('-', '_').lower()
    if exchange not in mq.exchanges:
        msg.reply_text(messages.UNSUPPORTED_EXCHANGE_CONV_TEXTS.format(exchange), parse_mode=messages.MARKDOWN)
        return ADD_RM_EX
    user_exchanges = mq.get_user_settings(msg.chat_id)[base_config.EXCHANGES]
    if exchange in user_exchanges:
        msg.reply_text(messages.ALREADY_ENABLED_EXCHANGE_TEXT.format(exchange_convert(exchange)), parse_mode=messages.MARKDOWN)
        return ADD_RM_EX
    mq.add_to_list(msg.chat_id, list=base_config.EXCHANGES, value=exchange)
    new_user_exchanges = '`' + '`, `'.join(set(exchange_convert(user_exchanges + [exchange]))) + '`'
    msg.reply_text(messages.ADD_EXCHANGE_SUCC_TEXT.format(new_user_exchanges), parse_mode=messages.MARKDOWN)
    return ADD_RM_EX


@run_async
def remove_exchange_dialog(bot, update):
    """Remove exchange from user's list and send message to user about operation's result"""

    msg = update.message
    exchange = msg.text[3:].strip(' \t\n\r').replace('-', '_').lower()
    user_exchanges = mq.get_user_settings(msg.chat_id)[base_config.EXCHANGES]
    if exchange not in user_exchanges:
        user_exchanges = exchange_convert(user_exchanges)
        msg.reply_text(messages.ALREADY_DISABLED_EXCHANGE_TEXT.format('`' + '`, `'.join(user_exchanges) + '`'),
                       parse_mode=messages.MARKDOWN)
        return ADD_RM_EX
    mq.remove_from_list(msg.chat_id, list=base_config.EXCHANGES, value=exchange)
    new_user_exchanges = '`' + '`, `'.join(exchange_convert(set(user_exchanges) - {exchange})) + '`'
    msg.reply_text(messages.REMOVE_EXCHANGE_SUCC_TEXT.format(new_user_exchanges), parse_mode=messages.MARKDOWN)
    return ADD_RM_EX


@run_async
def show_all_exchanges(bot, update):
    """
    Send message to user with all available exchanges
    """
    update.message.reply_text('`' + '`, `'.join(exchange_convert(mq.exchanges)) + '`', parse_mode=messages.MARKDOWN)
    return ADD_RM_EX


@run_async
def ex_help(bot, update):
    """
    Send message to user when bot gets unavailable exchange   
    """
    update.message.reply_text(messages.ADD_REMOVE_EXCHANGE_HELP_TEXT, parse_mode=messages.MARKDOWN)
    return ADD_RM_EX


@run_async
def show_settings(bot, update):
    """
    Send message to user with his current settings
    """
    msg = update.message
    user_settings = mq.get_user_settings(msg.chat_id)
    coins = '`' + '`, `'.join(user_settings[base_config.COINS]) + '`'
    exchanges = '`' + '`, `'.join(exchange_convert(user_settings[base_config.EXCHANGES])) + '`'
    threshold = str(user_settings[base_config.THRESHOLD])
    interval = str(user_settings[base_config.INTERVAL])
    notifications = 'enabled 🔊' if user_settings[base_config.NOTIFICATIONS] else 'disabled 🔇'
    settings_message = messages.SETTINGS_TEXT.format(notifications, interval, threshold, coins, exchanges)
    msg.reply_text(settings_message, parse_mode=messages.MARKDOWN)
    return ALERTS_MENU


@run_async
def back_to_alerts(bot, update):
    """Return user to alerts menu
    
        Returns:
            :return: alerts menu identifier
        
    """
    update.message.reply_text(messages.BACK_TEXT, reply_markup=kb_alerts, parse_mode=messages.MARKDOWN)
    return ALERTS_MENU
