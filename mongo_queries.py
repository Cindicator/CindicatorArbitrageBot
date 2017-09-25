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

"""This module contains DB connection and functions for work with collections in it"""

from math import ceil
from pymongo import MongoClient
from config import base as base_config
from config import local as local_config

# Mongo DB
mongo_client = MongoClient(local_config.MONGO_HOST, local_config.MONGO_PORT)
db = mongo_client[local_config.MONGO_DB]
db.authenticate(local_config.MONGO_BOT_USER, local_config.MONGO_BOT_PASSWORD)


# Dictionary that compares coin name with coin name on specific exchange
def _coin_map():
    return db.settings.find_one()['coin_map']
coin_map = _coin_map()


# All available coins
def _coins():
    return db.settings.find_one()['coin_map'].keys()
coins = _coins()


# Dictionary that compares exchange name from DB with real exchange name
def _exchange_map():
    return db.settings.find_one()['exchange_map']
exchange_map = _exchange_map()
# All available exchanges
exchanges = list(set([exchange for coin in coins for exchange in coin_map[coin].keys()]))


# Default settings for users
def _default_settings():
    return db.settings.find_one()['default_settings']
default_settings = _default_settings()


# Users collection

def get_users():
    """
    Return all users data
    
    Returns:
        :return: <list> of dict with user's data
        
    """
    return list(db['users'].find({}))


def add_user(msg, email):
    """
    Add new user to collection
    
    Args:
        :param msg: <telegram.message.Message> telegram's message with user data
        :param email: <string> users e-mail
        
    """
    db['users'].insert_one({base_config.CHAT_ID: str(msg.chat_id),
                            base_config.USERNAME: str(msg['chat']['username']),
                            base_config.EMAIL: str(email),
                            base_config.FIRST_NAME: str(msg['chat']['first_name']),
                            base_config.LAST_NAME: str(msg['chat']['last_name']),
                            base_config.SETTINGS: default_settings
                            })


def get_user(chat_id):
    """
    Return user's data

    Args:
        :param chat_id: <int> or <string> user's chat id
        
    Returns:
        :return: <dict> with user's data or None if user doesn't exist
        
    """
    return db['users'].find_one({base_config.CHAT_ID: str(chat_id)})


def get_user_by_email(email):
    """
    Return user's data 
    
    Args:
        :param email: <string> user's email
    
    Returns
        :return: <dict> with user's data or None if user doesn't exist
        
    """
    return db['users'].find_one({base_config.EMAIL: email})


def get_user_settings(chat_id):
    """
    Return settings for specific user

    Args:
        :param chat_id: <int> or <string> user's chat id
    
    Returns:
        :return: <dict> with user's settings or None if user doesn't exist
        
    """
    return get_user(chat_id).get(base_config.SETTINGS)


def update_setting(chat_id, setting, value):
    """
    Update user's setting with new value 
    
    Args:
        :param chat_id: <int> or <string> user's chat id
        :param setting: <string> setting name
        :param value: <int>, <float>, <bool> new setting value
        
    """
    db['users'].find_one_and_update({base_config.CHAT_ID: str(chat_id)},
                                    {'$set': {base_config.SETTINGS + '.' + setting: value}})


def add_to_list(chat_id, list, value):
    """
    Add new value to user's list
    
    Args:
        :param chat_id: <int> or <string> user's chat id
        :param list: <string> list name
        :param value: <string> value that will added to list
        
    """
    db['users'].update({base_config.CHAT_ID: str(chat_id)},
                       {'$push': {base_config.SETTINGS + '.' + list: value}})


def remove_from_list(chat_id, list, value):
    """
    Remove value from user's list
    
    Args:
        :param chat_id: <int> or <string> user's chat id
        :param list: <string> list name
        :param value: <string> value that will removed from list
        
    """
    db['users'].update({base_config.CHAT_ID: str(chat_id)},
                       {'$pull': {base_config.SETTINGS + '.' + list: value}})


# Coins collection

def get_coin(coin):
    """
    Return coin's data

    Args:
        :param coin: <string> coin name
        
    Returns:
        :return: <dict> with coin's data or None if coin doesn't exist
        
    """
    return db['coins'].find_one({'name': coin})


def add_coin(coin):
    """
    Add new coin with emtpy exchange list to collection
    
    Args:
        :param coin: <string> coin name
        
    """
    db['coins'].insert_one({'name': coin, 'exchanges': []})


def get_exchange(coin, exchange):
    """
    Return coin's data where coin contains specific exchange
    
    Args:
        :param coin: <string> coin name
        :param exchange: <string> exchange name
    
    Returns:
        :return: <dict> with coin's data or None if that coin doesn't exist
        
    """
    return db['coins'].find_one({'name': coin, 'exchanges.name': exchange})


def add_exchange(coin, exchange):
    """
    Add new exchange to coin's list  
    
    Args:
        :param coin: <string> coin name
        :param exchange: <string> exchange name 
         
    """
    db['coins'].update({'name': coin},
                       {'$push': {'exchanges': {'name': exchange,
                                                'ask': None,
                                                'bid': None}}})


def update_exchange(coin, exchange, ask, bid):
    """
    Update coin's price on exchange
    
    Args:
        :param coin: <string> coin name
        :param exchange: <string> exchange name 
        :param ask: <float> coin's ask price on exchange 
        :param bid: <float> coin's bid price on exchange
         
    """
    db['coins'].find_and_modify(query={'name': coin, 'exchanges.name': exchange},
                                update={'$set': {'exchanges.$.ask': ask,
                                                 'exchanges.$.bid': bid}})


# Coins history collection

def get_coin_h(coin):
    """
    Return coin's data

    Args:
        :param coin: <string> coin name

    Returns:
        :return: <dict> with coin's data or None if coin doesn't exist

    """
    return db['coins_history'].find_one({'name': coin})


def add_coin_h(coin):
    """
    Add new coin with emtpy exchange list to collection

    Args:
        :param coin: <string> coin name

    """
    db['coins_history'].insert_one({'name': coin, 'exchanges': []})


def get_exchange_h(coin, exchange):
    """
    Return coin's data where coin contains specific exchange

    Args:
        :param coin: <string> coin name
        :param exchange: <string> exchange name

    Returns:
        :return: <dict> with coin's data or None if that coin doesn't exist

    """
    return db['coins_history'].find_one({'name': coin, 'exchanges.name': exchange})


def add_exchange_h(coin, exchange):
    """
    Add new exchange with empty coin's price history to coin's list  

    Args:
        :param coin: <string> coin name
        :param exchange: <string> exchange name

    """
    db['coins_history'].update({'name': coin},
                               {'$push': {'exchanges': {'name': exchange,
                                                        'history': {str(hour): [] for hour in range(25)}}}})


def add_price_to_exchange_h(coin, exchange, time, ask, bid):
    """
    Add coin's price on exchange and time when this price get to history

    Args:
        :param coin: <string> coin name
        :param exchange: <string> exchange name 
        :param time: <datetime.datetime> UTC time
        :param ask: <float> coin's ask price on exchange
        :param bid: <float> coin's bid price on exchange 

    """
    db['coins_history'].find_and_modify(query={'name': coin, 'exchanges.name': exchange},
                                        update={'$push': {'exchanges.$.history.0': {'time': time,
                                                                                    'ask': ask,
                                                                                    'bid': bid}}})


def get_exchange_history(coin, exchange):
    """
    Return coin's price history on exchange

    Args:
        :param coin: <string> coin name
        :param exchange: <string> exchange name
        
    Returns:
        :return: <list> of coin's price history

    """
    db_history = db['coins_history'].find_one({'name': coin, 'exchanges.name': exchange},
                                        {'exchanges.$': 1})['exchanges'][0]['history']
    history = []
    for hour in range(25):
        history += db_history[str(hour)]
    return history


def update_exchange_h(coin, exchange, history, current_time):
    """
    Update coin's history on exchange

    Args:
        :param coin: <string> coin name
        :param exchange: <string> exchange name 
        :param history: <list> of dictionaries with next structure:
        {'time': <datetime.datetime>, 'price': {'ask': <float>, 'bid': <float>}}
        :param current_time: <datetime.datetime> current UTC time
            
    """
    db_history = {str(hour): [] for hour in range(25)}
    for timestamp in history:
        hour = ceil((current_time - timestamp['time']).total_seconds() / 3600)
        db_history[str(hour)].append(timestamp)
    db['coins_history'].find_and_modify(query={'name': coin, 'exchanges.name': exchange},
                                        update={'$set': {'exchanges.$.history': db_history}})


# Subscribers collection

def get_user_email(key):
    """
    Return subscriber's e-mail
    
    Args:
        :param key: <string> 
    
    Returns:
        :return: <string> user's e-mail or None if subscriber doesn't exist
    
    """
    user = db['subscribers'].find_one({'key': str(key)})
    if user:
        return user['email']
    else:
        return None
