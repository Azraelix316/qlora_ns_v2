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
