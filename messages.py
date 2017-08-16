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

MARKDOWN = 'Markdown'

HELLO_TEXT = """
Hello!
 
Thank you for joining [Cindicator](cindicator.com)
 
Your account has been activated! You will start receiving signals soon.

I send notifications when the price difference for a currency between different \
exchanges is higher than your threshold. Use these signals \
to monitor the possibility of favorable arbitrage between exchanges. \
You can set your own threshold but make sure it covers the transaction costs. 
 
I am currently monitoring eight exchanges: [Poloniex](poloniex.com), \
[Kraken](kraken.com), [Okcoin](okcoin.com), \
[Gemini](gemini.com), [Bitstamp](bitstamp.net), [Bittrex](bittrex.com) and \
[Bitfinex](bitfinex.com), but planning to add more very soon. \
However, you can turn some exchanges off individually in your dashboard if you would like.
 
Don’t forget to follow us on [Twitter](twitter.com/Crowd_indicator) for the latest news!
"""

ALERT_TEXT = """
#{}
Bid is higher on *{}*
than ask on *{}* by *{}%*
"""

CONTACTS_TEXT = """
This bot is made by Cindicator team.
Contact us: bot@cindicator.com
Here is the tipjar to show your love:
BTC: 16APoVRR2SKD7XfP7sau84FHVgTPLwqak7	
ETH: 0xfe5309Fa6f3Df393d88BB449AaCbc78551664a55
"""

FAQ_TEXT = """
*Who am I?*
I am an arbitrage bot created by [Cindicator](cindicator.com) team.

*What is arbitrage?*
Arbitrage is the simultaneous purchase and sale of an asset to profit from a \
difference in its price. It is a trade that profits by exploiting the price \
differences of identical or similar financial instruments on different markets \
or in different forms. Arbitrage exists as a result of market inefficiencies. \
([Investopedia](http://investopedia.com/terms/a/arbitrage.asp))

*So what do I do?*
I send notifications when the price difference for a cryptocurrency \
between different exchanges is higher than a threshold (it is 3.5% by default).


*What does that all mean?*
This means that by buying the cryptocurrency on the cheaper exchange and selling it on \
the more expensive one, you will make a gross profit of 3.5%. However, don’t forget \
about the transaction costs, which can greatly reduce your profits or even make the trade \
unprofitable. You can find information about transaction costs on the exchanges.


*What else?*
You can also set your own threshold. However, the higher the threshold, the less \
often you can make a trade. On rare occasions, when the market dives, the threshold \
can be as high as 10–12%.


*What currencies and exchanges are available?*
Available exchanges: [Poloniex](poloniex.com), \
[Kraken](kraken.com), [Okcoin](okcoin.com), \
[Gemini](gemini.com), [Bitstamp](bitstamp.net), [Bittrex](bittrex.com) and \
[Bitfinex](bitfinex.com) \
Available coins: [BTC](http://investopedia.com/terms/b/bitcoin.asp), \
[ETH](http://investopedia.com/terms/e/ethereum.asp), \
[LTC](http://investopedia.com/terms/l/litecoin.asp) (all against USD or USDT)

If you are not interested in some currencies, you can turn off alerts for them.

*Notifications are too rare or too frequent. How can I change that?*
You can set your own interval between notifications. It is 15 minutes by default, \
which means that the bot will send messages no more than once in 15 minutes.

You can also turn off notifications completely.

*Where can I find my current settings?*
All your settings can be seen at settings - alert settings - show my settings
"""

ABOUT_TEXT = """
Hello! I am an arbitrage bot created by [Cindicator](cindicator.com) team!
 
I send notifications when the price difference for a currency \
between different exchanges is higher than your threshold. Use these signals to \
monitor the possibility of favorable arbitrage between exchanges. You can \
set your own threshold but make sure it covers the transaction costs.

 
Available exchanges: [Poloniex](poloniex.com), \
[Kraken](kraken.com), [Okcoin](okcoin.com), \
[Gemini](gemini.com), [Bitstamp](bitstamp.net), [Bittrex](bittrex.com) and \
[Bitfinex](bitfinex.com) \
Available coins: [BTC](http://investopedia.com/terms/b/bitcoin.asp), \
[ETH](http://investopedia.com/terms/e/ethereum.asp), \
[LTC](http://investopedia.com/terms/l/litecoin.asp) (all against USD or USDT)

If you just signed up, I recommend checking out the FAQ first.

Enjoy and don’t forget to follow us on [Twitter](twitter.com/Crowd_indicator) for the latest news!
"""

# start texto
GET_REGISTRATION_TEXT = 'Please, get registration on cindicator.com/arbitrage-bot'
AUTHORIZATION_FAIL_TEXT = 'Authorization failed!'
AUTHORIZATION_SUCC_TEXT = 'Authorization succeed!'

# switch on text
ALREADY_ON_TEXT = 'Notifications already `enabled`!'
NOTIFICATIONS_ON_TEXT = '*Success!* Notifications `enabled`.'

# switch off text
ALREADY_OFF_TEXT = 'Notifications already `disabled`!'
NOTIFICATIONS_OFF_TEXT = '*Success!* Notifications `disabled`.'

# set interval text
SET_INTERVAL_BAD_VALUE_TEXT = 'Interval must be bigger then 0!'
SET_INTERVAL_SUCC_TEXT = '*Success!* New interval value: {}s.'
SET_INTERVAL_HELP_TEXT = '*Usage*: /set\_interval <`seconds`>'
SET_INTERVAL_HELP_CONV_TEXT = 'Please enter a *integer* number or press Back.'
SET_INTERVAL_BIG_VALUE_EXCEPTION = 'Too big value for interval'

# set threshold text
SET_THRESHOLD_BAD_VALUE_TEXT = 'Threshold must be bigger then 0'
SET_THRESHOLD_SUCC_TEXT = '*Success!* New threshold value: {}%'
SET_THRESHOLD_HELP_TEXT = '*Usage*: /set\_threshold <`percents`>'
SET_THRESHOLD_HELP_CONV_TEXT = 'Please enter a *float* number or press Back.'
SET_THRESHOLD_BIG_VALUE_EXCEPTION = 'Too big value for threshold'

# add coin text
UNSUPPORTED_COIN_TEXT = """
Sorry, we do not support this coin.
Please, choose from:
{}
"""
UNSUPPORTED_COIN_CONV_TEXT = """
Sorry, coin `{}` not available.
To see all available coins print: all
"""
ALREADY_ENABLED_COIN = 'You already have notification on coin `{}`'
ADD_COIN_SUCC_TEXT = """
*Success!* Coin added.
Now you have notifications on this coins:
{}
"""
ADD_COIN_HELP_TEXT = '*Usage*: /add\_coin <`coin`>'

# remove coin text
ALREADY_DISABLED_COIN = """
You have notification only on next coins:
{}
"""
REMOVE_COIN_SUCC_TEXT = """
*Success!* Coin removed.
Now you have notifications on this coins:
{}
"""
REMOVE_COIN_HELP_TEXT = '*Usage*: /remove\_coin <`coin`>'

ADD_REMOVE_COIN_HELP = """
Please enter a valid coin or press Back.
To see all available coins print: all
"""

# add exchange text
UNSUPPORTED_EXCHANGE_TEXT = """
Sorry, we do not support this exchange.
Please, choose from:
{}
"""
UNSUPPORTED_EXCHANGE_CONV_TEXTS = """
Sorry, exchange `{}` not available.
To see all available exchanges print: all
"""
ALREADY_ENABLED_EXCHANGE_TEXT = 'You already have notification on exchange {}'
ADD_EXCHANGE_SUCC_TEXT = """  
*Success!* Exchange added.
Now you have notifications on this exchanges:
{}
"""
ADD_EXCHANGE_HELP_TEXT = '*Usage*: /add\_exchange <`exchange`>'

# remove exchange text
ALREADY_DISABLED_EXCHANGE_TEXT = """
You have notification only on this exchanges:
{}
"""
REMOVE_EXCHANGE_SUCC_TEXT = """
*Success!* Exchange removed.
Now you have notifications on this exchanges:
{}
"""
REMOVE_EXCHANGE_HELP_TEXT = '*Usage*: /remove\_exchange <`exchange`>'

ADD_REMOVE_EXCHANGE_HELP_TEXT = """
Please enter a valid exchange or press Back.
To see all available exchanges print: all
"""

SETTINGS_TEXT = """
*Notifications*: {}
*Interval*: {}s.
*Threshold*: {}%
*Coins*:
{}
*Exchanges*:
{}
"""

SET_INTERVAL_TEXT = """
*Current interval value*: {}s.
Please, enter new value as number or press Back.
"""

SET_THRESHOLD_TEXT = """
*Current threshold value*: {}%
Please, enter new value as number or press Back.
"""

ADD_RM_COINS_TEXT = """
*You have notifications on this coins*:
{}
*To add coin print*: add <`coin`>
*To remove coin print*: rm <`coin`>
*To see all available coins print*: all
"""

ADD_RM_EX_TEXT = """
*You have notifications on this exchanges*:
{}
*To add exchange print*: add <`exchange`>
*To remove exchange print*: rm <`exchange`>
*To see all available exchanges print*: all
"""

SETTINGS_MENU_TEXT = 'Here is your settings'

ALERTS_MENU_TEXT = 'Here you can see your settings and add or remove coins and exchanges'

RESTART_TEXT = """
Hello, my friend! I was updated and became a little better. Your notifications and settings \
are the same. Just type /start and we can communicate again.
"""

OFFLINE_TEXT = """
Hello, my friend! I'm currently updating and offline because of that. \
But soon I'll become better and come back.
"""

ERROR_TEXT = 'Update {} caused error {}'

BACK_TEXT = 'Ok'
