#!/usr/bin/env python3
"""
MkDocs → DOCX + PDF export script
===================================
Beolvassa a mkdocs.yml nav struktúráját, és minden fő szekciót
külön DOCX + PDF fájlba exportál.

Követelmények:
  pip install pyyaml
  pip install weasyprint        (PDF-hez)
  pip install markdown pygments  (PDF-hez)
  pandoc telepítése: https://pandoc.org/installing.html

Futtatás:
  python mkdocs_export.py --mkdocs-yml "C:\\...\\mkdocs.yml"
  python mkdocs_export.py --mkdocs-yml "C:\\...\\mkdocs.yml" --output-dir export
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

# ── Függőség-ellenőrzés ─────────────────────────────────────────────────────
try:
    import yaml
except ImportError:
    print("Hiányzó csomag: pyyaml\n  pip install pyyaml")
    sys.exit(1)


# ── Segédfüggvények ──────────────────────────────────────────────────────────

def slugify(text: str) -> str:
    """Fájlnévként biztonságos string készítése a fejezetcímből."""
    text = re.sub(r'[^\w\s\-]', '', text, flags=re.UNICODE)
    text = text.strip().replace(' ', '_')
    text = re.sub(r'_+', '_', text)
    return text or "document"


def parse_nav_section(nav_items, docs_dir: Path, depth: int = 1):
    """
    Rekurzívan bejárja a nav struktúrát.
    Visszaad: [(cím, md_fájl_útvonal | None, mélység), ...]
    """
    entries = []
    for item in nav_items:
        if isinstance(item, str):
            continue
        if isinstance(item, dict):
            for title, value in item.items():
                if isinstance(value, str):
                    entries.append((title, docs_dir / value, depth))
                elif isinstance(value, list):
                    entries.append((title, None, depth))
                    entries.extend(parse_nav_section(value, docs_dir, depth + 1))
    return entries


def process_markdown(content: str, md_path: Path) -> str:
    """MkDocs-specifikus elemek tisztítása."""
    # Makrók eltávolítása: {{ ... }}
    content = re.sub(r'\{\{[^}]*\}\}', '', content)

    # MkDocs admonition → blockquote
    def admonition_replace(m):
        kind = m.group(1).lower()
        title = m.group(2) or kind.capitalize()
        body = re.sub(r'\n    ', '\n', m.group(3)).strip()
        return f"\n> **{title}:** {body}\n"

    content = re.sub(
        r'!!! (\w+)(?: "([^"]*)")?\n((?:    .+\n?)+)',
        admonition_replace,
        content
    )

    # Relatív képútvonalak → abszolút (JAVÍTÁS: file:// URI a PDF-hez)
    md_dir = md_path.parent
    def image_abs(m):
        prefix, path, suffix = m.group(1), m.group(2), m.group(3)
        if path.startswith('http') or path.startswith('/') or path.startswith('file://'):
            return m.group(0)
        abs_path = (md_dir / path).resolve()
        # FIX #2 – PDF: file:// URI nélkül a WeasyPrint nem tölti be a képeket
        return f"{prefix}{abs_path.as_uri()}{suffix}"

    content = re.sub(r'(!\[.*?\]\()([^)]+)(\))', image_abs, content)
    return content


def build_section_markdown(title: str, entries, docs_dir: Path) -> str:
    """Összefűzi egy szekció összes .md fájlját egyetlen Markdown stringgé."""
    parts = []

    parts.append(f'---\ntitle: "{title}"\ntoc: true\ntoc-depth: 3\n---\n\n')

    for entry_title, md_path, depth in entries:
        heading = "#" * min(depth, 6)

        if md_path is None:
            parts.append(f"\n{heading} {entry_title}\n\n")
            continue

        if not md_path.exists():
            print(f"    ⚠  Hiányzó fájl: {md_path}")
            parts.append(f"\n{heading} {entry_title}\n\n*[A fájl nem található: {md_path.name}]*\n\n")
            continue

        raw = md_path.read_text(encoding="utf-8")

        # Front-matter eltávolítása
        raw = re.sub(r'^---\n.*?\n---\n', '', raw, flags=re.DOTALL)

        processed = process_markdown(raw, md_path)

        # Fejléc szintek eltolása a nav-mélység szerint
        shift = depth
        def shift_headings(m, _shift=shift):
            hashes = m.group(1)
            rest = m.group(2)
            new_level = min(len(hashes) + _shift - 1, 6)
            return "#" * new_level + rest
        processed = re.sub(r'^(#+)( .+)$', shift_headings, processed, flags=re.MULTILINE)

        parts.append(f"\n{heading} {entry_title}\n\n")
        parts.append(processed.strip())
        parts.append("\n\n")

    return "".join(parts)


# ── Pandoc / PDF konverzió ───────────────────────────────────────────────────

def check_pandoc() -> bool:
    try:
        result = subprocess.run(["pandoc", "--version"], capture_output=True, text=True)
        print(f"  ✓ {result.stdout.split(chr(10))[0]}")
        return True
    except FileNotFoundError:
        print("  ✗ Pandoc nem található! Telepítés: https://pandoc.org/installing.html")
        return False


def convert_to_docx(md_file: Path, output_file: Path, reference_doc: Path = None) -> bool:
    """
    FIX #3 – DOCX tartalomjegyzék: a pandoc --toc flag csak az egyszerű
    szöveges TOC-ot szúrja be. Valódi, kattintható Word-TOC-hoz
    --lua-filter=toc.lua szükséges, VAGY a legegyszerűbb megoldás:
    egy üres TOC-placeholder bekezdés a sablonban, amelyet a pandoc
    nem érint – Word maga generálja azt megnyitáskor (F9).

    Ha nincs sablon, a pandoc alapból beilleszti a szöveges TOC-ot.
    Ha van sablon, a sablonban lévő TOC-mezőt Word frissíti.
    """
    cmd = [
        "pandoc", str(md_file),
        "-o", str(output_file),
        "--toc", "--toc-depth=3",
        "--from=markdown+smart",
        "--highlight-style=tango",
        "--wrap=none",
        # FIX #3 – pandoc beépített TOC blokkot illeszt be, ez Word-ben
        # automatikusan frissíthető; referencia-doc nélkül is működik.
    ]

    # FIX #4 – Sablon (reference-doc) helyes használata:
    # A pandoc reference-doc esetén a sablon ÖSSZES stílusát átveszi
    # (Normal, Heading 1..6, Code, Compact, Table stb.).
    # Ha a sablonban ezek a stílusok nincsenek definiálva / eltérő nevűek,
    # a kimenet rossz formázású lesz.
    #
    # Megoldás: a sablont pandoc-cal kell legenerálni:
    #   pandoc -o reference.docx --print-default-data-file reference.docx
    # Ezután a reference.docx stílusait kell szerkeszteni (ne szöveget!),
    # majd azt adni meg --reference-doc-nak.
    #
    # TILOS: teljesen egyedi .docx-et adni sablonnak, mert az nem tartalmaz
    # pandoc-stílusokat → a kimenet formázatlan lesz.
    if reference_doc and reference_doc.exists():
        cmd += ["--reference-doc", str(reference_doc)]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"    ✗ DOCX hiba: {result.stderr}")
        return False
    return True


def convert_to_pdf(md_file: Path, output_file: Path) -> bool:
    try:
        from weasyprint import HTML
        import markdown
        from pygments.formatters import HtmlFormatter
    except ImportError:
        print("    ✗ Hiányzó csomagok: pip install weasyprint markdown pygments")
        return False

    md_content = md_file.read_text(encoding="utf-8")
    md_content = re.sub(r'^---\n.*?\n---\n', '', md_content, flags=re.DOTALL)

    pygments_css = HtmlFormatter(style="tango").get_style_defs('.codehilite')

    md = markdown.Markdown(
        extensions=['toc', 'tables', 'fenced_code', 'codehilite', 'nl2br'],
        extension_configs={
            'codehilite': {'css_class': 'codehilite', 'linenums': False},
            'toc': {'toc_depth': 3},
        }
    )

    html_body_content = md.convert(md_content)
    toc_html = md.toc

    html_body = f"""
    <div class="toc">
    <h1>Tartalomjegyzék</h1>
    {toc_html}
    </div>

    {html_body_content}
    """

    css = f"""
    @page {{
        size: A4;
        margin: 2cm 2.5cm 2cm 2.5cm;
        @top-center {{ content: string(doc-title); font-size: 9pt; color: #666; }}
        @bottom-right {{ content: counter(page) " / " counter(pages); font-size: 9pt; color: #666; }}
    }}
    body {{ font-family: "Segoe UI", Arial, sans-serif; font-size: 10.5pt; line-height: 1.6; color: #1a1a1a; }}
    h1 {{
        string-set: doc-title content();
        font-size: 20pt; color: #1a56a0;
        border-bottom: 2px solid #1a56a0; padding-bottom: 6px;
        margin-top: 1.5em; page-break-before: always;
    }}
    h1:first-of-type {{ page-break-before: avoid; }}
    h2 {{ font-size: 15pt; color: #1a56a0; margin-top: 1.2em; }}
    h3 {{ font-size: 12pt; color: #2c6fad; margin-top: 1em; }}
    h4 {{ font-size: 10.5pt; color: #444; font-style: italic; }}
    .toc {{ background: #f0f4f8; border: 1px solid #c8d8e8; border-radius: 4px; padding: 16px 24px; margin-bottom: 2em; }}
    .toc ul {{ margin: 4px 0; padding-left: 20px; }}
    .toc a {{ color: #1a56a0; text-decoration: none; }}

    /* FIX #1 – Szöveg kilógás megelőzése */
    * {{ box-sizing: border-box; }}
    pre {{
        white-space: pre-wrap;       /* sortörés hosszú soroknál */
        word-break: break-all;       /* szó közepi törés ha szükséges */
        overflow-wrap: break-word;
    }}
    .codehilite {{
        background: #f6f8fa; border: 1px solid #e1e4e8; border-radius: 4px;
        padding: 12px 16px;
        /* overflow-x: auto helyett wrap: */
        white-space: pre-wrap;
        word-break: break-all;
        overflow-wrap: break-word;
        font-size: 9pt;
        line-height: 1.45; margin: 1em 0; page-break-inside: avoid;
        max-width: 100%;
    }}
    code {{ font-family: "Consolas", "Courier New", monospace; font-size: 9pt; background: #f0f0f0; padding: 1px 4px; border-radius: 3px; word-break: break-all; }}
    pre code {{ background: none; padding: 0; }}

    /* FIX #1 – Táblázatok se lógjanak ki */
    table {{
        border-collapse: collapse;
        width: 100%;
        max-width: 100%;
        table-layout: fixed;         /* fix szélesség, töri a szöveget */
        margin: 1em 0; font-size: 9.5pt; page-break-inside: avoid;
    }}
    th, td {{ word-wrap: break-word; overflow-wrap: break-word; }}
    th {{ background: #1a56a0; color: white; padding: 6px 10px; text-align: left; }}
    td {{ border: 1px solid #ddd; padding: 5px 10px; }}
    tr:nth-child(even) {{ background: #f5f8fc; }}

    /* FIX #1 – Képek se lógjanak ki */
    img {{
        max-width: 100%;
        height: auto;
        display: block;
    }}

    blockquote {{ border-left: 4px solid #1a56a0; background: #f0f4f8; margin: 1em 0; padding: 8px 16px; color: #333; }}
    {pygments_css}
    """

    full_html = f"""<!DOCTYPE html>
<html lang="hu"><head><meta charset="utf-8"><style>{css}</style></head>
<body>{html_body}</body></html>"""

    try:
        # FIX #2 – base_url = md_file.parent hogy a relatív képútvonalak feloldódjanak.
        # A process_markdown() már file:// URI-ra konvertálja a képutakat,
        # de a base_url megadása is szükséges tartalékként.
        HTML(string=full_html, base_url=str(md_file.parent)).write_pdf(str(output_file))
        return True
    except Exception as e:
        print(f"    ✗ PDF hiba: {e}")
        return False


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="MkDocs → külön DOCX + PDF szekciónként")
    parser.add_argument("--mkdocs-yml", default="mkdocs.yml")
    parser.add_argument("--docs-dir", default=None)
    parser.add_argument("--output-dir", default="export")
    parser.add_argument("--reference-doc", default=None, help="Pandoc DOCX sablon (.docx)")
    parser.add_argument("--no-pdf", action="store_true")
    parser.add_argument("--no-docx", action="store_true")
    args = parser.parse_args()

    mkdocs_yml = Path(args.mkdocs_yml)
    if not mkdocs_yml.exists():
        print(f"✗ Nem található: {mkdocs_yml}")
        sys.exit(1)

    with open(mkdocs_yml, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    docs_dir = Path(args.docs_dir) if args.docs_dir else mkdocs_yml.parent / "docs"
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    nav = config.get("nav", [])
    if not nav:
        print("✗ Nem található 'nav:' szekció.")
        sys.exit(1)

    print(f"\n{'='*55}")
    print("  MkDocs Export — szekciónként")
    print(f"{'='*55}")
    print(f"  Docs:    {docs_dir}")
    print(f"  Kimenet: {output_dir.resolve()}\n")

    pandoc_ok = check_pandoc() if not args.no_docx else False
    ref_doc = Path(args.reference_doc) if args.reference_doc else None

    generated = []

    # ── Fő szekciók feldolgozása (nav első szintje) ──────────────────────────
    for idx, item in enumerate(nav, start=1):
        if not isinstance(item, dict):
            continue

        for section_title, section_value in item.items():
            slug = slugify(section_title)
            prefix = f"{idx:02d}_{slug}"

            print(f"\n[{idx}] {section_title}")

            if isinstance(section_value, str):
                # Egyszerű oldal (pl. "🏠 Kezdőlap": index.md)
                entries = [(section_title, docs_dir / section_value, 1)]
            elif isinstance(section_value, list):
                entries = parse_nav_section(section_value, docs_dir, depth=1)
            else:
                print("    ⚠  Ismeretlen nav struktúra, kihagyva.")
                continue

            file_count = sum(1 for e in entries if e[1] is not None)
            print(f"    {file_count} markdown fájl")

            # Összefűzött Markdown mentése
            md_path = output_dir / f"{prefix}.md"
            combined_md = build_section_markdown(section_title, entries, docs_dir)
            md_path.write_text(combined_md, encoding="utf-8")

            # DOCX generálás
            if not args.no_docx and pandoc_ok:
                docx_path = output_dir / f"{prefix}.docx"
                if convert_to_docx(md_path, docx_path, ref_doc):
                    print(f"    ✓ DOCX: {docx_path.name}")
                    generated.append(docx_path.name)
                else:
                    print(f"    ✗ DOCX: sikertelen")

            # PDF generálás
            if not args.no_pdf:
                pdf_path = output_dir / f"{prefix}.pdf"
                if convert_to_pdf(md_path, pdf_path):
                    print(f"    ✓ PDF:  {pdf_path.name}")
                    generated.append(pdf_path.name)
                else:
                    print(f"    ✗ PDF:  sikertelen")

    print(f"\n{'='*55}")
    print(f"  Kész! {len(generated)} fájl generálva → {output_dir.resolve()}")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()
