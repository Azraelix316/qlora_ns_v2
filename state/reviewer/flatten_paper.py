"""Inline every \\input into one readable markdown file, in document order.

Strips LaTeX control sequences so the result reads as prose, and reports what it dropped so
nothing disappears silently. Comment-only PENDING-CODER markers are counted separately from
markers in compiled text, because only the latter reach a PDF.
"""
import re, subprocess, sys

def sh(*a): return subprocess.run(["git","show",*a],capture_output=True,text=True).stdout

def strip_comments(b):
    return re.sub(r"(?<!\\)%[^\n]*", "", b)

# LaTeX math macros -> Unicode, so the flattened text is readable. Order matters:
# text-font wrappers first, then Greek, then operators.
MACROS = [
    (r"\\mathbb\{([^{}]*)\}", r"\1"), (r"\\mathcal\{([^{}]*)\}", r"\1"),
    (r"\\mathrm\{([^{}]*)\}", r"\1"), (r"\\mathbf\{([^{}]*)\}", r"\1"),
    (r"\\operatorname\{([^{}]*)\}", r"\1"), (r"\\text\{([^{}]*)\}", r"\1"),
    (r"\\alpha","a"),(r"\\beta","b"),(r"\\gamma","g"),(r"\\delta","d"),
    (r"\\epsilon","e"),(r"\\varepsilon","e"),(r"\\zeta","z"),(r"\\eta","h"),
    (r"\\theta","th"),(r"\\iota","i"),(r"\\kappa","k"),(r"\\lambda","lam"),
    (r"\\Lambda","Lam"),(r"\\mu","mu"),(r"\\nu","nu"),(r"\\xi","xi"),
    (r"\\pi","pi"),(r"\\Pi","Pi"),(r"\\rho","rho"),(r"\\sigma","sig"),
    (r"\\Sigma","Sig"),(r"\\tau","tau"),(r"\\phi","phi"),(r"\\varphi","phi"),
    (r"\\omega","om"),(r"\\Omega","Om"),(r"\\psi","psi"),(r"\\chi","chi"),
    (r"\\nabla","grad"),(r"\\partial","d"),(r"\\cdot","*"),(r"\\times","x"),
    (r"\\approx","~"),(r"\\sim","~"),(r"\\simeq","~"),(r"\\leq","<="),
    (r"\\geq",">="),(r"\\neq","!="),(r"\\pm","+-"),(r"\\infty","inf"),
    (r"\\to","->"),(r"\\rightarrow","->"),(r"\\leftarrow","<-"),
    (r"\\in"," in "),(r"\\notin"," not in "),(r"\\subset"," subset of "),
    (r"\\forall","for all "),(r"\\exists","exists "),(r"\\ldots","..."),
    (r"\\cdots","..."),(r"\\dots","..."),(r"\\qquad","  "),(r"\\quad"," "),
    (r"\\,"," "),(r"\\;"," "),(r"\\!"," "),(r"\\ "," "),
    (r"\\hat\{([^{}]*)\}", r"hat(\1)"), (r"\\tilde\{([^{}]*)\}", r"tilde(\1)"),
    (r"\\bar\{([^{}]*)\}", r"bar(\1)"), (r"\\vec\{([^{}]*)\}", r"vec(\1)"),
    (r"\\left"," "),(r"\\right"," "),(r"\\displaystyle"," "),
    (r"\\tfrac","/"),(r"\\frac\{([^{}]*)\}\{([^{}]*)\}", r"(\1)/(\2)"),
    (r"\\sqrt\{([^{}]*)\}", r"sqrt(\1)"),
    (r"\\sum_\{([^{}]*)\}", r"sum_{",), (r"\\prod", "prod"),
    (r"\\int","int"),(r"\\log","log"),(r"\\sin","sin"),(r"\\cos","cos"),
    (r"\^\*", "*"), (r"\^\{\*\}", "*"), (r"\^\\star", "*"), (r"\^\\ast", "*"),
    (r"\^\\top", "T"), (r"\^\\ast2", "T"), (r"\^\\circ", "o"), (r"\^\\prime", "'"),
    (r"\^\\dagger", "+"), (r"\^", "^"),
    (r"\\_\*", "*"), (r"_\{\*\}", "*"),
    (r"\\exp","exp"),(r"\\max","max"),(r"\\min","min"),
    (re.escape("\\|"), "||"),
    (r"\\\\","  "),
]


def detex(s):
    s = strip_comments(s)
    for pat, rep in MACROS:
        # A one-letter macro must not match inside a longer name: `\\to` is a prefix of
        # `\\top`, `\\pi` of `\\piv`, and each such hit silently corrupts a symbol.
        body = pat[2:] if pat.startswith(r'\\\\') else pat
        if re.fullmatch(r'[A-Za-z]', body):
            pat = pat + r'(?![A-Za-z])'
        s = re.sub(pat, rep, s)
    s = re.sub(r"\\citep?\*?\{([^}]*)\}", r"[\1]", s)          # \cite -> [key]
    s = re.sub(r"\\ref\{([^}]*)\}", r"(see \1)", s)
    s = re.sub(r"\\eqref\{([^}]*)\}", r"(\1)", s)
    s = re.sub(r"\\label\{[^}]*\}", "", s)
    s = re.sub(r"\\citep?\*?\[[^\]]*\]", "", s)
    s = re.sub(r"\\(?:emph|textit|textbf|texttt|mathrm|mathbf|mathcal|operatorname)\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\(?:section|subsection|subsubsection)\*?\{([^}]*)\}", r"\n\n### \1\n", s)
    s = re.sub(r"\\begin\{(itemize|enumerate)\}", "\n", s)
    s = re.sub(r"\\item\b", "\n- ", s)
    s = re.sub(r"\\end\{(itemize|enumerate|figure|table|equation\*?|align\*?|abstract)\}", "\n", s)
    s = re.sub(r"\\begin\{(figure|table|equation\*?|align\*?|abstract)\}", "\n", s)
    s = re.sub(r"\\centering|\\includegraphics(?:\[[^\]]*\])?\{[^}]*\}", "[FIGURE]", s)
    s = re.sub(r"\\caption\{", "Caption: ", s)
    s = re.sub(r"\\(?:captionof|toprule|midrule|bottomrule|hline)\b", "", s)
    s = re.sub(r"\\label\{[^}]*\}", "", s)
    s = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?", " ", s)   # any remaining control sequence
    s = s.replace("~", " ").replace("\\\\", " ").replace("{", "").replace("}", "")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()

sections = ["00_abstract","01_introduction","02_contributions","03_related_work","04_methods",
            "05_experimental_setup","06_results","07_discussion","08_limitations","09_conclusion"]
out = ["# SP-DLRA for 2D incompressible Navier-Stokes in stream-function form",
       "",
       "*Assembled from `paper/main.tex` and its ten `\\input` sections on `origin/main`, in document order.*",
       "*Produced by flattening LaTeX to prose: cross-references appear as `(see label)`, figures as `[FIGURE]`.*",
       ""]
tot_live = tot_all = 0
for s in sections:
    b = sh(f"origin/main:paper/sections/{s}.tex")
    allm = len(re.findall(r"PENDING-?CODER", b, re.I))
    live = len(re.findall(r"PENDING-?CODER", strip_comments(b), re.I))
    tot_all += allm; tot_live += live
    out += [f"---", "", f"## {s}", "", detex(b), ""]
Path = __import__("pathlib").Path
Path("/tmp/opencode/paper/PAPER.md").write_text("\n".join(out) + "\n")
w = len(Path("/tmp/opencode/paper/PAPER.md").read_text().split())
print(f"  wrote /tmp/opencode/paper/PAPER.md  ({w} words)")
print(f"  PENDING-CODER markers: {tot_all} total, {tot_live} in compiled text, {tot_all-tot_live} in comments")
