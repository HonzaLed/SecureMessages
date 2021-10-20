from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from hashlib import sha512
from time import sleep
import requests
import binascii
import json

### ONLY IN DEV
debug = True

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
class Cipher:
    def __init__(self, privKey, pubKey):
        self.privKey = privKey
        self.pubKey = pubKey
        self.decryptor = PKCS1_OAEP.new(privKey)
    def sign(self, msg, privKey=None):
        try:
            msg = msg.encode()
        except:
            pass
        hash = int.from_bytes(sha512(msg).digest(), byteorder='big')
        if privKey==None:
            return pow(hash, self.privKey.d, self.privKey.n)
        else:
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

class ComHandler:
    def __init__(self, address, https=False):
        if https:
            self.address = "https://"+str(address)
        else:
            self.address = "http://"+str(address)
    def get_users(self):
        return json.loads(requests.get(self.address+"/users").text)["users"]
    def get_user(self, pubKeyID):
        return json.loads(requests.get(self.address+"/upload/"+str(pubKeyID)).text)
    def send(self, msg, sign, toPubKeyID, frmPubKeyID):
        data = {"msg":msg, "sign":sign, "frmPubKeyID":frmPubKeyID}
        return json.loads(requests.post(self.address+"/upload/"+str(toPubKeyID), json=data).text)
    def register(self, pubKeyID, nickname):
        data = {"pubKeyID":pubKeyID, "nickname":nickname}
        return json.loads(requests.post(self.address+"/register", json=data).text)
    def check_same_user(self, pubKeyID):
        users = self.get_users()
        for user in users:
            if user["pubKeyID"] == pubKeyID:
                return True
        return False
    def get_nickname(self, pubKeyID):
        return self.get_user(pubKeyID)["nickname"]
    def get_nicknames(self):
        nicknames = []
        for user in self.get_users():
            nicknames.append(self.get_nickname(user["pubKeyID"]))
        return nicknames
    def get_user_by_nickname(self, nickname):
        """Return user json by provided nickname"""
        for user in self.get_users():
            user = self.get_user(user["pubKeyID"])
            if user["nickname"] == nickname:
                return user
        return None

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
                if debug:
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
    privKey = RSA.generate(3072)
    pubKey = privKey.public_key()
    print("Generated new key, saving to the file")
    file = open("client.pem", "wb")
    if check("Do you want to secure file with the password(strongly recomended, and not working, select N) (y/n):", "y", "n"):
        psswd = input("Create password for the file with the key: ")
        if debug:
            print("[DEBUG]",psswd)
        file.write(privKey.export_key('PEM', psswd))
    else:
        file.write(privKey.export_key('PEM'))
    print("Successfully wrote key to the file!")
file.close()
pubKeyID = pubKey.export_key("DER").hex()
cipher = Cipher(privKey, pubKey)
if debug:
    print("[DEBUG]",privKey.export_key("PEM"))
    print("[DEBUG]",pubKey.export_key("PEM"))

### DEV SERVER
#server = "127.0.0.1:5000" # localhost only for testing
#useHttps = False
### PRODUCTION SERVER
server = "SecureMessagingServer.honzaled.repl.co"
useHttps = True

print("Connecting to server...")
com = ComHandler(server, https=useHttps)
print("Connected!")
if not com.check_same_user(pubKeyID):
    if not check("Your account was not found on the server, do you want to register on the server "+server+"? (y/n): ", "y", "n"):
        print("Without registering, app can't continue, exiting...")
        exit()
    else:
        print("OK, registering...")
        nickname = input("Please enter nickname you want to use: ")
        response = com.register(pubKeyID, nickname)
        if debug:
            print("[DEBUG]",response)
        sleep(0.5)
        print("Registered!")
else:
    print("Found your account!")
print("Your nickname:",com.get_nickname(pubKeyID))


def menu():
    print("What do you want to do?")
    print("1) Send a message")
    print("2) View received messages")
    print("3) Exit")
    return int(input("Select one option (1/2/3): "))

def sendMsgWizard():
    nicknames = com.get_nicknames()
    print("Select person to send message to")
    i = 1
    for a in nicknames:
        print(str(i)+")",a)
        i = i+1
    toIndex = int(input("Select one option: "))-1
    print("Selected",nicknames[toIndex], ", fetching user data...")
    user = com.get_user_by_nickname(nicknames[toIndex])
    userKey = RSA.import_key(fromHex(user["pubKeyID"]))
    print("User data loaded!")
    if debug:
        print("[DEBUG]", userKey.export_key())
    msg = input("Enter your message to send: ")
    cipherText = cipher.encrypt(msg, userKey)
    sign = cipher.sign(cipherText)
    response = com.send(cipherText.hex(), sign, user["pubKeyID"], pubKeyID)
    if response["status"] == "OK":
        print("Successfully sent!")
    else:
        print("Error",response["error"])
    




def showReceivedMsgs():
    print("Fetching messages...")
    userObj = com.get_user(pubKeyID)
    messages = userObj["messages"]
    for message in messages:
        ciphertextHex = message["msg"]
        sign = int(message["sign"])
        frmPubKeyID = message["frmPubKeyID"]
        frmPubKey = RSA.import_key(bytes.fromhex(frmPubKeyID))
        frmNickname = com.get_nickname(frmPubKeyID)
        ciphertext = bytes.fromhex(ciphertextHex)
        try:
            msg = cipher.decrypt(ciphertext).decode()
            try:
                ver = cipher.verify(ciphertext, sign, frmPubKey)
            except BaseException as err:
                print(bcolors.FAIL+"Verification error",err,bcolors.ENDC)
            if ver:
                print(bcolors.OKGREEN+"Message from", str(frmNickname)+":",msg,bcolors.ENDC)
            else:
                print(bcolors.FAIL+"Bad message from", str(frmNickname)+":",msg,bcolors.ENDC)
        except BaseException as err:
            print(bcolors.FAIL+"Decrypting error",err,bcolors.ENDC)

while True:
    cmd = menu()
    if cmd == 1:
        sendMsgWizard()
    elif cmd == 2:
        showReceivedMsgs()
    elif cmd == 3:
        print("Exiting...")
        exit()