from openai import AsyncOpenAI
import os
import dotenv

dotenv_path = os.path.join(os.getcwd(), ".env")
dotenv.load_dotenv(dotenv_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = AsyncOpenAI(api_key="sk-proj-SrTmNyfMh1ICu1GVkbYPT3BlbkFJfjD1yPZJRaJrEqLirbme")


class ImageGenerator:
    def __init__(self) -> None:
        pass

    async def generate(self, prompt, model="dall-e-3", size="1024x1024", quality="standard"):
        response = await client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
            quality=quality,
            n=1,
        )
        image_url = response.data[0].url
        return image_url