import requests
import tkinter as tk
import webbrowser

from config import SERPER_API_KEY

# === Web search using Serper API ===
def search_web(query):
    """
    Performs a web search using Serper API (Google-like search) and returns
    a formatted string with the top 3 results.
    
    Args:
        query (str): Search query string.
    
    Returns:
        str: Formatted search results or error message.
    """
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": SERPER_API_KEY, # Replace with your actual API key
        "Content-Type": "application/json"
    }
    payload = {
        "q": query, 
        "hl": "en" # Language for search results; change as needed
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        results = data.get("organic", [])
        output = "Search: " + query + "\n\n"
        for r in results[:3]:
            title = r.get("title")
            link = r.get("link")
            snippet = r.get("snippet")
            output += f"• {title}\n{snippet}\n{link}\n\n"
        return output.strip()
    except Exception as e:
        return f"Error during web search: {e}"
    
# === Get official website of a brand using Google Knowledge Graph API ===
def get_brand_website(brand, api_key):
    """
    Searches for the official website of a brand using Google Knowledge Graph Search API.
    
    Args:
        brand (str): Brand or company name to search.
        api_key (str): API key for Google Knowledge Graph.
    
    Returns:
        str or None: URL of the brand's official website or None if not found.
    """
    url = "https://kgsearch.googleapis.com/v1/entities:search"
    params = {
        "query": brand,
        "limit": 1,
        "indent": True,
        "key": api_key,
    }
    response = requests.get(url, params=params)
    data = response.json()

    try:
        website = data["itemListElement"][0]["result"]["url"]
        return website
    except (KeyError, IndexError):
        return None

def insert_link(text_widget, url):
    """
    Inserts a clickable hyperlink into a Tkinter Text widget.  
    Changes text color and underline, and changes mouse cursor on hover.
    
    Args:
        text_widget (tk.Text): The Text widget where the link will be inserted.
        url (str): The URL to insert as a clickable link.
    """
    text_widget.insert(tk.END, "Website: ")
    start = text_widget.index(tk.END + " -1c")  # Start index of the URL
    text_widget.insert(tk.END, url + "\n")
    end = text_widget.index(tk.END + " -1c")    # End index of the URL
    text_widget.tag_add(url, start, end)
    text_widget.tag_config(url, foreground="#00FFFF", underline=True)
    text_widget.tag_bind(url, "<Button-1>", lambda e, u=url: webbrowser.open_new(u))
    text_widget.tag_bind(url, "<Enter>", lambda e: text_widget.config(cursor="hand2"))
    text_widget.tag_bind(url, "<Leave>", lambda e: text_widget.config(cursor=""))
