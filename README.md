# ChatSorter Client

Add long-term memory to your chatbot in 5 minutes.

## 🚀 Quick Start

### 1. Get Your API Key
Email theiogamer1st@gmail.com with subject "ChatSorter Demo Key"

Demo keys are free during beta and include:
- 10,000 messages/month
- 5,000 searches/month
- All features enabled

### 2. Install
Make sure git is installed
```bash
pip install git+https://github.com/codeislife12/chatsorter-client.git
```

### 3. Add to Your Chatbot
```python
from chatsorter_client import ChatSorterClient

# Initialize with your API key
client = ChatSorterClient(api_key="sk_live_YOUR_KEY_HERE")

# Store a message
client.process(
    chat_id="user_123",  # Unique ID per user
    message="I love pizza and my name is John"
)

# Search memory
results = client.search(
    chat_id="user_123",
    query="What does the user like?"
)

# Use results in your prompt
for result in results:
    print(result['content'])  # "I love pizza and my name is John"
```

### 4. Full Example (Flask + Local GGUF)
```python
[Your complete chatbot example here]
```

## 📖 Documentation
[Link to full docs when you make them]

## 💰 Pricing
Free during beta. Paid plans starting at $40/month after launch.
