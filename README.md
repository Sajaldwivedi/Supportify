# Supportify - Intelligent Customer Support Chatbot

A modern, AI-powered customer support chatbot built with Python, Flask, and ChatterBot. Supportify provides instant, accurate responses to customer queries across various categories including shipping, returns, account management, and payment information.

## 🌟 Features

- **Smart Response System**
  - Natural Language Processing using NLTK
  - Context-aware responses
  - Pre-trained with extensive customer support knowledge
  - Custom training data for specific business needs

- **Modern User Interface**
  - Clean, responsive design
  - Category-based question organization
  - Real-time chat experience
  - Suggested questions for quick access
  - Mobile-friendly interface

- **Category Management**
  - Organized topics: Shipping, Returns, Account, Payment, Support
  - Dynamic question suggestions
  - Easy navigation between categories
  - All Topics view for general queries

- **Technical Features**
  - SQLite database for conversation storage
  - Real-time message processing
  - Typing indicators for better UX
  - Error handling and logging
  - Customizable response thresholds

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/supportify.git
cd supportify
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and navigate to:
```
http://localhost:5000
```

## 📁 Project Structure

```
supportify/
├── app.py              # Main Flask application
├── custom_training.yml # Custom training data
├── requirements.txt    # Project dependencies
├── templates/
│   └── index.html     # Frontend chat interface
└── chatbot.sqlite3    # SQLite database (created automatically)
```

## 🛠️ Customization

### Adding New Responses

1. Edit `custom_training.yml` to add new question-answer pairs:
```yaml
conversations:
  - - "Your question here?"
    - "Your answer here."
```

2. Categories are automatically detected and organized in the UI.

### Modifying the Interface

- Edit `templates/index.html` to customize:
  - Color scheme (CSS variables in `:root`)
  - Layout and dimensions
  - Category buttons
  - Question suggestions

## 🤖 How It Works

1. **User Input Processing**
   - Text preprocessing with NLTK
   - Stopword removal
   - Context preservation
   - Similarity matching

2. **Response Generation**
   - Best match selection
   - Category-based filtering
   - Default response handling
   - Error management

3. **Data Storage**
   - Conversation logging
   - SQLite database integration
   - Persistent storage

## 📱 Mobile Responsiveness

The interface is fully responsive and works on:
- Desktop browsers
- Tablets
- Mobile devices
- Different screen sizes

## 🔧 Configuration

Key configuration options in `app.py`:
- Similarity threshold
- Response selection method
- Database settings
- Logging preferences

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support

For support, email support@example.com or open an issue in the repository.

---

Made with ❤️ by [Your Name] 
