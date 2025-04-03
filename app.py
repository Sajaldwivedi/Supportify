from flask import Flask, request, jsonify
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

app = Flask(__name__)

# Sample responses
responses = {
    "hello": "Hello! How can I help you today?",
    "pricing": "You can check our pricing details on our website.",
    "refund": "Refunds are processed within 5-7 business days.",
    "support": "Our support team is available 24/7. How can we assist you?",
    "bye": "Goodbye! Have a great day!",
}

# Preprocess input (tokenization + removing stopwords)
def preprocess(text):
    nltk.download("punkt")
    nltk.download("stopwords")
    stop_words = set(stopwords.words("english"))
    words = word_tokenize(text.lower())
    return [word for word in words if word.isalnum() and word not in stop_words]

# Function to generate response
def get_response(user_input):
    words = preprocess(user_input)
    for word in words:
        if word in responses:
            return responses[word]
    return "I'm sorry, I didn't understand. Can you please rephrase?"

# API route for chatbot
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    bot_response = get_response(user_message)
    return jsonify({"response": bot_response})

if __name__ == "__main__":
    app.run(debug=True)
