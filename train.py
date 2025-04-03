from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

# Create a new chatbot instance
chatbot = ChatBot(
    'SupportBot',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    database_uri='sqlite:///faq.db'  # SQLite database
)

# Define some FAQs as training data
faq_data = [
    "What are your business hours?", 
    "We are open from 9 AM to 5 PM, Monday to Friday.",
    "How can I contact support?",
    "You can email us at support@example.com or call us at 123-456-7890.",
    "What is your return policy?",
    "We offer a 30-day return policy for unused items with a receipt.",
    "Where are you located?",
    "Our office is at 123 Main Street, City, Country.",
    "How do I reset my password?",
    "Go to the login page and click 'Forgot Password' to reset it."
]

# Train the chatbot with FAQs
trainer = ListTrainer(chatbot)
trainer.train(faq_data)

print("Chatbot training completed!")