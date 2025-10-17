# ChatSorter Client

Add long-term memory to your chatbot in 5 minutes.

---

## Step 1: Get Your API Key

Email **theiogamer1st@gmail.com** with subject: **"ChatSorter Demo Key"**

You'll receive your API key within 24 hours.

Demo keys include:
- 10,000 messages/month
- 5,000 searches/month  
- Free during beta

---

## Step 2: Install Git (If You Don't Have It)

**Windows:** Download from https://git-scm.com/download/win
**Mac:** Already installed
**Linux:** `sudo apt install git`

After installing, **restart your terminal**.

Check if Git is installed:
```bash
git --version
```

---

## Step 3: Install ChatSorter
```bash
pip install git+https://github.com/codeislife12/chatsorter-client.git
```

---

## Step 4: Add 3 Lines to Your Chatbot

### Line 1: Import ChatSorter
```python
from chatsorter_client import ChatSorterClient
```

### Line 2: Initialize with Your API Key
```python
client = ChatSorterClient(api_key="sk_live_YOUR_KEY_HERE")
```

### Line 3: Store and Search Messages
```python
# Store a message
client.process(chat_id="user_123", message="I love pizza")

# Search memory
results = client.search(chat_id="user_123", query="What does user like?")
```

**That's it!** Your chatbot now has memory.

---

## Full Example: Flask Chatbot
```python
from flask import Flask, request, jsonify
from chatsorter_client import ChatSorterClient

app = Flask(__name__)

# Initialize ChatSorter
client = ChatSorterClient(api_key="sk_live_YOUR_KEY_HERE")

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    user_id = request.json['user_id']
    
    # 1. Store message in memory
    client.process(chat_id=user_id, message=user_message)
    
    # 2. Search for relevant memories
    memories = client.search(chat_id=user_id, query=user_message)
    
    # 3. Build context from memories
    context = ""
    if memories:
        for mem in memories[:3]:
            context += f"Memory: {mem['content']}\n"
    
    # 4. Send to your AI model with context
    prompt = f"{context}\nUser: {user_message}"
    response = your_ai_model.generate(prompt)  # Your model here
    
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run()
```

---

## What is `chat_id`?

A unique identifier for each user/conversation.

Examples:
- `"user_123"` - Individual user
- `"conversation_abc"` - Group chat
- `request.session['user_id']` - From your session

**Each chat_id gets its own separate memory.**

---

## Need Help?

Email: theiogamer1st@gmail.com

---

## Pricing

Free during beta. Paid plans from $40/month after launch.
