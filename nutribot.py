from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

FOOD, MORE, ADD = range(3)

data = {
    "Chicken fried rice (198g)": [329, 41.8, 12.4, 11.9],
    "Macaroni Cheese (350g)": [361, 57.4, 18.9, 5.6],
    "14 inch Cheese Pizza (63g, 1 slice)": [192, 16.7, 8.9, 9.8],
    "Zinger Burger": [450, 47.5, 25.7, 17.5],
    "Egg (50g)": [74, 0.3, 6.2, 4.9]
}
dailyRecommended = { "Calories": [2000, "kcal"], 
    "Carbohydrates": [260, "g"], 
    "Protein": [50, "g"], 
    "Fat": [70, "g"] }

storage = {}
mealtypes = {}

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    name = update.message.from_user.first_name
    update.message.reply_text('Hi, ' + name + '! Nice to meet you! I\'m NutriBot!\n\n'
        'Send /help to see a list of available commands.\n'
        'Send /cancel to stop talking to me.', 
        reply_markup=ReplyKeyboardRemove(),
    )

def help(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Available commands:\n'
        '/start - start nutribot\n'
        '/help - show available commands\n'
        '/recommended - show recommended daily nutrient intake\n'
        '/add - add a meal\n'
        '/daily - show nutrient intake for today\n'
        '/cancel - stop nutribot', 
        reply_markup=ReplyKeyboardRemove(),
    )

def recommended(update: Update, context: CallbackContext) -> None:
    strings = []
    for e in dailyRecommended:
        strings.append(e + ": " + str(dailyRecommended[e][0]) + dailyRecommended[e][1])
    update.message.reply_text('Recommended daily nutrient intake:\n' + '\n'.join(strings), 
        reply_markup=ReplyKeyboardRemove(),
    )

def add(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Breakfast'], ['Lunch'], ['Dinner']]
    update.message.reply_text(
        'Please select meal type:',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return FOOD

def food(update: Update, context: CallbackContext) -> int:
    username = update.message.from_user.username
    text = update.message.text
    if text == 'Breakfast' or text == 'Lunch' or text == 'Dinner':
        mealtypes[username] = text

    reply_keyboard = []
    for e in list(data.keys()):
        reply_keyboard.append([e])
    update.message.reply_text(
        'What did you eat?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return MORE

def more(update: Update, context: CallbackContext) -> int:
    username = update.message.from_user.username
    date = update.message.date.date()
    mealtype = mealtypes[username]
    food = update.message.text

    if food not in data:
        reply_keyboard = []
        for e in list(data.keys()):
            reply_keyboard.append([e])
        update.message.reply_text(
            'Please select a food from the list given.',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )
        return MORE

    if username not in storage:
        storage[username] = {}
    if date not in storage[username]: 
        storage[username][date] = {}
    if mealtype not in storage[username][date]:
        storage[username][date][mealtype] = []
    arr = storage[username][date][mealtype]
    arr.append(food)

    reply_keyboard = [['Yes'], ['No']]
    update.message.reply_text(
        'Is there more food to be added?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return ADD

def add_success(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'The meal has been added!',
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END
    
def daily(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user.username
    date = update.message.date.date()
    reply = ''
    total_cal = 0
    total_carb = 0
    total_pro = 0
    total_fat = 0
    if user not in storage or date not in storage[user]:
        reply = 'No data for today!'
    else:
        print(storage[user][date])
        if 'Breakfast' in storage[user][date]:
            reply += '*Breakfast*\n'
            for food in storage[user][date]['Breakfast']:
                reply = reply + '- ' + food + '\n'
                total_cal += data[food][0]
                total_carb += data[food][1]
                total_pro += data[food][2]
                total_fat += data[food][3]
            reply += '\n'
        if 'Lunch' in storage[user][date]:
            reply += '*Lunch*\n'
            for food in storage[user][date]['Lunch']:
                reply = reply + '- ' + food + '\n'
                total_cal += data[food][0]
                total_carb += data[food][1]
                total_pro += data[food][2]
                total_fat += data[food][3]
            reply += '\n'
        if 'Dinner' in storage[user][date]:
            reply += '*Dinner*\n'
            for food in storage[user][date]['Dinner']:
                reply = reply + '- ' + food + '\n'
                total_cal += data[food][0]
                total_carb += data[food][1]
                total_pro += data[food][2]
                total_fat += data[food][3]
            reply += '\n'
        reply = reply + '*Total nutrients intake*' + '\nTotal calories: ' + "{:.1f}".format(total_cal) + ' kcal\nTotal carbohydrates: ' + "{:.1f}".format(total_carb) + ' g\nTotal protein: ' + "{:.1f}".format(total_pro) + ' g\nTotal fat: ' + "{:.1f}".format(total_fat) + ' g'
    update.message.reply_text(
        reply,
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END    

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'Bye! Hope we can talk again soon.', 
        reply_markup=ReplyKeyboardRemove(), 
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
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("cancel", cancel))
    dispatcher.add_handler(CommandHandler("daily", daily))
    dispatcher.add_handler(CommandHandler("recommended", recommended))

    # Add conversation handler with the states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add', add)],
        states={
            FOOD: [MessageHandler(Filters.regex('^(Breakfast|Lunch|Dinner)$'), food)],
            MORE: [MessageHandler(Filters.text & ~Filters.command, more)],
            ADD: [MessageHandler(Filters.regex('^Yes$'), food), 
                MessageHandler(Filters.regex('^No$'), add_success)],
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
