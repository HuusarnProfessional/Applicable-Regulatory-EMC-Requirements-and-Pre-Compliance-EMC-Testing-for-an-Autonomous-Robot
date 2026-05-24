from __future__ import annotations

import pathlib
import re


ROOT = pathlib.Path(__file__).resolve().parent.parent
REPORT = ROOT / "report.tex"
README = ROOT / "README.md"


def load_text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def extract(pattern: str, text: str) -> str:
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else ""


def clean_inline(text: str) -> str:
    text = text.replace("~", " ")
    text = text.replace("\\%", "%")
    text = text.replace("\\_", "_")
    text = text.replace("\\&", "&")
    text = re.sub(r"\\textit\{([^{}]*)\}", r"*\1*", text)
    text = re.sub(r"\\textbf\{([^{}]*)\}", r"**\1**", text)
    text = re.sub(r"\\href\{([^{}]*)\}\{([^{}]*)\}", r"[\2](\1)", text)
    text = re.sub(r"\\cite\{([^{}]*)\}", r"[\1]", text)
    text = re.sub(r"\\label\{[^{}]*\}", "", text)
    text = re.sub(r"\\ref\{([^{}]*)\}", r"\1", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def convert_math(text: str) -> str:
    text = re.sub(r"\\tag\*\{\[\\ref\{[^{}]*\}\]\}", "", text)
    text = re.sub(r"\\tag\*\{[^{}]*\}", "", text)
    text = re.sub(r"\\\((.*?)\\\)", lambda m: f"${m.group(1).strip()}$", text, flags=re.DOTALL)
    text = re.sub(r"\\\[(.*?)\\\]", lambda m: f"\n$$\n{m.group(1).strip()}\n$$\n", text, flags=re.DOTALL)
    text = re.sub(
        r"\\begin\{equation\*\}(.*?)\\end\{equation\*\}",
        lambda m: f"\n$$\n{m.group(1).strip()}\n$$\n",
        text,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"\\begin\{equation\}(.*?)\\end\{equation\}",
        lambda m: f"\n$$\n{m.group(1).strip()}\n$$\n",
        text,
        flags=re.DOTALL,
    )
    return text


def strip_latex_wrappers(text: str) -> str:
    text = text.replace("\\centering", "")
    text = text.replace("\\small", "")
    text = re.sub(r"\\setlength\{[^{}]*\}\{[^{}]*\}", "", text)
    text = re.sub(r"\\caption\{([^{}]*)\}", r"\nTable: \1\n", text)
    text = re.sub(r"\{\\raggedright", "", text)
    text = text.replace("\\par}", "")
    text = text.replace("{@{}p{0.30\\linewidth}p{0.32\\linewidth}p{0.32\\linewidth}@{}}", "")
    text = text.replace("{@{}p{0.25\\linewidth}p{0.22\\linewidth}p{0.23\\linewidth}p{0.22\\linewidth}@{}}", "")
    return text


def convert_figures(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        body = match.group(1)
        image_path = extract(r"\\includegraphics(?:\[[^\]]*\])?\{([^{}]*)\}", body)
        caption = extract(r"\\caption\{(.*?)\}", body)

        parts = []
        if image_path:
            alt_text = clean_inline(caption) if caption else pathlib.Path(image_path).stem
            parts.append(f"![{alt_text}]({image_path})")
        if caption:
            parts.append(f"*{clean_inline(caption)}*")
        return "\n\n" + "\n\n".join(parts) + "\n\n"

    return re.sub(r"\\begin\{figure\}\[H\](.*?)\\end\{figure\}", repl, text, flags=re.DOTALL)


def convert_tabular(tabular_text: str) -> str:
    rows = []
    for raw_row in tabular_text.split("\\\\"):
        row = raw_row.strip()
        if not row or row == r"\hline":
            continue
        row = row.replace(r"\hline", "")
        cols = [clean_inline(col) for col in row.split("&")]
        cols = [col for col in cols if col]
        if cols:
            rows.append(cols)
    if not rows:
        return ""
    width = max(len(row) for row in rows)
    normalized = [row + [""] * (width - len(row)) for row in rows]
    header = normalized[0]
    divider = ["---"] * width
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(divider) + " |",
    ]
    for row in normalized[1:]:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines) + "\n"


def convert_tables(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        body = strip_latex_wrappers(match.group(0))
        tabular = extract(r"\\begin\{tabular\}(.*?)\\end\{tabular\}", body)
        caption = extract(r"Table:\s*(.*?)\n", body)
        table_md = convert_tabular(tabular)
        parts = []
        if caption:
            parts.append(f"\n**{clean_inline(caption)}**\n")
        if table_md:
            parts.append(table_md)
        return "\n".join(parts)

    return re.sub(r"\\begin\{table\}\[H\].*?\\end\{table\}", repl, text, flags=re.DOTALL)


def convert_enumerate(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        items = re.findall(r"\\item\s+(.*?)(?=(\\item|$))", match.group(1), flags=re.DOTALL)
        lines = []
        for index, item in enumerate(items, start=1):
            lines.append(f"{index}. {clean_inline(item[0])}")
        return "\n" + "\n".join(lines) + "\n"

    return re.sub(r"\\begin\{enumerate\}(.*?)\\end\{enumerate\}", repl, text, flags=re.DOTALL)


def convert_sections(text: str) -> str:
    text = re.sub(r"\\section\{([^{}]*)\}", r"\n## \1\n", text)
    text = re.sub(r"\\subsection\{([^{}]*)\}", r"\n### \1\n", text)
    return text


def normalize_paragraphs(text: str) -> str:
    lines = [line.rstrip() for line in text.splitlines()]
    output = []
    paragraph = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            output.append(clean_inline(" ".join(paragraph)))
            paragraph = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            if output and output[-1] != "":
                output.append("")
            continue
        if stripped.startswith(("## ", "### ", "| ", "$$", "1. ", "2. ", "3. ", "4. ", "5. ", "**")):
            flush_paragraph()
            output.append(stripped)
            continue
        paragraph.append(stripped)

    flush_paragraph()
    return "\n".join(output)


def convert_content(text: str) -> str:
    text = convert_math(text)
    text = convert_figures(text)
    text = convert_tables(text)
    text = convert_enumerate(text)
    text = convert_sections(text)
    text = strip_latex_wrappers(text)
    text = re.sub(r"\\begin\{document\}|\\end\{document\}", "", text)
    return normalize_paragraphs(text).strip()


def build_readme() -> str:
    report = load_text(REPORT)
    title = clean_inline(extract(r"\\title\{(.*?)\}", report))
    author = clean_inline(extract(r"\\author\{(.*?)\}", report))
    inputs = re.findall(r"\\input\{([^{}]+)\}", report)

    parts = [f"# {title}", f"*Author: {author}*", ""]
    for input_name in inputs:
        tex_path = ROOT / f"{input_name}.tex"
        parts.append(convert_content(load_text(tex_path)))
        parts.append("")

    parts.append("> This README is generated from the LaTeX source files. Edit the `.tex` files, not this document.")
    return "\n".join(part for part in parts if part is not None).rstrip() + "\n"


def main() -> None:
    README.write_text(build_readme(), encoding="utf-8")


if __name__ == "__main__":
    main()
