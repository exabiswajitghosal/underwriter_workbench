from extraction import extract_files
from open_ai_api import extract_data_from_file

# Extract if it contains zip or similar files type
text = "Name:AXB GHAJ"
res = extract_data_from_file(text)
print("Response :", res)
