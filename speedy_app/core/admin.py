from django.contrib import admin

from .models import Zone, Hotel, CarType, Car, Rate, Reservation, Payment, Booking, Contact, WhatsAppConversation, WhatsAppMessage, Certificate

admin.site.register(Zone)
admin.site.register(Hotel)
admin.site.register(CarType)
admin.site.register(Car)
admin.site.register(Rate)
admin.site.register(Reservation)
admin.site.register(Payment)
admin.site.register(Booking)
admin.site.register(Contact)
admin.site.register(WhatsAppConversation)
admin.site.register(WhatsAppMessage)


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('title', 'certificate_type', 'display_order', 'is_active', 'created_at')
    list_filter = ('certificate_type', 'is_active', 'created_at')
    search_fields = ('title', 'description')
    list_editable = ('display_order', 'is_active')
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'certificate_type', 'is_active')
        }),
        ('Display Settings', {
            'fields': ('display_order', 'icon_color')
        }),
        ('Icon or Image', {
            'fields': ('image', 'icon_svg'),
            'description': 'Upload an image (JPG/PNG) OR enter an SVG path. If an image is provided, it will be used instead of the SVG.'
        }),
    )

from django.urls import path
from django.utils.html import format_html
from django.template.response import TemplateResponse
from django.contrib.admin import AdminSite
from django.contrib.admin.views.decorators import staff_member_required
from . import views_reports


def admin_reports_portal(request):
	# use existing reports portal template but render within admin layout
	context = {
		**globals(),
		'title': 'Reporting Portal',
	}
	return TemplateResponse(request, 'admin/reports_portal_admin.html', context)


@staff_member_required
def admin_sold_orders(request):
	resp = views_reports.sold_orders_report(request)
	# if it's an HttpResponse with content-disposition for files, return it directly
	content_disposition = resp.get('Content-Disposition', '') if hasattr(resp, 'get') else ''
	if 'attachment' in content_disposition:
		return resp
	# otherwise render within admin layout
	context = resp.context_data if hasattr(resp, 'context_data') else {}
	return TemplateResponse(request, 'admin/reports_sold_orders_admin.html', context)


@staff_member_required
def admin_sales_history(request):
	resp = views_reports.sales_history_report(request)
	content_disposition = resp.get('Content-Disposition', '') if hasattr(resp, 'get') else ''
	if 'attachment' in content_disposition:
		return resp
	context = resp.context_data if hasattr(resp, 'context_data') else {}
	return TemplateResponse(request, 'admin/reports_sales_history_admin.html', context)


def get_admin_urls(original_get_urls):
	def get_urls():
		my_urls = [
			path('reports/', admin_reports_portal, name='admin_reports_portal'),
			path('reports/sold-orders/', admin_sold_orders, name='admin_reports_sold_orders'),
			path('reports/sales-history/', admin_sales_history, name='admin_reports_sales_history'),
		]
		# Call the original get_urls() method lazily to ensure all models are registered
		urls = original_get_urls()
		return my_urls + urls
	return get_urls


# Note: The URL wrapping is now done in apps.py ready() method to ensure
# all admin modules are imported first. This prevents the URL pattern from
# being generated before all models are registered.



