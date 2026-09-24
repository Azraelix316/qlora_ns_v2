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
