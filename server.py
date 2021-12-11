# Ref CSE 312 Lecture from 11/17

import socketserver
import sys
from typing import KeysView
import server_build
import database
import pymongo
import time
import re
import hashlib
import secrets


class MyTCPHandler(socketserver.StreamRequestHandler):
    upgraded = False
    xsrftokens = []
    def handle(self):

        encoded_data = self.request.recv(2048)
        savedata = encoded_data
        
        sys.stdout.flush()
        sys.stderr.flush()
        time.sleep(0)

        header = encoded_data.split('\r\n\r\n'.encode())[0].decode()
        
        if header.find('/profile_upload')==5:
            content_header_parsed = re.split('\r\n|:|; |=', header)
            content_length = int(content_header_parsed[content_header_parsed.index('Content-Length')+1])

            boundary = content_header_parsed[content_header_parsed.index('boundary')+1]

            content_start = encoded_data.find('\r\n\r\n'.encode())+4
            length_so_far = len(encoded_data) - content_start
            while length_so_far < content_length:
                next_part = self.request.recv(1024)
                length_so_far = length_so_far + len(next_part)
                encoded_data = encoded_data + next_part
            parsed_encoded_data = encoded_data.split(boundary.encode())
            keys = []
            values = []
            for i in range(2, len(parsed_encoded_data) - 1):
                key = parsed_encoded_data[i].split('\r\n\r\n'.encode())[0]
                value = parsed_encoded_data[i].split('\r\n\r\n'.encode())[1]
                keys.append(key.decode())
                values.append(value[:-2])
            for x in range(0,len(content_header_parsed)):
                content_header_parsed[x] = content_header_parsed[x].strip()
            token = content_header_parsed[content_header_parsed.index('usertoken') + 1]

            hashed_token = hashlib.sha256(token.encode())
            cur = database.tokens.find_one({'token':hashed_token.digest()})
            if(cur == None or (not(values[0][0:-2].decode() in self.xsrftokens))):
                self.request.sendall("HTTP/1.1 403 Forbidden\r\nContent-Length: 42\r\nContent-Type: text/plain; charset=utf-8\r\nX-Content-Type-Options: nosniff\r\n\r\nGet a better token. Don't do what you did.".encode())
            else:
                usr = cur['user']
                adela = database.filepaths.find_one({'user':usr})
                if(adela != None):
                    image_file_name = adela['filename']
                    image_file = open('uploads/' + image_file_name, 'wb')
                else:
                    image_file_name = 'image'+ str(database.filepaths.count_documents({})) + '.jpg'
                    image_file = open('uploads/' + image_file_name, 'wb')
                    database.filepaths.insert_one({'filename':image_file_name, 'user': usr})
                image_file.write(values[1]) 
                image_file.close()
                self.request.sendall(("HTTP/1.1 301 Moved Permanently\r\nContent-Length: 0\r\nLocation: /\r\nX-Content-Type-Options: nosniff\r\n\r\n").encode())
        else:
    
            request_type = savedata.decode().split("\r\n")[0].split(" ")[0]
            request_path = savedata.decode().split("\r\n")[0].split(" ")[1]

            # All the HTML + CSS + JS
            if (request_type == "GET" and request_path == "/"):
                self.request.sendall(server_build.buildHomepageResponse(savedata, "text/html; charset = utf-8", server_build.readFile("index.html"), self))
            elif (request_type == "GET" and request_path == "/style.css"):
                self.request.sendall(server_build.buildOKResponse("text/css", server_build.readFile("style.css")))
            elif (request_type == "GET" and request_path == "/functions.js"):
                self.request.sendall(server_build.buildOKResponse("text/javascript", server_build.readFile("functions.js")))

            elif (request_type == "GET" and request_path == "/index.html"):
                self.request.sendall(server_build.buildOKResponse("text/html; charset = utf-8", server_build.readFile("index.html")))

            elif (request_type == "GET" and request_path == "/users_index.html"):
                self.request.sendall(server_build.buildOKResponse("text/html; charset = utf-8", server_build.readFile("users_index.html")))
            elif (request_type == "GET" and request_path == "/users_style.css"):
                self.request.sendall(server_build.buildOKResponse("text/css", server_build.readFile("users_style.css")))
            elif (request_type == "GET" and request_path == "/settings_style.css"):
                self.request.sendall(server_build.buildOKResponse("text/css", server_build.readFile("settings_style.css")))
            
            elif (request_type == "GET" and request_path == "/chatroom_index.html"):
                self.request.sendall(server_build.buildOKResponse("text/html; charset = utf-8", server_build.readFile("chatroom_index.html")))
            elif (request_type == "GET" and request_path == "/chatroom_style.css"):
                self.request.sendall(server_build.buildOKResponse("text/css", server_build.readFile("chatroom_style.css")))

            elif (request_type == "GET" and request_path == "/images/test.png"):
                self.request.sendall(server_build.buildOKResponse("image/png", server_build.readFile("images/test.png")))
            elif (request_type == "GET" and request_path[:9] == "/uploads/"):
                self.request.sendall(server_build.buildOKResponse("image/jpg", server_build.readFile(request_path[1:])))
            
            elif (request_type == "GET" and request_path == "/websocket"):
                self.request.sendall(server_build.buildHandshakeResponse(self, savedata))
                server_build.maintainSocket(self)
            elif (request_type == "GET" and request_path == '/loginpage.html'):
                self.request.sendall(server_build.buildSettingsResponse("text/html; charset = utf-8", server_build.readFile("loginpage.html"), self))
            elif (request_type == "GET" and request_path == '/settings_index.html'):
                self.request.sendall(server_build.buildSettingsResponse("text/html; charset = utf-8", server_build.readFile("settings_index.html"), self))
            elif (request_type == "POST" and request_path == '/login'):
                self.request.sendall(server_build.buildLoginResponse(self, savedata))
            elif (request_type == "POST" and request_path == '/signup'):
                self.request.sendall(server_build.buildSignupResponse(savedata, self))
            elif (request_type == "POST" and request_path == "/chat"):
                self.request.sendall(server_build.buildChatResponse(savedata, self))
            else:
                self.request.sendall(server_build.buildNoResponse("text/plain; charset = utf-8", "Beep Boop, nothing here!"))

# TCP Connection
if __name__ == "__main__":
    #server = socketserver.TCPServer(("0.0.0.0", 8000), MyTCPHandler)
    
    server = socketserver.ThreadingTCPServer(("0.0.0.0", 8000), MyTCPHandler)


    server.serve_forever()
