from openai import AsyncOpenAI
import os
import json
import dotenv
from fuzzywuzzy import process
from textblob import TextBlob

dotenv_path = os.path.join(os.getcwd(), ".env")
dotenv.load_dotenv(dotenv_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

system_prompts = os.path.join(
    os.getcwd(), "src", "prompt_templates", "system_prompts.json")


client = AsyncOpenAI(api_key=OPENAI_API_KEY)


class TextGenerator:
    def __init__(self) -> None:
        self.conversation_history = []
        with open(os.path.join(os.getcwd(), "src", "prompt_templates", "system_prompts.json"), "r") as file:
            self.system_prompts = json.load(file)
        self.allowed_topics = [
            "tax", "taxes", "taxation", "income tax", "itr", "gst", "deductions", "credits", "filing", "returns",
            "tax return", "tax filing", "tax slab", "tax bracket", "tax rate", "tax exemption", "tax rebate",
            "tax relief", "taxable income", "tax audit", "tax assessment", "tax payment", "tax refund", "tax savings",
            "tax planning", "tax evasion", "tax avoidance", "capital gains tax", "corporate tax", "wealth tax",
            "property tax", "service tax", "sales tax", "value added tax", "vat", "customs duty", "excise duty",
            "gift tax", "estate tax", "fringe benefit tax", "professional tax", "advance tax", "self-assessment tax",
            "tcs", "tax collected at source", "tds", "tax deducted at source", "section 80c", "section 80d",
            "section 80g", "section 10", "section 24", "section 44ada", "section 115bac", "section 87a", "u/s 80c",
            "u/s 80d", "u/s 80g", "u/s 10", "u/s 24", "u/s 44ada", "u/s 115bac", "u/s 87a", "new tax regime",
            "old tax regime", "income tax return", "business tax", "personal tax", "tax consultancy", "tax advisor",
            "income tax act", "tax laws", "tax compliance", "tax regulations", "tax code", "tax notice",
            "tax department", "tax office", "tax authority", "central board of direct taxes", "cbdt", "income tax department",
            "income tax officer", "tax form", "form 16", "form 26as", "form 10e", "form 12b", "form 15g", "form 15h",
            "form 3cd", "form 3ce", "form itr-1", "form itr-2", "form itr-3", "form itr-4", "form itr-5", "form itr-6",
            "form itr-7", "form itr-v", "tax year", "assessment year", "previous year", "financial year", "fiscal year",
            "annual income", "gross income", "net income", "house property income", "salary income", "business income",
            "capital gains", "long-term capital gains", "short-term capital gains", "dividends", "interest income",
            "rental income", "agricultural income", "tax calculator", "income tax calculator", "tax benefits",
            "tax incentives", "tax holiday", "tax break", "section 80e", "section 80ee", "section 80g", "section 80gga",
            "section 80u", "section 10a", "section 10b", "section 24b", "section 44ae", "section 44ab", "section 44bb",
            "section 44bbb", "section 44d", "section 44da", "section 54", "section 54b", "section 54d", "section 54ec",
            "section 54ee", "section 54f", "section 54g", "section 54ga", "section 54gb", "section 54h", "section 56",
            "section 57", "section 58", "section 60", "section 61", "section 62", "section 63", "section 64",
            "section 65", "section 66", "section 68", "section 69", "section 69a", "section 69b", "section 69c",
            "section 69d", "section 70", "section 71", "section 72", "section 73", "section 74", "section 75",
            "section 80", "section 80ia", "section 80ib", "section 80ic", "section 80id", "section 80ie", "section 80j",
            "section 80jj", "section 80p", "section 80q", "section 80r", "section 80t", "section 80u", "section 89",
            "section 90", "section 91", "section 92", "section 92a", "section 92b", "section 92c", "section 92d",
            "section 92e", "section 92f", "section 92g", "section 92h", "section 92i", "section 92j", "section 92k",
            "section 92l", "section 92m", "section 92n", "section 92o", "section 92p", "section 92q", "section 92r",
            "section 92s", "section 92t", "section 92u", "section 92v", "section 92w", "section 92x", "section 92y",
            "section 92z", "section 94", "section 94a", "section 94b", "section 94c", "section 94d", "section 94e",
            "section 94f", "section 94g", "section 94h", "section 94i", "section 94j", "section 94k", "section 94l",
            "section 94m", "section 94n", "section 94o", "section 94p", "section 94q", "section 94r", "section 94s",
            "section 94t", "section 94u", "section 94v", "section 94w", "section 94x", "section 94y", "section 94z"
        ]

    def correct_spelling(self, text):
        blob = TextBlob(text)
        return str(blob.correct())

    def is_relevant(self, text):
        corrected_text = self.correct_spelling(text)
        _, score = process.extractOne(corrected_text, self.allowed_topics)
        return score > 80

    async def generate(self, prompt, model="gpt-4"):
        if not self.is_relevant(prompt):
            return "I can only answer questions related to Indian taxes. Please ask a tax-related question."

        # Append new user message to the conversation history
        self.conversation_history.append({"role": "user", "content": prompt})

        # Prepare the messages for the API call, including the system prompt and conversation history
        messages = [{"role": "system", "content": self.system_prompts["1"]}
                    ] + self.conversation_history

        # Get the response from the API
        response = await client.chat.completions.create(
            model=model,
            messages=messages
        )

        # Extract the output from the response
        output = response.choices[0].message.content

        # Append the AI response to the conversation history
        self.conversation_history.append(
            {"role": "assistant", "content": output})

        return output