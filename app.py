import os
import json
import logging
import yaml
from flask import Flask, render_template, request, jsonify
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer, ChatterBotCorpusTrainer
from chatterbot.comparisons import LevenshteinDistance
from chatterbot.response_selection import get_first_response
from chatterbot.logic import BestMatch
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
import sqlite3
from datetime import datetime

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize chatbot with improved configuration
chatbot = ChatBot(
    'SupportBot',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    database_uri='sqlite:///chatbot.sqlite3',
    logic_adapters=[
        {
            'import_path': 'chatterbot.logic.BestMatch',
            'default_response': 'I am sorry, but I do not understand. Could you please rephrase your question?',
            'maximum_similarity_threshold': 0.65,
            'statement_comparison_function': LevenshteinDistance,
            'response_selection_method': get_first_response
        }
    ],
    preprocessors=[
        'chatterbot.preprocessors.clean_whitespace',
        'chatterbot.preprocessors.convert_to_ascii',
        'chatterbot.preprocessors.unescape_html'
    ]
)

def load_custom_training():
    try:
        with open('custom_training.yml', 'r', encoding='utf-8') as file:
            training_data = yaml.safe_load(file)
            
        conversations = training_data.get('conversations', [])
        trainer = ListTrainer(chatbot)
        
        for conversation in conversations:
            if isinstance(conversation, list) and len(conversation) == 2:
                question = str(conversation[0])
                answer = str(conversation[1])
                trainer.train([question, answer])
                
                # Add variations with common question words
                question_words = ['what', 'how', 'when', 'where', 'why', 'can', 'do', 'is', 'are']
                if any(word in question.lower() for word in question_words):
                    # Add variations without question words
                    words = question.lower().split()
                    filtered_words = [word for word in words if word not in question_words]
                    if filtered_words:
                        trainer.train([' '.join(filtered_words), answer])
                
        logger.info("Successfully loaded custom training data")
    except Exception as e:
        logger.error(f"Error loading custom training: {str(e)}")

def train_chatbot():
    try:
        # Train with custom data
        load_custom_training()
        
        # Train with ChatterBot corpus
        trainer = ChatterBotCorpusTrainer(chatbot)
        trainer.train(
            "chatterbot.corpus.english.greetings",
            "chatterbot.corpus.english.conversations"
        )
        
        logger.info("Chatbot training completed successfully")
    except Exception as e:
        logger.error(f"Error during chatbot training: {str(e)}")

def preprocess_text(text):
    try:
        # Convert to lowercase and strip whitespace
        text = text.lower().strip()
        
        # Common greetings and questions that should be preserved as-is
        preserved_phrases = [
            'hello', 'hi', 'hey', 'how are you', 
            'good morning', 'good afternoon', 'good evening',
            'what is', 'how do i', 'where is', 'when will',
            'what are', 'how can', 'where can', 'when can',
            'can i', 'do you', 'is there', 'are there'
        ]
        
        for phrase in preserved_phrases:
            if phrase in text:
                return text
        
        # For other queries, do minimal preprocessing
        # Only remove basic stopwords that don't affect meaning
        basic_stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to'}
        words = word_tokenize(text)
        filtered_words = [word for word in words if word.lower() not in basic_stopwords]
        
        return ' '.join(filtered_words)
    except Exception as e:
        logger.error(f"Error in text preprocessing: {str(e)}")
        return text

def log_conversation(user_message, bot_response):
    try:
        conn = sqlite3.connect('chatbot.sqlite3')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT,
                bot_response TEXT,
                timestamp DATETIME
            )
        ''')
        
        cursor.execute('''
            INSERT INTO conversations (user_message, bot_response, timestamp)
            VALUES (?, ?, ?)
        ''', (user_message, bot_response, datetime.now()))
        
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error logging conversation: {str(e)}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'response': 'Please enter a message.'})
        
        # Preprocess the user's message
        processed_message = preprocess_text(user_message)
        
        # Get chatbot response
        bot_response = chatbot.get_response(processed_message)
        response_text = str(bot_response)
        
        # If we get a default response, try with the original message
        if response_text == 'I am sorry, but I do not understand. Could you please rephrase your question?':
            bot_response = chatbot.get_response(user_message)
            response_text = str(bot_response)
            
            # If still no match, try with a more lenient preprocessing
            if response_text == 'I am sorry, but I do not understand. Could you please rephrase your question?':
                words = user_message.lower().split()
                filtered_words = [word for word in words if len(word) > 2]  # Keep only significant words
                if filtered_words:
                    bot_response = chatbot.get_response(' '.join(filtered_words))
                    response_text = str(bot_response)
        
        # Log the conversation
        log_conversation(user_message, response_text)
        
        return jsonify({'response': response_text})
    except Exception as e:
        logger.error(f"Error getting response: {str(e)}")
        return jsonify({'response': 'I am sorry, but I encountered an error. Please try again.'})

if __name__ == '__main__':
    train_chatbot()
    app.run(debug=True)
