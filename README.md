# ChatSorter Client

**Add long-term memory to your chatbot in 1 line of code.**

No vector databases. No complicated setup. Just memory that works.

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Get Your API Key

Email **theiogamer1st@gmail.com** with subject: **"ChatSorter Demo Key"**

You'll receive your API key within 24 hours.

**Demo keys include:**
- ✅ 10,000 messages/month
- ✅ 5,000 searches/month  
- ✅ Free during beta

---

### Step 2: Install Git (If You Don't Have It)

**Windows:** https://git-scm.com/download/win  
**Mac:** Already installed  
**Linux:** `sudo apt install git`

After installing, **restart your terminal**.

Verify Git is installed:
```bash
git --version
```

---

### Step 3: Install ChatSorter
```bash
pip install git+https://github.com/codeislife12/chatsorter-client.git
```

---

### Step 4: Add 1 Line to Your Chatbot

#### Before ChatSorter:
```python
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    
    # Your old prompt
    prompt = f"User: {user_message}"
    
    response = your_model.generate(prompt)
    return jsonify({'response': response})
```

#### After ChatSorter (1 line change):
```python
from chatsorter_client import ChatSorter

chatsorter = ChatSorter(api_key="sk_live_YOUR_KEY_HERE")

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    user_id = "user_123"  # Unique per user
    
    # Replace your prompt line with this:
    prompt = chatsorter.build_prompt(user_id, user_message, "User: {message}")
    
    response = your_model.generate(prompt)
    return jsonify({'response': response})
```

**That's it!** Your chatbot now has long-term memory across sessions.

---

## 📖 Full Examples

### Example 1: Flask + Local GGUF (Llama/Mistral)
```python
from flask import Flask, request, jsonify
from llama_cpp import Llama
from chatsorter_client import ChatSorter

app = Flask(__name__)

# Initialize your model
llm = Llama(model_path="your-model.gguf", n_ctx=2048)

# Initialize ChatSorter
chatsorter = ChatSorter(api_key="sk_live_YOUR_KEY_HERE")

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    user_id = request.json.get('user_id', 'default_user')
    
    # Build prompt with memory (1 line)
    prompt = chatsorter.build_prompt(user_id, user_message, 
        prompt_template="<s>[INST] {context}{message} [/INST]")
    
    # Generate response
    response = llm(prompt, max_tokens=512)
    bot_response = response['choices'][0]['text'].strip()
    
    return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run(port=5000)
```

### Example 2: Flask + OpenAI
```python
from flask import Flask, request, jsonify
from openai import OpenAI
from chatsorter_client import ChatSorter

app = Flask(__name__)
openai_client = OpenAI(api_key="your-openai-key")
chatsorter = ChatSorter(api_key="sk_live_YOUR_KEY_HERE")

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    user_id = request.json.get('user_id', 'default_user')
    
    # Get memory context
    context = chatsorter.get_context(user_id, user_message)
    
    # Store message
    chatsorter.process(user_id, user_message)
    
    # Call OpenAI with context
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"Previous context:\n{context}"},
            {"role": "user", "content": user_message}
        ]
    )
    
    return jsonify({'response': response.choices[0].message.content})

if __name__ == '__main__':
    app.run(port=5000)
```

### Example 3: Flask + Anthropic Claude
```python
from flask import Flask, request, jsonify
from anthropic import Anthropic
from chatsorter_client import ChatSorter

app = Flask(__name__)
anthropic_client = Anthropic(api_key="your-anthropic-key")
chatsorter = ChatSorter(api_key="sk_live_YOUR_KEY_HERE")

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    user_id = request.json.get('user_id', 'default_user')
    
    # Get memory context
    context = chatsorter.get_context(user_id, user_message)
    
    # Store message
    chatsorter.process(user_id, user_message)
    
    # Call Claude with context
    response = anthropic_client.messages.create(
        model="claude-3-5-sonnet-20241022",
        system=f"Previous context:\n{context}",
        messages=[{"role": "user", "content": user_message}]
    )
    
    return jsonify({'response': response.content[0].text})

if __name__ == '__main__':
    app.run(port=5000)
```

---

## 🎯 What is `chat_id`?

A unique identifier for each user or conversation.

**Examples:**
- `"user_123"` - Individual user
- `request.session['user_id']` - From your session
- `str(uuid.uuid4())` - Generate new ID per conversation

**Each `chat_id` gets its own separate memory.**

---

## 🔧 Advanced Usage

### Manual Control (Don't use `build_prompt`)
```python
# Store message manually
chatsorter.process(chat_id="user123", message="I love pizza")

# Search memory manually
results = chatsorter.search(chat_id="user123", query="food preferences")

if results['result']['found']:
    for item in results['result']['results']:
        print(f"- {item['content']}")
        print(f"  Importance: {item['decayed_importance']}")
        print(f"  Relevance: {item['retrieval_score']}")
```

### Get Statistics
```python
stats = chatsorter.get_stats(chat_id="user123")
print(f"Messages: {stats['stats']['message_count']}")
print(f"Summaries: {stats['stats']['summary_files']}")
```

### Health Check
```python
health = chatsorter.health_check()
print(f"Status: {health['status']}")
print(f"Version: {health['version']}")
```

---

## 💡 How It Works

1. **Every message is stored** with importance scoring (0-10)
2. **Semantic search** finds relevant memories when needed
3. **Time decay** - old memories naturally fade
4. **Entity extraction** - tracks people, places, preferences
5. **Automatic summarization** - condenses long conversations

---

## 💰 Pricing

**Demo:** Free during beta  
**After Launch:** $40-80/month (vs competitors at $200+)

---

## ❓ Troubleshooting

### "No module named chatsorter_client"

Make sure Git is installed and try again:
```bash
git --version
pip install git+https://github.com/codeislife12/chatsorter-client.git
```

### "401 Unauthorized"

Check your API key is correct:
```python
chatsorter = ChatSorter(api_key="sk_live_YOUR_ACTUAL_KEY")
```

### Memory not working?

Make sure you're using the same `chat_id` across requests:
```python
# ❌ Bad - generates new ID each time
chat_id = str(uuid.uuid4())

# ✅ Good - consistent per user
chat_id = request.session['user_id']
```

---

## 📧 Need Help?

Email: **theiogamer1st@gmail.com**

---

## 🎉 You're Done!

Your chatbot now has long-term memory. Test it by:
1. Telling it your name
2. Asking "What's my name?" in a new conversation
3. It should remember!

---

**Built with ❤️ by the ChatSorter team**