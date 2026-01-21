from django.shortcuts import render, redirect
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.contrib.auth.models import User
from .models import ChatAgent, ChatRoom, Message
from .serializers import ChatAgentSerializer, ChatRoomSerializer, MessageSerializer
from django.db.models import Q

class ChatAgentViewSet(viewsets.ModelViewSet):
    queryset = ChatAgent.objects.all()
    serializer_class = ChatAgentSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get'])
    def my_chats(self, request):
        agent = ChatAgent.objects.get(user=request.user)
        chats = ChatRoom.objects.filter(agent=agent)
        serializer = ChatRoomSerializer(chats, many=True)
        return Response(serializer.data)

class ChatRoomViewSet(viewsets.ModelViewSet):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer

    def get_permissions(self):
        """Allow unauthenticated POST (for widget), require auth for other operations"""
        if self.action == 'create':
            return [AllowAny()]  # Allow unauthenticated creation
        return [IsAuthenticated()]

    def get_queryset(self):
        """Filter chatrooms by the logged-in agent"""
        queryset = ChatRoom.objects.all()
        
        # If user is authenticated, try to filter by their agent profile
        if self.request.user.is_authenticated:
            try:
                agent = ChatAgent.objects.get(user=self.request.user)
                # Filter to show chats assigned to this agent OR unassigned (open) chats
                queryset = queryset.filter(Q(agent=agent) | Q(status='open'))
            except ChatAgent.DoesNotExist:
                # If user is not an agent, return empty queryset
                queryset = ChatRoom.objects.none()
        
        # Filter by status if provided (allow partial filtering)
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset

    @action(detail=True, methods=['post'])
    def assign_agent(self, request, pk=None):
        chat_room = self.get_object()
        agent_id = request.data.get('agent_id')
        
        try:
            agent = ChatAgent.objects.get(id=agent_id, is_available=True)
            chat_room.agent = agent
            chat_room.status = 'assigned'
            chat_room.save()
            return Response({'status': 'agent assigned'})
        except ChatAgent.DoesNotExist:
            return Response(
                {'error': 'Agent not found or not available'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

@xframe_options_exempt
def chat_widget(request):
    return render(request, 'chat/widget.html')

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        chat_room_id = self.request.query_params.get('chat_room', None)
        if chat_room_id:
            return Message.objects.filter(chat_room_id=chat_room_id)
        return Message.objects.none()

def chat_login(request):
    """Login view for chat agents"""
    if request.user.is_authenticated:
        # Check if user is a chat agent
        try:
            ChatAgent.objects.get(user=request.user)
            return redirect('chat:agent_portal')
        except ChatAgent.DoesNotExist:
            messages.error(request, 'You are not authorized to access the agent portal.')
            logout(request)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if user is a chat agent
            try:
                agent = ChatAgent.objects.get(user=user)
                if agent.is_available:
                    login(request, user)
                    return redirect('chat:agent_portal')
                else:
                    messages.error(request, 'Your agent account is not available.')
            except ChatAgent.DoesNotExist:
                messages.error(request, 'You are not authorized to access the agent portal.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'chat/login.html')

@login_required(login_url='/chat/login/')
def chat_agent_portal(request):
    """Agent portal - shows only the logged-in agent's chatrooms"""
    try:
        agent = ChatAgent.objects.get(user=request.user)
    except ChatAgent.DoesNotExist:
        messages.error(request, 'You are not authorized to access the agent portal.')
        logout(request)
        return redirect('chat:login')
    
    return render(request, 'chat/agent_portal.html', {'agent': agent})

def chat_logout(request):
    """Logout view for chat agents"""
    logout(request)
    return redirect('chat:login')

def customer_chat(request):
    """Customer chat interface"""
    return render(request, 'chat/customer_chat.html')