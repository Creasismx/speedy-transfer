
import os
import django
import re
import sys

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.develop")
django.setup()

from django.http.multipartparser import MultiPartParser, MultiPartParserError
import django.http.multipartparser
try:
    from django.http.multipartparser import _boundary_re
except ImportError:
    import re
    _boundary_re = re.compile(r'^[ -~]{0,200}[!-~]$') # Fallback approximation or just None

def debug_multipart():
    print("--- Debugging MultiPartParser ---")
    
    # The boundary from the logs that failed
    boundary_str = "----geckoformboundarye9da18854c9c006cf4e5713f63f6d97c"
    content_type = f"multipart/form-data; boundary={boundary_str}"
    
    META = {
        'CONTENT_TYPE': content_type,
        'CONTENT_LENGTH': '1234'
    }
    
    # Dummy stream
    import io
    input_data = io.BytesIO(b"fake data")
    
    print(f"Testing Content-Type: {content_type}")
    print(f"Django Version: {django.get_version()}")
    # Inspect the actual regex used by the loaded module
    import sys
    import re
    
    # Force import if not already
    try:
        from django.http.multipartparser import _boundary_re
    except ImportError:
        pass
        
    parser_module = sys.modules.get('django.http.multipartparser')
    if parser_module:
        print(f"Module dir: {dir(parser_module)}")
        if hasattr(parser_module, '_boundary_re'):
            real_re = parser_module._boundary_re
            print(f"Using REAL Django regex: {real_re.pattern}")
        else:
             print("Could not find _boundary_re in module.")
             # Look for other potential candidates
             for name in dir(parser_module):
                 if 're' in name.lower() or 'boundary' in name.lower():
                     val = getattr(parser_module, name)
                     print(f"Candidate: {name} = {val}")
             real_re = re.compile(r'^[ -~]{0,200}[!-~]$')
    else:
        print("Module not loaded?")
        real_re = re.compile(r'^[ -~]{0,200}[!-~]$')

    print(f"Boundary String (repr): {boundary_str!r}")

    # Test regex
    match = real_re.match(boundary_str)
    if match:
        print("✅ Regex MATCHES the boundary string.")
    else:
        print("❌ Regex FAILS to match the boundary string.")

    # Test with trailing space hypothesis
    boundary_with_space = boundary_str + " "
    print(f"Testing with trailing space: {boundary_with_space!r}")
    if real_re.match(boundary_with_space):
        print("✅ Regex MATCHES with trailing space.")
    else:
        print("❌ Regex FAILS with trailing space.")

        
    # Try parsing
    print("Attempting to instantiate MultiPartParser...")
    
    # MONKEYPATCH TEST
    # MONKEYPATCH TEST: Intercept __init__
    print("Monkeypatching MultiPartParser.__init__ to inspect boundary...")
    
    from django.http.multipartparser import MultiPartParser
    original_init = MultiPartParser.__init__
    
    def patched_init(self, META, input_data, upload_handlers, encoding=None):
        print(f"--- Patched Init Called ---")
        try:
            original_init(self, META, input_data, upload_handlers, encoding)
            print("Original Init Success")
        except Exception as e:
            print(f"Original Init Failed: {e}")
            # Try to inspect what it calculated (if available via self or local vars?)
            # We can't access local vars of original_init frames easily.
            # But we can replicate the extraction logic to see what it sees.
            ct = META.get('CONTENT_TYPE', '')
            print(f"META['CONTENT_TYPE']: {ct!r}")
            # Replicate extraction
            try:
                from django.http.multipartparser import parse_header
                ct_val, opts = parse_header(ct)
                boundary = opts.get('boundary')
                print(f"Extracted Boundary: {boundary!r}")
                if boundary:
                     # Check match here
                     import sys
                     pm = sys.modules.get('django.http.multipartparser')
                     # Try to access _boundary_re from the Frame of the traceback?
                     # No, let's just see the boundary value.
                     pass
            except ImportError:
                # parse_header might be in django.utils.http in newer versions?
                try:
                    from django.utils.http import parse_header_parameters
                    ct_val, opts = parse_header_parameters(ct)
                    boundary = opts.get('boundary')
                    print(f"Extracted Boundary (via utils): {boundary!r}")
                except Exception as ex:
                    print(f"Failed to reproduce extraction: {ex}")
            
            # Re-raise
            raise e

    MultiPartParser.__init__ = patched_init
    
    try:
        parser = MultiPartParser(META, input_data, [], 'utf-8')
        print("✅ MultiPartParser instantiated successfully WITH PATCH.")
    except MultiPartParserError as e:
        print(f"❌ MultiPartParser FAIL EVEN WITH PATCH: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    debug_multipart()
