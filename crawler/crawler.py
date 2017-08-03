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
from datetime import datetime, timedelta
from traceback import format_exc

from crawler.data_loader import loader


class Crawler:
    """
    Crawler that checks new prices on various coins/exchanges pairs, update this price in DB, and create 
    price history.
    
    Attributes:
        :param coin_map: <dict> where keys is coin name (in db) and values is <dict>
            with structure like {exchange name (in db): coin name (on exchange), ...}
        :param db: <object> to interact with DB that contain next functions:
            get_coin(coin), add_coin(coin),
            get_exchange(coin, exchange), add_exchange(coin, exchange, price), update_exchange(coin, exchange, price),
            get_coin_h(coin), add_coin_h(coin),
            get_exchange(coin, exchange), add_exchange_h(coin, exchange), get_exchange_history(coin, exchange),
            add_price_to_exchange_h(coin, exchange, time, price), update_exchange_h(coin, exchange, history)
        :param logger: <logging.Logger> crawler's logger
        :param timeout: <int>[optional=1] frequency (in seconds) of requesting new data
        :param history: <bool>[optional=True] will write coins price history if True
        :param h_update_time: <int>[optional=3600] frequency (in seconds) of history cleaning
        :param h_threshold_time: <int>[optional=1] time (in days) that price will exist in history
        
    """

    def __init__(self, coin_map, db, logger, timeout=1, history=True, h_update_time=3600, h_threshold_time=1):
        self.coin_map = coin_map
        self.db = db
        self.timeout = timeout
        self.loop = asyncio.get_event_loop()
        self.logger = logger
        self.history = history
        self.h_update_time = h_update_time
        self.h_threshold_time = h_threshold_time

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
        Update price of specific coin on specific exchange in db
        
        Args:
            :param coin: <string> coin name (in db)
            :param exchange: <string> exchange name
            :param price: <float> price
            
        """
        self.db.update_exchange(coin=coin, exchange=exchange, price=price)
        if self.history:
            self.db.add_price_to_exchange_h(coin=coin, exchange=exchange, time=datetime.utcnow(), price=price)

    def _check_existing(self, coin, exchange):
        """
        Check existence of coin/exchange pair in db and if not exist add them.
        
        Args:
            :param coin: <string> coin name (in db)
            :param exchange: <string> exchange name
            
        """
        if not self.db.get_coin(coin=coin):
            self.db.add_coin(coin=coin)
        if not self.db.get_exchange(coin=coin, exchange=exchange):
            self.db.add_exchange(coin=coin, exchange=exchange, price=None)

        if self.history:
            if not self.db.get_coin_h(coin=coin):
                self.db.add_coin_h(coin=coin)
            if not self.db.get_exchange_h(coin=coin, exchange=exchange):
                self.db.add_exchange_h(coin=coin, exchange=exchange)

    async def load_and_update(self, coin, exchange):
        """
        Check availability of coin/exchange pair. If available start infinite loop
        that gets new coin price from exchange site and updates this price in db
        
        Args:
            :param coin: <string> coin name (in db)
            :param exchange: <string> exchange name
            
        """
        if exchange == 'bitfinex':
            sleep_time = len(self.coin_map)
        else:
            sleep_time = self.timeout
        try:
            coin_name = self.coin_map[coin].get(exchange)
            if coin_name is not None:
                self._check_existing(coin=coin, exchange=exchange)
                while True:
                    try:
                        stime = datetime.now()
                        value = await self._load(coin=coin_name, exchange=exchange)
                        self._update(coin=coin, exchange=exchange, price=value)
                        await asyncio.sleep(sleep_time - (datetime.now() - stime).total_seconds())
                    except Exception as e:
                        self.logger.warning('Exception in thread\'s loop ({} {}): {}\n'
                                            '{}'.format(exchange, coin, str(e), format_exc()))
                        await asyncio.sleep(sleep_time)
        except Exception as e:
            self.logger.critical('Exception in crawler\'s thread ({} {}): {}\n'
                                 '{}'.format(exchange, coin, str(e), format_exc()))
            self.loop.stop()

    async def history_cleaner(self):
        """Clean history from old prices"""
        while True:
            for coin in self.coin_map.keys():
                for exchange in self.coin_map[coin].keys():
                    try:
                        new_history = []
                        time = datetime.utcnow() - timedelta(days=self.h_threshold_time)
                        for timestamp in self.db.get_exchange_history(coin=coin, exchange=exchange):
                            if timestamp['time'] > time:
                                new_history.append(timestamp)
                        self.db.update_exchange_h(coin=coin, exchange=exchange, history=new_history)
                    except Exception as e:
                        self.logger.warning('Exception in history_cleaner ({} {}): {}\n'
                                            '{}'.format(exchange, coin, str(e), format_exc()))
            await asyncio.sleep(self.h_update_time)

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
            if self.history:
                asyncio.ensure_future(self.history_cleaner())
            self.loop.run_forever()
        except Exception as e:
            self.logger.critical('Exception in creating crawler\'s threads: {}\n'
                                 '{}'.format(str(e), format_exc()))
            self.loop.stop()
            self.loop.close()
