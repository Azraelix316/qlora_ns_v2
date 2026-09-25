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

