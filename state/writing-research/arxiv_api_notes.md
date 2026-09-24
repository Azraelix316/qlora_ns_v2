=== File: test_arxiv.py ===
import subprocess

def test_curl():
    # Try to fetch the arXiv homepage first to see if it's a general block or API-specific
    cmd = ["curl", "-I", "https://arxiv.org/"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(f"Status Code: {result.returncode}")
    print(f"Headers: {result.stdout}")

    # Try to query the API with a custom User-Agent
    # Query for "dynamical low-rank approximation Navier-Stokes"
    query = "all:\"dynamical low-rank approximation\" AND all:\"Navier-Stokes\""
    api_url = f"http://export.arxiv.org/api/query?search_query={query}&max_results=5"
    cmd = ["curl", "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36", "-I", api_url]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(f"\nAPI Query Headers: {result.stdout}")

if __name__ == "__main__":
    test_curl()


=== File: test_arxiv_v2.py ===
import subprocess

def test_curl():
    print("--- Testing arXiv Homepage ---")
    cmd = ["curl", "-v", "https://arxiv.org/"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(f"STDOUT:\n{result.stdout}")
    print(f"STDERR:\n{result.stderr}")

    print("\n--- Testing arXiv API with User-Agent ---")
    query = "all:\"dynamical low-rank approximation\""
    api_url = f"http://export.arxiv.org/api/query?search_query={query}&max_results=1"
    # Using a more common user agent
    cmd = ["curl", "-A", "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)", "-v", api_url]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(f"STDOUT:\n{result.stdout}")
    print(f"STDERR:\n{result.stderr}")

if __name__ == "__main__":
    test_curl()


=== File: test_arxiv_v3.py ===
import requests

def test_requests():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    query = 'all:"dynamical low-rank approximation"'
    url = f"https://export.arxiv.org/api/query?search_query={query}&max_results=5"

    print(f"Testing URL: {url}")
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print("Headers:")
        for k, v in response.headers.items():
            print(f"  {k}: {v}")
        if response.status_code == 200:
            print("\nContent Preview (first 500 chars):")
            print(response.text[:500])
        else:
            print("\nError Body:")
            print(response.text)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_requests()


=== File: test_arxiv_v4.py ===
import requests

def test_requests():
    # Try different Accept headers and User-Agents
    test_cases = [
        {
            "name": "Standard Chrome",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "*/*"
            }
        },
        {
            "name": "Explicit Atom Accept",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "application/atom+xml,application/xml,text/xml"
            }
        },
        {
            "name": "Simple Python Requests",
            "headers": {
                "User-Agent": "python-requests/2.31.0",
                "Accept": "*/*"
            }
        },
        {
            "name": "Old Browser",
            "headers": {
                "User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
        }
    ]

    query = 'all:"dynamical low-rank approximation"'
    url = f"https://export.arxiv.org/api/query?search_query={query}&max_results=1"

    for case in test_cases:
        print(f"--- Testing Case: {case['name']} ---")
        print(f"URL: {url}")
        try:
            response = requests.get(url, headers=case['headers'])
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                print("SUCCESS!")
                print(response.text[:200])
            else:
                print(f"FAILED with status {response.status_code}")
        except Exception as e:
            print(f"Error: {e}")
        print("\n")

if __name__ == "__main__":
    test_requests()


=== File: test_arxiv_v5.py ===
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


