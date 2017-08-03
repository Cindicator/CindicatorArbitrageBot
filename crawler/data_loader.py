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

"""This module contains functions for loading coins prices at which the last order executed"""

import json
import aiohttp
from json.decoder import JSONDecodeError
from traceback import format_exc
from config import base as base_config


# Dict map, where keys are exchanges and values are functions with:
#   Args:
#     - coin name <string>
#   Returns:
#     - url <string> where is coin price at which the last order executed

URL_MAP = {
    'btc_e': lambda coin: base_config.BTCE_URL + coin,
    'poloniex': lambda coin: base_config.POLONIEX_URL,
    'kraken': lambda coin: base_config.KRAKEN_URL + coin,
    'okcoin': lambda coin: base_config.OKCOIN_URL + coin,
    'gemini': lambda coin: base_config.GEMINI_URL + coin,
    'bitstamp': lambda coin: base_config.BITSTAMP_URL + coin,
    'bittrex': lambda coin: base_config.BITTREX_URL + coin,
    'bitfinex': lambda coin: base_config.BITFINEX_URL + coin
}


def parse_kraken(data, coin):
    real_name = list(data['result'].keys())[0]
    return float(data['result'][real_name]['c'][0])


# Dict map, where keys are exchanges and values are functions with:
#   Args:
#     - data <dict> crawled data from exchange API
#     - coin name <string>
#   Returns:
#     - price <string>

PARSE_MAP = {
    'btc_e': lambda data, coin: data[coin]['last'],
    'poloniex': lambda data, coin: data[coin]['last'],
    'kraken': parse_kraken,
    'okcoin': lambda data, coin: data['ticker']['last'],
    'gemini': lambda data, coin: data['last'],
    'bitstamp': lambda data, coin: data['last'],
    'bittrex': lambda data, coin: data['result']['Last'],
    'bitfinex': lambda data, coin: data['last_price']
}


async def loader(coin, exchange, logger):
    """
    Retrieve data from exchange and return last coin price.
    
    Args:
        :param coin: <string> coin name (on exchange)
        :param exchange: <string> exchange name
        :param logger: <logging.Logger> crawler's logger
        
    Returns:
        :return: price as <float> or None if an exception was raised while getting data from url
        
    """
    try:
        url = URL_MAP[exchange](coin)
        async with aiohttp.ClientSession() as session:
            response = await session.get(url)
            data = json.loads(await response.text())
            return float(PARSE_MAP[exchange](data, coin))
    except JSONDecodeError as json_e:
        logger.warning('Parse/GET exception in {} exchange for {} coin: {}\n'
                       'response: {}\n'
                       '{}'.format(exchange, coin, str(json_e), response.text(), format_exc()))
    except Exception as e:
        logger.warning('Parse/GET exception in {} exchange for {} coin: {}\n'
                       '{}'.format(exchange, coin, str(e), format_exc()))
        return None
