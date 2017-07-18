# CindicatorArbitrageBot

The bot is used for sending notifications when the price difference for a currency between different exchanges is higher than a set threshold.
You can use these signals to monitor the possibility of favorable arbitrage between exchanges.

### What is arbitrage?

Arbitrage is the simultaneous purchase and sale of an asset to profit from a difference in its price.
It is a trade that profits by exploiting the price differences of identical or similar financial
instruments on different markets or in different forms. Arbitrage exists as a result of market inefficiencies.

### Registration

To start the bot working, a user must register on www.cindicator.com/arbitrage-bot by entering their email address.
Users will then receive a link to the telegram bot with a randomly generated unique hash key.
By following the link, users will be automatically registered in the system and can start to communicate with the bot and receive notifications.

### Deployment

To deploy the bot, first, you need to create a local.py module in the config folder with server settings.
The module must contain these values:

TOKEN - bot token

URL - server url in format: 'https://url:port/' \
PORT - server port

WEBHOOK_CERT - path to webhook certificate \
WEBHOOK_PKEY - path to webhook pkey

MONGO_HOST - mongodb host \
MONGO_PORT - mongodb port \
MONGO_DB - mongodb name

MONGO_BOT_USER - mongodb user \
MONGO_BOT_PASSWORD - mongodb password

Run the bot with the command: *python ArbitrageBot.py*
