import requests
import json

# Check the model repository info
repo = 'Harafu/roberta-risk-next'
url = f'https://huggingface.co/api/models/{repo}'

try:
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print('=== MODEL REPOSITORY INFO ===')
        print(f'Model ID: {data.get("modelId", "Unknown")}')
        print(f'Author: {data.get("author", "Unknown")}')
        print(f'Downloads: {data.get("downloads", "Unknown")}')
        print(f'Last Modified: {data.get("lastModified", "Unknown")}')
        print(f'Tags: {data.get("tags", [])}')

        # Check for tokenizer files
        siblings = data.get('siblings', [])
        tokenizer_files = [f for f in siblings if 'tokenizer' in f.get('rfilename', '')]
        print(f'\nTokenizer files found: {len(tokenizer_files)}')
        for f in tokenizer_files:
            print(f'  - {f.get("rfilename")} ({f.get("size", "unknown")} bytes)')

        print('\n=== CONFIG INFO ===')
        config = data.get('config', {})
        print(f'Model Type: {config.get("model_type", "unknown")}')
        print(f'Vocab Size: {config.get("vocab_size", "unknown")}')

    else:
        print(f'Failed to fetch repo info: {response.status_code}')

except Exception as e:
    print(f'Error checking repository: {e}')