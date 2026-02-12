
import sys

class DebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only inspect the test upload path or admin upload path
        if 'upload' in request.path or 'admin' in request.path:
            # Debugging disabled for production
            pass

        response = self.get_response(request)
        return response


class MarketingMiddleware:
    """
    Middleware to capture marketing parameters from the URL and store them in the session.
    Supported parameters:
    - utm_source
    - utm_medium
    - utm_campaign
    - utm_term
    - utm_content
    - gclid (Google Ads)
    - fbclid (Facebook)
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of parameters to track
        tracking_params = [
            'utm_source', 'utm_medium', 'utm_campaign', 
            'utm_term', 'utm_content', 'gclid', 'fbclid'
        ]
        
        # Check if any tracking parameter is present in the GET request
        params_found = {}
        for param in tracking_params:
            value = request.GET.get(param)
            if value:
                params_found[param] = value
        
        # If parameters were found, store/update them in the session
        if params_found:
            # Get existing data or initialize empty dict
            current_attribution = request.session.get('marketing_attribution', {})
            
            # Update with new values (overwriting old ones if present)
            current_attribution.update(params_found)
            
            # Save back to session
            request.session['marketing_attribution'] = current_attribution
            request.session.modified = True
            
            # Debug log (can be removed/commented in prod)
            # print(f"Marketing tracking captured: {params_found}")

        response = self.get_response(request)
        return response
