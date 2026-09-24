import requests
from urllib.parse import quote

def test_requests():
    # Test 1: Query without quotes, properly encoded
    print("--- Testing Case: No Quotes, Encoded ---")
    query = 'all:dynamical' # simplified
    encoded_query = quote(query)
    url = f"https://export.arxiv.org/api/query?search_query={encoded_query}&max_results=1"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/atom+xml"
    }

    try:
        response = requests.get(url, headers=headers)
        print(f"URL: {url}")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("SUCCESS!")
            print(response.text[:200])
        else:
            print(f"FAILED with status {response.status_code}")
            print(f"Body: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_requests()
