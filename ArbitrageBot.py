# -*- coding: utf-8 -*-
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

"""This module contains method for launching bot"""

from telegram.ext import Updater
from telegram.ext import CommandHandler, ConversationHandler, RegexHandler

import mongo_queries as mq
from config import local as local_config
from services import (
    core,
    commands,
    helpers,
    settings,
    alerts
)


def launch():
    updater = Updater(token=local_config.TOKEN)
    dispatcher = updater.dispatcher

    available_commands = [CommandHandler('start', commands.start,
                                         pass_args=True,
                                         pass_job_queue=True,
                                         pass_chat_data=True),
                          CommandHandler('switch_on', commands.switch_on,
                                         pass_job_queue=True,
                                         pass_chat_data=True),
                          CommandHandler('switch_off', commands.switch_off,
                                         pass_job_queue=True,
                                         pass_chat_data=True),
                          CommandHandler('set_interval', commands.set_interval,
                                         pass_args=True,
                                         pass_job_queue=True,
                                         pass_chat_data=True),
                          CommandHandler('set_threshold', commands.set_threshold, pass_args=True),
                          CommandHandler('add_coin', commands.add_coin, pass_args=True),
                          CommandHandler('remove_coin', commands.remove_coin, pass_args=True),
                          CommandHandler('show_coins', commands.show_your_coins),
                          CommandHandler('add_exchange', commands.add_exchange, pass_args=True),
                          CommandHandler('remove_exchange', commands.remove_exchange, pass_args=True),
                          CommandHandler('show_exchanges', commands.show_your_exchanges),
                          RegexHandler('(?!⬅Back)', commands.default_response)
                          ]

    # Menus constructor
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', commands.start,
                                     pass_args=True,
                                     pass_job_queue=True,
                                     pass_chat_data=True)],
        states={
            core.MAIN_MENU: [RegexHandler('^(🤖Settings)$', helpers.settings),
                             RegexHandler('^(🔬FAQ)$', helpers.faq),
                             RegexHandler('^(📱Contacts)$', helpers.contacts),
                             RegexHandler('^(👾About)$', helpers.about)
                             ] + available_commands,

            core.SETTINGS_MENU: [RegexHandler('^(🎚Set threshold)$', settings.threshold),
                                 RegexHandler('^(⏱Set interval)$', settings.interval),
                                 RegexHandler('^(🎛Alerts settings)$', settings.alerts_settings),
                                 RegexHandler('^(🔊Turn off/on notification)$', settings.switch,
                                              pass_job_queue=True,
                                              pass_chat_data=True)
                                 ] + available_commands,

            core.ALERTS_MENU: [RegexHandler('^(💎Add/remove coins)$', alerts.add_remove_coin),
                               RegexHandler('^(⚖️Add/remove exchanges)$', alerts.add_remove_exchange),
                               RegexHandler('^(⚙️Show my settings)$', alerts.show_settings),
                               RegexHandler('^(⬅Back)$', settings.back_to_settings)
                               ] + available_commands,

            core.SET_INTERVAL: [RegexHandler('^([0-9]+)$', settings.set_interval_dialog,
                                             pass_chat_data=True,
                                             pass_job_queue=True),
                                RegexHandler('^(⬅Back)$', settings.back_to_settings),
                                RegexHandler('\w*', settings.interval_help)
                                ],

            core.SET_THRESHOLD: [RegexHandler('^([0-9]+(\.[0-9]*){0,1})$', settings.set_threshold_dialog),
                                 RegexHandler('^(⬅Back)$', settings.back_to_settings),
                                 RegexHandler('\w*', settings.threshold_help)
                                 ],

            core.ADD_RM_COINS: [RegexHandler('^([aA][dD][dD][ \t\n\r]+[A-Za-z]{3}/[A-Za-z]{3})$', alerts.add_coin_dialog),
                                RegexHandler('^([rR][mM][ \t\n\r]+[A-Za-z]{3}/[A-Za-z]{3})$', alerts.remove_coin_dialog),
                                RegexHandler('^([aA][lL][lL])$', alerts.show_all_coins),
                                RegexHandler('^(⬅Back)$', alerts.back_to_alerts),
                                RegexHandler('\w*', alerts.coins_help)
                                ],

            core.ADD_RM_EX: [RegexHandler('^([aA][dD][dD][ \t\n\r]+[-\w]+)$', alerts.add_exchange_dialog),
                             RegexHandler('^([rR][mM][ \t\n\r]+[-\w]+)$', alerts.remove_exchange_dialog),
                             RegexHandler('^([aA][lL][lL])$', alerts.show_all_exchanges),
                             RegexHandler('^(⬅Back)$', alerts.back_to_alerts),
                             RegexHandler('\w*', alerts.ex_help)
                             ],

            core.BLACK_HOLE: [CommandHandler('start', commands.start,
                                             pass_args=True,
                                             pass_job_queue=True,
                                             pass_chat_data=True),
                              RegexHandler('\w*', commands.get_registration)]
        },
        fallbacks=[RegexHandler('⬅Back', helpers.back)]
    )

    dispatcher.add_handler(conv_handler)
    # Log all errors
    dispatcher.add_error_handler(commands.error)
    # Restart users notifications
    core.restart_jobs(dispatcher, mq.get_users())

    updater.start_webhook(listen='0.0.0.0',
                          port=local_config.PORT,
                          url_path=local_config.TOKEN,
                          key=local_config.WEBHOOK_PKEY,
                          cert=local_config.WEBHOOK_CERT,
                          webhook_url=local_config.URL+local_config.TOKEN)
    updater.idle()

if __name__ == '__main__':
    launch()
