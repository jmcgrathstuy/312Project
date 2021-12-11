import hashlib
import base64
import server
import sys
import frame_parsing
import database
import bcrypt
import random
import string
import pymongo
import re
import time
import json
import secrets

clients = [] #each item is a (handler, user)
signedinusers = []
thedict=[]

def readFile(f):
    f1 = open(f, "rb")
    return f1.read()

def buildOKResponse(content_type, content):
    response = "HTTP/1.1 200 OK\r\n"
    response += "Content-Type: " + content_type + "\r\n"
    response += "X-Content-Type-Options: nosniff\r\n"
    response += "Content-Length: " + str(len(content)) + "\r\n\r\n"
    if (isinstance(content, str)):
        response += content
        response = response.encode()
    else:
        response = response.encode() + content
    return response

def buildSettingsResponse(content_type, content, handler):
    contentdec = content.decode()
    response = "HTTP/1.1 200 OK\r\n"
    response += "Content-Type: " + content_type + "\r\n"
    response += "X-Content-Type-Options: nosniff\r\n"
    token = secrets.token_urlsafe(24)
    handler.xsrftokens.append(token)
    contentdec = contentdec.replace('{{token}}', token)
    response += "Content-Length: " + str(len(contentdec)) + "\r\n\r\n"
    response += contentdec
    response = response.encode()
    return response

def buildHomepageResponse(data, content_type, content, handler):
    response = "HTTP/1.1 200 OK\r\n"
    response += "Content-Type: " + content_type + "\r\n"
    response += "X-Content-Type-Options: nosniff\r\n"
    data = data.decode()
    content = content.decode()
    auth = False
    if(data.find('usertoken')!= -1):
        user_token = data.split('\r\n')
        index = [i for i, s in enumerate(user_token) if "Cookie:" in s]
        user_token = re.split(': |; |=', user_token[index[0]])
        index = user_token.index("usertoken")+1
        user_token = user_token[index]
        hashed_token = hashlib.sha256(user_token.encode())
        if(not database.tokens.find({"token":hashed_token.digest()})):
            content = content.replace('{{greeting}}', 'Welcome, please sign in for full functionality.')
        else:
            cursor = database.tokens.find_one({"token":hashed_token.digest()})
            usr = cursor['user']
            content = content.replace('{{greeting}}', 'Welcome back, ' + usr + '!')
            content = content.replace('<!--settings-->', "<li id = 'nav'><a href = 'settings_index.html'>SETTINGS</a></li>")
            auth = True
    else:
        content = content.replace('{{greeting}}', 'Welcome, you are not signed in.')
    
    for msg in database.messages.find({}):
        content = content.replace('{{No messages yet...}}', msg['message'] +'<br>Upvotes: <input type="button" value="'+ str(msg['upvotes'])+ '" id="' + str(msg['id']) + '"onClick="upvotePrompt(this.id)" /><br><br>' + '{{No messages yet...}}')
    for client in clients:
        if(client[1]!='none'):
            if auth:
                if(database.filepaths.find_one({'user':client[1]})):
                    cur = database.filepaths.find_one({'user':client[1]})
                    filename = cur['filename']
                    imgtag = '<img src = "uploads/'+ filename + '">'
                else:
                    imgtag = '<img src = "images/test.png">'
                content = content.replace('{{users}}', client[1]+'<br>'+imgtag+'<br><input type="button" value="Send DM" onClick="dmPrompt(\'' + client[1] + '\')" /><br><br>{{users}}')
            else:
                content = content.replace('{{users}}', client[1]+ '<br>{{users}}')
    content = content.replace('{{No messages yet...}}', '')
    content = content.replace('{{users}}','')
    xsrfy = secrets.token_urlsafe(24)
    handler.xsrftokens.append(xsrfy)
    content = content.replace('{{token}}', xsrfy)
    response  += "Content-Length: " + str(len(content)) + "\r\n\r\n" + content
    return response.encode()

def buildHandshakeResponse(handler, data):
    response = "HTTP/1.1 101 Switching Protocols\r\n"
    response += "Connection: Upgrade\r\nUpgrade: websocket\r\nSec-WebSocket-Accept: "
    data = data.decode()
    usr = 'none'
    if(data.find('usertoken')!= -1): #if cookie exists
        user_token = data.split('\r\n')
        index = [i for i, s in enumerate(user_token) if "Cookie:" in s]
        user_token = re.split(': |; |=', user_token[index[0]])
        index = user_token.index("usertoken")+1
        user_token = user_token[index]
        hashed_token = hashlib.sha256(user_token.encode())
        if(not database.tokens.find({"token":hashed_token.digest()})):
            pass
        else:
            cursor = database.tokens.find_one({"token":hashed_token.digest()})
            usr = cursor['user']
    keystart = data.find('Sec-WebSocket-Key: ') + 19
    data = data[keystart:data.find('==') + 2] + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
    databytes = data.encode()
    data64 = hashlib.sha1()
    data64.update(databytes)
    data64 = data64.digest()
    data64 = base64.b64encode(data64)
    response += data64.decode()
    response += "\r\nX-Content-Type-Options: nosniff\r\n\r\n"
    clients.append((handler, usr))
    handler.upgraded = True
    #print(response)
    return response.encode()

def buildNoResponse(content_type, content):
    response = "HTTP/1.1 404 Not Found\r\n"
    response += "Content-Type: " + content_type + "\r\n"
    response += "X-Content-Type-Options: nosniff\r\n"
    response += "Content-Length: " + str(len(content)) + "\r\n\r\n"
    if (isinstance(content, str)):
        response += content
        response = response.encode()
    else:
        response = response.encode() + content
    return response

def buildLoginResponse(handler, data):
    data = data.decode()
    namestartind = data.find('name="username"\r\n\r\n') + 19
    cutdata = data[namestartind:]
    cutdata = cutdata[:cutdata.find('\r\n')]
    inputuser = cutdata
    xsrfstartind = data.find('name="xsrf_token"\r\n\r\n') + 21
    cutdata2 = data[xsrfstartind:]
    cutdata2 = cutdata2[:cutdata2.find('\r\n')]
    xsrfy = cutdata2
    if not(xsrfy in handler.xsrftokens):
        handler.request.sendall("HTTP/1.1 403 Forbidden\r\nContent-Length: 42\r\nContent-Type: text/plain; charset=utf-8\r\nX-Content-Type-Options: nosniff\r\n\r\nGet a better token. Don't do what you did.".encode())
    else:
        curuser = database.users.find_one({"user":inputuser})
        if(curuser == None):
            return ("HTTP/1.1 200 OK\r\nContent-Length: 19\r\nContent-Type: text/plain; charset=utf-8\r\nX-Content-Type-Options: nosniff\r\n\r\nLog in unsuccessful").encode()

        #Isolate password:
        passstartind = data.find('name="password"\r\n\r\n') + 19
        cutdata = data[passstartind:]
        cutdata = cutdata[:cutdata.find('\r\n')]
        inputpass = cutdata

        #Retrieve salt from database then salt+hash the password:
        passenc = inputpass.encode()
        salt = curuser['salt']
        saltedpass = passenc + salt
        hashed = hashlib.sha256(saltedpass)
        hashed = (hashed.digest())
        auth = False

        if curuser['pass'] == hashed:
            auth = True
        if not auth:
            return ("HTTP/1.1 200 OK\r\nContent-Length: 19\r\nContent-Type: text/plain; charset=utf-8\r\nX-Content-Type-Options: nosniff\r\n\r\nLog in unsuccessful").encode()
        else:
            token_length = 20
            token = ''
            for i in range (token_length):
                token = token+random.SystemRandom().choice(string.ascii_letters + string.digits)
            encoded_token = hashlib.sha256(token.encode())
            logindata = {'user':inputuser, 'token':encoded_token.digest()}
            user_id = database.tokens.insert_one(logindata)
            signedinusers.append((user_id, handler))
            return(("HTTP/1.1 301 Moved Permanently\r\nContent-Length: 0\r\nLocation: /\r\nX-Content-Type-Options: nosniff\r\nSet-Cookie: usertoken="+token+"; HttpOnly; Max-Age=3600\r\n\r\n").encode())

def buildChatResponse(data, handler):

    data = data.decode()
    namestartind = data.find('name="message"\r\n\r\n') + 18
    cutdata = data[namestartind:]
    cutdata = cutdata[:cutdata.find('\r\n')]
    message = cutdata

    xsrfstartind = data.find('name="xsrf_token"\r\n\r\n') + 21
    cutdata2 = data[xsrfstartind:]
    cutdata2 = cutdata2[:cutdata2.find('\r\n')]
    xsrfy = cutdata2

    message = message.replace("&", "&amp;")
    message = message.replace("<", "&lt;")
    message = message.replace(">", "&gt;")


    if not(xsrfy in handler.xsrftokens):
        handler.request.sendall("HTTP/1.1 403 Forbidden\r\nContent-Length: 42\r\nContent-Type: text/plain; charset=utf-8\r\nX-Content-Type-Options: nosniff\r\n\r\nGet a better token. Don't do what you did.".encode())
    else:
        entry = {'message':message, 'upvotes':0, 'id':database.messages.count_documents({})}
        msg = database.messages.insert_one(entry)
        return(("HTTP/1.1 301 Moved Permanently\r\nContent-Length: 0\r\nLocation: /\r\nX-Content-Type-Options: nosniff\r\n\r\n").encode())

def buildSignupResponse(data, handler):
    salt = bcrypt.gensalt()
    data = data.decode()
    #Isolate username:
    namestartind = data.find('name="username"\r\n\r\n') + 19
    cutdata = data[namestartind:]
    cutdata = cutdata[:cutdata.find('\r\n')]
    inputuser = cutdata
    inputuser = inputuser.replace("&", "&amp;")
    inputuser = inputuser.replace("<", "&lt;")
    inputuser = inputuser.replace(">", "&gt;")

    xsrfstartind = data.find('name="xsrf_token"\r\n\r\n') + 21
    cutdata2 = data[xsrfstartind:]
    cutdata2 = cutdata2[:cutdata2.find('\r\n')]
    xsrfy = cutdata2

    if not(xsrfy in handler.xsrftokens):
        handler.request.sendall("HTTP/1.1 403 Forbidden\r\nContent-Length: 42\r\nContent-Type: text/plain; charset=utf-8\r\nX-Content-Type-Options: nosniff\r\n\r\nGet a better token. Don't do what you did.".encode())
    else:

        if(len(inputuser) > 20):
            return ("HTTP/1.1 200 OK\r\nContent-Length: 32\r\nContent-Type: text/plain; charset=utf-8\r\nX-Content-Type-Options: nosniff\r\n\r\nUsername must be <=20 characters.").encode()

        searchuser = database.users.find_one({"user":inputuser})
        if(searchuser != None):
            return ("HTTP/1.1 200 OK\r\nContent-Length: 14\r\nContent-Type: text/plain; charset=utf-8\r\nX-Content-Type-Options: nosniff\r\n\r\nUsername taken").encode()
            
        #Isolate password:
        passstartind = data.find('name="password"\r\n\r\n') + 19
        cutdata = data[passstartind:]
        cutdata = cutdata[:cutdata.find('\r\n')]
        inputpass = cutdata

        #Check that password meets requirements:
        invalid = False
        if(len(inputpass) > 20 or len(inputpass) < 8):
            invalid = True
        if(inputpass.isalnum()):
            invalid = True
        hasupper = False
        haslower = False
        hasnumber = False
        for i in inputpass:
            if(i.isupper()):
                hasupper = True
            if(i.islower()):
                haslower = True
            if(i.isdigit()):
                hasnumber = True
        if(not (hasupper and haslower and hasnumber and not invalid)):
            return ("HTTP/1.1 200 OK\r\nContent-Length: 34\r\nContent-Type: text/plain; charset=utf-8\r\nX-Content-Type-Options: nosniff\r\n\r\nInvalid Password, see requirements").encode()

        #Salt and hash password:
        passenc = inputpass.encode()
        saltedpass = passenc + salt
        hashed = hashlib.sha256(saltedpass)
        hashed = (hashed.digest())

        #Put username, hashed password, and salt into a dictionary and insert it to the database:
        logindata = {'user':inputuser, 'pass':hashed, 'salt':salt}
        user_id = database.users.insert_one(logindata)

        return ("HTTP/1.1 200 OK\r\nContent-Length: 17\r\nContent-Type: text/plain; charset=utf-8\r\nX-Content-Type-Options: nosniff\r\n\r\nSignup successful").encode()
            
def buildPicResponse(data, handler):
    handler.request.sendall("HTTP/1.1 403 Forbidden\r\nContent-Length: 42\r\nContent-Type: text/plain; charset=utf-8\r\nX-Content-Type-Options: nosniff\r\n\r\nGet a better token. Don't do what you did.".encode())
    return

def maintainSocket(handler):
    while True:
        data = handler.request.recv(2048).strip()
        if len(data) != 0:
            parsed = frame_parsing.handle(data)
            if(parsed[1] == 'text'):
                payload = parsed[0].decode()
                inputdict = json.loads(payload)
                sender = ''
                roycipient = None
                if(inputdict['type'] == 'dm'):
                    #find username using handler
                    for client in clients:
                        if client[0] == handler:
                            sender = client[1]
                        if(client[1] == inputdict['username']):
                            roycipient = client[0] #ASSUME RECIPIENT IS ONLINE

                    safemessage = inputdict['message']
                    safemessage = safemessage.replace("&", "&amp;")
                    safemessage = safemessage.replace("<", "&lt;")
                    safemessage = safemessage.replace(">", "&gt;")
                    
                    outputdict = {'username':sender, 'message':safemessage, 'type':'dm'}
                    jsonmsg = json.dumps(outputdict)
                    outputframe =  frame_parsing.buildFrame(jsonmsg.encode())
                    parsed2 = frame_parsing.handle(outputframe)
                    payload2 = parsed2[0].decode()
                    roycipient.request.sendall(outputframe)

                elif(inputdict['type'] == 'vote'):
                    msgid = inputdict['id']
                    cur = database.messages.find_one({"id":int(msgid)})
                    numvotes = int(cur['upvotes']) + 1
                    database.messages.update_one({"id":int(msgid)}, { "$set": { "upvotes": numvotes } })
                    
                    outputdict = {'id':msgid, 'type':'vote', 'upvotes':numvotes}
                    jsonmsg = json.dumps(outputdict)
                    outputframe =  frame_parsing.buildFrame(jsonmsg.encode())
                    for client in clients:
                        try: client[0].request.sendall(outputframe)
                        except: pass

            elif(parsed[1] == 'bytes'):
                pass
            elif( parsed[1] == 'close'):
                for client in clients:
                    if client[0] == handler:
                        clients.remove(client)
