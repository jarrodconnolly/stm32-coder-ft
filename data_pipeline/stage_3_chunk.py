# stage_3_chunk.py
import os
from pathlib import Path
from config import CONFIG
from langchain_text_splitters import RecursiveCharacterTextSplitter

def ensure_dir(path): os.makedirs(path, exist_ok=True)

def stage_3_chunk(args):
    print("=== Stage 3: Chunking ===")
    ensure_dir(CONFIG["chunks_dir"])
    chunks = []
    code_stats = {"whole": 0, "split_files": 0, "split_chunks": 0, "total_size": 0}
    
    for md_file in Path(CONFIG["extracted_dir"]).glob("*.md"):
        text = md_file.read_text(encoding="utf-8")
        file_type = md_file.stem.split('_')[0]  # e.g., 'code', 'pdf', 'web'
        
        if file_type == 'code':
            # Pre-split on file boundaries
            file_sections = text.split("\n### ")
            for i, section in enumerate(file_sections):
                if i == 0 and not section.startswith("### "):
                    # First part before any ###, skip if empty
                    continue
                section = ("### " + section) if i > 0 else section
                if len(section) < 8000:
                    # Keep whole
                    chunk_name = f"{md_file.stem}_file{i:04d}.txt"
                    Path(CONFIG["chunks_dir"]).joinpath(chunk_name).write_text(section, encoding="utf-8")
                    chunks.append(chunk_name)
                    code_stats["whole"] += 1
                    code_stats["total_size"] += len(section)
                else:
                    # Split with enhanced separators
                    separators = ["\n### ", "\n## ", "\n# ", "\nenum ", "\nstruct ", "\nunion ", "\nvoid ", "\nint ", "\n#define ", "\n\n", "\n", " "]
                    splitter = RecursiveCharacterTextSplitter(
                        separators=separators,
                        chunk_size=10000,  # Large to allow buffering
                        chunk_overlap=0,
                        length_function=len,
                        is_separator_regex=False
                    )
                    sub_chunks = splitter.split_text(section)
                    # Buffer sub-chunks
                    buffer = []
                    buffer_size = 0
                    chunk_count = 0
                    for sub in sub_chunks:
                        if buffer_size + len(sub) > 8000 and buffer:
                            # Yield buffer
                            combined = "\n".join(buffer)
                            chunk_name = f"{md_file.stem}_file{i:04d}_chunk{chunk_count:03d}.txt"
                            Path(CONFIG["chunks_dir"]).joinpath(chunk_name).write_text(combined, encoding="utf-8")
                            chunks.append(chunk_name)
                            code_stats["total_size"] += len(combined)
                            chunk_count += 1
                            buffer = [sub]
                            buffer_size = len(sub)
                        else:
                            buffer.append(sub)
                            buffer_size += len(sub)
                    # Yield remaining buffer
                    if buffer:
                        combined = "\n".join(buffer)
                        chunk_name = f"{md_file.stem}_file{i:04d}_chunk{chunk_count:03d}.txt"
                        Path(CONFIG["chunks_dir"]).joinpath(chunk_name).write_text(combined, encoding="utf-8")
                        chunks.append(chunk_name)
                        code_stats["total_size"] += len(combined)
                        chunk_count += 1
                    if chunk_count > 0:
                        code_stats["split_files"] += 1
                        code_stats["split_chunks"] += chunk_count
        else:
            # PDFs and web: paragraph-based
            separators = ["\n\n", "\n", " ", ""]
            splitter = RecursiveCharacterTextSplitter(
                separators=separators,
                chunk_size=2000,
                chunk_overlap=200,
                length_function=len,
                is_separator_regex=False
            )
            doc_chunks = splitter.split_text(text)
            for i, chunk in enumerate(doc_chunks):
                if len(chunk) < 200:
                    continue
                chunk_name = f"{md_file.stem}_chunk{i:03d}.txt"
                Path(CONFIG["chunks_dir"]).joinpath(chunk_name).write_text(chunk, encoding="utf-8")
                chunks.append(chunk_name)
    
    # Print stats
    total_chunks = len(chunks)
    if code_stats["whole"] + code_stats["split_chunks"] > 0:
        avg_size = code_stats["total_size"] / (code_stats["whole"] + code_stats["split_chunks"])
        print(f"Code stats: {code_stats['whole']} whole files, {code_stats['split_files']} split files into {code_stats['split_chunks']} chunks, avg size {avg_size:.0f} chars")
    print(f"Created {total_chunks} chunks total. Ready for generation.")
    return chunks

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    args = parser.parse_args()  # No args needed
    stage_3_chunk(args)