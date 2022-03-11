import logging
import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from googletrans import Translator
from binance.client import Client
from binance.exceptions import BinanceAPIException

# Enables logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

PORT = int(os.environ.get('PORT', '8443'))

client = Client(os.environ.get('API_KEY'),
                os.environ.get('API_SECRET'))

# We define command handlers. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Sends a message when the command /start is issued."""
    update.message.reply_text('🤖 Добро пожаловать в myBinanceBot!\n\n'+
                    '💸 В ответ на тикер myBinanceBot вышлет вам лучшую цену покупки и продажи в паре с USDT\n\n'+
                    'ℹ️ Для получения более подробной информации нажмите /help')

def help(update, context):
    """Sends a message when the command /help is issued."""
    update.message.reply_text('⚡ Для получения лучшей цены сделок просто введите тикер. Например:\n\n'+
                              '👨‍💻: BTC\n\n'+
                              '🤖:\n'+
                              '    📉 Покупка: 39449.61 USDT\n'+
                              '    📈 Продажа: 39449.60 USDT󠀠')

def treatSymbol(update, context):
    message = ''
    try:
        depth = client.get_order_book(symbol=update.message.text+'USDT')
        bid_best_price = depth.get('bids')[0][0]
        ask_best_price = depth.get('asks')[0][0]
        message = '📉 Покупка: ' + str(ask_best_price) + ' USDT\n'+\
                  '📈 Продажа: ' + str(bid_best_price) + ' USDT󠀠'
    except BinanceAPIException as e:
        translator = Translator()
        translated = translator.translate(e.message, src='en', dest='ru')
        message = '☹️Ошибка: '+translated
    update.message.reply_text(message)


def error(update, context):
    """Logs Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Starts the bot."""
    # Creates the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    #TOKEN = '5164276901:AAFHKb9hAWKdvOV_GHOZLrJlzmGOpoIK-S4'  # enter your token here
    #APP_NAME = 'https://my-own-binance-bot.herokuapp.com/'  # Edit the heroku app-name

    token = os.environ.get('BOT_TOKEN', None)
    app_name = os.environ.get('BOT_APP_NAME', None)
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, treatSymbol))

    # log all errors
    dp.add_error_handler(error)
    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=token, webhook_url=app_name + token)
    updater.idle()


if __name__ == '__main__':
    main()