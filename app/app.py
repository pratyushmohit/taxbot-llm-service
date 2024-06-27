from flask import Flask, request, jsonify, Response, stream_with_context
import json
from src.llms.openai import TextGenerator
from app.model import ChatModel, ChatHeaders, ChatResponse
from pydantic import BaseModel, ValidationError

app = Flask("project-onnecta")

@app.route("/", methods=["GET"])
def index():
    return "Project Onnecta!"


@app.route("/status", methods=["GET"])
def status():
    return jsonify({"status": "Running"})


@app.route("/chat", methods=["POST"])
async def generate_text():
    try:
        # Parse and validate the request JSON data against the Pydantic model
        data = ChatModel(**request.get_json())
    except ValidationError as e:
        # Return validation errors as a JSON response
        return jsonify({"status": "Failed", "errors": e.errors()}), 400
    
    textgen = TextGenerator()
    response = await textgen.generate(prompt=data.prompt)
    return jsonify({
        "status": "Successful",
        "output": response
    })




# @app.route("/stream", methods=["POST"])
# def stream_text():
#     data = request.json
#     prompt = data.get("prompt")
#     textgen = TextGenerator()

#     def generate():
#         for chunk in textgen.generate_stream(prompt=prompt):
#             if chunk.choices[0].delta.content is not None:
#                 yield f"{chunk.choices[0].delta.content}\n"

#     return Response(stream_with_context(generate()), content_type='text/plain')