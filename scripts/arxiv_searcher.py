import requests
import xml.etree.ElementTree as ET
import json
import urllib.parse

def fetch_arxiv(query, max_results=50):
    """Fetches papers from arXiv API using the exact method from test_arxiv_v3.py."""
    base_url = "https://export.arxiv.org/api/query"
    encoded_query = urllib.parse.quote(query)
    url = f"{base_url}?search_query={encoded_query}&max_results={max_results}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/atom+xml,application/xml,text/xml"
    }

    print(f"Requesting URL: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            print(f"Error fetching from arXiv: {response.status_code}")
            # Print first 500 chars of body for debugging
            print(f"Response Body Snippet: {response.text[:500]}")
            return ""
        return response.text
    except Exception as e:
        print(f"Exception during fetch: {e}")
        return ""

def parse_arxiv_xml(xml_content):
    """Parses arXiv XML response into a list of dicts."""
    if not xml_content:
        return []
    
    papers = []
    try:
        root = ET.fromstring(xml_content)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        for entry in root.findall('atom:entry', ns):
            paper = {}
            id_elem = entry.find('atom:id', ns)
            paper['id'] = id_elem.text.strip() if id_elem is not None else ""
            
            title_elem = entry.find('atom:title', ns)
            paper['title'] = title_elem.text.strip().replace('\n', ' ') if title_elem is not None else ""
            
            authors = []
            for author in entry.findall('atom:author', ns):
                name_elem = author.find('atom:name', ns)
                if name_elem is not None:
                    authors.append(name_elem.text.strip())
            paper['authors'] = authors
            
            summary_elem = entry.find('atom:summary', ns)
            paper['summary'] = summary_elem.text.strip().replace('\n', ' ') if summary_elem is not None else ""
            
            updated_elem = entry.find('atom:updated', ns)
            paper['updated'] = updated_elem.text if updated_elem is not None else ""
            
            papers.append(paper)
    except Exception as e:
        print(f"Error parsing XML: {e}")
    
    return papers

def main():
    # Start with a very simple query to ensure connectivity
    test_queries = [
        'all:"Navier-Stokes"',
        'all:"dynamical low-rank approximation" AND all:"Navier-Stokes"',
        '"divergence-free" AND "low-rank" AND "Navier-Stokes"'
    ]
    
    all_found_papers = []
    
    for query in test_queries:
        print(f"\n--- Running query: {query} ---")
        xml_data = fetch_arxiv(query)
        if xml_data:
            papers = parse_arxiv_xml(xml_data)
            print(f"Found {len(papers)} papers.")
            all_found_papers.extend(papers)
        else:
            print("No data returned for this query.")

    # Deduplicate by ID
    unique_papers = {}
    for p in all_found_papers:
        if p['id'] not in unique_papers:
            unique_papers[p['id']] = p
    
    final_list = list(unique_papers.values())
    print(f"\nTotal unique papers found: {len(final_list)}")
    
    output_file = 'arxiv_results_temp.json'
    with open(output_file, 'w') as f:
        json.dump(final_list, f, indent=2)
    print(f"Saved to {output_file}")

if __name__ == "__main__":
    main()
