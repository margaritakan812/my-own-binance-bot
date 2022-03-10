import logging
import os
import emoji
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enables logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

PORT = int(os.environ.get('PORT', '8443'))


# We define command handlers. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Sends a message when the command /start is issued."""
    update.message.reply_text('🤖 Добро пожаловать в myBinanceBot!\n\n'+
                    '💸 В ответ на тикер myBinanceBot вышлет вам лучшую цену покупки и продажи\n\n'+
                    'ℹ️ Для получения более подробной информации нажмите /help')

def help(update, context):
    """Sends a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update, context):
    """Echos the user message."""
    update.message.reply_text(update.message.text)


def error(update, context):
    """Logs Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Starts the bot."""
    # Creates the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    TOKEN = '5164276901:AAFHKb9hAWKdvOV_GHOZLrJlzmGOpoIK-S4'  # enter your token here
    APP_NAME = 'https://my-own-binance-bot.herokuapp.com/'  # Edit the heroku app-name

    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)
    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN, webhook_url=APP_NAME + TOKEN)
    updater.idle()


if __name__ == '__main__':
    main()