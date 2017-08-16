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

"""This module contains method for notifying all users with specific text"""

import sys
import time
import telegram
from datetime import datetime

import messages
import mongo_queries as mq
import config.base as base_config
import config.local as local_config


def notify_users(bot, users, text, msg_num_limit=29, msg_time_limit=1):
    """
    Send all users specific text (in 'msg_time_limit' can be send only 
    'msg_num_limit' messages)
    
    Args: 
        :param bot: <telegram.bot.Bot> instance
        :param users: <list> of dict with user's data
        :param text: <string> that will send to users
        :param msg_num_limit: <int>[optional=29] num of message
        :param msg_time_limit: <float>[optional=1] time in seconds
    """
    # Num of message that was send in 'msg_num_limit' seconds
    msg_num = 0
    for user in users:
        # New second time starts if num of message equal to zero
        if msg_num == 0:
            s_time = datetime.utcnow()

        try:
            bot.send_message(chat_id=int(user[base_config.CHAT_ID]), text=text)
        except Exception as e:
            print('chat_id: {}; error: {}'.format(user[base_config.CHAT_ID], str(e)))
        finally:
            msg_num += 1

        # If was sent 'msg_time_limit' messages in less than 'msg_num_limit' seconds
        if msg_num >= msg_num_limit and (datetime.utcnow() - s_time).total_seconds() < msg_time_limit:
            time.sleep(msg_time_limit)
            msg_num = 0
        # If was sent less than 'msg_time_limit' messages in 'msg_num_limit' seconds
        elif (datetime.utcnow() - s_time).total_seconds() > msg_time_limit:
            msg_num = 0

if __name__ == '__main__':
    if len(sys.argv) > 1:
        notify_text = sys.argv[1]
    else:
        notify_text = messages.OFFLINE_TEXT
    bot = telegram.bot.Bot(local_config.TOKEN)

    notify_users(bot, mq.get_users(), notify_text)
