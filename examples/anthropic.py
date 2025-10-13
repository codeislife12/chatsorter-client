from chatsorter_client import ChatSorter
import anthropic

memory = ChatSorter(api_key="sk_test_...")
claude = anthropic.Anthropic(api_key="your-claude-key")

def chat_with_memory(user_id, message):
    # Get context
    context = memory.get_context(chat_id=user_id, message=message)
    
    # Call Claude
    response = claude.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"Context: {context}\n\nUser: {message}"
        }]
    )
    
    # Store interaction
    memory.add_message(chat_id=user_id, message=message)
    
    return response.content[0].text