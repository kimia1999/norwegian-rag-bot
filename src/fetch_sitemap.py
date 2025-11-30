import requests
import xml.etree.ElementTree as ET


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

for child in root:
    print(child.tag, child.attrib)




