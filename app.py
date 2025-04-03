from flask import Flask, render_template, request, jsonify
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer, ListTrainer
from chatterbot.response_selection import get_random_response
from chatterbot.logic import BestMatch
import sqlite3
import nltk
import os
import yaml
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import logging
import traceback
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download NLTK data if not already downloaded
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('wordnet')
    nltk.download('punkt_tab')

# Initialize Flask app
app = Flask(__name__)

# Initialize the chatbot with a more specific configuration
chatbot = ChatBot(
    'Supportify',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    database_uri='sqlite:///chatbot.sqlite3',
    logic_adapters=[
        {
            'import_path': 'chatterbot.logic.BestMatch',
            'default_response': 'I am sorry, but I do not understand. Please try rephrasing your question.',
            'maximum_similarity_threshold': 0.60  # Even lower threshold for better matching
        }
    ],
    response_selection_method=get_random_response
)

def load_custom_training():
    try:
        with open('custom_training.yml', 'r', encoding='utf-8') as file:
            training_data = yaml.safe_load(file)
            conversations = training_data.get('conversations', [])
            
            # Create a list trainer for custom data
            list_trainer = ListTrainer(chatbot)
            
            # Train with each conversation
            for conversation in conversations:
                if isinstance(conversation, list) and len(conversation) == 2:
                    # Convert to strings to ensure proper format
                    question = str(conversation[0])
                    answer = str(conversation[1])
                    list_trainer.train([question, answer])
                    
                    # Add variations with common typos and word order changes
                    if "product" in question.lower():
                        # Add variation with typo
                        typo_question = question.lower().replace("available", "availabe")
                        list_trainer.train([typo_question, answer])
                        
                        # Add variation with different word order
                        if "is" in question.lower():
                            reordered = question.lower().replace("is", "").strip()
                            list_trainer.train([reordered, answer])
                
            logger.info(f"Custom training data loaded successfully with {len(conversations)} conversations")
    except Exception as e:
        logger.error(f"Error loading custom training: {str(e)}")
        logger.error(traceback.format_exc())

# Train the chatbot with both custom data and ChatterBot corpus
def train_chatbot():
    try:
        # First train with custom data
        load_custom_training()
        
        # Then train with ChatterBot corpus
        trainer = ChatterBotCorpusTrainer(chatbot)
        trainer.train(
            "chatterbot.corpus.english.greetings",
            "chatterbot.corpus.english.conversations"
        )
        logger.info("Chatbot training completed successfully")
    except Exception as e:
        logger.error(f"Error during training: {str(e)}")
        logger.error(traceback.format_exc())

# Train the chatbot when the application starts
train_chatbot()

# Function to preprocess user input
def preprocess_text(text):
    try:
        # Convert to lowercase
        text = text.lower()
        
        # Fix common typos
        text = text.replace("availabe", "available")
        text = text.replace("shipment", "shipment")
        text = text.replace("delivery", "delivery")
        
        # Remove punctuation except for question marks
        text = re.sub(r'[^\w\s?]', '', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords but keep important words
        stop_words = set(stopwords.words('english'))
        keep_words = {'how', 'does', 'is', 'are', 'what', 'when', 'where', 'can', 'my', 'shipment', 'delivery', 'order', 'track', 'status', 'hello', 'hi', 'hey', 'product', 'available', 'stock'}
        
        filtered_tokens = [word for word in tokens if word not in stop_words or word in keep_words]
        
        # Join tokens back into a string
        processed = ' '.join(filtered_tokens)
        
        logger.info(f"Original: {text} | Processed: {processed}")
        return processed
    except Exception as e:
        logger.error(f"Error in preprocessing: {str(e)}")
        logger.error(traceback.format_exc())
        return text  # Return original text if preprocessing fails

# Function to log conversation in SQLite
def log_conversation(user_input, bot_response):
    try:
        conn = sqlite3.connect('faq.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS conversations 
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                           user_input TEXT, 
                           bot_response TEXT, 
                           timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        cursor.execute("INSERT INTO conversations (user_input, bot_response) VALUES (?, ?)", 
                       (user_input, bot_response))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error logging conversation: {str(e)}")
        logger.error(traceback.format_exc())

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Chat route
@app.route('/get_response', methods=['POST'])
def get_response():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'response': 'Please provide a message.'})
        
        # Preprocess the input
        processed_input = preprocess_text(user_message)
        
        # Get response from chatbot
        response = chatbot.get_response(processed_input)
        
        # Log the conversation
        logger.info(f"User: {user_message}")
        logger.info(f"Bot: {response}")
        
        # Log the conversation
        log_conversation(user_message, str(response))
        
        return jsonify({'response': str(response)})
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'response': 'Hello! How can I help you today?'})

if __name__ == '__main__':
    app.run(debug=True)
