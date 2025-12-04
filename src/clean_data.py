import os
from langdetect import detect, LangDetectException

DATA_DIR = "data/scraped_text"

def clean_files():
    if not os.path.exists(DATA_DIR):
        print(f" Error: Directory '{DATA_DIR}' not found.")
        return

    print(f"Starting cleanup in '{DATA_DIR}'...")
    
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".txt")]
    deleted_empty = 0
    deleted_non_english = 0
    kept = 0

    for filename in files:
        filepath = os.path.join(DATA_DIR, filename)
        
        try:
            
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read().strip()

            
            if not content:
                print(f"Deleting EMPTY file: {filename}")
                f.close() 
                os.remove(filepath)
                deleted_empty += 1
                continue

            
            try:
                lang = detect(content)
                
                if lang != 'en':
                    print(f" Deleting {lang.upper()} file: {filename}")
                    os.remove(filepath)
                    deleted_non_english += 1
                else:
                    kept += 1
                    
            except LangDetectException:
            
                print(f" Could not detect language (Junk data): {filename}")
                os.remove(filepath)
                deleted_empty += 1

        except Exception as e:
            print(f" Error processing {filename}: {e}")

    print("-" * 30)
    print(" Cleanup Complete!")
    print(f"    Deleted Empty/Junk: {deleted_empty}")
    print(f"    Deleted Non-English: {deleted_non_english}")
    print(f"    Files Remaining:     {kept}")
    print("-" * 30)

if __name__ == "__main__":
    clean_files()