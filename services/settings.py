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

"""This module contains logic and interactive replies for user's bot settings.
All methods has the same arguments signature which described in set_interval_dialog method. Not all methods
may contain the whole list of described arguments"""

from telegram.ext.dispatcher import run_async

import messages
import mongo_queries as mq
from config import base as base_config
from services.commands import switch_on, switch_off
from services.core import (
    notify,
    kb_back,
    kb_settings,
    kb_alerts,
    SETTINGS_MENU,
    ALERTS_MENU,
    SET_INTERVAL,
    SET_THRESHOLD
)


@run_async
def set_interval_dialog(bot, update, chat_data, job_queue):
    """
    Begin the dialog with for setting an interval value
    
    Args:
        :param bot: <object> bot instance 
        :param update: <dict> update object that contains updates from user chat
        :param chat_data: <dict> stores the data for the chat. In this case a job object stores in it
        :param job_queue: <object> queue of jobs. The notify job automatically adds to queue after start 
        
    Returns:
        :return: settings menu identifier
    """

    msg = update.message
    interval = int(msg.text)
    if interval <= 0:
        msg.reply_text(messages.SET_INTERVAL_BAD_VALUE_TEXT, parse_mode=messages.MARKDOWN)
    else:
        mq.update_setting(msg.chat_id, setting=base_config.INTERVAL, value=interval)
        if mq.get_user_settings(msg.chat_id)[base_config.NOTIFICATIONS]:
            chat_data['job'].schedule_removal()
            job = job_queue.run_repeating(notify, interval, context={"chat_id": msg.chat_id})
            chat_data['job'] = job
            msg.reply_text(messages.SET_INTERVAL_SUCC_TEXT.format(interval),
                           reply_markup=kb_settings, parse_mode=messages.MARKDOWN)
        return SETTINGS_MENU
    return SET_INTERVAL


@run_async
def set_threshold_dialog(bot, update):
    """
    Begin the dialog with for setting an threshold value
    
    Returns:
        :return: settings menu identifier
    """

    msg = update.message
    threshold = float(msg.text)
    if threshold <= 0:
        msg.reply_text(messages.SET_THRESHOLD_BAD_VALUE_TEXT, parse_mode=messages.MARKDOWN)
    else:
        mq.update_setting(msg.chat_id, setting=base_config.THRESHOLD, value=threshold)
        msg.reply_text(messages.SET_THRESHOLD_SUCC_TEXT.format(threshold),
                       reply_markup=kb_settings, parse_mode=messages.MARKDOWN)
        return SETTINGS_MENU
    return SET_THRESHOLD


@run_async
def switch(bot, update, job_queue, chat_data):
    """Switch notifications on/off"""

    if mq.get_user_settings(update.message.chat_id)[base_config.NOTIFICATIONS]:
        switch_off(bot, update, job_queue, chat_data)
    else:
        switch_on(bot, update, job_queue, chat_data)
    return SETTINGS_MENU


@run_async
def interval(bot, update):
    """
    Send static message for interval setting
    
    Returns:
        :return: interval menu identifier
    """

    msg = update.message
    interval = mq.get_user_settings(msg.chat_id)[base_config.INTERVAL]
    msg.reply_text(messages.SET_INTERVAL_TEXT.format(interval), reply_markup=kb_back, parse_mode=messages.MARKDOWN)
    return SET_INTERVAL


@run_async
def interval_help(bot, update):
    """Send static helper message for interval setting"""

    update.message.reply_text(messages.SET_INTERVAL_HELP_CONV_TEXT, parse_mode=messages.MARKDOWN)
    return SET_INTERVAL


@run_async
def threshold(bot, update):
    """
    Send static message for threshold setting

    Returns:
        :return: threshold menu identifier
    """

    msg = update.message
    threshold = mq.get_user_settings(msg.chat_id)[base_config.THRESHOLD]
    msg.reply_text(messages.SET_THRESHOLD_TEXT.format(threshold), reply_markup=kb_back, parse_mode=messages.MARKDOWN)
    return SET_THRESHOLD


@run_async
def threshold_help(bot, update):
    """Send static helper message for threshold setting"""

    update.message.reply_text(messages.SET_THRESHOLD_HELP_CONV_TEXT, parse_mode=messages.MARKDOWN)
    return SET_THRESHOLD


@run_async
def alerts_settings(bot, update):
    """
    Open the menu for alerts settings
    
    Returns:
        :return: alerts settings menu identifier
    """

    update.message.reply_text(messages.ALERTS_MENU_TEXT, reply_markup=kb_alerts, parse_mode=messages.MARKDOWN)
    return ALERTS_MENU


@run_async
def back_to_settings(bot, update):
    """
    Return user to settings menu
    
    Returns:
        :return: settings menu identifier
    """

    update.message.reply_text(messages.BACK_TEXT, reply_markup=kb_settings, parse_mode=messages.MARKDOWN)
    return SETTINGS_MENU
