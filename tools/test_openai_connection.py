
import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_openai():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment variables.")
        return

    print(f"Testing OpenAI API with key: {api_key[:10]}...{api_key[-5:]}")
    
    client = AsyncOpenAI(api_key=api_key)
    
    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Hello, are you working?"}
            ],
            max_tokens=10
        )
        print("Success! Response from OpenAI:")
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"Failed to connect to OpenAI API: {e}")

if __name__ == "__main__":
    asyncio.run(test_openai())
