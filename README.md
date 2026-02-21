

## Running the pipeline
```
cd ~/stm32-coder-ft/data_pipeline

# Stage 1: Download everything (first run ~10-20 min)
python stage_1_download.py --force

# Stage 2: Extract (PDFs → markdown, repos → structured code)
python stage_2_extract.py

# Stage 3: Chunk (creates ~100-200 manageable pieces)
python stage_3_chunk.py

# Stage 4: Generate pairs (this is the fun one — uses your GPU, ~30-90 min depending on chunks)
# First time: run with limit to test
python stage_4_generate.py --max-chunks 20

# Then full run (aims for 800-1200 pairs)
python stage_4_generate.py

# Stage 5: Dedup, shuffle, split
python stage_5_finalize.py
```

```
python stage_1_download.py --force   # downloads (~10-15 min)
python stage_2_extract.py            # extract
python stage_3_chunk.py              # chunk
python stage_4_generate.py --max-chunks 15   # test generation on just 15 chunks (5-10 min)
```

