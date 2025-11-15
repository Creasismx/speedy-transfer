from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import ChatAgent, ChatRoom, Message


@admin.register(ChatAgent)
class ChatAgentAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_available', 'created_at', 'updated_at')
    list_filter = ('is_available', 'created_at')
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('created_at', 'updated_at')


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('created_at', 'sender_type', 'formatted_content')
    fields = ('created_at', 'sender_type', 'formatted_content')
    can_delete = False
    can_add = False
    show_change_link = True
    
    def formatted_content(self, obj):
        if obj:
            # Truncate long messages for inline view
            content = obj.content
            if len(content) > 150:
                content = content[:150] + '...'
            
            # Color code by sender type
            colors = {
                'customer': '#3b82f6',  # Blue
                'agent': '#10b981',      # Green
                'ai': '#8b5cf6'          # Purple
            }
            color = colors.get(obj.sender_type, '#6b7280')
            
            return format_html(
                '<div style="color: {}; font-weight: {}; padding: 5px;">{}</div>',
                color,
                'bold' if obj.sender_type == 'ai' else 'normal',
                content
            )
        return '-'
    formatted_content.short_description = 'Content'


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'customer_email', 'status', 'agent', 'message_count', 'created_at', 'last_message')
    list_filter = ('status', 'created_at', 'agent')
    search_fields = ('customer_name', 'customer_email')
    readonly_fields = ('created_at', 'updated_at', 'message_count_display')
    inlines = [MessageInline]
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer_name', 'customer_email')
        }),
        ('Chat Management', {
            'fields': ('status', 'agent')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'message_count_display'),
            'classes': ('collapse',)
        }),
    )
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'
    
    def last_message(self, obj):
        last_msg = obj.messages.order_by('-created_at').first()
        if last_msg:
            return format_html(
                '<span style="color: #6b7280;">{}</span><br><small>{}</small>',
                last_msg.content[:50] + ('...' if len(last_msg.content) > 50 else ''),
                last_msg.created_at.strftime('%Y-%m-%d %H:%M')
            )
        return '-'
    last_message.short_description = 'Last Message'
    
    def message_count_display(self, obj):
        count = obj.messages.count()
        return format_html(
            '<strong>{}</strong> message{}',
            count,
            's' if count != 1 else ''
        )
    message_count_display.short_description = 'Total Messages'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat_room_link', 'sender_type', 'content_preview', 'created_at')
    list_filter = ('sender_type', 'created_at', 'chat_room__status')
    search_fields = ('content', 'chat_room__customer_name', 'chat_room__customer_email')
    readonly_fields = ('created_at', 'formatted_content')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Message Information', {
            'fields': ('chat_room', 'sender_type', 'formatted_content', 'content')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def chat_room_link(self, obj):
        if obj.chat_room:
            url = reverse('admin:chat_chatroom_change', args=[obj.chat_room.id])
            return format_html(
                '<a href="{}">Chat #{}</a> - {}',
                url,
                obj.chat_room.id,
                obj.chat_room.customer_name
            )
        return '-'
    chat_room_link.short_description = 'Chat Room'
    chat_room_link.admin_order_field = 'chat_room__id'
    
    def content_preview(self, obj):
        content = obj.content
        if len(content) > 80:
            content = content[:80] + '...'
        
        # Color code by sender type
        colors = {
            'customer': '#3b82f6',  # Blue
            'agent': '#10b981',      # Green
            'ai': '#8b5cf6'          # Purple
        }
        color = colors.get(obj.sender_type, '#6b7280')
        
        return format_html(
            '<span style="color: {}; font-weight: {};">{}</span>',
            color,
            'bold' if obj.sender_type == 'ai' else 'normal',
            content
        )
    content_preview.short_description = 'Content'
    
    def formatted_content(self, obj):
        # Color code by sender type
        colors = {
            'customer': '#3b82f6',  # Blue
            'agent': '#10b981',      # Green
            'ai': '#8b5cf6'          # Purple
        }
        color = colors.get(obj.sender_type, '#6b7280')
        
        # Format with line breaks
        formatted = obj.content.replace('\n', '<br>')
        
        return format_html(
            '<div style="color: {}; font-weight: {}; padding: 10px; background-color: {}20; border-left: 3px solid {}; border-radius: 4px;">{}</div>',
            color,
            'bold' if obj.sender_type == 'ai' else 'normal',
            color,
            color,
            formatted
        )
    formatted_content.short_description = 'Formatted Content'

