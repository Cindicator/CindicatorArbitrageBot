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

"""This module contains main logic for crawler."""

import asyncio
from datetime import datetime
from traceback import format_exc

from crawler.data_loader import loader


class Crawler:
    """
    Crawler that checks new prices on various coins/exchanges pairs and update this price in DB.
    
    Attributes:
        :param coin_map: <dict> where keys is coin name (in BD) and values is <dict>
            with structure like {exchange name (in BD): coin name (on exchange), ...}
        :param bd: <object> to interact with BD that contain next functions:
            update_exchange(coin, exchange, price), get_coin(coin), add_coin(coin),
            get_exchange(coin, exchange, price) add_exchange(coin, exchange, price)
        :param logger: <logging.Logger> crawler's logger
        :param timeout: <int>[optional] frequency (in seconds) of requesting new data
        
    """
    def __init__(self, coin_map, bd, logger, timeout=1):
        self.coin_map = coin_map
        self.bd = bd
        self.timeout = timeout
        self.loop = asyncio.get_event_loop()
        self.logger = logger

    async def _load(self, coin, exchange):
        """
        Return the price on specific coin at which the last order executed on
        specific exchange.
        
        Args:
            :param coin: <string> coin name (on exchange)
            :param exchange: <string> exchange name
            
        Returns:
            :return: <float> price
            
        """
        return await loader(coin, exchange, self.logger)

    def _update(self, coin, exchange, price):
        """
        Update price of specific coin on specific exchange in BD
        
        Args:
            :param coin: <string> coin name (in BD)
            :param exchange: <string> exchange name
            :param price: <float> price
            
        """
        self.bd.update_exchange(coin=coin, exchange=exchange, price=price)

    def _check_existing(self, coin, exchange):
        """
        Check existence of coin/exchange pair in BD and if not exist add them.
        
        Args:
            :param coin: <string> coin name (in BD)
            :param exchange: <string> exchange name
            
        """
        db_coin = self.bd.get_coin(coin=coin)
        if not db_coin:
            self.bd.add_coin(coin=coin)
        db_exchange = self.bd.get_exchange(coin=coin, exchange=exchange)
        if not db_exchange:
            self.bd.add_exchange(coin=coin, exchange=exchange, price=None)

    async def load_and_update(self, coin, exchange):
        """
        Check availability of coin/exchange pair. If available start infinite loop
        that gets new coin price from exchange site and updates this price in BD
        
        Args:
            :param coin: <string> coin name (in BD)
            :param exchange: <string> exchange name
            
        """
        try:
            coin_name = self.coin_map[coin].get(exchange)
            if coin_name is not None:
                self._check_existing(coin=coin, exchange=exchange)
                while True:
                    try:
                        stime = datetime.now()
                        value = await self._load(coin=coin_name, exchange=exchange)
                        self._update(coin=coin, exchange=exchange, price=value)
                        await asyncio.sleep(self.timeout - (datetime.now() - stime).total_seconds())
                    except Exception as e:
                        self.logger.warning('Exception in thread\'s loop ({}{}): {}'
                                            '{}'.format(exchange, coin, str(e), format_exc()))
                        await asyncio.sleep(self.timeout)
        except Exception as e:
            self.logger.critical('Exception in crawler\'s thread ({}{}): {}'
                                 '{}'.format(exchange, coin, str(e), format_exc()))
            self.loop.stop()

    def launch(self):
        """
        Start function of Crawler (start asynchronous load_and_update() tasks for
        all available combinations of coins and exchanges).
        """
        try:
            for coin in self.coin_map.keys():
                for exchange in self.coin_map[coin].keys():
                    asyncio.ensure_future(self.load_and_update(coin=coin,
                                                               exchange=exchange))
            self.loop.run_forever()
        except Exception as e:
            self.logger.critical('Exception in creating crawler\'s threads: {}'
                                 '{}'.format(str(e), format_exc()))
            self.loop.stop()
            self.loop.close()
