# Supportify - Customer Support Chatbot

A smart chatbot for handling customer support queries using Python, Flask, and ChatterBot.

## Features

- Real-time chat interface
- Natural language processing using NLTK
- SQLite database for storing conversations
- Modern and responsive UI
- Pre-trained with English corpus

## Setup Instructions

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to:
```
http://localhost:5000
```

## Project Structure

- `app.py`: Main Flask application
- `templates/index.html`: Frontend chat interface
- `requirements.txt`: Project dependencies
- `database.sqlite3`: SQLite database (created automatically)

## Technologies Used

- Python 3.x
- Flask
- ChatterBot
- NLTK
- SQLite
- Bootstrap 5 
