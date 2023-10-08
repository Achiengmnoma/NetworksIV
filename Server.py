# Group 7:
# Adam Smith (2449898)
# Celeste Artley (2600927)
# Daniel Niven (2481553)
# Stacy Onyango (2437819)
# Ross Mcbride (r.s.z.mcbride)

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
            print(f"Accepted connection from {addr}")

            # Create a new thread to handle this client
            threading.Thread(target=this.handle_client, args=(user_socket, addr)).start()

    # send function, which is used to send messages to the clients
    def Send(this, message):
        for user in this.users:
            user.send(message)

    def Receive(this, message):
        this.server.recv(1024).decode('ascii')
        print(f'{this.address} TEST')
    
    def handle_client(this, user, addr):
        registered = False
        while True:
            message = user.recv(1024).decode('ascii')
            
            # Parse the message by spliting and then pulling out the all caps word to run the if statement on.
            command = message.split(' ')[0].upper()

            if command == 'NICK':
                nick = message.split(' ')[1].strip()
                # Add your code to register the nickname, validate etc.
                this.nicks.append(nick)

            elif command == 'USER':
                # Parsing username, hostname, servername and realname
                user_details = message.split(' ')[1:]
                username = user_details[0]
                realname = user_details[-1][1:]  # The realname starts with a ':' so use the -1
                # Add your code to register the user
                this.users.append(username)

            if nick and username:
                registered = True
                # Send welcome message etc. as per IRC RFC
                # Update registered = True

# creates the new instance of the server, and launches it
server = Server(addr, port)
server.launch()