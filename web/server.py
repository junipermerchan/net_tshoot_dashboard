#!/usr/bin/env python3
import http.server
import socketserver
import sys
import os
from pathlib import Path

PORT = 8085
WEB_DIR = Path(__file__).resolve().parent

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Always serve relative to the web/ directory
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

def run_server():
    # Change directory to web/
    os.chdir(str(WEB_DIR))
    
    # Allow port reuse
    socketserver.TCPServer.allow_reuse_address = True
    
    try:
        with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
            print("=============================================================")
            print(f"🌐  Servidor web del Dashboard iniciado en: http://localhost:{PORT}")
            print("=============================================================")
            print("Presione Ctrl+C para detener el servidor.")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nDeteniendo el servidor web. ¡Hasta luego!")
        sys.exit(0)
    except Exception as e:
        print(f"Error al iniciar el servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_server()
