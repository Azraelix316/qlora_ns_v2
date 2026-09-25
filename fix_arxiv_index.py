import json

path = 'state/writing-research/arxiv_index.json'
with open(path, 'r') as f:
    data = json.load(f)

# A1 - Entry 15 (Index 14)
if len(data) > 14:
    entry = data[14]
    if "10.1016/j.compflu.2022.105536" in entry['id']:
        entry['id'] = entry['id'].replace('compflu', 'compfluid')
        print("Fixed A1: Entry 15 DOI")

# A4 - Entry 26 (Index 25)
if len(data) > 25:
    entry = data[25]
    if entry.get('type') == 'query_result':
        entry['query'] = 'all:"divergence-free" AND all:"dynamical low-rank"'
        entry['count'] = 0
        entry['notes'] = "No arXiv record matches both exact phrases."
        print("Fixed A4: Entry 26 query/notes")

# A2 - Entry 27 (Index 26) -> Replace with Lubich & Oseledets
if len(data) > 26:
    data[26] = {
        "id": "https://doi.org/10.1007/s10543-013-0454-0",
        "title": "A projector-splitting integrator for dynamical low-rank approximation",
        "updated": "2026-09-25T00:00:00Z",
        "summary": "Develops projector-splitting methods for the efficient and robust integration of dynamical systems on low-rank manifolds.",
        "authors": ["Christian Lubich", "Ivan V. Oseledets"],
        "relevant": True
    }
    print("Fixed A2: Entry 27 replaced with correct record")

# A3 - Entry 28 (Index 27) -> Olga to Othmar
if len(data) > 27:
    entry = data[27]
    authors = entry.get('authors', [])
    new_authors = ["Othmar Koch" if a == "Olga Koch" else a for a in authors]
    entry['authors'] = new_authors
    print("Fixed A3: Entry 28 author name")

with open(path, 'w') as f:
    json.dump(data, f, indent=2)
