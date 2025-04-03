from flask import Flask, render_template, request
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
import sqlite3
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Download NLTK data (run once)
nltk.download('punkt')
nltk.download('stopwords')

# Initialize Flask app
app = Flask(__name__)

# Initialize Chatbot
chatbot = ChatBot(
    'SupportBot',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    database_uri='sqlite:///faq.db',
    logic_adapters=[
        'chatterbot.logic.BestMatch',
        'chatterbot.logic.MathematicalEvaluation'
    ]
)

# Function to preprocess user input
def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]
    return ' '.join(filtered_tokens)

# Function to log conversation in SQLite
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

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Chat route
@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.form['message']
    processed_input = preprocess_text(user_input)
    bot_response = str(chatbot.get_response(processed_input))
    
    # Log the conversation
    log_conversation(user_input, bot_response)
    
    return bot_response

if __name__ == '__main__':
    app.run(debug=True)