# stage_4_generate.py
import os
from pathlib import Path
from tqdm import tqdm
import re
import json
from unsloth import FastLanguageModel
from config import CONFIG

def ensure_dir(path): os.makedirs(path, exist_ok=True)

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

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-chunks", type=int, default=None)
    args = parser.parse_args()
    stage_4_generate(args)