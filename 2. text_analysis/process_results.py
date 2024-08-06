import json
import matplotlib.pyplot as plt
import numpy as np
import re
from deep_translator import GoogleTranslator

def parse_gpt_result(result):
    total_score_line = None
    for line in result:
        if 'Total score' in line:
            total_score_line = line
            break

    if not total_score_line:
        raise ValueError("Total score not found in the GPT result.")

    scores = list(map(int, re.findall(r'\d+', total_score_line)))
    return scores

def extract_key_interest(result):
    for line in result:
        if 'Key Areas of Interest' in line:
            key_interest = line.split(': ')[1].strip()
            return key_interest

    raise ValueError("Key Areas of Interest not found in the GPT result.")

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

# GPT 결과에서 점수 추출
scores = parse_gpt_result(gpt_result[0])

# GPT 결과에서 키 이슈 추출
try:
    key_interest = extract_key_interest(gpt_result[0])
    print("Key Area of Interest:", key_interest)
except ValueError as e:
    print(e)
    key_interest = None

# 레이더 차트 그리기
labels = [
    'Page Structure and Layout',
    'Depth and Quality of Content',
    'Usage of Notion Features',
    'Visual Elements',
    'Readability and Accessibility'
]

num_vars = len(labels)
angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
scores += scores[:1]
angles += angles[:1]

fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

# y축 값을 0부터 5까지로 설정
ax.set_ylim(0, 5)

# y축 눈금을 고정하고 레이블 설정
ax.set_yticks(range(1, 6))
ax.set_yticklabels(range(1, 6))

ax.fill(angles, scores, color='blue', alpha=0.25)
ax.plot(angles, scores, color='blue', linewidth=2)

# 각 데이터 점에 레이블 추가
ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels)

# 차트 제목 추가
plt.title('Total Score Radar Chart', size=20, color='blue', y=1.1)

# 차트 저장
plt.savefig('radar_chart.png')
plt.close(fig)  # 화면에 표시하지 않고 닫기

# 평가 이유 번역 및 출력
translated_result = parse_and_translate(gpt_result[0])
for line in translated_result:
    print(line)

# 결과를 파일로 저장
with open('translated_results.txt', 'w') as f:
    for line in translated_result:
        f.write(line + '\n')

