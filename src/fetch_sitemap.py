import requests
import xml.etree.ElementTree as ET
import json
import os

URL = "https://www.udi.no/sitemap.xml"
headers = {'User-Agent': 'MyStudentProject/1.0'}
r = requests.get(url = URL, headers = headers)

if r.status_code == 200:
    print(f' {URL} was found')
    root = ET.fromstring(r.content)
    print(f"XML Parsed successfully. Root tag is: {root.tag}")
else:
    print(f' {URL} was NOT found')

print( type(root))
print(f"📦 Number of items found: {len(root)}")

if len(root) > 0:
    first_child = root[1]
    print(f" First Child Tag: {first_child.tag}")

    for grandchild in first_child:
        print(f"  grand: {grandchild.tag}: {grandchild.text}")


namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'} #as url is long we call it with ns 
output_file = "data/safe_urls.json"
safe_urls = []
for i, child in enumerate(root):
    loc_tag = child.find('ns:loc', namespaces)
    
    if loc_tag is not None:
        url = loc_tag.text
        if "/Util/" in url:
            continue 
            
        if url.endswith((".pdf", ".jpg", ".png", ".docx")):
            continue   
        safe_urls.append(url)
    # Ensure the data folder exists
    os.makedirs("data", exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(safe_urls, f, indent=2)
print(f" Success. Processed {len(root)} raw items.")
print(f"Saved {len(safe_urls)} safe URLs to '{output_file}'.")

if __name__ == "__main__":
    fetch_and_save_sitemap()
    


