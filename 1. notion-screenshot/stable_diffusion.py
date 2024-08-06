import requests
import sys
import os

# Stability API Key
STABILITY_KEY = 'sk-8ab1RFJ6KVxTfGIx8nKtTTEjbzwhhyvBkKxg4laV5PJyy36I'

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

# Key action을 인자로 받음
if len(sys.argv) < 2:
    print("Usage: python3 stable_diffusion.py <key_action>")
    sys.exit(1)

# keyaction에서 따옴표 제거
keyaction = sys.argv[1].replace('"', '')
print(f"Generating image for key action: {keyaction}")
# !! 이거 Harry Potter 부분도 나중에 웹개발 하고 나면 변수화해야할 것 같아요 !!
prompt = f"Harry Potter is {keyaction}, 4k, 8k, unreal engine, octane render photorealistic by cosmicwonder, hdr, photography by cosmicwonder, high definition, symmetrical face, volumetric lighting, dusty haze, photo, octane render, 24mm, 4k, 24mm, DSLR, high quality, 60 fps, ultra realistic"
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

try:
    response = send_generation_request(host, params)
    output_image = response.content

    # Save and display result
    output_path = "static/output_image.jpeg"
    with open(output_path, "wb") as f:
        f.write(output_image)
    print(f"Saved image {output_path}")

except Exception as e:
    print(f"Image generation error: {e}")
    sys.exit(1)
