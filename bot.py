import logging
import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from deep_translator import GoogleTranslator
from binance.client import Client
from binance.exceptions import BinanceAPIException
import decimal

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
    update.message.reply_text('🤖 Добро пожаловать в myBinanceBot!\n\n' +
                              '💸 В ответ на тикер myBinanceBot вышлет вам лучшую цену покупки и продажи в паре с USDT\n\n' +
                              'ℹ️ Для получения более подробной информации нажмите /help')


def help(update, context):
    """Sends a message when the command /help is issued."""
    update.message.reply_text('⚡ Для получения лучшей цены сделок просто введите тикер. Например:\n\n' +
                              '👨‍💻: BTC\n\n' +
                              '🤖:\n' +
                              '    📉 Покупка: 39449.61 USDT\n' +
                              '    📈 Продажа: 39449.60 USDT󠀠')


info = client.get_exchange_info()


def get_precision(symbol):
    for x in info['symbols']:
        if x['symbol'] == symbol:
            for y in x['filters']:
                if y['filterType'] == 'PRICE_FILTER':
                    return abs(decimal.Decimal(y['tickSize']).normalize().as_tuple().exponent)


def treat_symbol(update, context):
    message = '☹️ Ошибка: '
    try:
        symbol = update.message.text + 'USDT'
        depth = client.get_order_book(symbol=symbol)
        if len(depth.get('bids')) == 0 or len(depth.get('asks')) == 0:
            raise KeyError('Нет данных о тикере.')
        precision = get_precision(symbol)
        bid_best_price = round(decimal.Decimal(depth.get('bids')[0][0]), precision)
        ask_best_price = round(decimal.Decimal(depth.get('asks')[0][0]), precision)
        message = '📉 Покупка: ' + str(ask_best_price) + ' USDT\n' + \
                  '📈 Продажа: ' + str(bid_best_price) + ' USDT󠀠'
    except BinanceAPIException as e:
        translated = GoogleTranslator(source='en', target='ru').translate(e.message)
        message += translated
    except KeyError as ke:
        message += str(ke).replace("'", "")
    update.message.reply_text(message)


def error(update, context):
    """Logs Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Starts the bot."""
    # Creates the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary

    token = os.environ.get('BOT_TOKEN', None)
    app_name = os.environ.get('BOT_APP_NAME', None)
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, treat_symbol))

    # log all errors
    dp.add_error_handler(error)
    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=token, webhook_url=app_name + token)
    updater.idle()


if __name__ == '__main__':
    main()
