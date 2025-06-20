import os
from http.server import BaseHTTPRequestHandler, HTTPServer

hostName = "localhost"  # Адрес для доступа по сети
serverPort = 8080  # Порт для доступа по сети


class MyServer(BaseHTTPRequestHandler):
    """Класс обработки входящих запросов от клиентов"""

    def do_GET(self):
        """Метод для обработки входящих GET-запросов"""
        content_types = {
            ".html": "text/html",
            ".css": "text/css",
            ".js": "application/javascript",
            ".png": "image/png",
            ".jpg": "image/jpeg",
        }

        try:
            if self.path == "/":
                self.path = "/html/contacts_page.html"

            file_extension = os.path.splitext(self.path)[1]

            with open(self.path[1:], "rb") as page:
                self.send_response(200)
                self.send_header("Content-type", content_types.get(file_extension, "text/plain"))
                self.end_headers()
                self.wfile.write(page.read())  # Тело ответа
        except FileNotFoundError:
            self.send_error(404, "File Not Found")

    def do_POST(self):
        """Метод для обработки входящих POST-запросов"""
        content_length = int(self.headers["Content-Length"])
        body = self.rfile.read(content_length)
        print(body)
        self.send_response(200)
        self.end_headers()


if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    webServer.server_close()
    print("Server stopped.")
