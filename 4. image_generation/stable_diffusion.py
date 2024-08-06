import requests
import sys
import os
import time
from flask import Flask, jsonify, send_from_directory, request
from keyaction_prompt import extract_keyaction

API_KEY = "sk-None-RBABrRpY6QTyj87O2Pb4T3BlbkFJaud6a8XmRdr9WdMmTMIk"
STABILITY_KEY ='sk-8ab1RFJ6KVxTfGIx8nKtTTEjbzwhhyvBkKxg4laV5PJyy36I'

sys.path.append(os.path.dirname(__file__))

app = Flask(__name__)

image_output_path = 'C:/STUDY/KAIROS/Project/DASH/image/output_image.jpeg'
start_time = None
generation_time_estimate = 60  # 예측되는 전체 작업 시간 (초)

def send_generation_request(host, params):
    headers = {
        "Accept": "image/*",
        "Authorization": f"Bearer {STABILITY_KEY}"
    }

    # Encode parameters
    files = {}
    image = params.pop("image", None)
    mask = params.pop("mask", None)
    if image is not None and image != '':
        files["image"] = open(image, 'rb')
    if mask is not None and mask != '':
        files["mask"] = open(mask, 'rb')
    if len(files) == 0:
        files["none"] = ''

    # Send request
    print(f"Sending REST request to {host}...")
    response = requests.post(
        host,
        headers=headers,
        files=files,
        data=params
    )
    if not response.ok:
        raise Exception(f"HTTP {response.status_code}: {response.text}")

    return response

def generate_image():
    global start_time
    start_time = time.time()

    keyaction = extract_keyaction(API_KEY)
    print(keyaction)

    prompt = f"Harry Potter, {keyaction}, 4k, 8k, unreal engine, octane render photorealistic by cosmicwonder, hdr, photography by cosmicwonder, high definition, symmetrical face, volumetric lighting, dusty haze, photo, octane render, 24mm, 4k, 24mm, DSLR, high quality, 60 fps, ultra realistic"
    negative_prompt = "painting, extra fingers, mutated hands, poorly drawn hands, poorly drawn face, deformed, ugly, blurry, bad anatomy, bad proportions, extra limbs, cloned face, skinny, glitchy, double torso, extra arms, extra hands, mangled fingers, missing lips, ugly face, distorted face, extra legs, anime"
    aspect_ratio = "1:1"
    seed = 0
    output_format = "jpeg"

    host = f"https://api.stability.ai/v2beta/stable-image/generate/sd3"

    params = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "aspect_ratio": aspect_ratio,
        "seed": seed,
        "output_format": output_format,
        "model": "sd3-large",
        "mode": "text-to-image"
    }

    response = send_generation_request(host, params)

    # Decode response
    output_image = response.content
    finish_reason = response.headers.get("finish-reason")
    seed = response.headers.get("seed")

    # Check for NSFW classification
    if finish_reason == 'CONTENT_FILTERED':
        raise Warning("Generation failed NSFW classifier")

    # Save and display result
    with open(image_output_path, "wb") as f:
        f.write(output_image)
    print(f"Saved image {image_output_path}")

@app.route('/start_image_generation', methods=['POST'])
def start_image_generation():
    global start_time
    start_time = time.time()
    generate_image()
    return jsonify(status='started')

@app.route('/progress', methods=['GET'])
def progress():
    if start_time is None:
        return jsonify(progress=0)

    elapsed_time = time.time() - start_time
    progress = min(100, (elapsed_time / generation_time_estimate) * 100)

    if os.path.exists(image_output_path):
        progress = 100

    return jsonify(progress=progress)

@app.route('/image/<path:filename>')
def download_file(filename):
    return send_from_directory('C:/STUDY/KAIROS/Project/DASH/image', filename)

if __name__ == '__main__':
    app.run(debug=True)
