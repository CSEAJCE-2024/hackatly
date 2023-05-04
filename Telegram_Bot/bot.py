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
    fever = types.InlineKeyboardButton('Fever', callback_data='fever')
    breathing_difficulty = types.InlineKeyboardButton('Breathing Difficulty', callback_data='breathing')
    heartache = types.InlineKeyboardButton('Heart Ache', callback_data='heart')
    stomach_pain = types.InlineKeyboardButton('Stomach Pain', callback_data='stomach')
    others = types.InlineKeyboardButton('Others....', callback_data='others')

    # Add emergency options to the keyboard
    keyboard.add(fever, breathing_difficulty, heartache, stomach_pain, others)

    bot.send_message(message.chat.id, 'Please select the type of medical emergency:', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data in ['fever', 'breathing', 'heartache', 'stomach_pain', 'others']:
        # Request user's location
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        location_button = types.KeyboardButton(text="Send Location", request_location=True)
        markup.add(location_button)

        bot.send_message(call.message.chat.id, "Please share your location:", reply_markup=markup)


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
    register_btn = types.InlineKeyboardMarkup(row_width = 2)
    register = types.InlineKeyboardButton('Register', callback_data='register')
    register_btn.add(register)

    bot.send_message(message.chat.id, "Register yourself here", reply_markup=register_btn)

# User input handler
@bot.message_handler(func=lambda message: True)
def handle_user_input(message):
    # Check if the user is in the registration state
    name = message.text
    bot.send_message(message.chat.id, f"Registration successful! Welcome, {name}.")

        
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == 'fever' or call.data == 'breathing' or call.data == 'heartache' or call.data == 'stomach_pain' or call.data == 'others':
        # Request user's location
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        location_button = types.KeyboardButton(text="Send Location", request_location=True)
        markup.add(location_button)

        bot.send_message(call.message.chat.id, "Please share your location:", reply_markup=markup)
        
    if call.data == 'register':
        # Send a message asking the user to enter their name
        bot.send_message(call.message.chat.id, "Please enter your name:")



# Start the bot
bot.polling()
