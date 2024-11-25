from helper.searxng import VideoSearch
from database.db import get_chat_history

def video_search_agent(user_id, chat_id, query=None):
    """
    Agent interface for video search using the VideoSearch class.
    """
    print(f"Processing video search query for user {user_id}, chat ID {chat_id}.")

    # Step 1: Fetch chat history
    chat_history = get_chat_history(user_id, chat_id)
    if not chat_history:
        print(f"No chat history found for user {user_id} and chat ID {chat_id}.")
        context = "No prior context available."
    else:
        # Prepare a summary of the user's recent chat history
        context = "\n".join([f"- {msg.content}" for msg in chat_history[-5:]])  # Last 5 messages

    # Step 2: Use the provided query or infer search intent from chat history
    if not query:
        query = f"Based on the chat history:\n{context}\nWhat should I search for?"

    print(f"Inferred query: {query}")

    # Step 3: Perform a video search using the VideoSearch class
    video_search = VideoSearch()  # Initialize the VideoSearch instance
    search_results = video_search.search(query, engine="youtube")
    if not search_results:
        return "Failed to retrieve video search results."

    # Step 4: Prepare and return a summary of video search results
    video_summary = "\n".join(
        [f"{idx + 1}. {result.get('title', 'No Title')}: {result.get('url', 'No URL')}" for idx, result in enumerate(search_results[:5])]
    )

    return f"Here are the top video results for your query:\n{video_summary}"
