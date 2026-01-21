import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import ChatRoom, Message, ChatAgent
from .ai_handler import ChatAIHandler

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            print("WebSocket connection attempt received")
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.room_group_name = f'chat_{self.room_name}'
            self.ai_handler = ChatAIHandler()

            print(f"Attempting to join room: {self.room_group_name}")
            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            print("Accepting connection")
            await self.accept()
            print("Connection accepted")

            print("Connection accepted")

            # Check if this is a new chat or reconnection
            if not await self.has_messages():
                # Send and save welcome message only for new chats
                welcome_message = 'Hello! I\'m the virtual assistant for Speedy Transfer. How can I help you today?'
                await self.save_message(welcome_message, 'ai')
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': welcome_message,
                        'sender_type': 'ai',
                        'timestamp': timezone.now().isoformat()
                    }
                )
                print("Welcome message sent and saved")
            else:
                print("Reconnected to existing chat")

        except Exception as e:
            print(f"Error in connect: {str(e)}")
            raise

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        ) 
    
    @database_sync_to_async
    def has_messages(self):
        chat_room = ChatRoom.objects.get(id=int(self.room_name))
        return chat_room.messages.exists()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender_type = text_data_json.get('sender_type', 'customer')

        # Save customer message to database
        await self.save_message(message, sender_type)

        # Send customer message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_type': sender_type,
                'timestamp': timezone.now().isoformat()
            }
        )

        # Handle explicit request for an agent
        if message == '/request_agent' or text_data_json.get('command') == 'request_agent':
            await self.trigger_agent_handoff(reason="Customer requested a live agent.")
            return

        # Generate and send AI response if no agent is assigned
        if sender_type == 'customer':
            chat_room = await self.get_chat_room()
            # Only use AI if no agent is assigned and chat is open
            if not chat_room.agent and chat_room.status != 'closed':
                # Get conversation history for context
                history = await self.get_chat_history()
                
                # Get AI response
                ai_response = await self.ai_handler.get_ai_response(message, history)
                
                if ai_response:
                    # Save AI response to database
                    await self.save_message(ai_response, 'ai')
                    # Send AI response to room group
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'message': ai_response,
                            'sender_type': 'ai',
                            'timestamp': timezone.now().isoformat()
                        }
                    )
                else:
                    # AI Failed (e.g. Quota exceeded) - Trigger Automatic Handoff
                    print("AI failed to generate response. Triggering handoff.")
                    await self.trigger_agent_handoff(reason="AI service unavailable (technical issue).")

    async def trigger_agent_handoff(self, reason="Assistance required"):
        """
        Notify the user that an agent is being requested and send email notification.
        """
        fallback_msg = "I'm connecting you to a live agent who can better assist you. Please wait a moment..."
        
        await self.save_message(fallback_msg, 'system')
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': fallback_msg,
                'sender_type': 'System',
                'timestamp': timezone.now().isoformat()
            }
        )
        
        # Notify Admin/Agents via Email
        await self.notify_admins_email(reason)

    @database_sync_to_async
    def notify_admins_email(self, reason):
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            chat_room = ChatRoom.objects.get(id=int(self.room_name))
            subject = f"New Chat Request: {chat_room.customer_name}"
            message = f"""
            Customer {chat_room.customer_name} ({chat_room.customer_email}) is requesting assistance.
            
            Reason: {reason}
            Chat ID: {chat_room.id}
            
            Please log in to the agent portal to reply.
            """
            
            print(f"Sending email notification to {settings.DEFAULT_FROM_EMAIL}...")
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL], # Send to admin/support email
                fail_silently=False,
            )
            print("Email notification sent.")
            
            # Update status to open/pending if not already
            chat_room.status = 'open'
            chat_room.save()
            
        except Exception as e:
            print(f"Error sending email notification: {e}")

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_type': event['sender_type'],
            'timestamp': event['timestamp']
        }))

    @database_sync_to_async
    def save_message(self, message, sender_type):
        chat_room = ChatRoom.objects.get(id=int(self.room_name))
        Message.objects.create(
            chat_room=chat_room,
            content=message,
            sender_type=sender_type
        )
    
    @database_sync_to_async
    def get_chat_room(self):
        return ChatRoom.objects.get(id=int(self.room_name))

    @database_sync_to_async
    def get_chat_history(self):
        """Get the last few messages from the chat history for context"""
        chat_room = ChatRoom.objects.get(id=int(self.room_name))
        messages = Message.objects.filter(chat_room=chat_room).order_by('-created_at')[:5]
        
        # Convert to format suitable for OpenAI API
        history = []
        for msg in reversed(messages):
            role = "assistant" if msg.sender_type == "ai" else "user"
            history.append({
                "role": role,
                "content": msg.content
            })
            
        return history