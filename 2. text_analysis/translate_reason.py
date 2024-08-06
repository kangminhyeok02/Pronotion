from deep_translator import GoogleTranslator
import json
import re

def translate_reason(text):
    return GoogleTranslator(source='en', target='ko').translate(text)

def parse_and_translate(result):
    criteria = [
        '1. 페이지 구조와 레이아웃',
        '2. 내용의 깊이와 질',
        '3. 노션 기능 활용도',
        '4. 시각적 요소',
        '5. 가독성 및 접근성'
    ]

    translated_result = []

    for i, line in enumerate(result):
        match = re.match(r'\d+\. [^:]+ \((\d+\/5)\): (.+)', line)
        if match:
            score = match.group(1)
            reason = match.group(2)
            translated_reason = translate_reason(reason)
            translated_result.append(f"{criteria[i]} ({score}): {translated_reason}")

    return translated_result

# JSON 파일에서 GPT 결과 읽기
with open('gpt_vision_result.json', 'r') as file:
    gpt_result = json.load(file)

# 결과 번역 및 출력
translated_result = parse_and_translate(gpt_result[0])
for line in translated_result:
    print(line)
