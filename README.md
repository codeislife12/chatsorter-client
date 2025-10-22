# ChatSorter - Semantic Memory for Chatbots

## What It Does

Adds semantic memory to your chatbot in 5 minutes. Reduces API costs by 95% and enables long-term memory retention.

**Your chatbot gets:**
- Semantic search (meaning-based, not keyword)
- Importance scoring (critical info never decays)
- Time-weighted retrieval (recent + important = prioritized)
- Cross-session persistence (remembers after restarts)
- Automatic summarization (every 5 messages)

**You save:**
- 95% on API costs (sends only relevant context, not entire history)
- 200+ hours building it yourself
- Infrastructure costs (no vector DB needed)

---

## Memory Retention vs Manual History

| Feature | Manual `conversation_history = []` | ChatSorter |
|---------|-----------------------------------|------------|
| **Long-term retention** | ❌ Drops old messages when window fills | ✅ Important info retained indefinitely |
| **Semantic search** | ❌ Can't find "pizza" when asked "what food?" | ✅ Meaning-based retrieval |
| **Cross-session** | ❌ Lost on restart/browser close | ✅ Persistent storage |
| **Noise filtering** | ❌ Keeps "ok", "lol", "thanks" | ✅ Auto-filters low-importance messages |
| **Context limit** | ❌ Hits token limits at scale | ✅ Never hits limits (retrieves top 3-5) |
| **Cost per request** | 💸 $1.50 (1000 messages @ GPT-4) | 💸 $0.002 (relevant context only) |

**Companies value this:** Users don't repeat themselves. Bot builds relationships over weeks/months. Higher UX = higher retention.

---

## Quick Start

### Install
```bash
pip install git+https://github.com/codeislife12/chatsorter-client.git
```

### Get API Key
Email: theiogamer1st@gmail.com  
Subject: "ChatSorter Demo Key"

---

## Integration (3 Lines)

### Step 1: Import & Initialize
```python
from chatsorter_client import ChatSorter

chatsorter = ChatSorter(api_key="sk_live_xxx")  # Or use os.getenv("CHATSORTER_API_KEY")
```

### Step 2: Replace Your Prompt Line

**Before:**
```python
prompt = f"User: {user_message}\nAssistant:"
```

**After:**
```python
prompt = chatsorter.build_prompt(
    chat_id=session['user_id'],  # Or however you identify users
    message=user_message,
    prompt_template="User: {message}\nAssistant:"
)
```

**Done.** Your model call stays the same.

---

## Framework-Specific Examples

### Flask + Local GGUF (Llama/Mistral)

```python
from flask import Flask, request, jsonify
from llama_cpp import Llama
from chatsorter_client import ChatSorter
import re

app = Flask(__name__)
llm = Llama(model_path="model.gguf", n_ctx=2048, n_threads=8, n_gpu_layers=0)
chatsorter = ChatSorter(api_key="sk_live_xxx")

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    user_id = request.json.get('user_id', 'default')
    
    prompt = chatsorter.build_prompt(
        chat_id=user_id,
        message=user_message,
        prompt_template="{context}User: {message}\nAssistant:",
        simple_context=True  # Use for 7B/quantized models
    )
    
    response = llm(prompt, max_tokens=512, temperature=0.7, stop=["User:", "\n\n"])
    bot_response = response['choices'][0]['text'].strip()
    
    # Clean metadata (for small models)
    bot_response = re.sub(r'\(importance:.*?\)', '', bot_response).strip()
    
    return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run(port=5000)
```

**For quantized/small models (Q2_K, Q4_K_M, 7B):** Use `simple_context=True` to prevent metadata bleeding into responses.

---

### Flask + OpenAI

```python
from flask import Flask, request, jsonify
from openai import OpenAI
from chatsorter_client import ChatSorter

app = Flask(__name__)
openai_client = OpenAI(api_key="sk-xxx")
chatsorter = ChatSorter(api_key="sk_live_xxx")

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    user_id = request.json.get('user_id', 'default')
    
    # Get context and store message
    context = chatsorter.get_context(user_id, user_message)
    chatsorter.process(user_id, user_message)
    
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"Previous context: {context}"},
            {"role": "user", "content": user_message}
        ]
    )
    
    return jsonify({'response': response.choices[0].message.content})

if __name__ == '__main__':
    app.run(port=5000)
```

---

### Flask + Anthropic Claude

```python
from flask import Flask, request, jsonify
from anthropic import Anthropic
from chatsorter_client import ChatSorter

app = Flask(__name__)
anthropic_client = Anthropic(api_key="sk-ant-xxx")
chatsorter = ChatSorter(api_key="sk_live_xxx")

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    user_id = request.json.get('user_id', 'default')
    
    context = chatsorter.get_context(user_id, user_message)
    chatsorter.process(user_id, user_message)
    
    message = anthropic_client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        system=f"Previous context: {context}",
        messages=[{"role": "user", "content": user_message}]
    )
    
    return jsonify({'response': message.content[0].text})

if __name__ == '__main__':
    app.run(port=5000)
```

---

### FastAPI (Async)

```python
from fastapi import FastAPI, Request
from chatsorter_client import ChatSorter

app = FastAPI()
chatsorter = ChatSorter(api_key="sk_live_xxx")

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_message = data['message']
    user_id = data.get('user_id', 'default')
    
    # ChatSorter is sync but works fine in async
    prompt = chatsorter.build_prompt(
        chat_id=user_id,
        message=user_message,
        prompt_template="User: {message}\nAssistant:"
    )
    
    response = await your_async_model.generate(prompt)
    return {"response": response}
```

---

### Multi-User (Sessions)

```python
from flask import Flask, request, jsonify, session
from chatsorter_client import ChatSorter
import uuid

app = Flask(__name__)
app.secret_key = "your-secret-key"
chatsorter = ChatSorter(api_key="sk_live_xxx")

@app.route('/chat', methods=['POST'])
def chat():
    # Create unique ID per session
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    
    user_id = session['user_id']
    user_message = request.json['message']
    
    prompt = chatsorter.build_prompt(
        chat_id=user_id,
        message=user_message,
        prompt_template="User: {message}\nAssistant:"
    )
    
    response = your_model.generate(prompt)
    return jsonify({'response': response})
```

---

## API Methods

### `build_prompt()` - One-Line Integration
```python
prompt = chatsorter.build_prompt(
    chat_id="user_123",
    message="What's my name?",
    prompt_template="User: {message}\nAssistant:",
    simple_context=False,  # True for 7B/quantized models
    max_memories=3  # Number of relevant memories to include
)
```
Automatically stores message, searches memory, and builds prompt.

---

### `get_context()` + `process()` - Manual Control
```python
# Get relevant context
context = chatsorter.get_context(
    chat_id="user_123",
    message="What food do I like?",
    max_results=3,
    simple_context=False
)

# Store message
chatsorter.process(
    chat_id="user_123",
    message="What food do I like?"
)
```
Use when you need separate context retrieval and storage steps (e.g., OpenAI/Claude).

---

### `search()` - Direct Search
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

---

### `get_stats()` - Usage Stats
```python
stats = chatsorter.get_stats(chat_id="user_123")
# Returns: message_count, summary_files, master_exists, performance metrics
```

---

### `get_memory_analysis()` - Detailed Memory View
```python
analysis = chatsorter.get_memory_analysis(chat_id="user_123")
# Returns: all memory items, importance scores, entities, intents, decay stats
```

---

## Configuration Options

### `simple_context` Parameter

**Use `simple_context=True` for:**
- 7B models (Mistral 7B, Llama 2 7B)
- Quantized models (Q2_K, Q4_K_M, Q5_K_M)
- Any model that shows `(importance: 8.5)` in responses

**Use `simple_context=False` (default) for:**
- GPT-4, GPT-3.5-turbo
- Claude 2, Claude 3
- Llama 2 13B+ (unquantized)
- Mixtral 8x7B

**What it does:**
- `False`: Includes metadata (importance scores, age) in context
- `True`: Just the content, no metadata

---

### Template Variables

Your `prompt_template` must include:
- `{message}` - Where user's current message goes
- `{context}` (optional) - Where memory context goes

**Examples:**
```python
# Simple
"User: {message}\nAssistant:"

# With context
"{context}User: {message}\nAssistant:"

# Instruct format
"[INST] {context}{message} [/INST]"

# System prompt
"System: You are helpful.\n{context}User: {message}\nAssistant:"
```

**If using f-strings, use double braces:**
```python
prompt_template=f"System: You are {bot_name}.\nUser: {{message}}\nAssistant:"
```

---

## What Gets Stored

ChatSorter automatically creates:

### Summary Files (Every 5 Messages)
```
{chat_id}_summary.json       # Messages 1-5
{chat_id}_summary_2.json     # Messages 6-10
{chat_id}_summary_3.json     # Messages 11-15
```

Contains:
- Aggregated summary of 5 messages
- Entities extracted (people, places, skills)
- Intents detected (questions, preferences, goals)
- Topic shift detection
- Semantic embeddings
- Importance score (averaged across messages)

### Master JSON (High-Importance Items)
```
{chat_id}_master.json
```

Contains:
- Individual messages with importance ≥ 7.0
- Manually flagged items (importance 10.0)
- Full metadata (entities, intents, decisions)
- Never decays if importance ≥ 9.0

---

## View Your Data

### Get All Data for a User
```bash
curl -H "Authorization: Bearer sk_live_xxx" \
  https://chatsorter-api.onrender.com/download/user_123
```

Returns all summary files + master JSON.

### Get Only Important Moments (≥8.0)
```bash
curl -H "Authorization: Bearer sk_live_xxx" \
  https://chatsorter-api.onrender.com/moments/user_123
```

### Add Debug Routes
```python
@app.route('/debug/memory')
def debug_memory():
    return jsonify(chatsorter.get_memory_analysis(chat_id="user_123"))

@app.route('/debug/stats')
def debug_stats():
    return jsonify(chatsorter.get_stats(chat_id="user_123"))
```

---

## Common Issues

### Import Error
```
ModuleNotFoundError: No module named 'chatsorter_client'
```
**Fix:**
```bash
pip install git+https://github.com/codeislife12/chatsorter-client.git
```

---

### 401 Unauthorized
**Fix:** Check API key has no spaces, starts with `sk_live_` or `sk_test_`

---

### Memory Not Working
**Check:**
1. Using same `chat_id` for same user (not random UUID each time)
2. Wait 2-3 seconds between test messages
3. Look for `[ChatSorter]` logs in terminal

---

### Metadata Bleeding (Small Models)
Bot responds with: `"Your name is Jacob (importance: 8.5)"`

**Fix 1:** Use `simple_context=True`
```python
prompt = chatsorter.build_prompt(..., simple_context=True)
```

**Fix 2:** Regex cleanup
```python
import re
response = re.sub(r'\(importance:.*?\)', '', response).strip()
```

---

### Multiple Variables in Template
```python
prompt_template=f"System: {bot_name}.\nUser: {user_message}"  # ❌ Conflict
```

**Fix:** Use double braces for ChatSorter placeholders
```python
prompt_template=f"System: {bot_name}.\nUser: {{message}}"  # ✅ Works
```

---

## Production Deployment

### Environment Variable (Recommended)
```python
import os
chatsorter = ChatSorter(api_key=os.getenv("CHATSORTER_API_KEY"))
```

Set on your server:
```bash
export CHATSORTER_API_KEY="sk_live_xxx"
```

### Use Real User IDs
```python
# ❌ Testing
chat_id = "default"

# ✅ Production
chat_id = session['user_id']         # Flask
chat_id = request.user.id             # Django
chat_id = request.json.get('user_id') # API
```

---

## API Endpoints (Advanced)

Base URL: `https://chatsorter-api.onrender.com`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/process` | POST | Store message |
| `/search` | POST | Search memories |
| `/flag` | POST | Mark as critical (importance 10.0) |
| `/download/{chat_id}` | GET | Download all JSON files |
| `/moments/{chat_id}` | GET | Get high-importance (≥8.0) |
| `/stats?chat_id=X` | GET | Usage statistics |
| `/memory/{chat_id}` | GET | Full memory analysis |
| `/health` | GET | API health check |

All require `Authorization: Bearer YOUR_API_KEY` header.

---

## How It Works

1. **Message arrives** → Extracts entities (people, places), detects intent (question/preference/goal), scores importance (0-10)
2. **Stores intelligently:**
   - Every 5 messages → Creates summary JSON
   - Importance ≥ 7.0 → Stores in master JSON
   - Importance ≥ 9.0 → Never decays
3. **Retrieves semantically:**
   - Creates embedding for current message
   - Searches past embeddings (cosine similarity)
   - Ranks by: similarity × importance × recency
   - Returns top 3-5 relevant memories
4. **Time decay:**
   - High importance (9.0+): 98% retention per 30 days
   - Important (8.0+): 95% retention per 30 days
   - Medium (6.0+): 90% retention per 30 days
   - Low (<6.0): 85% retention per 30 days

**Performance:** 0.5ms average retrieval time, stays constant regardless of total messages.

---

## Pricing

- **Demo:** Free during beta
- **Production:** $40-80/month (vs $200+ competitors)
- **ROI:** Save $20K+/month on API costs (95% context reduction)

---

## Support

**Email:** theiogamer1st@gmail.com  
**Subject:** "ChatSorter Integration Help"

Include:
1. Your chat function code (~20-50 lines)
2. Error message (if any)
3. Framework (Flask/FastAPI/etc.)
4. Model (OpenAI/Claude/local GGUF)

Response within 24 hours.