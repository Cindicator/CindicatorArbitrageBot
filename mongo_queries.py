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

from pymongo import MongoClient
from config import base as base_config
from config import local as local_config

# Mongo DB
mongo_client = MongoClient(local_config.MONGO_HOST, local_config.MONGO_PORT)
db = mongo_client[local_config.MONGO_DB]
db.authenticate(local_config.MONGO_BOT_USER, local_config.MONGO_BOT_PASSWORD)

# Dictionary that compares coin name with coin name on specific exchange
coin_map = db.settings.find_one()['coin_map']
# All available coins
coins = db.settings.find_one()['coin_map'].keys()
# Dictionary that compares exchange name from DB with real exchange name
exchange_map = db.settings.find_one()['exchange_map']
# All available exchanges
exchanges = list(set([exchange for coin in coins for exchange in coin_map[coin].keys()]))
# Default settings for users
default_settings = db.settings.find_one()['default_settings']


# Users collection

def get_users():
    """
    Return all users data
    
    Returns:
        :return: <list> of dict with user's data
        
    """
    return db['users'].find({})


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


def add_exchange(coin, exchange, price):
    """
    Add new exchange with coin's price to coin's list  
    
    Args:
        :param coin: <string> coin name
        :param exchange: <string> exchange name 
        :param price: <float> coin's price on exchange
         
    """
    db['coins'].update({'name': coin},
                       {'$push': {'exchanges': {'name': exchange,
                                          'price': price}}})


def update_exchange(coin, exchange, price):
    """
    Update coin's price on exchange
    
    Args:
        :param coin: <string> coin name
        :param exchange: <string> exchange name 
        :param price: <float> coin's price on exchange 
         
    """
    db['coins'].find_and_modify(query={'name': coin, 'exchanges.name': exchange},
                                update={"$set": {'exchanges.$.price': price}})


# Subscribers collection

def get_user_email(key):
    """
    Return subscriber's e-mail
    
    Args:
        :param key: <string> 
    
    Returns:
        :return: <string> user's e-mail or None if subscriber doesn't exist
    
    """
    user = db.subscribers.find_one({"key": str(key)})
    if user:
        return user["email"]
    else:
        return None