from Crypto.Cipher import AES
import base64

key = b'ThisIsASecretKey'  # 16-byte key

def pad(s):
    return s + (16 - len(s) % 16) * chr(16 - len(s) % 16)

def unpad(s):
    return s[:-ord(s[len(s)-1:])]

def encrypt(data):
    cipher = AES.new(key, AES.MODE_ECB)
    encrypted = cipher.encrypt(pad(data).encode())
    return base64.b64encode(encrypted).decode()

def decrypt(data):
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted = cipher.decrypt(base64.b64decode(data))
    return unpad(decrypted.decode())