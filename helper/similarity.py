import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from database.db import get_history

# Initialize Sentence Transformer for embedding
model = SentenceTransformer('all-MiniLM-L6-v2')


def compute_similarity(user_id, query):
    """
    Compute cosine similarity between the current query and stored history for a specific user.
    """
    query_embedding = model.encode(query).reshape(1, -1)
    history = get_history(user_id)
    if not history:
        return []

    embeddings = np.array([np.array(row['embedding']) for row in history])
    similarities = cosine_similarity(query_embedding, embeddings).flatten()

    # Sort by similarity score
    similar_items = sorted(zip(history, similarities), key=lambda x: x[1], reverse=True)
    return [item[0] for item in similar_items if item[1] > 0.7]  # Return only highly similar items
