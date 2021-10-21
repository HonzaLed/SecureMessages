from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from hashlib import sha512
from time import sleep
import requests
import binascii
import argparse
import random
import json
import sys

### ONLY IN DEV
debug = False

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
    def __init__(self, address, skipCheck):
        ### URL CHECK
        #### PROTOCOL CHECK (http/https)
        # if address has no http:// or https://, then add it
        if address[0:7] != "http://" and address[:8] != "https://":
            address = "http://"+address
        try:
            r=requests.get(address)
        except requests.exceptions.ConnectionError as err:
            print(bcolors.FAIL+"Connection error, please try again",bcolors.ENDC)
            sys.exit(1)
        #set url address
        self.address = r.url
        #### SERVER CHECK (if running correct software)
        if skipCheck:
            return None
        randomBytes = bytes(random.getrandbits(8) for _ in range(32)).hex()
        hash = int.from_bytes(sha512(randomBytes.encode()).digest(), byteorder='big')
        try:
            response = requests.get(self.address+"/vrf/"+randomBytes)
        except requests.exceptions.ConnectionError as err:
            print(bcolors.FAIL+"Failed connecting to the server, check if server is running the right software",bcolors.ENDC)
            sys.exit(1)
        try:
            data=json.loads(response.text)
        except:
            print(bcolors.FAIL+"Server check failed, check if server is running the right software",bcolors.ENDC)
            sys.exit(1)
        if data["status"] == "OK":
            if hash == data["hash"]:
                #check passed
                if debug:
                    print("[DEBUG] Server confirmed!")
            else:
                if debug:
                    print("[DEBUG] Server responded but error "+data["error"])
        else:
            print(bcolors.FAIL+"Detected server error, try restarting server",bcolors.ENDC)
            sys.exit(1)
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
    def deleteMessageById(self,msgID, pubKeyID, sign):
        return requests.delete(self.address+"/delete/"+str(pubKeyID)+"/"+str(msgID)+"/"+str(sign))

def check(question, optionA, optionB):
    msg = input(question)
    if msg.lower() == optionA.lower():
        return True
    elif msg.lower() == optionB.lower():
        return False
    else:
        print("Unrecognized option, please try again!")
        return check(question, optionA, optionB)
def checkInt(question):
    answer = input(question)
    try:
        return int(answer)
    except:
        print("Please enter a number")
        return checkInt(question)
def fromHex(hex):
    return bytes.fromhex(hex)
def toHex(bytes):
    return bytes.hex()

### ARGPARSE

parser = argparse.ArgumentParser(description='Client for secure communication service')

#### SERVER

##### DEV SERVER
#parser.add_argument("-s", "--server", action="store", dest="server", default="SecureMessagingServer.honzaled.repl.co:5000", type=str, help="Server to connect to (for example example.com, example.com:8080, 127.0.0.1:5000)")

##### PRODUCTION SERVER
parser.add_argument("-s", "--server", action="store", dest="server", default="SecureMessagingServer.honzaled.repl.co", type=str, help="Server to connect to (for example example.com, example.com:8080, 127.0.0.1:5000)")

#### CHECK SERVER
parser.add_argument("-nc", "--no-check", action="store_true", dest="check", help="Skip server check")

arguments = parser.parse_args()
server = arguments.server

### MAIN
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
            sys.exit(0)
    finally:
        print("Successfully loaded key from file!")
    pubKey = privKey.public_key()
except FileNotFoundError:
    if not check("No key was found in current directory, do you want to generate new key? (Y/N): ","y","n"):
        sys.exit(0)
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

print("Connecting to server...")
com = ComHandler(server, arguments.check)
print("Connected!")
if not com.check_same_user(pubKeyID):
    if not check("Your account was not found on the server, do you want to register on the server ? (y/n): ", "y", "n"):
        print("Without registering, app can't continue, exiting...")
        sys.exit(0)
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
    print("")
    print("What do you want to do?")
    print("1) Send a message")
    print("2) View received messages")
    print("3) Delete messages")
    print("4) Exit")
    return checkInt("Select one option (1/2/3/4): ")

def sendMsgWizard():
    nicknames = com.get_nicknames()
    print("Select person to send message to (to cancel type 0)")
    i = 1
    for a in nicknames:
        print(str(i)+")",a)
        i = i+1
    toIndex = checkInt("Select one option: ")-1
    if toIndex == -1:
        return None
    print("Selected",nicknames[toIndex], ", fetching user data...")
    user = com.get_user_by_nickname(nicknames[toIndex])
    userKey = RSA.import_key(fromHex(user["pubKeyID"]))
    print("User data loaded!")
    if debug:
        print("[DEBUG]", userKey.export_key())
    msg = input("Enter your message to send: ")
    try:
        cipherText = cipher.encrypt(msg, userKey)
        try:
            sign = cipher.sign(cipherText)
            try:
                response = com.send(cipherText.hex(), sign, user["pubKeyID"], pubKeyID)
                if response["status"] == "OK":
                    print(bcolors.OKGREEN, "Successfully sent!", bcolors.ENDC)
                else:
                    print(bcolors.FAIL, "Error",response["error"], bcolors.ENDC)
            except:
                print(bcolors.FAIL, "Error sending message, check your internet connection", bcolors.ENDC)
        except:
            print(bcolors.FAIL, "Message signing error, please try again", bcolors.ENDC)
    except ValueError as err:
        if "Plaintext is too long" in str(err):
            print(bcolors.FAIL, "Encryption error, your message is too long", bcolors.ENDC)
    except:
        print(bcolors.FAIL, "Unknown encryption error, please try again", bcolors.ENDC)
    


def deleteMessagesWizard():
    deletions = 0
    print("Your messages")
    showReceivedMsgs(showIndex=True)
    usrInput = input("Enter ID of messages you want to delete, 0 for cancel (select multiple separated by comma, for example 1,2,4): ")
    if usrInput == "0":
        return None
    messagesIDs = usrInput.split(",")
    try:
        i = 0
        for item in messagesIDs:
            messagesIDs[i] = int(item)
            i = i+1
    except TypeError:
        print("You didn't entered numbers, returning to main menu")
    try:
        for i in messagesIDs:
            if debug:
                print("[DEBUG] deleting message",i)
            msgID = (i-1)-deletions
            sign = cipher.sign(pubKeyID+str(msgID))
            response = com.deleteMessageById(msgID, pubKeyID, sign)
            if debug:
                print(response.text)
            if response.status_code == 200:
                deletions = deletions+1
                print(bcolors.OKGREEN, "Successfully deleted!", bcolors.ENDC)
            else:
                print(bcolors.FAIL, "Error", json.loads(response.text)["error"], bcolors.ENDC)
    except BaseException as err:
        print("Error",err)


def showReceivedMsgs(showIndex=False):
    userObj = com.get_user(pubKeyID)
    messages = userObj["messages"]
    i = 1
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
                print(bcolors.FAIL+"Verification error (maybe fake message?) on message "+msg+" from "+frmNickname,err,bcolors.ENDC)
            if ver:
                if showIndex:
                    print(bcolors.OKGREEN+str(i)+") Message from", str(frmNickname)+":",msg,bcolors.ENDC)
                else:
                    print(bcolors.OKGREEN+"Message from", str(frmNickname)+":",msg,bcolors.ENDC)                
            else:
                if showIndex:
                    print(bcolors.FAIL+str(i)+") Bad message from (maybe fake message?) from", str(frmNickname)+":",msg,bcolors.ENDC)
                else:
                    print(bcolors.FAIL+"Bad message (maybe fake message?) from", str(frmNickname)+":",msg,bcolors.ENDC)
            print("")
        except BaseException as err:
            print(bcolors.FAIL+"Decrypting error",err,bcolors.ENDC)
        i = i+1

while True:
    cmd = menu()
    if cmd == 1:
        sendMsgWizard()
    elif cmd == 2:
        print("Fetching messages...")
        showReceivedMsgs()
    elif cmd == 3:
        deleteMessagesWizard()
    elif cmd == 4:
        print("Exiting...")
        sys.exit(0)
