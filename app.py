from flask import Flask, render_template, request, jsonify
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer, ListTrainer
from chatterbot.logic import LogicAdapter
import sqlite3
import nltk
import os
import yaml
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from datetime import datetime

# Download NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('wordnet')
    nltk.download('punkt_tab')

app = Flask(__name__)

# Custom Logic Adapter
class DynamicResponseAdapter(LogicAdapter):
    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)

    def can_process(self, statement):
        return True

    def process(self, statement, additional_response_selection_parameters=None):
        from chatterbot.conversation import Statement
        input_text = statement.text.lower()

        if "how are you" in input_text:
            response_text = "I'm doing great, thanks for asking! How can I assist you today?"
            confidence = 0.95
        elif "weather" in input_text:
            response_text = "I don’t have real-time weather data, but you can check your local weather service!"
            confidence = 0.8
        elif "time" in input_text:
            current_time = datetime.now().strftime("%H:%M:%S")
            response_text = f"The current time is {current_time} (based on my server’s clock)."
            confidence = 0.8
        else:
            response_text = "I’m not sure about that, but I’m here to help with business-related questions. What else can I assist you with?"
            confidence = 0.1

        response = Statement(text=response_text)
        response.confidence = confidence
        return response

# Initialize Chatbot
chatbot = ChatBot(
    'Supportify',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    logic_adapters=[
        {
            'import_path': '__main__.DynamicResponseAdapter'
        },
        {
            'import_path': 'chatterbot.logic.BestMatch',
            'default_response': 'I am sorry, but I do not understand.',
            'maximum_similarity_threshold': 0.90
        },
        'chatterbot.logic.MathematicalEvaluation'
    ],
    database_uri='sqlite:///database.sqlite3'
)

# Load and train with custom data
def load_custom_training():
    try:
        with open('custom_training.yml', 'r', encoding='utf-8') as file:
            training_data = yaml.safe_load(file)
            trainer = ListTrainer(chatbot)
            for conversation in training_data['conversations']:
                trainer.train(conversation)
    except Exception as e:
        print(f"Error loading custom training: {str(e)}")

trainer = ChatterBotCorpusTrainer(chatbot)
trainer.train("chatterbot.corpus.english")
load_custom_training()

# Preprocess text
def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    if len(tokens) > 3:
        filtered_tokens = [word for word in tokens if word not in stop_words]
    else:
        filtered_tokens = tokens
    processed = ' '.join(filtered_tokens)
    print(f"Original: {text} | Processed: {processed}")
    return processed

# Log conversation
def log_conversation(user_input, bot_response):
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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    if not request.is_json:
        return jsonify({'response': 'Error: Request must be JSON'}), 415
    
    try:
        user_input = request.json.get('message', '')
        if not user_input:
            return jsonify({'response': 'Error: No message provided'}), 400
        
        processed_input = preprocess_text(user_input)
        response = str(chatbot.get_response(processed_input))
        log_conversation(user_input, response)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'response': f"I'm sorry, I encountered an error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)