import json
import time
import requests
import os
from bs4 import BeautifulSoup


INPUT_FILE = "data/safe_urls.json"
OUTPUT_DIR = "data/scraped_text"
HEADERS = {'User-Agent': 'MyStudentProject/1.0 (Educational RAG Experiment)'}


LIMIT = 400

def scrape_all_urls():
    
    if not os.path.exists(INPUT_FILE):
        print(" error: safe_urls.json not found. Run Step 1 first ")
        return

    with open(INPUT_FILE, "r") as f:
        urls = json.load(f)


    target_urls = urls[:LIMIT] if LIMIT else urls
    
    print(f"Starting scrape for {len(target_urls)} pages ")
    print(f" Saving to: {OUTPUT_DIR}")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for i, url in enumerate(target_urls): 
        
    
        filename = os.path.join(OUTPUT_DIR, f"doc_{i}.txt")
        
    
        if os.path.exists(filename):
            print(f"[{i+1}] Skipping (Already exists): {url}")
            continue
        

        try:
            print(f"[{i+1}] Scraping: {url}")
            
            
            response = requests.get(url, headers=HEADERS)
            
            if response.status_code != 200:
                print(f" Failed: Status {response.status_code}")
                continue

            
            soup = BeautifulSoup(response.content, "html.parser")
            
            
            for junk in soup(["script", "style", "nav", "footer", "header", "form", "noscript", "aside"]):
                junk.decompose()

        
            content_div = soup.find('div', class_='main-content') or soup.find('main') or soup.body
            
            if content_div:
                clean_text = content_div.get_text(separator=' ', strip=True)
            else:
                clean_text = ""

            
            file_content = f"Source: {url}\n\n{clean_text}"
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(file_content)

            
            time.sleep(2)

        except Exception as e:
            print(f"  Critical Error on {url}: {e}")

    print("\n Scraping session complete ")

if __name__ == "__main__":
    scrape_all_urls()