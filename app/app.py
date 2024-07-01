import asyncio
import logging

from flask import Flask, jsonify, request
from pydantic import ValidationError

from app.model import ChatModel
from src.llms.langchain import TaxBot
from src.llms.openai import TextGenerator

app = Flask("project-onnecta")

# Set logging level to INFO
logging.basicConfig(level=logging.INFO)

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
def conversational_chat():
    logging.info('Received POST request')
    try:
        # Parse and validate the request JSON data against the Pydantic model
        data = ChatModel(**request.get_json())
    except ValidationError as e:
        # Return validation errors as a JSON response
        return jsonify({"status": "Failed", "errors": e.errors()}), 400

    taxbot = TaxBot()

    # Create a new event loop if one does not exist
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    response, chat_history = loop.run_until_complete(taxbot.generate(**data.model_dump()))

    return jsonify({
        "status": "Successful",
        "output": response,
        "chat_history": chat_history
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
