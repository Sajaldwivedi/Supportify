from flask import Flask, request, jsonify, render_template_string
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string

app = Flask(__name__)

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# Predefined responses for common customer queries
responses = {
    "greeting": "Hello! How can I assist you today?",
    "order_status": "Could you please provide your order number so I can check the status?",
    "shipping": "Shipping usually takes 3-5 business days. Would you like to track your package?",
    "return": "To process a return, please provide your order number and reason for return.",
    "hours": "Our customer support is available 24/7!",
    "default": "I'm sorry, I didn't quite understand that. How can I help you?"
}

def classify_intent(user_input):
    tokens = word_tokenize(user_input.lower())
    stop_words = set(stopwords.words('english') + list(string.punctuation))
    filtered_tokens = [token for token in tokens if token not in stop_words]
    
    if any(word in filtered_tokens for word in ['hi', 'hello', 'hey']):
        return "greeting"
    elif any(word in filtered_tokens for word in ['order', 'status', 'where']):
        return "order_status"
    elif any(word in filtered_tokens for word in ['shipping', 'delivery', 'track']):
        return "shipping"
    elif any(word in filtered_tokens for word in ['return', 'refund', 'exchange']):
        return "return"
    elif any(word in filtered_tokens for word in ['hours', 'time', 'available']):
        return "hours"
    else:
        return "default"

def get_response(user_input):
    intent = classify_intent(user_input)
    return responses.get(intent, responses["default"])

@app.route('/')
def home():
    return "Customer Support Chatbot is running!"

@app.route('/interface')
def chat_interface():
    try:
        with open('index.html', 'r') as f:
            html_content = f.read()
        return render_template_string(html_content)
    except FileNotFoundError:
        return "Error: index.html not found in the same directory as app.py", 500

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    print("Received data:", data)  # Debug print
    user_message = data.get('message', '')
    print("User message:", user_message)  # Debug print
    
    if not user_message:
        return jsonify({'response': 'Please send a message!'}), 400
    
    bot_response = get_response(user_message)
    print("Bot response:", bot_response)  # Debug print
    return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)