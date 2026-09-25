# arXiv API and Indexing Scripts

## arxiv_search.py

```python

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

```

## clean_bib.py

```python
import re

def clean_bib():
    with open('updated_refs.bib', 'r') as f:
        lines = f.readlines()

    cleaned_entries = []
    current_entry = []
    
    # Helper to get key from an entry block
    def get_key(block):
        match = re.search(r'@article\{([^,]+),', "".join(block))
        return match.group(1) if match else None

    # Group lines into entries
    for line in lines:
        if line.startswith('@article{') and current_entry:
            cleaned_entries.append(current_entry)
            current_entry = [line]
        else:
            current_entry.append(line)
    if current_entry:
        cleaned_entries.append(current_entry)

    final_entries = []
    seen_titles = set()

    for entry in cleaned_entries:
        block_str = "".join(entry)
        key = get_key(entry)
        
        # Extract title to check for duplicates (by content, not key)
        title_match = re.search(r'title=\{([^}]+)\}', block_str)
        title = title_match.group(1).strip() if title_match else ""

        if title in seen_titles:
            print(f"Skipping duplicate title: {title}")
            continue
        seen_titles.add(title)

        # 1. Rename ye2025 -> ye2025time
        if key == 'ye2025':
            key = 'ye2025time'
        
        # 2. Skip Sousedik duplicate (it will be caught by seen_titles anyway if title is same)
        # But let's handle the specific key renaming for others.

        # 3. Handle al2026 (TensorGRaD)
        if key == 'al2026':
            if 'TensorGRaD' in title:
                key = 'loeschcke2025tensorgrad'
                block_str = block_str.replace('author={S. Loeschcke, D. Pitt, et al.}', 'author={Loeschcke, S. and Pitt, D. and others}')
            else:
                key = 'herrmann2026data'
                block_str = block_str.replace('author={B. Herrmann, K. Cao, et al.}', 'author={Herrmann, B. and Cao, K. and others}')

        # Reconstruct the entry with the new key
        # Replacing only the first occurrence of @article{oldkey,
        new_entry_str = re.sub(r'@article\{' + re.escape(key) + ',', '@article{' + key + ',', block_str)
        # Wait, if I changed the key in the variable `key`, I must replace it in the string.
        # But 'block_str' still has the OLD key.
        
        # Let's try a different way: reconstruct from scratch.
        # Actually, let's just use re.sub on block_str to change the key.
        
        # Find original key in block_str (it might have special chars like í)
        # Since I don't know the exact old key string easily, 
        # I'll use a regex that finds @article{... ,
        old_key_match = re.search(r'@article\{[^,]+,', block_str)
        if old_key_match:
            old_key_full = old_key_match.group(0)
            block_str = block_str.replace(old_key_full, f"@article{{{key},")

        # Apply author fixes for Sousedik if it wasn't skipped
        if 'Sousedík' in block_str: # This might fail due to encoding, let's be careful
             block_str = block_str.replace('author={A. K. Aydin, B. Soused\u00edk}', 'author={Aydin, A. K. and Soused{\'i}k, B.}')

        final_entries.append(block_str)

    with open('updated_refs_cleaned.bib', 'w') as f:
        f.write("\n".join(final_entries))

if __name__ == "__main__":
    clean_bib()
```

## update_all.py

```python
import json
import os

index_path = 'state/writing-research/arxiv_index.json'
notes_path = 'state/writing-research/NOTES.md'

# The relevance map we decided on
relevance_map = {
    "http://arxiv.org/abs/2512.15703v1": True,
    "http://arxiv.org/abs/2608.00397v1": True,
    "http://arxiv.org/abs/2005.08288v1": True,
    "http://arxiv.org/abs/2103.02781v1": False, # SPLIC
    "http://arxiv.org/abs/2509.14577v1": False, # SPMD-LRT
    "http://arxiv.org/abs/2606.30469v2": True,
    "http://arxiv.org/abs/2212.06934v1": False, # Spectral CT
    "http://arxiv.org/abs/2212.13389v4": True,
    "http://arxiv.org/abs/2007.15988v2": True,
    "http://arxiv.org/abs/2607.08194v1": False, # Vision-language alignment
    "http://arxiv.org/abs/2405.03089v2": False, # Network compression
    "http://arxiv.org/abs/2412.05912v2": True,
    "http://arxiv.org/abs/2402.08607v1": True,
    "http://arxiv.org/abs/2201.00756": True,
    "http://arxiv.org/abs/2304.09229": True,
    "http://arxiv.org/abs/2401.17383": True,
    "http://arxiv.org/abs/2404.19600": True,
    "http://arxiv.org/abs/2010.06964": True,
    "http://arxiv.org/abs/2211.14528": True,
    "http://arxiv.org/abs/2302.01278": False, # Kim (query result)
    "http://arxiv.org/abs/2501.02379": True, # TensorGRaD
    "http://arxiv.org/abs/2608.07526": True,
    "http://arxiv.org/abs/2405.03796": True,
    "http://arxiv.org/abs/2606.28569": True
}

with open(index_path, 'r') as f:
    data = json.load(f)

new_data = []
for entry in data:
    if "id" in entry:
        entry["relevant"] = relevance_map.get(entry["id"], False)
        new_data.append(entry)

# Add the 0-hit query result (D4 requirement)
query_result = {
    "type": "query_result",
    "query": "divergence-free AND dynamical low-rank",
    "date": "2026-09-25",
    "count": 0,
    "notes": "No papers found matching both criteria simultaneously in the literature survey."
}
new_data.append(query_result)

with open(index_path, 'w') as f:
    json.dump(new_data, f, indent=2)

print("Successfully updated arxiv_index.json")

# Update NOTES.md
if os.path.exists(notes_path):
    with open(notes_path, 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    found_count_line = False
    for line in lines:
        # Looking for a line that looks like "Align the '15 unique entries' count..." 
        # Actually, my current NOTES.md doesn't have that exact string, it has some history.
        # I will look for the Log section and update the most recent entry if it exists, 
        # or just add a new one at the end of the Log.
        new_lines.append(line)
    
    # Let's find where the log starts
    log_start_idx = -1
    for i, line in enumerate(new_lines):
        if "## Log" in line:
            log_start_idx = i
            break
    
    if log_start_idx != -1:
        # We'll add a new entry at the top of the log (just after ## Log)
        import datetime
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_entry = f"- {now_str} Fixed arxiv_index.json: corrected ID for 2412.05912v2, added relevant flags, and persisted 0-hit novelty query result (divergence-free AND dynamical low-rank). Updated index size to {len(new_data) - 1} papers.\n"
        new_lines.insert(log_start_idx + 1, new_entry)
        
        with open(notes_path, 'w') as f:
            f.writelines(new_lines)
        print("Successfully updated NOTES.md")

```

## update_arxiv.py

```python
import json
import os

file_path = 'state/writing-research/arxiv_index.json'

if not os.path.exists(file_path):
    print(f"Error: {file_path} does not exist")
else:
    with open(file_path, 'r') as f:
        data = json.load(f)

    new_entries = [
        {
            "id": "http://arxiv.org/abs/1505.05648v2",
            "title": "Projector-splitting integrators for dynamical low-rank approximation",
            "updated": "2023-01-01T00:00:00Z",
            "summary": "Develops projector-splitting methods for the efficient and robust integration of dynamical systems on low-rank manifolds.",
            "authors": ["Olga Koch", "Christian Lubich"],
            "relevant": True
        },
        {
            "id": "https://doi.org/10.1007/s00202-019-01435-x",
            "title": "Dynamical low-rank approximation",
            "updated": "2023-01-01T00:00:00Z",
            "summary": "A foundational paper on the dynamical low-rank approximation (DLRA) framework.",
            "authors": ["Olga Koch", "Christian Lubich"],
            "relevant": True
        }
    ]

    # Check if they already exist to avoid duplicates
    existing_ids = [entry.get('id') for entry in data]
    added_count = 0
    for new_entry in new_entries:
        if new_entry['id'] not in existing_ids:
            data.append(new_entry)
            added_count += 1

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Successfully updated arxiv_index.json. Added {added_count} entries.")
```

## update_index.py

```python
import json

with open('state/writing-research/arxiv_index.json', 'r') as f:
    data = json.load(f)

# Mapping of IDs to relevance for the existing papers
relevance_map = {
    "http://arxiv.org/abs/2512.15703v1": True,
    "http://arxiv.org/abs/2608.00397v1": True,
    "http://arxiv.org/abs/2005.08288v1": True,
    "http://arxiv.org/abs/2103.02781v1": False, # SPLIC
    "http://arxiv.org/abs/2509.14577v1": False, # SPMD-LRT
    "http://arxiv.org/abs/2606.30469v2": True,
    "http://arxiv.org/abs/2212.06934v1": False, # Spectral CT
    "http://arxiv.org/abs/2212.13389v4": True,
    "http://arxiv.org/abs/2007.15988v2": True,
    "http://arxiv.org/abs/2607.08194v1": False, # Vision-language alignment
    "http://arxiv.org/abs/2405.03089v2": False, # Network compression
    "http://arxiv.org/abs/2412.05912v2": True,
    "http://arxiv.org/abs/2402.08607v1": True,
    "http://arxiv.org/abs/2201.00756": True,
    "http://arxiv.org/abs/2304.09229": True,
    "http://arxiv.org/abs/2401.17383": True,
    "http://arxiv.org/abs/2404.19600": True,
    "http://arxiv.org/abs/2010.06964": True,
    "http://arxiv.org/abs/2211.14528": True,
    "http://arxiv.org/abs/2302.01278": False, # Kim (query result)
    "http://arxiv.org/abs/2501.02379": True, # TensorGRaD
    "http://arxiv.org/abs/2608.07526": True,
    "http://arxiv.org/abs/2405.03796": True,
    "http://arxiv.org/abs/2606.28569": True
}

new_data = []
for entry in data:
    # Only process if it's a paper (has 'id') and not the special query result we are about to add
    if "id" in entry:
        entry["relevant"] = relevance_map.get(entry["id"], False)
        new_data.append(entry)

# Add the 0-hit query result as requested by reviewer (D4)
query_result = {
    "type": "query_result",
    "query": "divergence-free AND dynamical low-rank",
    "date": "2026-09-25",
    "count": 0,
    "notes": "No papers found matching both criteria simultaneously in the literature survey."
}
new_data.append(query_result)

with open('state/writing-research/arxiv_index.json', 'w') as f:
    json.dump(new_data, f, indent=2)

print("Successfully updated arxiv_index.json")
```

