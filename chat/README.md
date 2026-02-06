# AI Chat Module

## Status: DISABLED

This module contains the code for the AI-powered chat system. 
It has been disabled in favor of a direct WhatsApp integration to provide more immediate human support.

### How to Re-enable
1. Uncomment `path('chat/', include('chat.urls', namespace='chat')),` in `config/urls.py`.
2. Uncomment the chat widget include in `templates/base.html` or `templates/speedy_app/base.html`.
3. Verify `templates/chat/include/chat_button.html` has the correct `iframe` src uncommented.
4. Ensure OpenAI API keys are configured in `.env`.

### Contents
- `ai_handler.py`: Logic for interacting with OpenAI.
- `consumers.py`: WebSocket consumers for real-time chat (if using Channels).
- `views.py`: Chat views and API endpoints.
