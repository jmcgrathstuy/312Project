# Ref CSE 312 Lecture from 11/17

import socketserver
import sys
import server_build

class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        # Get data from server
        data = self.request.recv(1024).strip()

        # Prints out the data the server gets
        print("Sent Data:")
        print(data.decode())
        print("\n\n")
        sys.stdout.flush()
        sys.stderr.flush()
    
        request_type = data.decode().split("\r\n")[0].split(" ")[0]
        request_path = data.decode().split("\r\n")[0].split(" ")[1]

        if (request_type == "GET" and request_path == "/"):
            self.request.sendall(server_build.buildOKResponse("text/html; charset = utf-8", server_build.readFile("index.html")))
        elif (request_type == "GET" and request_path == "/style.css"):
            self.request.sendall(server_build.buildOKResponse("text/css", server_build.readFile("style.css")))
        elif (request_type == "GET" and request_path == "/functions.js"):
            self.request.sendall(server_build.buildOKResponse("text/javascript", server_build.readFile("functions.js")))
        else:
            self.request.sendall(server_build.buildNoResponse("text/plain; charset = utf-8", "Beep Boop, nothing here!"))

# TCP Connection
if __name__ == "__main__":
    server = socketserver.TCPServer(("0.0.0.0", 8000), MyTCPHandler)
    server.serve_forever()