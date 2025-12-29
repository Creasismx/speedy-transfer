
import logging

logger = logging.getLogger(__name__)

def apply_multipart_fix():
    """
    Monkey-patch Django's MultiPartParser to fix a compatibility issue with Python 3.13+.
    
    The issue:
    Django 3.2's MultiPartParser passes the boundary as bytes to `cgi.valid_boundary`, 
    but Python 3.13's `cgi` module (and its replacements) expects a string.
    This causes 'Invalid boundary in multipart' errors.
    
    This patch wraps the parsing logic or pre-validates the boundary.
    Actually, the easiest fix is to patch `django.http.multipartparser.MultiPartParser`'s initialization 
    or the way it parses headers if possible.
    
    However, the error happens in `__init__`.
    
    We will monkey patch `cgi.valid_boundary` if it exists, to accept bytes.
    This is safer than rewriting the complex MultiPartParser class.
    """
    import cgi
    import sys
    
    # Check if we are on Python 3.13+
    if sys.version_info >= (3, 13):
        original_valid_boundary = getattr(cgi, 'valid_boundary', None)
        
        if original_valid_boundary:
            def valid_boundary_wrapper(s, *args, **kwargs):
                if isinstance(s, bytes):
                    try:
                        s = s.decode('ascii')
                    except Exception:
                        pass # Let the original function handle it (or fail)
                return original_valid_boundary(s, *args, **kwargs)
            
            cgi.valid_boundary = valid_boundary_wrapper
            logger.info("Applied monkey-patch to cgi.valid_boundary for Python 3.13 compatibility.")
