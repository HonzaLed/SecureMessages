from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from hashlib import sha512
import binascii

class Cipher:
    def __init__(self):
        pass
    def sign(self, msg, privKey):
        try:
            msg = msg.encode()
        except:
            pass
        hash = int.from_bytes(sha512(msg).digest(), byteorder='big')
        return pow(hash, privKey.d, privKey.n)
    def verify(self, msg, signature, pubKey):
        try:
            msg = msg.encode()
        except:
            pass
        hash = int.from_bytes(sha512(msg).digest(), byteorder='big')
        hashFromSignature = pow(signature, pubKey.e, pubKey.n)
        return hash==hashFromSignature


user = int(input("Enter user ID (1/2): "))
with open("client"+str(user)+"-priv.pem", "r") as file:
    privKey = RSA.import_key(file.read())

pubKeys = [0]
for i in range(1,3):
    with open("client"+str(i)+"-pub.pem", "r") as file:
        pubKeys.append(RSA.import_key(file.read()))


ciphers = [0]
for i in range(1,3):
    ciphers.append(PKCS1_OAEP.new(pubKeys[i]))

decr = PKCS1_OAEP.new(privKey)
cipher = Cipher()

def enc(to,msg):
    try:
        encodedMsg = msg.encode()
    except:
        encodedMsg = msg
    encMsg = ciphers[to].encrypt(encodedMsg)
    signMsg = cipher.sign(encMsg, privKey)
    return (msg, encMsg, signMsg)
def vrf(frm, msg, sign):
    return cipher.verify(msg,sign,pubKeys[frm])

"""
while True:
    cmd = input(": ")
    if cmd == "enc":
        to = int(input("Enter user ID to encrypt for (1/2): "))
        msg = input("Enter the message for user "+str(to)+": ")
        encMsg = ciphers[to].encrypt(msg.encode())
        signMsg = cipher.sign(encMsg, privKey)
        print("Encrrypted msg: ",encMsg)
        print("Signature: ",signMsg)
    elif cmd == "vrf":
        frm = int(input("From waht user is the message (1/2): "))
        msg = input("Enter the message to verify: ")
        sign = int(input("Enter signature of the message: "))
        print("Signature valid: ", cipher.verify(msg,sign,pubKeys[frm]))
"""
