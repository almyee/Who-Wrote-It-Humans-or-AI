import nltk
from nltk.chat.util import Chat, reflections

# Define a set of input-response pairs that the chatbot will use to engage in conversation
pairs = [
    (r'hi|hello|hey', ['Hello! How can I help you today?', 'Hey there! What’s up?']),
    (r'bye', ['Goodbye! It was nice talking to you.', 'See you later!']),
    (r'(.*)', ['Sorry, I didn’t quite understand that. Could you rephrase your question?'])
]

# Create the chatbot by passing the pairs and reflection dictionary
chatbot = Chat(pairs, reflections)

# Start a conversation with the user
chatbot.converse()  # This function will keep the conversation going until the user ends it

