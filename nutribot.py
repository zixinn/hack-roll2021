import os
import json
import pandas as pd
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

FOOD, MORE, ADD, FOODNAME, FOODCAL, FOODCARB, FOODPROTEIN, FOODFAT = range(8)

userdata = {}

data = pd.read_csv("Food.csv").iloc[:20,[1,3,4,5,6]]
data = data.set_index('Name').T.to_dict('list')

dailyRecommended = { "Calories": [2000, "kcal"], 
    "Carbohydrates": [260, "g"], 
    "Protein": [50, "g"], 
    "Fat": [70, "g"] }

mealtypes = {}
storage = {}
text = ''
if os.path.exists("storage.txt"):
    f = open("storage.txt", "r")
    text = f.read()
if text != '':
    storage = json.loads(text)

userdatatext = ''
if os.path.exists("userdata.txt"):
    f = open("userdata.txt", "r")
    userdatatext = f.read()
if userdatatext != '':
    userdata = json.loads(userdatatext)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    name = update.message.from_user.first_name
    username = update.message.from_user.username
    if username not in userdata:
        userdata[username] = []
        temp = data.copy()
        userdata[username].append(temp)
        userdata[username].append("null")
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
        '/info - show nutritional information of food available\n'
        '/recommended - show recommended daily nutrient intake\n'
        '/add - add a meal\n'
        '/daily - show nutrient intake for today\n'
        '/monthly - show average nutrient intake for the current month\n'
        '/addfood - add new food into food list\n'
        '/cancel - stop nutribot', 
        reply_markup=ReplyKeyboardRemove(),
    )

def info(update: Update, context: CallbackContext) -> None:
    string = ""
    username = update.message.from_user.username
    for item in userdata[username][0]:
        string += "*"
        string += item
        string += "*\n"
        string += "{:.1f}".format(userdata[username][0][item][0]) + " kcal Calories, " + "{:.1f}".format(userdata[username][0][item][1]) + " g Carbohydrates, " + "{:.1f}".format(userdata[username][0][item][2]) + " g Protein, " + "{:.1f}".format(userdata[username][0][item][3]) + " g Fats" + "\n\n"

    update.message.reply_text(
        string, 
        parse_mode='Markdown', 
        reply_markup=ReplyKeyboardRemove(),)

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
    for e in list(userdata[username][0].keys()):
        reply_keyboard.append([e])
    update.message.reply_text(
        'What did you eat?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return MORE

def more(update: Update, context: CallbackContext) -> int:
    username = update.message.from_user.username
    month = update.message.date.date().strftime("%m/%Y")
    date = update.message.date.date().strftime("%d/%m/%Y")
    mealtype = mealtypes[username]
    food = update.message.text

    if food not in userdata[username][0]:
        reply_keyboard = []
        for e in list(userdata[username][0].keys()):
            reply_keyboard.append([e])
        update.message.reply_text(
            'Please select a food from the list given.',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )
        return MORE

    if username not in storage:
        storage[username] = {}
    if month not in storage[username]:
        storage[username][month] = {}
    if date not in storage[username][month]:
        storage[username][month][date] = {}
    if mealtype not in storage[username][month][date]:
        storage[username][month][date][mealtype] = []
    arr = storage[username][month][date][mealtype]
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
    f = open("storage.txt", "w")
    f.write(json.dumps(storage))
    return ConversationHandler.END

def daily(update: Update, context: CallbackContext) -> None:
    username = update.message.from_user.username
    month = update.message.date.date().strftime("%m/%Y")
    date = update.message.date.date().strftime("%d/%m/%Y")
    reply = ''
    total_cal = 0
    total_carb = 0
    total_pro = 0
    total_fat = 0
    
    if username not in storage or date not in storage[username][month]:
        reply = 'No data for today!'
    else:
        if 'Breakfast' in storage[username][month][date]:
            reply += '*Breakfast*\n'
            for food in storage[username][month][date]['Breakfast']:
                reply = reply + '- ' + food + '\n'
                total_cal += userdata[username][0][food][0]
                total_carb += userdata[username][0][food][1]
                total_pro += userdata[username][0][food][2]
                total_fat += userdata[username][0][food][3]
            reply += '\n'
            
        if 'Lunch' in storage[username][month][date]:
            reply += '*Lunch*\n'
            for food in storage[username][month][date]['Lunch']:
                reply = reply + '- ' + food + '\n'
                total_cal += userdata[username][0][food][0]
                total_carb += userdata[username][0][food][1]
                total_pro += userdata[username][0][food][2]
                total_fat += userdata[username][0][food][3]
            reply += '\n'

        if 'Dinner' in storage[username][month][date]:
            reply += '*Dinner*\n'
            for food in storage[username][month][date]['Dinner']:
                reply = reply + '- ' + food + '\n'
                total_cal += userdata[username][0][food][0]
                total_carb += userdata[username][0][food][1]
                total_pro += userdata[username][0][food][2]
                total_fat += userdata[username][0][food][3]
            reply += '\n'
        reply = reply + '*Total nutrients intake*' + '\nTotal calories: ' + "{:.1f}".format(total_cal) + ' kcal\nTotal carbohydrates: ' + "{:.1f}".format(total_carb) + ' g\nTotal protein: ' + "{:.1f}".format(total_pro) + ' g\nTotal fat: ' + "{:.1f}".format(total_fat) + ' g'
    update.message.reply_text(
        reply,
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END

def monthly(update: Update, context: CallbackContext) -> None:
    username = update.message.from_user.username
    month = update.message.date.date().strftime("%m/%Y")
    reply = ''
    total_cal = 0
    total_carb = 0
    total_pro = 0
    total_fat = 0
    if username not in storage or month not in storage[username]:
        reply = 'No data for this month!'
    else:
        total_days = len(storage[username][month])
        for date in storage[username][month]:
            reply += '*%s*\n' % date
            if 'Breakfast' in storage[username][month][date]:
                reply += '*Breakfast*\n'
                for food in storage[username][month][date]['Breakfast']:
                    reply = reply + '- ' + food + '\n'
                    total_cal += userdata[username][0][food][0]
                    total_carb += userdata[username][0][food][1]
                    total_pro += userdata[username][0][food][2]
                    total_fat += userdata[username][0][food][3]
            if 'Lunch' in storage[username][month][date]:
                reply += '*Lunch*\n'
                for food in storage[username][month][date]['Lunch']:
                    reply = reply + '- ' + food + '\n'
                    total_cal += userdata[username][0][food][0]
                    total_carb += userdata[username][0][food][1]
                    total_pro += userdata[username][0][food][2]
                    total_fat += userdata[username][0][food][3]
            if 'Dinner' in storage[username][month][date]:
                reply += '*Dinner*\n'
                for food in storage[username][month][date]['Dinner']:
                    reply = reply + '- ' + food + '\n'
                    total_cal += userdata[username][0][food][0]
                    total_carb += userdata[username][0][food][1]
                    total_pro += userdata[username][0][food][2]
                    total_fat += userdata[username][0][food][3]
            reply += '\n'

        average_cal = total_cal / total_days
        average_carb = total_carb / total_days
        average_pro = total_pro / total_days
        average_fat = total_fat / total_days
        reply = reply + '*Total nutrients intake for this month*' + '\nTotal calories: ' + "{:.1f}".format(total_cal) + ' kcal\nTotal carbohydrates: ' + "{:.1f}".format(total_carb) + ' g\nTotal protein: ' + "{:.1f}".format(total_pro) + ' g\nTotal fat: ' + "{:.1f}".format(total_fat) + ' g\n\n'
        reply = reply + '*Average nutrients intake for this month*' + '\nAverage calories: ' + "{:.1f}".format(average_cal) + ' kcal\nAverage carbohydrates: ' + "{:.1f}".format(average_carb) + ' g\nAverage protein: ' + "{:.1f}".format(average_pro) + ' g\nAverage fat: ' + "{:.1f}".format(average_fat) + ' g'
    update.message.reply_text(
        reply,
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END

def addFood(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Please enter the name of food',reply_markup=ReplyKeyboardRemove())
    
    return FOODNAME

def foodName(update: Update, context: CallbackContext) -> int:
    username = update.message.from_user.username
    response = update.message.text
    userdata[username][0][response] = []
    userdata[username][1] = response
    
    update.message.reply_text('Please enter the Calories of food',reply_markup=ReplyKeyboardRemove())
    
    return FOODCAL

def foodCal(update: Update, context: CallbackContext) -> int:
    response = update.message.text
    if (not response.isdigit()):
        update.message.reply_text('Please give a number',
            reply_markup=ReplyKeyboardRemove(),
        )
        return FOODCAL
    username = update.message.from_user.username
    userdata[username][0][userdata[username][1]].append(int(response))
    update.message.reply_text('Please enter the Carbohydrates of food',reply_markup=ReplyKeyboardRemove())
    
    return FOODCARB

def foodCarb(update: Update, context: CallbackContext) -> int:
    response = update.message.text
    if (not response.isdigit()):
        update.message.reply_text('Please give a number',
            reply_markup=ReplyKeyboardRemove(),
        )
        return FOODCARB
    username = update.message.from_user.username
    userdata[username][0][userdata[username][1]].append(int(response))
    update.message.reply_text('Please enter the Protein of food',reply_markup=ReplyKeyboardRemove())
    
    return FOODPROTEIN

def foodProtein(update: Update, context: CallbackContext) -> int:
    response = update.message.text
    if (not response.isdigit()):
        update.message.reply_text('Please give a number',
            reply_markup=ReplyKeyboardRemove(),
        )
        return FOODPROTEIN
    username = update.message.from_user.username
    userdata[username][0][userdata[username][1]].append(int(response))
    update.message.reply_text('Please enter the Fat of food',reply_markup=ReplyKeyboardRemove())
    
    return FOODFAT

def foodFat(update: Update, context: CallbackContext) -> int:
    response = update.message.text
    if (not response.isdigit()):
        update.message.reply_text('Please give a number',
            reply_markup=ReplyKeyboardRemove(),
        )
        return FOODFAT
    username = update.message.from_user.username
    userdata[username][0][userdata[username][1]].append(int(response))
    update.message.reply_text('Your food has been added!',reply_markup=ReplyKeyboardRemove())
    f = open("userdata.txt", "w")
    f.write(json.dumps(userdata))
    
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
    
    dispatcher.add_handler(CommandHandler("info", info))
    dispatcher.add_handler(CommandHandler("recommended", recommended))
    dispatcher.add_handler(CommandHandler("daily", daily))
    dispatcher.add_handler(CommandHandler("monthly", monthly))

    # Add conversation handler with the states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add', add),
            CommandHandler('addfood', addFood)],
        states={
            FOOD: [MessageHandler(Filters.regex('^(Breakfast|Lunch|Dinner)$'), food)],
            MORE: [MessageHandler(Filters.text & ~Filters.command, more)],
            ADD: [MessageHandler(Filters.regex('^Yes$'), food), 
                MessageHandler(Filters.regex('^No$'), add_success)],
            FOODNAME: [MessageHandler(Filters.text, foodName)],
            FOODCAL: [MessageHandler(Filters.text, foodCal)],
            FOODCARB: [MessageHandler(Filters.text, foodCarb)],
            FOODPROTEIN: [MessageHandler(Filters.text, foodProtein)],
            FOODFAT: [MessageHandler(Filters.text, foodFat)],
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
