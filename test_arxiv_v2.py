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
