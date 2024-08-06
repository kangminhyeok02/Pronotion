import json
import re

def extract_key_interest():
    # JSON 파일에서 GPT 결과 읽기
    gpt_vision_filepath = 'C:/STUDY/KAIROS/Project/DASH/notion-screenshot/gpt_vision_result.json'
    with open(gpt_vision_filepath, 'r') as file:
        gpt_result = json.load(file)
    result = gpt_result[0]

    key_interest_line = None
    for line in result:
        if 'Key Areas of Interest' in line:
            key_interest_line = line
            break

    if not key_interest_line:
        raise ValueError("Key Areas of Interest not found in the GPT result.")

    key_interest = key_interest_line.split(': ')[1].strip()
    return key_interest


# GPT 결과에서 키 이슈 추출
try:
    key_interest = extract_key_interest()
    print("Key Area of Interest:", key_interest)
except ValueError as e:
    print(e)
    key_interest = None
