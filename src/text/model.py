from openai import AsyncOpenAI
import os
import dotenv

dotenv_path = os.path.join(os.getcwd(), ".env")
dotenv.load_dotenv(dotenv_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


class TextGenerator:
    def __init__(self) -> None:
        pass

    async def generate(self, prompt, model="gpt-4"):
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        output = response.choices[0].message.content
        return output
