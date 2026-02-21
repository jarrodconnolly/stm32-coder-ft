from unsloth import FastLanguageModel
from trl import SFTTrainer
from datasets import load_dataset
import torch

max_seq_length = 4096
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/Qwen2.5-Coder-7B-Instruct",
    max_seq_length = max_seq_length,
    dtype = None,
    load_in_4bit = True,
)

model = FastLanguageModel.get_peft_model(
    model,
    r = 32,                    # higher = better quality, still tiny
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                      "gate_proj", "up_proj", "down_proj"],
    lora_alpha = 64,
    lora_dropout = 0,
    bias = "none",
    use_gradient_checkpointing = "unsloth",
    random_state = 3407,
    use_rslora = False,
    loftq_config = None,
)

# Load your dataset (change path)
dataset = load_dataset("json", data_files="stm32_dataset.jsonl", split="train")

trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    dataset_text_field = "conversations",   # or "text" depending on format
    max_seq_length = max_seq_length,
    dataset_num_proc = 4,
    packing = False,   # set True if you want faster but less precise
    args = SFTTrainer.get_training_args(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 8,   # effective batch ~16
        warmup_steps = 10,
        max_steps = 300,                   # ~1 epoch on 800 examples; change to -1 for full
        learning_rate = 2e-4,
        fp16 = not torch.cuda.is_bf16_supported(),
        bf16 = torch.cuda.is_bf16_supported(),
        logging_steps = 1,
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 3407,
        output_dir = "outputs",
        report_to = "none",   # or "wandb"
    ),
)

trainer.train()

# Save
model.save_pretrained("stm32-coder-qlora")  # adapters only (~50–80 MB)
tokenizer.save_pretrained("stm32-coder-qlora")