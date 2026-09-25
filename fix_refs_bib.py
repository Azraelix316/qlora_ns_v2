import re

path = 'refs.bib'
with open(path, 'r') as f:
    content = f.read()

# 1. Fix Olga Koch -> Othmar Koch
# The line is: author={Koch, Olga and Lubich, Christian},
new_content = re.sub(
    r'author=\{Koch, Olga and Lubich, Christian\}',
    'author={Koch, Othmar and Lubich, Christian}',
    content
)

if new_content != content:
    print("Fixed Olga Koch -> Othmar Koch in refs.bib")
else:
    print("Could not find Olga Koch entry to fix.")

# 2. Add Lubich & Oseledets (2014) citation
lubich_oseledets = """
@article{lubich2014projector,
  title={A projector-splitting integrator for dynamical low-rank approximation},
  author={Lubich, Christian and Oseledets, Ivan V.},
  journal={BIT Numerical Mathematics},
  volume={54},
  number={1},
  pages={171--188},
  year={2014},
  doi={10.1007/s10543-013-0454-0}
}
"""

if "lubich2014projector" not in new_content:
    new_content = new_content.strip() + "\n" + lubich_oseledets.strip() + "\n"
    print("Added Lubich & Oseledets citation")
else:
    print("Lubich & Oseledets citation already exists")

with open(path, 'w') as f:
    f.write(new_content)
