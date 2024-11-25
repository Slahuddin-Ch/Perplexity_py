import openai

# Set your OpenAI API key
# openai.api_key = 
def query_openai(prompt, model="gpt-4"):
    """
    Query OpenAI API with a given prompt and model.
    """
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an academic assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        # Extract and return the model's response
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error querying OpenAI: {e}")
        return None
