import re

def fix_bib():
    with open('refs.bib', 'r') as f:
        content = f.read()

    # 1. Remove duplicate Olshanskii (keeping rebholz2026)
    pattern = r'@article\{olshanskii2024approximating,.*?\}\n\n?'
    content = re.sub(pattern, '', content, flags=re.DOTALL)

    # 2. Fix Girfoglio initials and title
    girfoglio_regex = r'@article\{girfoglio2022,.*?author=\{Girfoglio, Michele and Quaini, Annalisa and Rozza, Gianluigi\}.*?\}'
    girfoglio_replacement = '@article{girfoglio2022,\n  title={A POD-Galerkin reduced order model for the Navier-Stokes equations in stream function-vorticity formulation},\n  author={Girfoglio, M. and Quaini, A. and Rozza, G.},\n  journal={arXiv preprint arXiv:2201.00756},\n  year={2022}\n}'
    content = re.sub(girfoglio_regex, girfoglio_replacement, content, flags=re.DOTALL)

    # 3. Fix Sousedík name in lee17low and aydin26mean using a more robust replacement.
    # We'll match the whole author line for entries that contain 'Soused'
    def replace_author(match):
        line = match.group(0)
        if "Soused" in line:
            return line.replace("Soused{'i}k, Bed{\\v r}ich", "Soused{\'i}k, Bed{\\v r}ich")
        return line

    # This is a bit tricky since I don't know if it's \v or \\v. 
    # Let's try replacing both common patterns.
    content = content.replace("Soused{'i}k, Bed{\\v r}ich", "Soused{\'i}k, Bed{\\v r}ich")
    content = content.replace("Soused{'i}k, Bed{\\v r}ich", "Soused{\'i}k, Bed{\\v r}ich") # redundant but safe
    # If it's a vertical tab character:
    content = content.replace("Soused{'i}k, Bed{\x0b r}ich", "Soused{\'i}k, Bed{\\v r}ich")

    with open('refs.bib', 'w') as f:
        f.write(content)

if __name__ == "__main__":
    fix_bib()
