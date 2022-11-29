import base64


def decrypt(credentials):
    return base64.b64decode(credentials).decode('ascii')
