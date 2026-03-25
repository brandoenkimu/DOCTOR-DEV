#!C:\Program Files\Python313\python.exe
"""
CGI Compatibility Module for Python 3.13
Place this file in your cgi-bin directory and import it first
"""

import sys
import os
# Handle missing cgi module
try:
    import cgi
    import cgitb
    print("DEBUG: Native cgi module found", file=sys.stderr)
except ImportError:
    try:
        import cgi
        print("DEBUG: Using legacy_cgi module", file=sys.stderr)
        
        # Create a simple cgitb replacement
        class SimpleCGITB:
            @staticmethod
            def enable():
                import traceback
                def excepthook(exctype, value, tb):
                    import html
                    trace = ''.join(traceback.format_exception(exctype, value, tb))
                    print("Content-Type: text/html\n")
                    print(f"<html><body><pre>{html.escape(trace)}</pre></body></html>")
                sys.excepthook = excepthook
        cgitb = SimpleCGITB()
        print("DEBUG: cgitb replacement created", file=sys.stderr)
    except ImportError:
        print("ERROR: Neither cgi nor legacy_cgi found!", file=sys.stderr)
        print("Please install legacy-cgi: pip install legacy-cgi", file=sys.stderr)
        sys.exit(1)

# Make them available globally
sys.modules['cgi'] = cgi
sys.modules['cgitb'] = cgitb

print("DEBUG: CGI compatibility module loaded successfully", file=sys.stderr)