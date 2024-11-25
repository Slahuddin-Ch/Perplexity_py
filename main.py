import os
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from database.db import (
    add_message,
    get_chat_history,
    authenticate_user,
    initialize_user_database,
    get_all_chat_ids,  # Helper to fetch all chat IDs
)
from agents.GoogleSearch import academic_search_agent
from agents.VideoSearch import video_search_agent 

def fetch_all_contexts(user_id):
    """
    Fetch all chat contexts for the user.
    """
    chat_ids = get_all_chat_ids(user_id)  # Get all chat IDs for the user
    if not chat_ids:
        return "No chats found for this user."

    history = []
    for chat_id in chat_ids:
        context = fetch_context_from_history(user_id, chat_id)
        history.append(f"Chat ID: {chat_id}\n{context}\n")
    return "\n".join(history)


def fetch_context_from_history(user_id, chat_id):
    """
    Fetch recent chat history to determine the context for the agent.
    """
    chat_history = get_chat_history(user_id, chat_id)
    if not chat_history:
        return "No prior context available."

    # Map SQLAlchemy rows to dictionary-like access or access by tuple index
    return "\n".join(
        [
            f"{msg.role.capitalize()}: {msg.content}"
            if hasattr(msg, "role")
            else f"{msg[4].capitalize()}: {msg[1]}"
            for msg in chat_history[-5:]
        ]
    )


def main():
    """
    Main entry point for managing users, their databases, and chat interactions.
    """
    print("Welcome to the Chat System!")
    
    # Authenticate user
    user_id = authenticate_user()  # Use `user_id` directly

    # Initialize user database
    initialize_user_database(user_id)

    while True:
        # Show options before prompting for chat ID
        print("\nOptions:")
        print("1. Send a message to the current agent")
        print("2. View chat history")
        print("\nEnter chat ID (or type 'new' for a new chat):")
        chat_id_or_action = input().strip()

        if chat_id_or_action == "1":
            agent_name = input("Enter agent name (e.g., academic, video): ").strip().lower()
            chat_id = input(f"Enter chat ID for {agent_name} agent (or type 'new' for a new chat): ").strip()
            is_new_chat = chat_id.lower() == "new"
            if is_new_chat:
                chat_id = f"{agent_name}_chat_{datetime.now().strftime('%Y:%m:%d:%H:%M')}"
                print(f"Starting a new chat session with ID: {chat_id}")
            else:
                print(f"Using existing chat session with ID: {chat_id}")

        elif chat_id_or_action == "2":
            print("\nAll Chat Histories:")
            print(fetch_all_contexts(user_id))  # Fetch and display all chat histories
            continue  # Restart the loop to show the main options again

        else:
            agent_name = "general"  # Default agent name if not specified
            chat_id = chat_id_or_action
            is_new_chat = chat_id.lower() == "new"
            if is_new_chat:
                chat_id = f"{agent_name}_chat_{datetime.now().strftime('%Y:%m:%d:%H:%M')}"
                print(f"Starting a new chat session with ID: {chat_id}")
            else:
                print(f"Using existing chat session with ID: {chat_id}")

        current_agent = None  # Track the currently selected agent

        while True:
            if not current_agent:
                # Show options for selecting an agent
                print("\nOptions:")
                print("1. Academic Search")
                print("2. Video Search")
                print("3. Quit Chat")
                choice = input("Choose an option (1/2/3): ").strip()

                if choice == "3" or choice.lower() == "quit":
                    print(f"Exiting chat session {chat_id}.")
                    break
                elif choice == "1":
                    current_agent = academic_search_agent
                    agent_name = "academic"
                elif choice == "2":
                    current_agent = video_search_agent
                    agent_name = "video"
                else:
                    print("Invalid choice. Please try again.")
                    continue

            # User message
            user_message = input("\nYou: ").strip()
            if user_message == "@help":
                print("\nOptions:")
                print("1. Send a message to the current agent")
                print("2. View chat history")
                print("3. Change agent")
                option = input("Choose an option (1/2/3): ").strip()

                if option == "3":
                    # Reset the current agent and show the agent selection menu
                    current_agent = None
                    continue
                elif option == "2":
                    # Show chat history
                    print(f"\nChat Context:\n{fetch_context_from_history(user_id, chat_id)}")
                    continue
                elif option != "1":
                    print("Invalid choice. Please try again.")
                    continue

            if not user_message:
                print("Message cannot be empty. Please try again.")
                continue

            # Save user message to chat history
            try:
                add_message(
                    user_id=user_id,
                    chat_id=chat_id,
                    message_id=f"{chat_id}_msg_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    content=user_message,
                    role="user",
                )
            except IntegrityError as e:
                print(f"Error saving message: {e}")
                continue

            # Process the message using the current agent
            response = current_agent(user_id, chat_id, user_message)
            print(f"Agent: {response}")

            # Save agent response to chat history
            try:
                add_message(
                    user_id=user_id,
                    chat_id=chat_id,
                    message_id=f"{chat_id}_response_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    content=response,
                    role="assistant",
                )
            except IntegrityError as e:
                print(f"Error saving response: {e}")
                continue

        # Optionally, confirm if the user wants another session
        continue_chat = input("\nDo you want to start another chat? (yes/no): ").strip().lower()
        if continue_chat != "yes":
            print("Goodbye!")
            break


if __name__ == "__main__":
    main()
