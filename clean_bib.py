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
