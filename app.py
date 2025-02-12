import asyncio
from telegram import Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telethon import TelegramClient, errors
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import threading
import gradio as gr
import json
import os
import logging
import re
import time
import joblib  # Import joblib to load the model and vectorizer

# Download VADER lexicon if not already downloaded
nltk.download('vader_lexicon')

# Load the trained model and vectorizer
model = joblib.load('scam_model.pkl')  # Load the trained model
vectorizer = joblib.load('vectorizer.pkl')  # Load the vectorizer

TOKEN = '7718098452:AAFNngD67_ymjhO-GzRJkSnyOZ0P4N_OUPA'

# Set up the Telegram Client (using Telethon)
api_id = 29680616
api_hash = '673acd28ac10e32b05ef7facbdd4d502'
client = TelegramClient('session_name', api_id, api_hash)

# Set up sentiment analyzer and keywords for scam detection
analyzer = SentimentIntensityAnalyzer()
scam_keywords = ["guaranteed returns", "crypto", "forex", "investment", "risk-free", "profits", "scam"]

# Logging setup
logging.basicConfig(
    filename='bot_logs.log',
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Global list to store user IDs
user_list = set()

# Function to fetch messages from a channel
async def fetch_channel_messages(channel_name):
    try:
        async with client:
            messages = []
            async for message in client.iter_messages(channel_name,limit=100):
                if message.text:
                    messages.append({
                        'sender': message.sender_id,
                        'text': message.text,
                        'date': message.date
                    })
            return messages
    except errors.UsernameInvalidError:
        print(f"Invalid username: {channel_name}")
        return []

# Check if the message contains any scam-related keywords
def contains_scam_keywords(text: str) -> bool:
    scam_patterns = r"\b(guaranteed\s*returns|crypto|forex|investment|risk[-\s]*free|profits|scam)\b"
    return bool(re.search(scam_patterns, text, re.IGNORECASE))

scam_patterns = r"\b(guaranteed\s*returns|crypto|forex|investment|risk[-\s]*free|profits|scam)\b"

# Analyze investment scam and return sentiment scores
def analyze_investment_scam(text: str):
    if text is None:
        return False, None  # Return default if text is empty or None
    
    # Preprocess the text (consistent with training)
    processed_text = text.lower()
    
    # Vectorize the text using the loaded vectorizer
    text_vectorized = vectorizer.transform([processed_text])
    
    # Predict using the loaded model
    scam_detected = model.predict(text_vectorized)[0]  # 1 for scam, 0 for normal
    
    # Get sentiment score (optional, for additional context)
    sentiment_score = analyzer.polarity_scores(text)
    
    return scam_detected, sentiment_score

# Handler for receiving messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    scam_detected, sentiment_score = analyze_investment_scam(text)

    # Store the last message and prediction for feedback logging
    context.user_data['last_message'] = text
    context.user_data['last_prediction'] = "Scam" if scam_detected else "Safe"

    sentiment_text = f"Sentiment Score: {sentiment_score}"
    
    if scam_detected:
        response = f" This looks like a scam! {sentiment_text}\n\nIs this detection correct?"
    else:
        response = f"This seems safe. {sentiment_text}\n\nIs this detection correct?"

    # Show "Correct" and "Incorrect" buttons
    keyboard = [
        [InlineKeyboardButton(" Correct", callback_data="correct"),
         InlineKeyboardButton(" Incorrect", callback_data="incorrect")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(response, reply_markup=reply_markup)

# Button handler for feedback logging
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    print("Button pressed")  # Debugging line

    # Get the user ID from the callback query
    user_id = query.from_user.id
    print(f"User ID: {user_id}")  # Debugging line

    # Retrieve the last message and prediction from user data
    last_message = context.user_data.get('last_message', "No recorded message")
    last_prediction = context.user_data.get('last_prediction', "Unknown")

    # Get feedback (Correct or Incorrect)
    feedback = "Correct" if query.data == "correct" else "Incorrect"
    print(f"Feedback: {feedback}")  # Debugging line

    # Get the current timestamp
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f"Timestamp: {timestamp}")  # Debugging line

    # Log the feedback with all relevant information
    log_feedback(user_id, last_message, last_prediction, feedback, timestamp)

    # Send confirmation to the user
    await query.edit_message_text(f"Your feedback has been recorded: {feedback}")

# Updated log_feedback function to include timestamp
def log_feedback(user_id, message, prediction, feedback, timestamp):
    log_file = 'feedback_log.json'

    # Debugging line
    print("Logging feedback...")

    # Load existing feedback logs or create a new one
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            try:
                feedback_logs = json.load(f)
            except json.JSONDecodeError:
                feedback_logs = []
    else:
        feedback_logs = []

    # Append the new feedback entry with timestamp and user_id
    feedback_logs.append({
        'user_id': user_id,
        'message': message,
        'prediction': prediction,
        'feedback': feedback,
        'timestamp': timestamp  # Log timestamp
    })

    # Write the updated feedback logs to the file
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(feedback_logs, f, indent=4)

    print(f"Feedback from User {user_id} recorded: {feedback} at {timestamp}")  # Debugging line

# Command to start the bot
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_list.add(user_id)  # Add user to the list
    await update.message.reply_text("Welcome! I am your Scam Detection Bot.")

# Command to show help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("I help detect scams and analyze channels. Type a message to get started.")

# Command to analyze messages from a channel
async def analyze_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) > 0:
        channel_name = context.args[0]  # Channel username passed as argument
        messages = await fetch_channel_messages(channel_name)
        
        if not messages:
            await update.message.reply_text("No valid messages found or invalid channel.")
            return
        
        for message in messages:
            scam_detected, sentiment_score = analyze_investment_scam(message['text'])
            if scam_detected:
                await update.message.reply_text(f"Scam detected: {message['text']}")
            else:
                await update.message.reply_text(f"Normal message: {message['text']}")
    else:
        await update.message.reply_text("Please provide a channel username (link) after the command. Example: /analyze_channel channel_name_link")

# Function to send alerts to all users
async def send_alert_to_all(message_text: str):
    """
    Sends an alert to all users about a detected scam message.
    """
    for user_id in user_list:  # Assuming you have a list of user IDs
        try:
            await app.bot.send_message(chat_id=user_id, text=f"Scam Alert: {message_text}")
        except Exception as e:
            logging.error(f"Failed to send alert to user {user_id}: {e}")

# Set up the Application and Handlers
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler('start', start_command))
app.add_handler(CommandHandler('help', help_command))
app.add_handler(CommandHandler('analyze_channel', analyze_channel))  # Command for channel analysis
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CallbackQueryHandler(button_handler)) # Feedback responses

def run_bot():
    # Create a new event loop and set it as current for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    print("Bot is running...")
    loop.run_until_complete(app.run_polling(poll_interval=10))

if __name__ == "__main__":
    # Start the Telegram bot in a separate thread
    threading.Thread(target=run_bot).start()

    # Start Gradio interface in the main thread
    import gradio_interface  # This will launch your Gradio app