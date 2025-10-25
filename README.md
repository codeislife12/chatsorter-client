# ChatSorter - Semantic Memory for AI Chatbots

Stop sending entire chat histories to your LLM. ChatSorter compresses conversations by 95% using semantic search and importance scoring.

**What you get:**
- 95% cost reduction on API calls
- Semantic retrieval (finds "pizza" when asked "what food?")
- Automatic importance scoring (critical info never decays)
- Zero infrastructure (no vector DB, no Redis)
- 5-minute integration

---

## Quick Start

```bash
pip install git+https://github.com/codeislife12/chatsorter-client.git
```

Get a demo key: Email `theiogamer1st@gmail.com` with subject "ChatSorter Demo Key"

Or use the public demo key (100 messages limit):
```python
api_key = "sk_test_demo123"
```

---

## Integration

### Basic Usage

```python
from chatsorter_client import ChatSorter

chatsorter = ChatSorter(api_key="sk_live_xxx")

# Replace this:
prompt = f"User: {user_message}\nAssistant:"

# With this:
prompt = chatsorter.build_prompt(
    chat_id=user_id,
    message=user_message,
    prompt_template="User: {message}\nAssistant:"
)

# Your LLM call stays the same
response = llm(prompt)
```

That's it. ChatSorter handles memory storage, retrieval, and compression automatically.

---

## Examples

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
    data = request.json
    user_id = data['user_id']
    message = data['message']
    
    context = chatsorter.get_context(user_id, message)
    chatsorter.process(user_id, message)
    
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"Context: {context}"},
            {"role": "user", "content": message}
        ]
    )
    
    return jsonify({'response': response.choices[0].message.content})
```

### Flask + Local GGUF

```python
from flask import Flask, request, jsonify
from llama_cpp import Llama
from chatsorter_client import ChatSorter

app = Flask(__name__)
llm = Llama(model_path="model.gguf")
chatsorter = ChatSorter(api_key="sk_live_xxx")

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    
    prompt = chatsorter.build_prompt(
        chat_id=data['user_id'],
        message=data['message'],
        prompt_template="{context}User: {message}\nAssistant:",
        simple_context=True  # For quantized/7B models
    )
    
    response = llm(prompt, max_tokens=512)
    return jsonify({'response': response['choices'][0]['text']})
```

### Flask + Claude

```python
from anthropic import Anthropic
from chatsorter_client import ChatSorter

anthropic = Anthropic(api_key="sk-ant-xxx")
chatsorter = ChatSorter(api_key="sk_live_xxx")

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    
    context = chatsorter.get_context(data['user_id'], data['message'])
    chatsorter.process(data['user_id'], data['message'])
    
    message = anthropic.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        system=f"Context: {context}",
        messages=[{"role": "user", "content": data['message']}]
    )
    
    return jsonify({'response': message.content[0].text})
```

---

## API Methods

### `build_prompt()` - All-in-One

Stores message, retrieves relevant memories, builds prompt.

```python
prompt = chatsorter.build_prompt(
    chat_id="user_123",
    message="What's my name?",
    prompt_template="User: {message}\nAssistant:",
    simple_context=False,  # Set True for small/quantized models
    max_memories=3
)
```

### `get_context()` + `process()` - Manual Control

For when you need separate retrieval and storage (e.g., OpenAI/Claude).

```python
# Retrieve relevant memories
context = chatsorter.get_context(
    chat_id="user_123",
    message="What food do I like?",
    max_results=3
)

# Store message
chatsorter.process(
    chat_id="user_123",
    message="What food do I like?"
)
```

### `search()` - Direct Search

```python
results = chatsorter.search(
    chat_id="user_123",
    query="food preferences"
)

for item in results['result']['results']:
    print(f"{item['content']} (score: {item['retrieval_score']})")
```

---

## Configuration

### Prompt Templates

Must include `{message}`. Optionally include `{context}` for memory.

```python
# Simple
"User: {message}\nAssistant:"

# With context
"{context}User: {message}\nAssistant:"

# Instruct format
"[INST] {context}{message} [/INST]"
```

If using f-strings, escape ChatSorter placeholders:
```python
prompt_template = f"System: You are {bot_name}.\nUser: {{message}}\nAssistant:"
```

### Simple Context Mode

Set `simple_context=True` for:
- 7B models (Llama 7B, Mistral 7B)
- Quantized models (Q2_K, Q4_K_M, Q5_K_M)
- Models that leak metadata into responses

This strips importance scores and metadata from context.

```python
prompt = chatsorter.build_prompt(..., simple_context=True)
```

---

## How It Works

1. **Message arrives** → Scores importance (0-10), extracts entities, detects intent
2. **Stores intelligently:**
   - Every 5 messages → Creates summary
   - Importance ≥ 7.0 → Stores individually
   - Importance ≥ 9.0 → Never decays
3. **Retrieves semantically:**
   - Embeds current message
   - Searches past embeddings (cosine similarity)
   - Ranks by: similarity × importance × recency
   - Returns top 3-5 memories
4. **Time decay** gradually reduces importance of old, low-value messages

**Performance:** 0.5ms retrieval time, regardless of history length.

---

## Pricing

- **Demo:** 100 messages (testing only)
- **Starter:** $60/month - 10K messages, 30-day retention
- **Pro:** $150/month - 50K messages, 90-day retention
- **Enterprise:** Custom pricing - unlimited everything

Email for production API key: `theiogamer1st@gmail.com`

---

## Production Checklist

```python
# Use environment variables
import os
chatsorter = ChatSorter(api_key=os.getenv("CHATSORTER_API_KEY"))

# Use real user IDs (not "default")
chat_id = session['user_id']  # Flask
chat_id = request.user.id      # Django
```

---

## Troubleshooting

**401 Unauthorized**
- Check API key starts with `sk_live_` or `sk_test_`
- Verify no extra spaces

**Memory not working**
- Use consistent `chat_id` for same user
- Don't generate new UUID each request

**Metadata bleeding into responses** (e.g., "Your name is Alex (importance: 8.5)")
- Set `simple_context=True`
- Or strip metadata: `re.sub(r'\(importance:.*?\)', '', response)`

**Import error**
```bash
pip install git+https://github.com/codeislife12/chatsorter-client.git
```

---

## API Endpoints

Base: `https://chatsorter-api.onrender.com`

All require `Authorization: Bearer YOUR_API_KEY` header.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/process` | POST | Store message |
| `/search` | POST | Search memories |
| `/flag` | POST | Mark as critical (importance 10.0) |
| `/moments/{chat_id}` | GET | High-importance memories (≥8.0) |
| `/stats?chat_id=X` | GET | Usage statistics |
| `/health` | GET | API status |

---

## Support

**Email:** theiogamer1st@gmail.com  
**Subject:** "ChatSorter Help"

Include:
1. Code snippet (~20-50 lines)
2. Error message
3. Framework and model type

Response within 24 hours.

---

## Why ChatSorter vs Building It Yourself

| Task | Time | ChatSorter |
|------|------|------------|
| Semantic embeddings | 2 weeks | ✅ Included |
| Importance scoring logic | 1 week | ✅ Included |
| Time decay algorithm | 3 days | ✅ Included |
| Entity extraction | 1 week | ✅ Included |
| Storage optimization | 1 week | ✅ Included |
| **Total** | **6+ weeks** | **5 minutes** |

**Gleam.ai comment:** *"Took us 3 months to build something similar. Would use ChatSorter if starting fresh."*

---

**Note:** Demo key (`sk_test_demo123`) limited to 100 messages for testing. Email for production key.