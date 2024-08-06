import json
import matplotlib.pyplot as plt
import numpy as np
import re
from deep_translator import GoogleTranslator
import qrcode
import matplotlib.font_manager as fm
import subprocess

# 한글 폰트 설정
font_path = '/Users/apple/notion-screenshot/Nanum_Gothic/NanumGothic-Regular.ttf'  # Mac 경로
font_prop = fm.FontProperties(fname=font_path)

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
    key_interest_line = None
    for line in result:
        if 'Key Areas of Interest' in line or 'Key Area of Interest' in line:
            key_interest_line = line
            break

    if not key_interest_line:
        raise ValueError("Key Areas of Interest not found in the GPT result.")

    key_interest = key_interest_line.split(': ')[1].strip()
    return key_interest

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
        match = re.match(r'\d+\. [^:]+ \((\d+\/20)\): (.+)', line)
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
    print("관심 분야:", key_interest)
except ValueError as e:
    print(e)
    key_interest = None

# 레이더 차트 그리기 (한글)
labels = [
    '페이지 구조와 레이아웃',
    '내용의 깊이와 질',
    '노션 기능 활용도',
    '시각적 요소',
    '가독성 및 접근성'
]

num_vars = len(labels)
angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
scores += scores[:1]
angles += angles[:1]

fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

# y축 값을 0부터 20까지로 설정
ax.set_ylim(0, 20)

# y축 눈금을 고정하고 레이블 설정
ax.set_yticks([4, 8, 12, 16, 20])
ax.set_yticklabels([4, 8, 12, 16, 20], fontproperties=font_prop)

ax.fill(angles, scores, color='skyblue', alpha=0.4)
ax.plot(angles, scores, color='blue', linewidth=2, linestyle='solid')

# 각 데이터 점에 레이블 추가
ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels, fontproperties=font_prop)

# 차트 제목 추가
plt.title('당신의 점수는?', size=50, color='black', y=1.1, fontproperties=font_prop)

# 차트 저장
chart_path = 'static/radar_chart.png'
plt.savefig(chart_path, dpi=150, bbox_inches='tight')
plt.close(fig)  # 화면에 표시하지 않고 닫기

# 평가 이유 번역 및 출력
translated_result = parse_and_translate(gpt_result[0])
translated_result_text = "<br>".join(translated_result)
for line in translated_result:
    print(line)

# 결과를 HTML 파일로 저장 (한국어)
html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>평가 보고서</title>
</head>
<body>
    <h1>평가 보고서</h1>
    <img src="/static/radar_chart.png" alt="레이더 차트">
    <h2>관심 분야: {key_interest}</h2>
    <h2>분석 내용:</h2>
    <p>{translated_result_text}</p>
</body>
</html>
"""

with open('static/report.html', 'w') as f:
    f.write(html_content)

# QR 코드 생성
report_url = "http://localhost:3000/report"
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(report_url)
qr.make(fit=True)
img = qr.make_image(fill='black', back_color='white')
img.save("static/qrcode.png")

print(report_url)

# keyaction.py 실행
subprocess.run(["python3", "keyaction.py"])
