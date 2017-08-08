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

"""This module contains constants (urls for exchanges and fields name in DB)"""

# Exchanges url
POLONIEX_URL = 'https://poloniex.com/public?command=returnTicker'
KRAKEN_URL = 'https://api.kraken.com/0/public/Ticker?pair='
OKCOIN_URL = 'https://www.okcoin.com/api/v1/ticker.do?symbol='
GEMINI_URL = 'https://api.gemini.com/v1/pubticker/'
BITSTAMP_URL = 'https://www.bitstamp.net/api/v2/ticker/'
BITTREX_URL = 'https://bittrex.com/api/v1.1/public/getticker?market='
BITFINEX_URL = 'https://api.bitfinex.com/v1/pubticker/'

# Names in DB
CHAT_ID = 'chat_id'
USERNAME = 'username'
FIRST_NAME = 'first_name'
LAST_NAME = 'last_name'
EMAIL = 'email'
SETTINGS = 'settings'
# Names in settings
NOTIFICATIONS = 'notifications'
THRESHOLD = 'threshold'
INTERVAL = 'interval'
COINS = 'coins'
EXCHANGES = 'exchanges'
