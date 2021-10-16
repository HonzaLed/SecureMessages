"""
A pure python (slow) implementation of rijndael with a decent interface

To include -
"""
from rijndael import rijndael
"""
To do a key setup -

key must be a string of length 16, 24, or 32
blocksize must be 16, 24, or 32. Default is 16

To use -

ciphertext = r.encrypt(plaintext)
plaintext = r.decrypt(ciphertext)

If any strings are of the wrong length a ValueError is thrown
"""

def pad(s):
    block_size = 16
    remainder = len(s) % block_size
    padding_needed = block_size - remainder
    return s + padding_needed * ' '
def unpad(s): 
    return s.rstrip()
"""
key = pad("SecurePassword")
rCipher = rijndael(key, block_size = 16)
"""

class rijndaelCipher:
    def __init__(self, key, block_size=16):
        self.r = rijndael(pad(key), block_size=block_size)
    def encrypt(self,plaintext):
        return self.r.encrypt(pad(plaintext))
    def decrypt(self,ciphertext):
        return unpad(self.r.decrypt(ciphertext))

r = rijndaelCipher("SecurePassword")
