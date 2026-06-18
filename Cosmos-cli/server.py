import os, http.server, socketserver

port = int(os.environ.get("PORT", 10000))
site_dir = os.environ.get("SITE_DIR", "design/main")
os.chdir(os.path.join(os.path.dirname(__file__), site_dir))

Handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(("", port), Handler) as httpd:
    print(f"Serving {site_dir} on port {port}")
    httpd.serve_forever()
