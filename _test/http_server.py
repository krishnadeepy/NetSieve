import http.server
import socketserver

PORT = 8000
DIRECTORY = "html-files"

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/a.com':
            self.path = '/index.html'
        elif self.path == '/b.com':
            self.path = '/b.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def translate_path(self, path):
        return f"./{path}"

handler_object = MyHttpRequestHandler
my_server = socketserver.TCPServer(("0.0.0.0", PORT), handler_object)

print(f"Serving HTTP on port {PORT}")
my_server.serve_forever()