# data_pipeline/config.py
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG = {
    "board_name": "SparkFun Thing Plus - STM32 (STM32F405RGT6)",
    "mcu": "STM32F405RGT6",
    "target_pairs": 1000,          # we'll aim for this range
    
    # Sources
    "pdfs": {
        "stm32f4_datasheet": "https://www.st.com/resource/en/datasheet/dm00037051.pdf",
        "rm0090_ref_manual": "https://www.st.com/resource/en/reference_manual/dm00031020-stm32f405-415-stm32f407-417-stm32f427-437-and-stm32f429-439-advanced-arm-based-32-bit-mcus-stmicroelectronics.pdf",
        "um1725_hal_ll": "https://www.st.com/resource/en/user_manual/um1725-description-of-stm32f4-hal-and-lowlayer-drivers-stmicroelectronics.pdf",
        "sparkfun_schematic": "https://cdn.sparkfun.com/assets/7/7/2/1/9/SparkFun_STM32_Thing_Plus.pdf",
    },
    
    "repos": {
        "stm32cubef4": "https://github.com/STMicroelectronics/STM32CubeF4.git",
        "sparkfun_thing_plus": "https://github.com/sparkfun/STM32_Thing_Plus.git",  # if it exists; script will skip gracefully
    },
    
    "web": {
        "sparkfun_hookup": "https://learn.sparkfun.com/tutorials/stm32-thing-plus-hookup-guide/all",
    },
    
    # Local folders (add your code here anytime)
    "local_code_dir": "../local_sources/my_code",
    "local_extra_pdfs": "../local_sources/extra_pdfs",
    
    # Generation settings
    "pairs_per_chunk": 8,          # 8 high-quality convos per chunk → ~100-150 chunks = 800-1200 pairs
    "max_chunk_tokens": 3000,
    
    # Paths
    "raw_pdfs_dir": os.path.join(BASE_DIR, "data_pipeline/raw_downloads/pdfs"),
    "raw_repos_dir": os.path.join(BASE_DIR, "data_pipeline/raw_downloads/repos"),
    "raw_web_dir": os.path.join(BASE_DIR, "data_pipeline/raw_downloads/web"),
    "extracted_dir": os.path.join(BASE_DIR, "data_pipeline/extracted"),
    "chunks_dir": os.path.join(BASE_DIR, "data_pipeline/chunks"),
    "generated_dir": os.path.join(BASE_DIR, "data_pipeline/generated_pairs"),
    "final_dir": os.path.join(BASE_DIR, "data_pipeline/final"),
}