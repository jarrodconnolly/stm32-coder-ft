# data_pipeline/config.py
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG = {
    "board_name": "SparkFun Thing Plus - STM32 (STM32F405RGT6)",
    "mcu": "STM32F405RGT6",
    "target_pairs": 1000,          # we'll aim for this range
    
    # Sources
    "pdfs": {
        "stm32f4_datasheet": "https://www.st.com/resource/en/datasheet/stm32f405rg.pdf",
        "rm0090_ref_manual": "https://www.st.com/resource/en/reference_manual/dm00031020-stm32f405-415-stm32f407-417-stm32f427-437-and-stm32f429-439-advanced-arm-based-32-bit-mcus-stmicroelectronics.pdf",
        "um1725_hal_ll": "https://www.st.com/resource/en/user_manual/um1725-description-of-stm32f4-hal-and-lowlayer-drivers-stmicroelectronics.pdf",
        "sparkfun_schematic": "https://cdn.sparkfun.com/assets/7/7/2/1/9/SparkFun_STM32_Thing_Plus.pdf",
        "an4013_timers": "https://www.st.com/resource/en/application_note/an4013-introduction-to-timers-for-stm32-mcus-stmicroelectronics.pdf",
        "an4759_rtc_tamp": "https://www.st.com/resource/en/application_note/an4759-introduction-to-using-the-hardware-realtime-clock-rtc-and-the-tamper-management-unit-tamp-with-stm32-mcus-stmicroelectronics.pdf",
        "an4838_mpu": "https://www.st.com/resource/en/application_note/an4838-introduction-to-memory-protection-unit-management-on-stm32-mcus-stmicroelectronics.pdf",
        "an5156_security": "https://www.st.com/resource/en/application_note/an5156-introduction-to-security-for-stm32-mcus-stmicroelectronics.pdf",
        "an4776_timer_cookbook": "https://www.st.com/resource/en/application_note/an4776-generalpurpose-timer-cookbook-for-stm32-microcontrollers-stmicroelectronics.pdf",
        "an4488_getting_started": "https://www.st.com/resource/en/application_note/an4488-getting-started-with-stm32f4xxxx-mcu-hardware-development-stmicroelectronics.pdf",
        "pm0214_programming_manual": "https://www.st.com/resource/en/programming_manual/pm0214-stm32-cortexm4-mcus-and-mpus-programming-manual-stmicroelectronics.pdf",
        "an3126_dac_audio": "https://www.st.com/resource/en/application_note/an3126-audio-and-waveform-generation-using-the-dac-in-stm32-products-stmicroelectronics.pdf",
    },
    
    "repos": {
        "stm32cubef4": {
            "url": "https://github.com/STMicroelectronics/STM32CubeF4.git",
            "include_folders": ["Documentation", "Drivers", "Middlewares"]
        },
        "stm32_codes": {
            "url": "https://github.com/OkBeiRohan/STM32-Codes.git",
            "include_folders": ["STM32"]
        },
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
    "raw_pdfs_dir": os.path.join(BASE_DIR, "data/raw_downloads/pdfs"),
    "raw_repos_dir": os.path.join(BASE_DIR, "data/raw_downloads/repos"),
    "raw_web_dir": os.path.join(BASE_DIR, "data/raw_downloads/web"),
    "extracted_dir": os.path.join(BASE_DIR, "data/extracted"),
    "chunks_dir": os.path.join(BASE_DIR, "data/chunks"),
    "generated_dir": os.path.join(BASE_DIR, "data/generated_pairs"),
    "final_dir": os.path.join(BASE_DIR, "data/final"),
}