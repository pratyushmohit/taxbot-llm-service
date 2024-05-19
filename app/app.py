from flask import Flask, request, jsonify
import json
from src.image.model import ImageGenerator
from src.text.model import TextGenerator

app = Flask("project-onnecta")

@app.route("/", methods=["GET"])
def index():
    return "Project Onnecta!"


@app.route("/status", methods=["GET"])
def status():
    return jsonify({"status": "Running"})


@app.route("/generate-image", methods=["POST"])
async def generate_image():
    data = request.get_json()
    prompt = data.get("prompt")
    imagegen = ImageGenerator()
    response = await imagegen.generate(prompt=prompt)
    return jsonify({
        "status": "Successful",
        "image_url": response
    })

@app.route("/generate-text", methods=["POST"])
async def generate_text():
    data = request.get_json()
    prompt = data.get("prompt")
    textgen = TextGenerator()
    response = await textgen.generate(prompt=prompt)
    parsed_response = json.loads(response)
    return jsonify({
        "status": "Successful",
        "output": parsed_response
    })