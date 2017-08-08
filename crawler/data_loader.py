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

"""This module contains functions for loading best bid and best ask coins prices"""

import json
import aiohttp
from traceback import format_exc
from json.decoder import JSONDecodeError
from concurrent.futures._base import TimeoutError

from config import base as base_config


# Dict map, where keys are exchanges and values are functions with:
#   Args:
#     - coin name <string>
#   Returns:
#     - url <string> where is coin price at which the last order executed

URL_MAP = {
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
    return {'ask': float(data['result'][real_name]['a'][0]),
            'bid': float(data['result'][real_name]['b'][0])}


# Dict map, where keys are exchanges and values are functions with:
#   Args:
#     - data <dict> crawled data from exchange API
#     - coin name <string>
#   Returns:
#     - <dict> with structure like: {'ask': best ask price, 'bid': best bid price}

PARSE_MAP = {
    'poloniex': lambda data, coin: {'ask': float(data[coin]['lowestAsk']),
                                    'bid': float(data[coin]['highestBid'])},
    'kraken': parse_kraken,
    'okcoin': lambda data, coin: {'ask': float(data['ticker']['sell']),
                                  'bid': float(data['ticker']['buy'])},
    'gemini': lambda data, coin: {'ask': float(data['ask']),
                                  'bid': float(data['bid'])},
    'bitstamp': lambda data, coin: {'ask': float(data['ask']),
                                    'bid': float(data['bid'])},
    'bittrex': lambda data, coin: {'ask': float(data['result']['Ask']),
                                   'bid': float(data['result']['Bid'])},
    'bitfinex': lambda data, coin: {'ask': float(data['ask']),
                                    'bid': float(data['bid'])}
}


async def loader(coin, exchange, logger):
    """
    Retrieve data from exchange and return best bid and ask prices.
    
    Args:
        :param coin: <string> coin name (on exchange)
        :param exchange: <string> exchange name
        :param logger: <logging.Logger> crawler's logger
        
    Returns:
        :return: <dict> with structure like: {'ask': best ask price, 'bid': best bid price}
            ({'ask': None, 'bid': None} if an exception was raised while getting data from url)
        
    """
    result = {'ask': None, 'bid': None}
    try:
        url = URL_MAP[exchange](coin)
        async with aiohttp.ClientSession() as session:
            response = await session.get(url)
            data = json.loads(await response.text())
            result = PARSE_MAP[exchange](data, coin)
    except TimeoutError as time_out_e:
        logger.warning('Parse/GET exception in {} exchange for {} coin: {}'
                       '(concurrent.futures._base.TimeoutError)'.format(exchange, coin, str(time_out_e)))
    except JSONDecodeError as json_e:
        logger.warning('Parse/GET exception in {} exchange for {} coin: {}\n'
                       'response: {}'.format(exchange, coin, str(json_e), await response.status))
    except Exception as e:
        logger.warning('Parse/GET exception in {} exchange for {} coin: {}\n'
                       '{}'.format(exchange, coin, str(e), format_exc()))
    finally:
        return result


async def exchange_loader(coins, exchange, logger):
    """
    Retrieve data from exchange and return best bid and ask coins prices.
    
    Args:
        :param coins: <list> of <string> coin name (in db)
        :param exchange: <string> exchange name
        :param logger: <logging.Logger> crawler's logger
        
    Returns:
        :return: <dict> where keys is coins names and value is <dict> with structure like:
            {'ask': best ask price, 'bid': best bid price} ({'ask': None, 'bid': None} if
            an exception was raised while getting data from url)
        
    """
    result = {coin: {'ask': None, 'bid': None} for coin in coins}
    try:
        url = URL_MAP[exchange](None)
        async with aiohttp.ClientSession() as session:
                response = await session.get(url)
                data = json.loads(await response.text())
                for coin in coins:
                    try:
                        result[coin] = PARSE_MAP[exchange](data, coin)
                    except Exception as e:
                        logger.warning('Parse data exception in {} exchange for {} coin: {}\n'
                                       '{}'.format(exchange, coin, str(e), format_exc()))
    except TimeoutError as time_out_e:
        logger.warning('Parse/GET exception in {} exchange: {}'
                       '(concurrent.futures._base.TimeoutError)'.format(exchange, str(time_out_e)))
    except JSONDecodeError as json_e:
        logger.warning('Parse/GET exception in {} exchange: {}\n'
                       'response: {}'.format(exchange, str(json_e), await response.status))
    except Exception as e:
        logger.warning('Parse/GET exception in {} exchange: {}\n'
                       '{}'.format(exchange, str(e), format_exc()))
    finally:
        return result
