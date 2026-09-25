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
