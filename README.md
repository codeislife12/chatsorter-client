# ChatSorter Client

**Add long-term memory to your chatbot in 5 steps.**

---

## Prerequisites

- Python 3.8+
- Git installed ([Download here](https://git-scm.com/downloads))
- A ChatSorter API key (email theiogamer1st@gmail.com with subject "ChatSorter Demo Key")

---

## Step 1: Install ChatSorter
```bash
pip install git+https://github.com/codeislife12/chatsorter-client.git
```

**Verify it installed:**
```bash
python -c "from chatsorter_client import ChatSorter; print('✅ Installed')"
```

You should see: `✅ Installed`

---

## Step 2: Add Import Statement

**At the very top of your chatbot file**, add this line:
```python
from chatsorter_client import ChatSorter
```

**Example:**
```python
from flask import Flask, request, jsonify
from llama_cpp import Llama
from chatsorter_client import ChatSorter  # ← Add this line

app = Flask(__name__)
```

---

## Step 3: Initialize ChatSorter

**After your imports, before your routes/functions**, add:
```python
chatsorter = ChatSorter(api_key="YOUR_API_KEY_HERE")
```

**Replace `YOUR_API_KEY_HERE` with your actual API key.**

**Example:**
```python
from flask import Flask, request, jsonify
from chatsorter_client import ChatSorter

app = Flask(__name__)
chatsorter = ChatSorter(api_key="sk_live_abc123...")  # ← Add this line

llm = Llama(model_path="model.gguf")
```

---

## Step 4: Find Your Chat Function

Look for the function that handles user messages. 

**It might look like:**
- `@app.route('/chat', methods=['POST'])`
- `def chat():`
- `async def handle_message():`

**Inside that function, find the line that builds your AI prompt.**

**Common examples:**
- `prompt = f"User: {user_message}"`
- `prompt = f"<s>[INST] {user_message} [/INST]"`
- `messages = [{"role": "user", "content": user_message}]`

**Write down what YOUR line looks like.**

---

## Step 5: Replace Your Prompt Line

**Replace the line from Step 4** with the appropriate pattern below:

### Pattern A: Simple String Prompt

**If your old line was:**
```python
prompt = f"User: {user_message}"
```

**Replace with:**
```python
prompt = chatsorter.build_prompt(
    chat_id="user_123",
    message=user_message,
    prompt_template="User: {message}"
)
```

---

### Pattern B: Mistral/Llama Instruct Format

**If your old line was:**
```python
prompt = f"[INST] {user_message} [/INST]"
```

**Replace with:**
```python
prompt = chatsorter.build_prompt(
    chat_id="user_123",
    message=user_message,
    prompt_template="[INST] {context}{message} [/INST]"
)
```

---

### Pattern C: OpenAI/Claude Messages Array

**If your old line was:**
```python
messages = [{"role": "user", "content": user_message}]
```

**Replace with:**
```python
context = chatsorter.get_context("user_123", user_message)
chatsorter.process("user_123", user_message)

messages = [
    {"role": "system", "content": f"Context: {context}"},
    {"role": "user", "content": user_message}
]
```

---

### Pattern D: My Code Looks Different

**See the "Common Fixes" section below, or email us for help.**

---

## Step 6: Test That Memory Works

1. **Run your chatbot**
2. **Send message:** "My name is Alex and I love pizza"
3. **Restart your chatbot** (or close and reopen the browser)
4. **Send message:** "What's my name?"
5. **Bot should respond** with your name (Alex)
6. **Send message:** "What food do I like?"
7. **Bot should respond** mentioning pizza

**If it remembers:** ✅ **You're done!**  
**If it doesn't remember:** See "Common Fixes" below

---

## Common Fixes

### "ModuleNotFoundError: No module named 'chatsorter_client'"

**Solution:**
```bash
pip install git+https://github.com/codeislife12/chatsorter-client.git
```

Make sure Git is installed first.

---

### "401 Unauthorized" Error

**Cause:** Wrong API key

**Solution:** 
1. Check your API key is copied correctly (no extra spaces)
2. Make sure you're using `sk_live_...` or `sk_test_demo123`
3. Email us if your key doesn't work

---

### Bot Doesn't Remember Anything

**Possible causes:**

**1. Using Random chat_id**

❌ **Wrong:**
```python
import uuid
chat_id = str(uuid.uuid4())  # New ID every time!
```

✅ **Right:**
```python
chat_id = "user_123"  # Same ID every time
# Or get from session: chat_id = session['user_id']
```

**2. Not enough time passed**

Wait 2-3 seconds between messages, or restart your chatbot between tests.

**3. Check terminal for errors**

Look for `[ChatSorter]` messages in your terminal:
- `✅ Stored message` = Working
- `❌ Failed to store` = Problem with API key or connection

---

### My Code Structure Is Different

**Common variations:**

**You use different variable names:**
```python
# Your code might use:
msg = request.json['text']  # Instead of user_message
uid = session['id']         # Instead of user_id

# Just use YOUR variable names:
prompt = chatsorter.build_prompt(
    chat_id=uid,              # ← Your variable
    message=msg,              # ← Your variable
    prompt_template="User: {message}"
)
```

**You have async functions:**
```python
async def chat():
    msg = await request.json()
    # Use ChatSorter normally (it's not async, but that's okay)
    prompt = chatsorter.build_prompt("user_123", msg, "User: {message}")
```

**You use streaming responses:**
```python
def chat():
    msg = request.json['message']
    
    # Build prompt with memory BEFORE streaming
    prompt = chatsorter.build_prompt("user_123", msg, "User: {message}")
    
    # Then stream as normal
    def generate():
        for chunk in llm(prompt, stream=True):
            yield chunk['text']
    
    return Response(generate(), mimetype='text/plain')
```

---

### I Get "[ChatSorter] ❌ Failed" Messages

**Check:**
1. Internet connection is working
2. API key is correct
3. ChatSorter API is online: https://chatsorter-api.onrender.com/health

If health check fails, email us.

---

### My Prompt Template Has Variables

**Example:** Your old prompt used multiple variables:
```python
prompt = f"System: You are {bot_name}. User: {user_message}"
```

**Solution:** Put ALL your variables in the template:
```python
prompt = chatsorter.build_prompt(
    chat_id="user_123",
    message=user_message,
    prompt_template=f"System: You are {bot_name}. User: {{message}}"
)
# Note: Use {{message}} not {message} when inside f-string
```

---

## Complete Examples

### Example 1: Flask + Local GGUF
```python
from flask import Flask, request, jsonify
from llama_cpp import Llama
from chatsorter_client import ChatSorter

app = Flask(__name__)
llm = Llama(model_path="model.gguf", n_ctx=2048)
chatsorter = ChatSorter(api_key="sk_live_YOUR_KEY")

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    
    # Build prompt with memory
    prompt = chatsorter.build_prompt(
        chat_id="user_123",
        message=user_message,
        prompt_template="[INST] {context}{message} [/INST]"
    )
    
    # Generate response
    response = llm(prompt, max_tokens=512)
    bot_response = response['choices'][0]['text'].strip()
    
    return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run(port=5000)
```

---

### Example 2: Flask + OpenAI
```python
from flask import Flask, request, jsonify
from openai import OpenAI
from chatsorter_client import ChatSorter

app = Flask(__name__)
openai_client = OpenAI(api_key="your-openai-key")
chatsorter = ChatSorter(api_key="sk_live_YOUR_KEY")

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    
    # Get memory context
    context = chatsorter.get_context("user_123", user_message)
    chatsorter.process("user_123", user_message)
    
    # Call OpenAI with context
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"Context: {context}"},
            {"role": "user", "content": user_message}
        ]
    )
    
    return jsonify({'response': response.choices[0].message.content})

if __name__ == '__main__':
    app.run(port=5000)
```

---

### Example 3: With User Sessions
```python
from flask import Flask, request, jsonify, session
from chatsorter_client import ChatSorter

app = Flask(__name__)
app.secret_key = "your-secret-key"
chatsorter = ChatSorter(api_key="sk_live_YOUR_KEY")

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    
    # Get user ID from session (each user gets separate memory)
    if 'user_id' not in session:
        import uuid
        session['user_id'] = str(uuid.uuid4())
    
    user_id = session['user_id']
    
    # Build prompt with user-specific memory
    prompt = chatsorter.build_prompt(
        chat_id=user_id,
        message=user_message,
        prompt_template="User: {message}"
    )
    
    response = your_model.generate(prompt)
    return jsonify({'response': response})
```

---

## Advanced Usage

### View Memory Stats
```python
@app.route('/stats')
def stats():
    result = chatsorter.get_stats(chat_id="user_123")
    return jsonify(result)
```

Visit: `http://localhost:5000/stats`

---

### Manual Control (Don't Use build_prompt)
```python
# Store message manually
chatsorter.process(chat_id="user_123", message="I love pizza")

# Search memory manually
results = chatsorter.search(chat_id="user_123", query="food preferences")

if results['result']['found']:
    for item in results['result']['results']:
        print(f"- {item['content']}")
        print(f"  Importance: {item['decayed_importance']}")
```

---
## View Your Memory Data

### See What's Stored

Add this route to your chatbot to see memory stats:
```python
@app.route('/memory-stats')
def memory_stats():
    stats = chatsorter.get_stats(chat_id="user_123")
    return jsonify(stats)
```

Visit: `http://localhost:5000/memory-stats`

**You'll see:**
- Total messages stored
- Number of summaries created
- Memory items count

---

### View Detailed Memories
```python
@app.route('/memory-details')
def memory_details():
    analysis = chatsorter.get_memory_analysis(chat_id="user_123")
    return jsonify(analysis)
```

Visit: `http://localhost:5000/memory-details`

**You'll see:**
- All stored memories
- Importance scores
- Time decay information
- Entities extracted
- Intent detection results

---

### View Only Important Moments
```python
@app.route('/memorable-moments')
def memorable_moments():
    import requests
    response = requests.get(
        "https://chatsorter-api.onrender.com/moments/user_123",
        headers={"Authorization": f"Bearer {chatsorter.api_key}"}
    )
    return jsonify(response.json())
```

Visit: `http://localhost:5000/memorable-moments`

**Shows only high-importance memories (8.0+)**

## Need Help?

**Email:** theiogamer1st@gmail.com

**Include:**
1. Your chat function code (just the function, not the whole file)
2. What error you're seeing (if any)
3. What you expected to happen

We'll respond within 24 hours with exactly what to change.

---

## Pricing

**Demo:** Free during beta  
**After Launch:** $40-80/month

---

**Built with ❤️ by the ChatSorter team**