# NAUB Enquiry Chatbot — Setup & Run Guide

## Project Overview
An AI-powered enquiry chatbot for Nigerian Army University Biu (NAUB).
Built with Python, Django, and a TF-IDF + Cosine Similarity matching engine.

---

## Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

---

## Step-by-Step Setup (Windows)

### 1. Install Python
Download from https://www.python.org/downloads/
During installation, tick "Add Python to PATH".

### 2. Create a virtual environment
Open Command Prompt (cmd) in the project folder, then run:
```
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```
pip install -r requirements.txt
```

### 4. Run database migrations
```
python manage.py migrate
```

### 5. Create an admin account (optional — for admin dashboard)
```
python manage.py createsuperuser
```
Follow the prompts to set username and password.

### 6. Start the development server
```
python manage.py runserver
```

### 7. Open in your browser
Go to: http://127.0.0.1:8000/

Admin dashboard: http://127.0.0.1:8000/admin/

---

## Project Structure

```
naub_chatbot/
├── manage.py                     # Django management script
├── requirements.txt              # Python dependencies
├── db.sqlite3                    # SQLite database (auto-created)
├── knowledge_base/
│   └── faqs.json                 # NAUB FAQ data (edit to add more Q&A)
├── naub_chatbot/
│   ├── settings.py               # Django configuration
│   └── urls.py                   # Root URL routing
└── chatbot/
    ├── engine.py                 # TF-IDF + Cosine Similarity matching engine
    ├── models.py                 # Database models (ChatSession, ConversationLog)
    ├── views.py                  # Django views (chat page + API endpoint)
    ├── urls.py                   # Chatbot URL routes
    ├── admin.py                  # Admin dashboard configuration
    ├── templates/chatbot/
    │   └── index.html            # Chat interface HTML
    └── static/chatbot/
        ├── css/style.css         # Chat interface styles
        └── js/chat.js            # Frontend JavaScript
```

---

## How to Add More FAQ Entries
1. Open `knowledge_base/faqs.json`
2. Add a new intent block following this format:
```json
{
  "id": 21,
  "intent": "your_intent_name",
  "patterns": [
    "question variant 1",
    "question variant 2",
    "question variant 3"
  ],
  "response": "Your answer here."
}
```
3. Save the file and restart the server — changes take effect immediately.

---

## Testing the Engine Directly
```
python chatbot/engine.py
```
This runs the engine against sample queries and prints matched intents and scores.
