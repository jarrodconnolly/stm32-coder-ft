# stage_1_download.py
import os
from pathlib import Path
import requests
from tqdm import tqdm
import git
from config import CONFIG

def ensure_dir(path): os.makedirs(path, exist_ok=True)

def stage_1_download(args):
    print("=== Stage 1: Download (idempotent) ===")
    ensure_dir(CONFIG["raw_pdfs_dir"])
    ensure_dir(CONFIG["raw_repos_dir"])
    ensure_dir(CONFIG["raw_web_dir"])
    
    # PDFs
    for name, url in CONFIG["pdfs"].items():
        path = Path(CONFIG["raw_pdfs_dir"]) / f"{name}.pdf"
        if path.exists() and not args.force:
            print(f"✓ {name}.pdf already exists")
            continue
        print(f"↓ Downloading {name}...")
        headers = {
            'accept-language': 'en-GB,en;q=0.7',
            'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Brave";v="144"',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36'
        }
        r = requests.get(url, headers=headers, stream=True)
        with open(path, "wb") as f:
            for chunk in tqdm(r.iter_content(chunk_size=8192), unit="MB", total=int(r.headers.get("content-length", 0))//8192):
                f.write(chunk)
    
    # Repos
    for name, url in CONFIG["repos"].items():
        path = Path(CONFIG["raw_repos_dir"]) / name
        if path.exists() and not args.force:
            print(f"✓ Repo {name} already cloned")
            continue
        print(f"↓ Cloning {name}...")
        try:
            git.Repo.clone_from(url, path)
        except Exception as e:
            print(f"⚠️ Could not clone {name}: {e} (skipping)")
    
    # Web
    for name, url in CONFIG["web"].items():
        path = Path(CONFIG["raw_web_dir"]) / f"{name}.md"
        if path.exists() and not args.force:
            print(f"✓ {name} already scraped")
            continue
        print(f"↓ Scraping {name}...")
        import trafilatura
        downloaded = trafilatura.fetch_url(url)
        text = trafilatura.extract(downloaded, include_comments=False, include_tables=True)
        path.write_text(text or "No content", encoding="utf-8")
    
    print("Stage 1 complete!")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    stage_1_download(args)