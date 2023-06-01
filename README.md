# SecureMessages
This app was created so that I could try working with asymmetric encryption.

The app consists of two parts, the client, and the server.

## The server

It's just a dumb, sort of a "database" server, but it uses JSON files instead of a real database.  
I might one day migrate it to MongoDB.  
- Stores encrypted and signed messages
- Stores user nicknames and public keys
- Can delete messages, but must first verify user signature

## The client

- Provides command-line interface to the user
- Decrypts and encrypts messages
- Sends messages
- Checks the message signature and shows the message in green when singed, and in red when the signature is not correct
