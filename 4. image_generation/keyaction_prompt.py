from openai import OpenAI
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'notion-screenshot'))

from extract_key_interest import extract_key_interest

def extract_keyaction(API_KEY):
    # Set OpenAI API key from Streamlit secrets
    client = OpenAI(api_key=API_KEY)

    keyword = extract_key_interest()
    # gpt 호출하기
    response = client.chat.completions.create(
    model="gpt-4-turbo", ## 모델 종류에 따라서 모델명을 지정해주면 된다. gpt4-turbo는 -> 'gpt-4-turbo-preview'
    messages=[
        {
            "role": "system",
            "content": '''
            instruction: Create prompt to use in image generation prompt.
            Conditions

            1. Actions that are universally likely to be done by someone interested in the given keyword
            2. Presented in verb form
            3. Described in a simple way without using difficult jargon
            4. Create a prompt that will generate images when used as a prompt to create images
            5. Doesn't have to be a realistic behaviour.
            6. Just one sentence, but not too long sentence.

            wait user give a keyword.
            '''
        },
        {
            "role": "user",
            "content": f"keyword: {keyword}"
        }
    ],
    temperature=1,
    max_tokens=256,
    )
    return response.choices[0].message.content