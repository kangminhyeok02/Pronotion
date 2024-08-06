import json
import requests
import subprocess

# API_KEY = '***************************8'

# gpt_vision_result.json 파일에서 키워드 추출
with open('gpt_vision_result.json', 'r') as file:
    gptVisionResult = json.load(file)

key_interest = None
for line in gptVisionResult[0]:
    if 'Key Areas of Interest:' in line or 'Key Area of Interest:' in line:
        key_interest = line.split(': ')[1].strip()
        break

if not key_interest:
    print("Key Areas of Interest not found in the GPT result.")
    exit(1)

# GPT-4를 호출하여 키 액션 생성
headersForKeyAction = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

payloadForKeyAction = {
    "model": "gpt-4-turbo",
    "messages": [
        {
            "role": "system",
            "content": """
            instruction: Create prompt to use in image generation prompt.
            Conditions

            1. Actions that are universally likely to be done by someone interested in the given keyword
            2. Presented in gerund form.
            3. Described in a simple way without using difficult jargon.
            4. Create a prompt that will generate images when used as a prompt to create images
            5. Doesn't have to be a realistic behaviour.
            6. Just one sentence, but not too long sentence.
            
            example: Analyzing graphs using multiple monitors.

            wait user give a keyword.
            """
        },
        {
            "role": "user",
            "content": f"keyword: {key_interest}"
        }
    ],
    "temperature": 1,
    "max_tokens": 256,
}

responseForKeyAction = requests.post('https://api.openai.com/v1/chat/completions', headers=headersForKeyAction, json=payloadForKeyAction)

if responseForKeyAction.status_code != 200:
    print(f"API request failed with status code {responseForKeyAction.status_code}: {responseForKeyAction.text}")
    exit(1)

keyaction = responseForKeyAction.json()['choices'][0]['message']['content']
print(keyaction)

# Key action을 사용하여 stable_diffusion.py 실행
subprocess.run(["python3", "stable_diffusion.py", keyaction])
