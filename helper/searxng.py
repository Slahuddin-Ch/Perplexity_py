import requests

# Default configurations for SearxNG
SEARXNG_URL = "http://localhost:32768"  # Replace with your SearxNG API endpoint
SEARXNG_HEADERS = {"Content-Type": "application/json"}

class GoogleSearch:
    @staticmethod
    def search_searxng(query, engine="google"):
        """
        Query SearxNG and retrieve search results.
        :param query: Search query string.
        :param engine: Specific search engine to use (default: "google").
        :return: List of search results or None in case of an error.
        """
        params = {
            "q": query,
            "engines": engine,
            "format": "json"
        }
        try:
            response = requests.get(SEARXNG_URL, headers=SEARXNG_HEADERS, params=params, timeout=10)
            response.raise_for_status()
            return response.json().get("results", [])
        except requests.RequestException as e:
            print(f"Error querying SearxNG: {e}")
            return None



class VideoSearch:
    def __init__(self, searxng_url="http://localhost:32768"):
        """
        Initialize the VideoSearch instance with a SearXNG URL.
        :param searxng_url: URL of the SearXNG instance.
        """
        self.searxng_url = searxng_url

    def search(self, query, engine="youtube"):
        """
        Perform a video search using SearXNG.
        :param query: The search query string.
        :param engine: The specific search engine to use (default: "youtube").
        :return: A list of search results.
        """
        params = {
            "q": query,
            "engines": engine,
            "format": "json",
        }
        try:
            response = requests.get(self.searxng_url, params=params, timeout=10)
            response.raise_for_status()
            return response.json().get("results", [])
        except requests.RequestException as e:
            print(f"Error querying SearXNG: {e}")
            return []
