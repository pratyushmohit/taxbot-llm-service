import logging

from flask import Flask, jsonify, request
from pydantic import ValidationError

from app.model import ChatModel, ChatResponse
from src.llms.agent import ChatAgent
from src.llms.assistant import ChatAssistant

# Configure root logger
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(asctime)s - %(message)s')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask("taxbot-llm-service")

@app.route("/", methods=["GET"])
def index():
    return "Hi, I'm an AI-powered taxbot. How can I help you?!"


@app.route("/status", methods=["GET"])
def status():
    return jsonify({"status": "Running"})


@app.route("/chat", methods=["POST"])
async def conversational_chat_agent() -> ChatResponse:
    logging.info('Received POST request')
    try:
        # Parse and validate the request JSON data against the Pydantic model
        data = ChatModel(**request.get_json())
    except ValidationError as e:
        # Return validation errors as a JSON response
        return jsonify({"status": "Failed", "errors": e.errors()}), 400

    taxbot = ChatAgent()
    # taxbot = ChatAssistant()

    response, chat_history = await taxbot.generate(**data.model_dump())

    return jsonify({
        "status": "Successful",
        "output": response,
        "chat_history": chat_history
    })
