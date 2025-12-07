from urllib import response
import requests
from fastmcp import FastMCP
BASE_URL = "https://openlibrary.org"
# MCP server global
mcp = FastMCP("OpenLibrary Assistant")
@mcp.tool()
def search_books(query: str) -> list:
    """
    Search for books in OpenLibrary using a query string.
    Returns a list of titles with their work IDs.
    """
    response = requests.get(
        f"{BASE_URL}/search.json",
        params={"q": query},
        timeout=10
    )
 
    if response.status_code != 200:
        return {"error": f"API Error {response.status_code}"}
 
    data = response.json()
 
    books = data.get("docs", [])[:10]  # limit to first 10 results
 
    return [
        {
            "title": b.get("title"),
            "author": b.get("author_name", ["Unknown"])[0],
            "year": b.get("first_publish_year"),
            "work_id": b.get("key")  # e.g. "/works/OL82563W"
        }
        for b in books
    ]
if __name__ == "__main__":
    
    mcp.run(transport="stdio")