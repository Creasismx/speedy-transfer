import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load .env explicitly
load_dotenv('c:/Users/adolf/Documents/speedy-transfer/.env')

async def test_key():
    api_key = os.getenv('OPENAI_API_KEY')
    print(f"API Key found: {api_key[:10]}...{api_key[-5:] if api_key else 'None'}")
    
    if not api_key:
        print("Error: No API key found in environment.")
        return

    client = AsyncOpenAI(api_key=api_key)
    
    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello, are you working?"}],
            max_tokens=10
        )
        print("Success! Response:")
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"Error calling OpenAI: {e}")

if __name__ == "__main__":
    asyncio.run(test_key())
