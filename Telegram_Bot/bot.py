import telebot, os
from telebot import types
import requests

# Create a new bot instance
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    # Send the welcome message
    bot.send_message(message.chat.id, "Welcome to Life Bot! I am here to help you with your emergency needs and services. Use /emergency command so that I can assist you with your needs.")

@bot.message_handler(commands=['emergency'])
def handle_emergency(message):
    # Create emergency options as inline buttons
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    poison = types.InlineKeyboardButton('Poisoning', callback_data='poison')
    breathing_difficulty = types.InlineKeyboardButton('Breathing Difficulty', callback_data='breathing')
    heartache = types.InlineKeyboardButton('Heart Ache', callback_data='heart')
    stomach_pain = types.InlineKeyboardButton('Stomach Pain', callback_data='stomach')
    others = types.InlineKeyboardButton('Others....', callback_data='others')

    # Add emergency options to the keyboard
    keyboard.add(poison, breathing_difficulty, heartache, stomach_pain, others)

    bot.send_message(message.chat.id, 'Please select the type of medical emergency:', reply_markup=keyboard)


@bot.message_handler(content_types=['location'])
def handle_location(message):
    # Get user's location details
    latitude = message.location.latitude
    longitude = message.location.longitude

    data = {
        'lat': latitude,
        'long': longitude
    }

    url = 'http://127.0.0.1:5000/save'  # Replace with your actual URL
    response = requests.post(url, json=data)

    print(response.json())

    # Confirm the location with the user
    bot.send_message(message.chat.id, f"Your location: Latitude: {latitude}, Longitude: {longitude}")

# Register button handler

@bot.message_handler(commands=['register'])
def register_user(message):
    # Send the initial registration message and request for name
    bot.send_message(message.chat.id, "Register yourself here")
    bot.send_message(message.chat.id, "Please enter your name:")

    bot.register_next_step_handler(message, get_name)

def get_name(message):
    name = message.text

    data = {
        'name': name,
        'tel_id': message.chat.id
    }

    url = 'http://127.0.0.1:5000/registerDriver'  # Replace with your actual URL
    response = requests.post(url, json=data)

    # Send a confirmation message to the user
    bot.send_message(message.chat.id, f"Thanks for registering, {name}! {response.json()['status']}")

        
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data in ['poison', 'breathing', 'heartache', 'stomach_pain', 'others']:
        # Request user's location
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        location_button = types.KeyboardButton(text="Send Location", request_location=True)
        markup.add(location_button)

        bot.send_message(call.message.chat.id, "Please share your location:", reply_markup=markup)
        bot.register_next_step_handler(call.message, getDriver)
        # @bot.message_handler(content_types=['location'])
    elif call.data in ['yes', 'no']:
        if call.data == 'yes':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            driver_avail(call.message.chat.id)
        elif call.data == 'no':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, "Alert Removed")

def driver_avail(chat_id):
    bot.send_message(chat_id, "You responded with yes")

def getDriver(message):
    # Send GET request to the server with location parameters
    lat = message.location.latitude
    long = message.location.longitude
    url = f"http://127.0.0.1:5000/getDriver"
    response = requests.get(url)
    details = response.json()
    for detail in details:
        chat_id = detail['tel_id']
        name = detail['name']
        msg = f"Hello {name} there is an alert nearby!! Please repond weather you are available or not!"
        markup = types.InlineKeyboardMarkup(row_width=2)
        yes_btn = types.InlineKeyboardButton("Yes", callback_data='yes')
        no_btn = types.InlineKeyboardButton("No", callback_data='no')
        markup.add(yes_btn, no_btn)
        bot.send_location(chat_id, lat, long)
        bot.send_message(chat_id, msg, reply_markup=markup)
# Start the bot
bot.polling()
