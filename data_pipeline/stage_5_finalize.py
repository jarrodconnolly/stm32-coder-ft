# stage_5_finalize.py
import os
import json
import hashlib
from pathlib import Path
from tqdm import tqdm
from datasets import Dataset
import random
from config import CONFIG

def ensure_dir(path): os.makedirs(path, exist_ok=True)

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
    import argparse
    parser = argparse.ArgumentParser()
    args = parser.parse_args()  # No args needed
    stage_5_finalize(args)