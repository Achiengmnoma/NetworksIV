# Group 7:
# Adam Smith (2449898)
# Daniel Niven (2481553)
# Stacy Onyango (2437819)
# Ross Mcbride (r.s.z.mcbride)

from asyncio.windows_events import NULL
import socket

# set the correct values for the address, and the port
addr = '::1'
port = 6667

# defines the server class, in which the server operations are executed
class Server:

    # creates the instance of the Server object, and instantiates the variables
    def __init__(this, addr, port):

        # socket connection, using IPv6
        this.server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

        # creates empty arrays to store users and the nicknames of these users
        this.users = []
        this.nicks = []

        # assigns the correct values to the addr and port variables of the object
        this.addr = addr
        this.port = port

    def launch(this):

        # binds the socket to the address and port
        this.server.bind((this.addr, this.port))

        # listens for connections, and limits the number of connections to 2 for now
        this.server.listen(2)

        # displays that the server is listening for connections, as well as the addr address and port that it is listening on
        print("Listening on port " + str(this.port))

        # begins an infinite loop, so that new clients are always accepted by the server
        # the following youtube video was partially referenced when writing this loop : https://www.youtube.com/watch?v=3UOyky9sEQY&t=940s
        while True:

            # accepts the connection, and displays that the connection was succesful
            user, addr = this.server.accept()
            this.address = str(addr).split("'")[1].split("'")[0] + ":" + str(addr).split(", ")[1].split(",")[0]
            print("Accepted connection from " + this.address)

            # receives the nickname of the client, and decodes it
            PASS = user.recv(1024).decode('ascii')   
            NICK = user.recv(1024).decode('ascii')
            USER = user.recv(1024).decode('ascii')
            print("First thing received:")
            this.DispReceive(PASS)
            print("Second thing Received:")
            this.DispReceive(NICK)
            print("Third thing received:")
            this.DispReceive(USER)
            #if PASS != NULL:
                #this.DispReceive(f"THIS WILL EVENTUALLY BE A BUNCH OF REGISTRATION INFORMATION")
            #this.DispReceive(f'NICK {nick}USER {username} 0 * :{realname}')

            #user.send(nick.encode('ascii'))
            

            # some very brief validation for the username
            #if nick in this.users:
                #user.send("Please choose a unique name!")
            #else:
                # adds the user and their nickname to the relevant arrays
                #this.nicks.append(nick)
                #this.users.append(user)
            
            # welcomes the new client to the server, and tells all other clients that a new user has joined

    # send function, which is used to send messages to the clients
    def Send(this, message):
        for user in this.users:
            user.send(message)

    def DispReceive(this, msg):
        print(f"[{this.address}] -> b {msg}")

    def DispSend(this, msg):
        print(f"[{this.address}] <- b {msg}")

# creates the new instance of the server, and launches it
server = Server(addr, port)
server.launch()