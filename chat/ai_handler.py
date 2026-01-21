import os
from openai import AsyncOpenAI
from django.conf import settings

class ChatAIHandler:
    def __init__(self):
        # Initialize the async OpenAI client
        api_key = os.getenv('OPENAI_API_KEY', settings.OPENAI_API_KEY if hasattr(settings, 'OPENAI_API_KEY') else None)
        self.client = AsyncOpenAI(api_key=api_key) if api_key else None
        
    async def get_ai_response(self, message, context=None):
        try:
            if not self.client:
                return "Sorry, the AI service is not configured correctly. An agent will assist you shortly."

            # Create system message for context
            system_message = """You are a friendly and professional assistant for Speedy Transfer, 
            a private transportation service in Puerto Vallarta. 
            
            IMPORTANT: Always respond in English only, regardless of the language the customer uses. 
            If the customer writes in Spanish or any other language, respond in English and acknowledge 
            their message. Provide brief, accurate, and helpful responses. Be courteous and professional at all times."""

            # Prepare conversation history
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": message}
            ]

            if context:
                messages.extend(context)

            # Get response from OpenAI
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=150,
                temperature=0.7,
                presence_penalty=0
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error in AI response generation: {str(e)}")
            # Return None to signal failure so the consumer can trigger handoff
            return None