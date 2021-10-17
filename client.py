from typing import final
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from hashlib import sha512
import binascii

debug = True

class Cipher:
    def __init__(self, privKey, pubKey):
        self.privKey = privKey
        self.pubKey = pubKey
        self.decryptor = PKCS1_OAEP.new(privKey)
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
    def encrypt(self, plaintext, pubKey):
        try:
            plaintext = plaintext.encode()
        except:
            pass
        return PKCS1_OAEP.new(pubKey).encrypt(plaintext)
    def decrypt(self, ciphertext):
        try:
            ciphertext = ciphertext.encode()
        except:
            pass
        return self.decryptor.decrypt(ciphertext)

def check(question, optionA, optionB):
    msg = input(question)
    if msg.lower() == optionA.lower():
        return True
    elif msg.lower() == optionB.lower():
        return False
    else:
        print("Unrecognized option, please try again!")
        return check(question, optionA, optionB)
def toHex(bytes):
    return bytes.hex()
def fromHex(hex):
    return bytes.fromhex(hex)


try:
    file = open("client.pem", "r")
    print("Found key file, trying to load...")
    try:
        privKey = RSA.import_key(file.read())
    except ValueError:
        print("Key is protected by password")
        attemps = 0
        while attemps < 4:
            psswd = input("Please enter pasword: ")
            try:
                print("[DEBUG]",psswd)
                privKey = RSA.import_key(file.read(), psswd)
                break
            except ValueError as err:
                print("Wrong password, you have",3-attemps,"attemps left, please try again!")
                print(err)
                attemps = attemps+1
        if attemps<3:
            print("Successfully loaded key from file!")
        else:
            print("You entered wrong password 3 times, program is exiting, please restart program and try again!")
            exit()
    finally:
        print("Successfully loaded key from file!")
    pubKey = privKey.public_key()
except FileNotFoundError:
    if not check("No key was found in current directory, do you want to generate new key? (Y/N): ","y","n"):
        exit()
    privKey = RSA.generate(1024)
    pubKey = privKey.public_key()
    print("Generated new key, saving to the file")
    file = open("client.pem", "wb")
    if check("Do you want to secure file with the password(strongly recomended, and not working, select N) (y/n):", "y", "n"):
        psswd = input("Create password for the file with the key: ")
        print("[DEBUG]",psswd)
        file.write(privKey.export_key('PEM', psswd))
    else:
        file.write(privKey.export_key('PEM'))
    print("Successfully wrote key to the file!")
file.close()
pubKeyID = pubKey.export_key("DER").hex()
if debug:
    print("[DEBUG]",privKey.export_key("PEM"))
    print("[DEBUG]",pubKey.export_key("PEM"))


