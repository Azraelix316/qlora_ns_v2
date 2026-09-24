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
