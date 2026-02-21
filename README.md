

## Running the pipeline
```
cd ~/stm32-coder-ft/data_pipeline

# Stage 1: Download everything (first run ~10-20 min)
python pipeline.py --stage 1

# Stage 2: Extract (PDFs → markdown, repos → structured code)
python pipeline.py --stage 2

# Stage 3: Chunk (creates ~100-200 manageable pieces)
python pipeline.py --stage 3

# Stage 4: Generate pairs (this is the fun one — uses your GPU, ~30-90 min depending on chunks)
# First time: run with limit to test
python pipeline.py --stage 4 --max-chunks 20

# Then full run (aims for 800-1200 pairs)
python pipeline.py --stage 4

# Stage 5: Dedup, shuffle, split
python pipeline.py --stage 5
```

```
python pipeline.py --stage 1          # downloads (~10-15 min)
python pipeline.py --stage 2          # extract
python pipeline.py --stage 3          # chunk
python pipeline.py --stage 4 --max-chunks 15   # test generation on just 15 chunks (5-10 min)
```