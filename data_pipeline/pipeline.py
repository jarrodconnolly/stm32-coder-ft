# data_pipeline/pipeline.py
import argparse
import os
import json
import hashlib
from pathlib import Path
import requests
from tqdm import tqdm
import git
import pymupdf4llm
import trafilatura
from unsloth import FastLanguageModel
from datasets import Dataset
import re
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
        r = requests.get(url, stream=True)
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
        downloaded = trafilatura.fetch_url(url)
        text = trafilatura.extract(downloaded, include_comments=False, include_tables=True)
        path.write_text(text or "No content", encoding="utf-8")
    
    print("Stage 1 complete!")

def stage_2_extract(args):
    print("=== Stage 2: Extract to Markdown ===")
    ensure_dir(CONFIG["extracted_dir"])
    
    # PDFs → Markdown (pymupdf4llm is excellent for code/tables)
    for pdf_file in Path(CONFIG["raw_pdfs_dir"]).glob("*.pdf"):
        out_path = Path(CONFIG["extracted_dir"]) / f"{pdf_file.stem}.md"
        if out_path.exists() and not args.force:
            continue
        print(f"Extracting {pdf_file.name}...")
        md = pymupdf4llm.to_markdown(str(pdf_file))
        out_path.write_text(md, encoding="utf-8")
    
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
            if any(ex in str(file) for ex in [".git", "__pycache__"]):
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

def stage_4_generate(args):
    print("=== Stage 4: Generate ShareGPT pairs with base model ===")
    ensure_dir(CONFIG["generated_dir"])
    
    # Load base model for inference (fast on your 4080)
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name="unsloth/Qwen2.5-Coder-7B-Instruct",
        max_seq_length=8192,
        dtype=None,
        load_in_4bit=True,
    )
    FastLanguageModel.for_inference(model)
    
    system_prompt = f"""You are an expert STM32 embedded C/C++ engineer specializing in the {CONFIG['board_name']} ({CONFIG['mcu']}). 
You know HAL, LL, CMSIS, register-level details, SparkFun pinout (LED on PC13, Qwiic I2C on PB6/PB7, etc.), common pitfalls, debugging, and best practices.
Always respond with complete, commented, production-ready code when asked. Include board-specific notes."""

    chunk_files = list(Path(CONFIG["chunks_dir"]).glob("*.txt"))
    if args.max_chunks:
        chunk_files = chunk_files[:args.max_chunks]
    
    total_pairs = 0
    for chunk_file in tqdm(chunk_files):
        chunk_text = chunk_file.read_text(encoding="utf-8")
        prompt = f"""{system_prompt}

Here is a document chunk from STM32F4 / SparkFun documentation or examples:

{chunk_text[:CONFIG['max_chunk_tokens']]}

Generate exactly {CONFIG['pairs_per_chunk']} diverse, realistic multi-turn ShareGPT conversations a developer would have with Continue.dev in VSCode while working on this board.
Each conversation must:
- Start with a realistic user question (code generation, explanation, debugging, refactoring, HAL vs LL, board-specific pinout, etc.)
- Have 2-6 turns (user/assistant)
- Include full working code with comments when relevant
- Mention SparkFun Thing Plus specifics when appropriate
- Cover edge cases, errors, optimizations

Output ONLY valid JSONL. Each line must be a complete JSON object:
{{"conversations": [ {{"from": "system", "value": "..."}}, {{"from": "user", "value": "..."}}, {{"from": "assistant", "value": "..."}} , ... ] }}
No extra text, no markdown.
"""
        
        inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
        #outputs = model.generate(**inputs, max_new_tokens=4096, temperature=0.7, top_p=0.95, do_sample=True)
        outputs = model.generate(**inputs, max_new_tokens=4096, temperature=0.6, top_p=0.92, do_sample=True, repetition_penalty=1.1)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True).split("Output ONLY valid JSONL")[-1].strip()
        
        json_lines = re.findall(r'\{.*?\}(?=\s*\{|\s*$)', response, re.DOTALL | re.MULTILINE)
        for i, line in enumerate(json_lines):
            try:
                # Remove any markdown code fences the model sometimes adds
                cleaned = re.sub(r'```json|```', '', line).strip()
                ex = json.loads(cleaned)
                if isinstance(ex.get("conversations"), list) and len(ex["conversations"]) >= 2:
                    out_file = Path(CONFIG["generated_dir"]) / f"{chunk_file.stem}_pairs_{i:03d}.jsonl"
                    out_file.write_text(json.dumps(ex, ensure_ascii=False) + "\n", encoding="utf-8")
                    total_pairs += 1
            except Exception:
                pass  # silently skip any malformed output
        
        if total_pairs >= CONFIG["target_pairs"] * 1.2:
            break  # safety buffer
    
    print(f"Generated ~{total_pairs} pairs. Review them in data_pipeline/generated_pairs/")

def stage_5_finalize(args):
    print("=== Stage 5: Finalize dataset ===")
    ensure_dir(CONFIG["final_dir"])
    
    all_files = list(Path(CONFIG["generated_dir"]).glob("*.jsonl"))
    examples = []
    seen = set()
    
    for f in tqdm(all_files):
        for line in f.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                ex = json.loads(line)
                # dedup by hash of conversations
                h = hashlib.md5(str(ex["conversations"]).encode()).hexdigest()
                if h not in seen:
                    seen.add(h)
                    examples.append(ex)
            except:  # noqa: E722
                pass
    
    # Shuffle & split
    import random
    random.shuffle(examples)
    n = len(examples)
    train = examples[:int(n*0.90)]
    val = examples[int(n*0.90):int(n*0.95)]
    test = examples[int(n*0.95):]
    
    def save_split(data, name):
        ds = Dataset.from_list(data)
        ds.to_json(Path(CONFIG["final_dir"]) / f"stm32_f405_{name}.jsonl")
    
    save_split(train, "train")
    save_split(val, "val")
    save_split(test, "test")
    
    print("Final dataset ready!")
    print(f"   Train: {len(train)} pairs")
    print(f"   Val:   {len(val)} pairs")
    print(f"   Test:  {len(test)} pairs")
    print("Files in data_pipeline/final/ — ready for training!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", type=int, required=True, choices=[1,2,3,4,5])
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--max-chunks", type=int, default=None)
    args = parser.parse_args()
    
    if args.stage == 1:
        stage_1_download(args)
    elif args.stage == 2:
        stage_2_extract(args)
    elif args.stage == 3:
        stage_3_chunk(args)
    elif args.stage == 4:
        stage_4_generate(args)
    elif args.stage == 5:
        stage_5_finalize(args)