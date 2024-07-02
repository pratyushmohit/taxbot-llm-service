import logging

from flask import Flask, jsonify, request
from pydantic import ValidationError

from app.model import ChatModel, ChatResponse
from src.llms.langchain import ConversationalBot
from src.llms.openai import TextGenerator

app = Flask("project-onnecta")

# Set logging level to INFO
logging.basicConfig(level=logging.INFO)
logging.getLogger('werkzeug').setLevel(logging.WARNING)

@app.route("/", methods=["GET"])
def index():
    return "Project Onnecta!"


@app.route("/status", methods=["GET"])
def status():
    return jsonify({"status": "Running"})


@app.route("/chat", methods=["POST"])
async def generate_text():
    logging.info('Received POST request')
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


@app.route("/conversational-chat", methods=["POST"])
async def conversational_chat() -> ChatResponse:
    logging.info('Received POST request')
    try:
        # Parse and validate the request JSON data against the Pydantic model
        data = ChatModel(**request.get_json())
    except ValidationError as e:
        # Return validation errors as a JSON response
        return jsonify({"status": "Failed", "errors": e.errors()}), 400

    taxbot = ConversationalBot()

    response, chat_history = await taxbot.generate(**data.model_dump())

    return jsonify({
        "status": "Successful",
        "output": response,
        "chat_history": chat_history
    })