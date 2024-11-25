from helper.searxng import GoogleSearch
from helper.ollama import query_openai
from database.db import get_chat_history


def academic_search_agent(user_id, chat_id, query=None):
    """
    Agent interface for academic search using SearxNG, Ollama, and user-specific history.
    """
    print(f"Processing academic query for user {user_id}, chat ID {chat_id}.")

    # Step 1: Fetch chat history from the user's database
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

    # Step 3: Perform an academic search using SearxNG
    search_results = GoogleSearch(query, engine="google scholar")
    if not search_results:
        return "Failed to retrieve academic search results."

    # Step 4: Prepare a summary of search results for Ollama
    search_summary = "\n".join(
        [f"- {result['title']}: {result['url']}" for result in search_results[:5]]
    )

    prompt = (
        f"I conducted an academic search for user '{user_id}' with the query '{query}'. "
        f"Here are the top results:\n"
        f"{search_summary}\n\n"
        f"Please summarize these academic resources or provide recommendations."
    )

    # Step 5: Use Ollama to process the results
    ollama_response = query_openai(prompt)
    if not ollama_response:
        return "Failed to retrieve response from Ollama."

    return ollama_response

