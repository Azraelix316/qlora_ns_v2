
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

def search_arxiv(query):
    base_url = 'http://export.arxiv.org/api/query'
    params = {
        'search_query': query,
        'start': 0,
        'max_results': 10
    }
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(base_url, params=params, headers=headers)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return []
    
    root = ET.fromstring(response.content)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    
    results = []
    for entry in root.findall('atom:entry', ns):
        title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
        arxiv_id = entry.find('atom:id', ns).text.split('/')[-1]
        published_str = entry.find('atom:published', ns).text
        # published format is usually 2025-01-01T00:00:00Z
        published_date = datetime.strptime(published_str[:10], '%Y-%m-%d')
        summary = entry.find('atom:summary', ns).text.strip()
        
        results.append({
            'id': arxiv_id,
            'title': title,
            'date': published_date,
            'summary': summary
        })
    return results

queries = [
    'all:"Navier-Stokes"'
]

all_findings = []
seen_ids = set()

for q in queries:
    print(f"Searching for: {q}")
    try:
        found = search_arxiv(q)
        for item in found:
            if item['id'] not in seen_ids:
                # Check if published in 2025 or 2026
                if item['date'].year >= 2025:
                    all_findings.append(item)
                    seen_ids.add(item['id'])
    except Exception as e:
        print(f"Error searching {q}: {e}")

print("\n--- RESULTS ---")
if not all_findings:
    print("No relevant papers found for 2025-2026.")
else:
    for item in all_findings:
        print(f"ID: {item['id']}")
        print(f"Title: {item['title']}")
        print(f"Date: {item['date'].strftime('%Y-%m-%d')}")
        print(f"Summary: {item['summary'][:200]}...")
        print("-" * 30)

