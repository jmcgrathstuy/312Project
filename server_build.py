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