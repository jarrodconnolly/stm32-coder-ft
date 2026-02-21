# stage2.py - Isolated Stage 2 for debugging PDF extraction
import os
from pathlib import Path
import pdfplumber  # Alternative to pymupdf4llm
from config import CONFIG

def ensure_dir(path): os.makedirs(path, exist_ok=True)

def stage_2_extract(args):
    print("=== Stage 2: Extract to Markdown (Isolated with pdfplumber) ===")
    ensure_dir(CONFIG["extracted_dir"])
    
    # PDFs → Markdown
    for pdf_file in Path(CONFIG["raw_pdfs_dir"]).glob("*.pdf"):
        out_path = Path(CONFIG["extracted_dir"]) / f"{pdf_file.stem}.md"
        if out_path.exists() and not args.force:
            print(f"Skipping {pdf_file.name} (already exists)")
            continue
        print(f"Extracting {pdf_file.name}...")
        try:
            with pdfplumber.open(pdf_file) as pdf:
                md_content = []
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        md_content.append(text)
                md = "\n\n".join(md_content)
            out_path.write_text(md, encoding="utf-8")
            print(f"✓ Extracted {len(md)} chars")
        except Exception as e:
            print(f"⚠️ Failed {pdf_file.name}: {e}")
    
    # Repos → structured Markdown
    for repo_dir in Path(CONFIG["raw_repos_dir"]).glob("*"):
        if not repo_dir.is_dir():
            continue
        out_path = Path(CONFIG["extracted_dir"]) / f"{repo_dir.name}_code.md"
        if out_path.exists() and not args.force:
            continue
        print(f"Extracting code from {repo_dir.name}...")
        content = []
        for file in repo_dir.rglob("*.[chmd]"):  # .c .h .md
            if any(ex in str(file) for ex in [".git", "__pycache__", "Utilities", "Projects"]):
                continue
            try:
                rel = file.relative_to(repo_dir)
                content.append(f"### File: {rel}\n```{file.suffix[1:]}\n{file.read_text(encoding='utf-8', errors='ignore')}\n```\n")
            except:  # noqa: E722
                pass
        out_path.write_text("\n".join(content), encoding="utf-8")
    
    # Web + Local
    for src_dir, prefix in [(CONFIG["raw_web_dir"], "web_"), (CONFIG["local_code_dir"], "mycode_"), (CONFIG["local_extra_pdfs"], "extra_")]:
        for f in Path(src_dir).glob("**/*"):
            if f.is_file() and f.suffix in [".md", ".txt", ".c", ".h"]:
                out_path = Path(CONFIG["extracted_dir"]) / f"{prefix}{f.stem}.md"
                if out_path.exists() and not args.force:
                    continue
                text = f.read_text(encoding="utf-8", errors="ignore")
                if f.suffix in [".c", ".h"]:
                    text = f"### File: {f.name}\n```c\n{text}\n```"
                out_path.write_text(text, encoding="utf-8")
    
    print("Stage 2 complete!")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")  # Not used, but for consistency
    args = parser.parse_args()
    stage_2_extract(args)