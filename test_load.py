from unsloth import FastLanguageModel
import torch

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/Qwen2.5-Coder-7B-Instruct",
    max_seq_length = 4096,
    dtype = None,           # Auto-detect (BF16 on your 4080)
    load_in_4bit = True,
    # token = "hf_..."      # only if using gated models
)

print("✅ Model loaded successfully in 4-bit! VRAM should be ~6 GB")
FastLanguageModel.for_inference(model)  # speeds up inference