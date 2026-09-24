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
