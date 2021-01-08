from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

MEALTYPE, FOOD = range(2)

data = {
    "Chicken fried rice (198g)": [329, 41.8, 12.4, 11.9],
    "Macaroni Cheese (350g)": [361, 57.4, 18.9, 5.6],
    "14 inch Cheese Pizza (63g, 1 slice)": [192, 16.7, 8.9, 9.8],
    "Zinger Burger": [450, 47.5, 25.7, 17.5],
    "Egg (50g)": [74, 0.3, 6.2, 4.9]
}
dailyRecommended = [2000, 260, 50, 70]

storage = []

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    name = update.message.from_user.first_name
    update.message.reply_text('Hi, ' + name + '! Nice to meet you! I\'m NutriBot!\n\n'
        'Send /help to see a list of available commands.\n'
        'Send /cancel to stop talking to me.')

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def add_command(update: Update, context: CallbackContext) -> None:
    reply_keyboard = [['Breakfast'], ['Lunch'], ['Dinner']]
    update.message.reply_text(
        'Please select meal type:',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return MEALTYPE

def mealtype(update: Update, context: CallbackContext) -> int:
    reply_keyboard = []
    for e in list(data.keys()):
        reply_keyboard.append([e])
    update.message.reply_text(
        'What did you eat?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True),
    )
    return FOOD

def food(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        'The meal has been added!',
        reply_markup=ReplyKeyboardRemove(),
    )
    return

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'Bye! Hope we can talk again soon.', reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("TOKEN", use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # Add conversation handler with the states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add', add_command)],
        states={
            MEALTYPE: [MessageHandler(Filters.regex('^(Breakfast|Lunch|Dinner)$'), mealtype)],
            FOOD: [MessageHandler(Filters.text & ~Filters.command, food)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
