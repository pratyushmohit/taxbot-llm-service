from flask import Flask, request, jsonify
from llms.openai.model import ImageGenerator

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