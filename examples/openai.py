from chatsorter_client import ChatSorter
import openai

memory = ChatSorter(api_key="sk_test_...")
openai.api_key = "your-openai-key"

def chat_with_memory(user_id, message):
    # Get relevant context from memory
    context = memory.get_context(chat_id=user_id, message=message)
    
    # Build prompt with context
    messages = [
        {"role": "system", "content": f"Relevant context:\n{context}"},
        {"role": "user", "content": message}
    ]
    
    # Call OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    
    # Store the interaction
    memory.add_message(chat_id=user_id, message=message)
    
    return response.choices[0].message.content

# Use it
response = chat_with_memory("user123", "What's my favorite food?")
print(response)  # "Based on what you've told me, your favorite food is pizza!"