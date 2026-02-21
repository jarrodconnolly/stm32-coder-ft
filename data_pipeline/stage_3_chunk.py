# stage_3_chunk.py
import os
from pathlib import Path
from config import CONFIG

def ensure_dir(path): os.makedirs(path, exist_ok=True)

def stage_3_chunk(args):
    print("=== Stage 3: Chunking ===")
    ensure_dir(CONFIG["chunks_dir"])
    chunks = []
    for md_file in Path(CONFIG["extracted_dir"]).glob("*.md"):
        text = md_file.read_text(encoding="utf-8")
        # Simple heading-based chunking
        sections = text.split("\n## ")
        for i, sec in enumerate(sections):
            chunk = "## " + sec if i > 0 else sec
            if len(chunk) < 200:
                continue
            chunk_name = f"{md_file.stem}_chunk{i:03d}.txt"
            Path(CONFIG["chunks_dir"]).joinpath(chunk_name).write_text(chunk, encoding="utf-8")
            chunks.append(chunk_name)
    print(f"Created {len(chunks)} chunks. Ready for generation.")
    return chunks

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    args = parser.parse_args()  # No args needed
    stage_3_chunk(args)