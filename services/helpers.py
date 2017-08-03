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

"""This module contains static replies for user messages. Method name speak for itself"""

from telegram.ext.dispatcher import run_async

import messages
from services.core import (
    kb_main,
    kb_settings,
    MAIN_MENU,
    SETTINGS_MENU
)


@run_async
def settings(bot, update):
    update.message.reply_text(messages.SETTINGS_MENU_TEXT, reply_markup=kb_settings, parse_mode=messages.MARKDOWN)
    return SETTINGS_MENU


@run_async
def faq(bot, update):
    update.message.reply_text(messages.FAQ_TEXT, parse_mode=messages.MARKDOWN)
    return MAIN_MENU


@run_async
def about(bot, update):
    update.message.reply_text(messages.ABOUT_TEXT, parse_mode=messages.MARKDOWN)
    return MAIN_MENU


@run_async
def contacts(bot, update):
    update.message.reply_text(messages.CONTACTS_TEXT, parse_mode=messages.MARKDOWN)
    return MAIN_MENU


@run_async
def back(bot, update):
    update.message.reply_text(messages.BACK_TEXT, reply_markup=kb_main, parse_mode=messages.MARKDOWN)
    return MAIN_MENU
