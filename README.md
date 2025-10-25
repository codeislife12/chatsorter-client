# ChatSorter - Memory for AI Chatbots

Add long-term memory to your chatbot in 5 minutes. Works with any LLM - GPT-4, Claude, Llama, Mistral, or local GGUF models.

**What it does:**
- Compresses 100 messages → 20 summaries + important facts
- Retrieves only relevant context (not entire history)
- 95% cost reduction, 0.5ms retrieval time

---

## Install
```bash
pip install git+https://github.com/codeislife12/chatsorter-client.git
```

---

## Get Your API Key

**Request a free demo key (100 messages):**

Email: **theiogamer1st@gmail.com**  
Subject: **"ChatSorter Demo Key Request"**

Include:
- Your name
- Company/Project name
- Use case (optional)

You'll receive your unique demo key within 24 hours.

**Production pricing:** $60/month for 10,000 messages

---

## Quick Start

Once you have your API key:
```python
from chatsorter_client import ChatSorter

# Use your unique demo key
chatsorter = ChatSorter(api_key="sk_demo_YOUR_KEY_HERE")

# One line to add memory
prompt = chatsorter.build_prompt(
    chat_id="user_123",
    message="My name is Alex",
    prompt_template="User: {message}\nAssistant:"
)

# Use prompt with your LLM
response = your_llm(prompt)
```

---

## Integration Examples

### OpenAI (GPT-4, GPT-3.5)
```python
from flask import Flask, request, jsonify
from openai import OpenAI
from chatsorter_client import ChatSorter

app = Flask(__name__)
openai_client = OpenAI(api_key="sk-xxx")
chatsorter = ChatSorter(api_key="sk_demo_xxx")  # Your demo key

@app.route('/chat', methods=['POST'])
def chat():
    user_id = request.json['user_id']
    message = request.json['message']
    
    # Get relevant context from ChatSorter
    context = chatsorter.get_context(user_id, message)
    
    # Store message in memory
    chatsorter.process(user_id, message)
    
    # Call OpenAI with context
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"Context: {context}"},
            {"role": "user", "content": message}
        ]
    )
    
    return jsonify({'response': response.choices[0].message.content})

if __name__ == '__main__':
    app.run(port=5000)
```

---

### Anthropic (Claude)
```python
from flask import Flask, request, jsonify
from anthropic import Anthropic
from chatsorter_client import ChatSorter

app = Flask(__name__)
anthropic_client = Anthropic(api_key="sk-ant-xxx")
chatsorter = ChatSorter(api_key="sk_demo_xxx")

@app.route('/chat', methods=['POST'])
def chat():
    user_id = request.json['user_id']
    message = request.json['message']
    
    # Get context and store message
    context = chatsorter.get_context(user_id, message)
    chatsorter.process(user_id, message)
    
    # Call Claude
    response = anthropic_client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        system=f"Context: {context}",
        messages=[{"role": "user", "content": message}]
    )
    
    return jsonify({'response': response.content[0].text})

if __name__ == '__main__':
    app.run(port=5000)
```

---

### Local GGUF Models (Llama, Mistral, Qwen)

**For llama-cpp-python:**
```python
from flask import Flask, request, jsonify
from llama_cpp import Llama
from chatsorter_client import ChatSorter

app = Flask(__name__)
llm = Llama(model_path="model.gguf", n_ctx=2048)
chatsorter = ChatSorter(api_key="sk_demo_xxx")

@app.route('/chat', methods=['POST'])
def chat():
    user_id = request.json['user_id']
    message = request.json['message']
    
    # Build prompt with memory (simple_context=True for small models)
    prompt = chatsorter.build_prompt(
        chat_id=user_id,
        message=message,
        prompt_template="{context}User: {message}\nAssistant:",
        simple_context=True  # Important for quantized/7B models
    )
    
    # Generate response
    response = llm(prompt, max_tokens=512, temperature=0.7)
    bot_response = response['choices'][0]['text'].strip()
    
    return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run(port=5000)
```

**For Ollama:**
```python
from flask import Flask, request, jsonify
import requests
from chatsorter_client import ChatSorter

app = Flask(__name__)
chatsorter = ChatSorter(api_key="sk_demo_xxx")

@app.route('/chat', methods=['POST'])
def chat():
    user_id = request.json['user_id']
    message = request.json['message']
    
    # Build prompt with memory
    prompt = chatsorter.build_prompt(
        chat_id=user_id,
        message=message,
        prompt_template="{context}User: {message}\nAssistant:",
        simple_context=True
    )
    
    # Call Ollama
    response = requests.post('http://localhost:11434/api/generate', json={
        'model': 'llama2',
        'prompt': prompt,
        'stream': False
    })
    
    return jsonify({'response': response.json()['response']})

if __name__ == '__main__':
    app.run(port=5000)
```

---

### HuggingFace Transformers
```python
from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
from chatsorter_client import ChatSorter

app = Flask(__name__)
model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")
tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")
chatsorter = ChatSorter(api_key="sk_demo_xxx")

@app.route('/chat', methods=['POST'])
def chat():
    user_id = request.json['user_id']
    message = request.json['message']
    
    # Build prompt
    prompt = chatsorter.build_prompt(
        chat_id=user_id,
        message=message,
        prompt_template="[INST] {context}{message} [/INST]",
        simple_context=True
    )
    
    # Generate
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=512)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(port=5000)
```

---

## API Methods

### Option 1: `build_prompt()` - All-in-One (Recommended)

Automatically stores message, retrieves context, and builds prompt.
```python
prompt = chatsorter.build_prompt(
    chat_id="user_123",              # Unique ID per user
    message="What's my name?",       # Current message
    prompt_template="User: {message}\nAssistant:",  # Your prompt format
    simple_context=False,            # Set True for small/quantized models
    max_memories=3                   # How many memories to retrieve
)
```

**Use this for:** Local models, simple integrations

---

### Option 2: `get_context()` + `process()` - Manual Control

Separate retrieval and storage steps.
```python
# Get relevant memories
context = chatsorter.get_context(
    chat_id="user_123",
    message="What's my name?",
    max_results=3,
    simple_context=False
)

# Store message
chatsorter.process(
    chat_id="user_123",
    message="What's my name?"
)
```

**Use this for:** OpenAI, Claude, when you need control over system prompts

---

### Option 3: `search()` - Direct Search

Search memory without storing a new message.
```python
results = chatsorter.search(
    chat_id="user_123",
    query="food preferences",
    simple_context=False
)

if results['result']['found']:
    for item in results['result']['results']:
        print(f"{item['content']} (score: {item['retrieval_score']})")
```

**Use this for:** Debugging, analytics, custom workflows

---

## Configuration

### Prompt Templates

Must include `{message}`. Optionally include `{context}`.
```python
# Simple
"User: {message}\nAssistant:"

# With context
"{context}User: {message}\nAssistant:"

# Instruct format (Llama, Mistral)
"[INST] {context}{message} [/INST]"

# ChatML format (some models)
"system\n{context}\nuser\n{message}"
```

**If using f-strings, escape ChatSorter placeholders:**
```python
bot_name = "Assistant"
prompt_template = f"System: You are {bot_name}.\nUser: {{message}}\nAssistant:"
# Note: {{message}} not {message}
```

---

### Simple Context Mode

**When to use `simple_context=True`:**

- 7B models (Llama 7B, Mistral 7B)
- Quantized models (Q2_K, Q4_K_M, Q5_K_M)
- Models that output metadata like `(importance: 8.5)` in responses

**What it does:**
- Strips importance scores and metadata from context
- Returns clean text only
- Prevents small models from "bleeding" metadata into responses

**When to use `simple_context=False` (default):**

- GPT-4, GPT-3.5
- Claude (all versions)
- Large models (13B+, unquantized)
```python
# For small/quantized models
prompt = chatsorter.build_prompt(..., simple_context=True)

# For large/API models
context = chatsorter.get_context(..., simple_context=False)
```

---

## Multi-User Setup

**Important:** Use consistent `chat_id` for each user. Don't generate new IDs each request.

### Flask with Sessions
```python
from flask import Flask, session
import uuid

app = Flask(__name__)
app.secret_key = "your-secret-key"

@app.route('/chat', methods=['POST'])
def chat():
    # Create persistent user ID
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    
    user_id = session['user_id']
    message = request.json['message']
    
    prompt = chatsorter.build_prompt(
        chat_id=user_id,  # Same user_id across requests
        message=message,
        prompt_template="User: {message}\nAssistant:"
    )
    
    response = your_llm(prompt)
    return jsonify({'response': response})
```

### API with Database
```python
@app.route('/chat', methods=['POST'])
def chat():
    user_id = request.json['user_id']  # From your database
    message = request.json['message']
    
    # user_id could be: database ID, email hash, UUID, etc.
    prompt = chatsorter.build_prompt(
        chat_id=user_id,
        message=message,
        prompt_template="User: {message}\nAssistant:"
    )
    
    response = your_llm(prompt)
    return jsonify({'response': response})
```

---

## Production Checklist

### 1. Use Environment Variables
```python
import os
chatsorter = ChatSorter(api_key=os.getenv("CHATSORTER_API_KEY"))
```

Set on your server:
```bash
export CHATSORTER_API_KEY="sk_live_xxx"
```

### 2. Use Real User IDs
```python
# ❌ Bad (generates new ID each time)
chat_id = str(uuid.uuid4())

# ✅ Good (consistent per user)
chat_id = session['user_id']  # Flask
chat_id = request.user.id      # Django
chat_id = user.id              # Your database
```

### 3. Error Handling
```python
try:
    prompt = chatsorter.build_prompt(...)
except Exception as e:
    print(f"ChatSorter error: {e}")
    # Fallback: use message without context
    prompt = f"User: {message}\nAssistant:"
```

---

## Troubleshooting

### 401 Unauthorized

**Problem:** API key invalid or missing

**Fix:**
- Check key starts with `sk_demo_` or `sk_live_`
- Remove any extra spaces
- Verify you received the key via email

---

### Memory Not Working

**Problem:** Bot doesn't remember past conversations

**Fix:**
- Use same `chat_id` for same user (don't generate new UUIDs)
- Wait for summaries to process (every 5 messages)
- Check terminal for `[ChatSorter]` logs
```python
# Debug: Check what's stored
from chatsorter_client import ChatSorter
chatsorter = ChatSorter(api_key="sk_demo_xxx")

# Send some messages
chatsorter.process("user_test", "My name is Alex")
chatsorter.process("user_test", "I love pizza")
chatsorter.process("user_test", "I work as an engineer")
chatsorter.process("user_test", "I live in NYC")
chatsorter.process("user_test", "I play guitar")

# Search to verify storage
results = chatsorter.search("user_test", "name")
print(results)  # Should find "My name is Alex"
```

---

### Metadata Bleeding (Small Models)

**Problem:** Bot outputs text like: `Your name is Alex (importance: 8.5)`

**Fix:** Use `simple_context=True`
```python
prompt = chatsorter.build_prompt(
    chat_id="user_123",
    message="What's my name?",
    prompt_template="User: {message}\nAssistant:",
    simple_context=True  # Strips metadata
)
```

Or clean output:
```python
import re
response = llm(prompt)
response = re.sub(r'\(importance:.*?\)', '', response).strip()
```

---

### Import Error

**Problem:** `ModuleNotFoundError: No module named 'chatsorter_client'`

**Fix:**
```bash
pip install git+https://github.com/codeislife12/chatsorter-client.git
```

If still broken:
```bash
pip uninstall chatsorter-client
pip install --upgrade git+https://github.com/codeislife12/chatsorter-client.git
```

---

## How It Works

ChatSorter uses **episodic memory compression** (like your brain):

### 1. Messages → Episodes
```
Messages 1-5   → Episode 1: "User discussed weekend plans"
Messages 6-10  → Episode 2: "User asked about features"
Messages 11-15 → Episode 3: "User shared feedback"
```

Every 5 messages = 1 summary (90% compression)

### 2. Important Facts → Permanent Storage
```
"My name is Alex" → Importance 8.5 → Saved permanently
"ok thanks"       → Importance 2.0 → Fades after 30 days
```

### 3. Smart Retrieval
```
User asks: "What's my name?"
→ Searches 20 episode summaries (not 100 messages)
→ Finds: "My name is Alex" (importance 8.5)
→ Returns in 0.5ms
```

**Result:** 95% cost reduction, 100% context retention

---

## Pricing

| Plan | Price | Messages/Month | Retention | How to Get |
|------|-------|----------------|-----------|------------|
| **Demo** | FREE | 100 | 7 days | Email theiogamer1st@gmail.com |
| **Starter** | $60 | 10,000 | 30 days | Email theiogamer1st@gmail.com |
| **Pro** | $150 | 50,000 | 90 days | Email theiogamer1st@gmail.com |
| **Enterprise** | Custom | Unlimited | Unlimited | Email theiogamer1st@gmail.com |

**ROI Calculator:**
- Sending 100 messages to GPT-4 = ~50K tokens = $1.50
- ChatSorter: Sends 3 summaries = ~500 tokens = $0.015
- **Savings: $1.48 per conversation = 99% reduction**

If you have 1,000 conversations/month:
- Without ChatSorter: $1,500/month
- With ChatSorter: $60/month
- **You save: $1,440/month**

---

## Support

**Email:** theiogamer1st@gmail.com  
**Subject:** "ChatSorter Help"

Include:
1. Code snippet (20-50 lines)
2. Error message (if any)
3. Framework (Flask/FastAPI/etc)
4. Model (GPT-4/Claude/Llama/etc)

Response within 24 hours.

---

## License

MIT

✅ Now for the Backend (auth.py helper):
Add this function to make creating demo keys easier:
python# Add to auth.py after create_customer() function

def create_demo_customer(email: str) -> Dict:
    """
    Create a demo customer with 100 message limit
    
    Args:
        email: Customer email
    
    Returns:
        Dict with api_key and customer info
    """
    api_key = generate_api_key(prefix="sk_demo")
    customer_id = f"demo_{secrets.token_hex(8)}"
    
    customer_data = {
        "customer_id": customer_id,
        "customer_name": f"Demo - {email}",
        "email": email,
        "plan": "demo",
        "limits": PLAN_LIMITS["demo"],
        "created_at": datetime.now().isoformat(),
        "active": True,
        "expires_at": (datetime.now() + timedelta(days=7)).isoformat()  # 7 day expiry
    }
    
    try:
        db.collection('customers').document(api_key).set(customer_data)
        
        # Initialize usage
        current_month = datetime.now().strftime("%Y-%m")
        usage_data = {
            "messages_used": 0,
            "searches_used": 0,
            "period_start": datetime.now().isoformat()
        }
        db.collection('usage').document(api_key).collection('months').document(current_month).set(usage_data)
        
        print(f"[AUTH] ✅ Created demo customer: {email}")
        print(f"[AUTH] 🔑 Demo API Key: {api_key}")
        print(f"[AUTH] ⏰ Expires: 7 days")
        
        return {
            "success": True,
            "api_key": api_key,
            "customer_id": customer_id,
            "email": email,
            "plan": "demo",
            "limits": PLAN_LIMITS["demo"],
            "expires_at": customer_data["expires_at"]
        }
        
    except Exception as e:
        print(f"[AUTH] ❌ Error creating demo customer: {e}")
        return {
            "success": False,
            "error": str(e)
        }

✅ How You Create Keys When Someone Emails:
When you get email: "ChatSorter Demo Key Request":
bashcd C:\Users\theio\OneDrive\Desktop\chatsorter-api
python
pythonfrom auth import create_demo_customer

# Create demo key
result = create_demo_customer("customer@company.com")

print(f"Send them: {result['api_key']}")
```

**Reply to customer:**
```
Hi [Name],

Here's your ChatSorter demo API key:

sk_demo_abc123xyz456...

Limits:
- 100 messages
- 7 days (expires Oct 32, 2025)

Getting started:
https://github.com/codeislife12/chatsorter-client

Questions? Just reply to this email.
