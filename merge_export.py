# export_to_gguf.py
# Self-contained Merge + GGUF Export for Unsloth QLoRA
# Run this AFTER training (in the same folder as your "stm32-coder-qlora" directory)

from unsloth import FastLanguageModel

# ================== CONFIG ==================
ADAPTER_PATH = "stm32-coder-qlora"      # ← this is where training saved your adapters
OUTPUT_BASE_NAME = "stm32-coder"        # final model name (will become stm32-coder_q5_k_m etc.)
MAX_SEQ_LENGTH = 8192                   # safe to go higher for export than training

# Recommended quants for a 7B coding model on RTX 4080:
# q5_k_m = best quality/size balance (recommended first)
# q4_k_m = smaller & still excellent
QUANT_METHODS = ["q5_k_m", "q4_k_m"]
# ===========================================

print(f"🔄 Loading base model + your LoRA adapters from '{ADAPTER_PATH}'...")

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = ADAPTER_PATH,
    max_seq_length = MAX_SEQ_LENGTH,
    dtype = None,           # Auto BF16 on your 4080
    load_in_4bit = True,
)

print("✅ Base + LoRA loaded successfully (should use ~7-8 GB VRAM)")

# Optional quick test inference (uncomment if you want to verify before export)
# print("\nRunning quick test inference...")
# FastLanguageModel.for_inference(model)
# test_prompt = """<|im_start|>system
# You are an expert STM32 embedded C/C++ engineer.<|im_end|>
# <|im_start|>user
# Write a complete HAL blink example for PA5 on STM32G474RE that toggles at 1 Hz with proper init and error handling.<|im_end|>
# <|im_start|>assistant
# """
# inputs = tokenizer([test_prompt], return_tensors="pt").to("cuda")
# outputs = model.generate(**inputs, max_new_tokens=512, temperature=0.2)
# print(tokenizer.decode(outputs[0], skip_special_tokens=True))

print("\n🚀 Starting GGUF export(s)... (first time builds llama.cpp — 5-20 min total)")

for quant in QUANT_METHODS:
    save_dir = f"{OUTPUT_BASE_NAME}_{quant}"
    print(f"→ Exporting {quant} → ./{save_dir}/")
    
    model.save_pretrained_gguf(
        save_dir,
        tokenizer,
        quantization_method=quant,
    )
    print(f"   ✅ {quant} finished!\n")

print("🎉 All GGUF exports completed!")
print(f"Files are in folders like ./{OUTPUT_BASE_NAME}_q5_k_m/")