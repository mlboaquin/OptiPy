import json
import os

def transform_code_snippets(file_path):
    # Read the existing JSON file with UTF-8 encoding
    with open(file_path, 'r', encoding='utf-8') as f:
        code_snippets = json.load(f)
    
    # Transform list into indexed dictionary
    indexed_snippets = {
        str(i + 1): snippet 
        for i, snippet in enumerate(code_snippets)
    }
    
    # Write back to the same file with pretty printing and UTF-8 encoding
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(indexed_snippets, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully transformed {len(indexed_snippets)} code snippets")

if __name__ == "__main__":
    file_path = "C:/Users/user/Desktop/Career/BCS35/Sem_1/Machine Learning/WPH/PROJECT/src/dataset/test/code_snippets.json"
    transform_code_snippets(file_path) 