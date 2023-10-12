# Group 7:
# Adam Smith (2449898)
# Celeste Artley (2600927)
# Daniel Niven (2481553)
# Stacy Onyango (2437819)
# Ross Mcbride (r.s.z.mcbride)

from itertools import count
import socket
import threading
import queue

# set the correct values for the address, and the port
addr = '::1'
port = 6667

# defines the server class, in which the server operations are executed
class Server:

    # creates the instance of the Server object, and instantiates the variables
    def __init__(this, addr, port):

        # socket connection, using IPv6
        this.server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

        # creates empty arrays to store users and the nicknames of these users as well as connection in a list of dictionaries.
        this.users = []

        # dictionary for channels { "#channel_name": [list_of_users] }
        this.channels = {}  

        # assigns the correct values to the addr and port variables of the object
        this.addr = addr
        this.port = port
        
        #prevents accessing data at the same time with multi threads by locking it
        this.lock = threading.Lock()  

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

            #This is a que for the messages sent to register the users
            user_queue = queue.Queue()
            # Create a new thread to handle this client and allowing for multiple users connections
            threading.Thread(target=this.handle_client, args=(user, addr, user_queue)).start()
            threading.Thread(target=this.process_client_messages, args=(user, addr, user_queue)).start()

    # send function, which is used to send messages to the clients
    def Send(this, message):
        with this.lock:
            for user in this.users:
                user['user'].send(message) # need to have the user sent to this function to have it send data. it would access it through the dictionary

    def Receive(this, message):
        this.server.recv(1024).decode('ascii')
        print(f'{this.address} TEST')
    
    def handle_client(this, user, addr, user_queue):
        user_details = {"addr": addr, "user": user, "nick": "", "username": "", "registered": False}
        buffer = ""
        while True:
            data = user.recv(1024).decode('ascii')
            if not data:
                break

            buffer += data

            while "\r\n" in buffer:
                line, buffer = buffer.split("\r\n", 1)
                user_queue.put(line)

    def process_client_messages(this, user, addr, user_queue):
        user_details = {"addr": addr, "user": user, "nick": "", "username": "", "registered": False}
        addr_header_send = f"[{user_details['addr'][0]}:{user_details['addr'][1]}] <- b'"
        addr_header_recieve = f"[{user_details['addr'][0]}:{user_details['addr'][1]}] -> b'"
        while True:
            if not user_queue.empty():
                #uses the queue to get the next message
                message = user_queue.get()
                words = message.split()
                #recieved message log into the server
                print (f"{addr_header_recieve} {message}")
                
                # Parse the message by spliting and then pulling out the all caps word to run the if statement on.
                command = words[0].upper()
                if command == 'PASS':
                    user_details["password"] = words[1].strip()

                    #used for debuging PASS command
                    # print(f"{addr_header_send} PASS command received. Password set to {user_details['password']}")

                elif command == 'NICK':
                    user_details["nick"] = words[1].strip()

                    #used for debuging NICK command
                    #print(f"{addr_header_send} NICK command received. Nick set to {user_details['nick']}")

                elif command == 'USER':
                    # Parsing username, hostname, servername and realname from the words list
                    username = words[1]
                    hostname = words[2]
                    servername = words[3]
                    realname = message.split(":", 1)[1].strip()

                    # Placing them in the dictionary
                    user_details["username"] = username
                    user_details["hostname"] = hostname
                    user_details["servername"] = servername
                    user_details["realname"] = message.split(":", 1)[1].strip()  # Stripping the leading ':'
                    
                    #used for debuging USAER command
                    #print(f"{addr_header_send} USER command received. Username set to {user_details['username']}")
                    #print(f"{addr_header_send} Hostname set to {user_details['hostname']}")
                    #print(f"{addr_header_send} Servername set to {user_details['servername']}")
                    #print(f"{addr_header_send} Realname set to {user_details['realname']}")

                elif command == 'CAP':
                    #need to create a CAP command that sets a clients capablilities format CAP  <Arguments>

                    #used for debuging CAP command
                    print(f"{addr_header_send} user set the permissions")

                elif command == 'JOIN':
                    channel_name = words[1].strip()
        
                    # Create the channel if it does not exist
                    if channel_name not in this.channels:
                        this.channels[channel_name] = []
                    
                    # Add the user to the channel
                    this.channels[channel_name].append(user_details)

                    #log to the server what the channel the client is in
                    print(f"{addr_header_send} User {user_details['nick']} joined channel {channel_name}")

                    #Building the names list for the 353 command to be sent to each user
                    names_list = " ".join([u['nick'] for u in this.channels[channel_name]])

                    # Broadcast to the other users of that server that the client has JOINed
                    # This happens regularly and needs to be able to be sent more often using the LIST command I think
                    for channel_user in this.channels[channel_name]:
                        channel_user['user'].send(f":{user_details['nick']}!{user_details['username']}@{addr[0]} JOIN {channel_name}\r\n".encode('ascii'))

                        # Trying to implement the topic lookup if statement but the Data Structure does not work for this
                        # if this.channels[channel_name].get("topic", None):
                        #     channel_user['user'].send(f":{user_details['hostname']} 331 {user_details['nick']} {channel_name} :{this.channels[channel_name]['topic']}\r\n".encode('ascii'))
                        # else:
                        channel_user['user'].send(f":{user_details['hostname']} 331 {user_details['nick']} {channel_name} :No Topic is set\r\n".encode('ascii'))
                        #This is where you send the name list info
                        channel_user['user'].send(f":{user_details['hostname']} 353 {user_details['nick']} = {channel_name} :{names_list}\r\n".encode('ascii'))
                        #This is where you tell the client that you are at the end of the names list
                        channel_user['user'].send(f":{user_details['hostname']} 366 {user_details['nick']} {channel_name} :End of names list\r\n".encode('ascii'))

                elif command == 'PART':
                    #need to create a part command that puts a user in the channel they need be in format PART #channel_name
                    print(f"{addr_header_send} user left channel ____")
                
                elif command == 'QUIT':
                    # Parse optional quit message then split it from the command word
                    optional_message = ''
                    if len(words) > 1:
                        optional_message = message.split(" ", 1)[1].strip()

                    # Broadcast quit message to all the users channels
                    for channel_name, channel_users in this.channels.items():
                        if user_details in channel_users:
                            for channel_user in channel_users:
                                channel_user['user'].send(f":{user_details['nick']}!{user_details['username']}@{addr[0]} QUIT :{optional_message}\r\n".encode('ascii'))
                            # Remove the user from this channel
                            channel_users.remove(user_details)

                    # Remove user from the users list
                    this.users.remove(user_details)

                    # Close the socket
                    user.close()

                    print(f"{addr_header_send} user has quit. Message: {optional_message}")

                    # Break out of the while loop to end this thread for the user
                    break
                
                elif command == 'LIST':
                    # need to create a list command that shows all the available channels format LIST
                    num = 0

                    for channel_name, channel_users in this.channels.items():
                        # Reset num for each channel
                        num = 0

                        # Count users in the current channel
                        for channel_user in channel_users:
                            if user_details != channel_user:  # Exclude the current user from the count
                                num += 1

                        # Send information about the channel to the user
                        user_details['user'].send(f":{user_details['hostname']} 322 {user_details['nick']} {channel_name} {num} :\r\n".encode('ascii'))
                        print(f"{addr_header_send}:{user_details['hostname']} 322 {user_details['nick']} {channel_name} {num} :")

                    user_details['user'].send(f"{user_details['hostname']} 323 {user_details['nick']} :End of LIST\r\n".encode('ascii'))
                    print(f"{addr_header_send}:{user_details['hostname']} 323 {user_details['nick']} :End of LIST\r\n")

                elif command == 'PRIVMSG':
                    # Takes the target, which could be a  channel or a nickname to be used to send to the right client
                    target = words[1]  
                    #Gets the message from the split using the : and then strips the info after it
                    message_text = message.split(":", 1)[1].strip()  

                    # Check to see if it's a channel
                    if target.startswith("#"):
                        if target in this.channels:  # Make sure channel exists
                            # Send the message to all users in the channel
                            for channel_user in this.channels[target]:
                                # however you don't want to send the message twice so you need to exclude yourself as a channel_user from the channels list
                                if channel_user['addr'] != addr:
                                    channel_user['user'].send(f":{user_details['nick']}!{user_details['username']}@{addr[0]} PRIVMSG {target} :{message_text}\r\n".encode('ascii'))
                                
                    # If the target is a nickname
                    else:
                        # Send the message to the user with the target nickname
                        for user in this.users:
                            if user['nick'] == target:
                                user['user'].send(f":{user_details['nick']}!{user_details['username']}@{addr[0]} PRIVMSG {target} :{message_text}\r\n".encode('ascii'))
                                break 
                    #Logs the message to the Server in the correct way
                    print(f"{addr_header_send} Message sent to {target}")
                
                elif command == "SLAP":
                    if len(words) >= 2:  # Ensure that there are at least 2 elements in the words list
                        # Get a list of users in the channel
                        channel_name = words[1].strip()  # Assuming the channel name is the argument after SLAP
                        channel_users = this.channels.get(channel_name, [])

                        # Exclude the user who sent the command from the list of potential targets
                        potential_targets = [user['nick'] for user in channel_users if user['nick'] != user_details['nick']]

                        if potential_targets:
                            # Choose a random target from the list
                            target = random.choice(potential_targets)

                            # Send the slap message to the channel
                            slap_message = f":{user_details['nick']}!{user_details['username']}@{addr[0]} PRIVMSG {'#Bot_Commands'} :{target}, you've been slapped!\r\n"
                            this.Send(slap_message.encode('ascii'))
                    
                            # Log the action in the server
                            print(f"{addr_header_send} {user_details['nick']} slapped {target}")
                        else:
                            # Inform the user that there's no one to slap
                            user_details['user'].send(f":{user_details['hostname']} NOTICE {user_details['nick']} :No one to slap in {channel_name}\r\n".encode('ascii'))
                    else:
                        # Inform the user that the SLAP command is not properly formatted
                        user_details['user'].send(f":{user_details['hostname']} NOTICE {user_details['nick']} :SLAP command should be formatted as SLAP #channel\r\n".encode('ascii'))
                elif command == 'TOPIC':
                    print(f"User tryed to change the topic")
              
                
                elif command == 'PONG':
                    # Need to create a PONG to keep the server in registered status True
                    # Also need to setup a server send to client PIMGing them
                    print(f"{addr_header_send} user replyed to PING")
                
                # Checks that the user info is enough to be registered to the users list.
                # Has the user_details stored in a local dictionary but not with the full details guaraneteed and should make sure all data is verified before finish.
                if user_details["nick"] and user_details["username"] and not user_details["registered"]:
                    # Update registered = True
                    user_details["registered"] = True
                    # Send welcome message etc. as per IRC 002
                    print(f"{addr_header_send}:{user_details['hostname']} 001 {user_details['nick']} :Hi, welcome to IRC.")
                    user_details['user'].send(f":{user_details['hostname']} 001 {user_details['nick']} :Hi, welcome to IRC.\r\n".encode("ascii"))
                    # Send version number per 002
                    print(f"{addr_header_send}:{user_details['hostname']} 002 {user_details['nick']} :Your host is {user_details['hostname']} running version Group 7 IRC 1.0")
                    user_details['user'].send(f":{user_details['hostname']} 002 {user_details['nick']} :Your host is {user_details['hostname']} running version Group 7 IRC 1.0\r\n".encode("ascii"))
                    # Send Server created time per 003
                    print(f"{addr_header_send}:{user_details['hostname']} 003 {user_details['nick']} :This server was created sometime")
                    user_details['user'].send(f":{user_details['hostname']} 003 {user_details['nick']} :This server was created sometime\r\n".encode("ascii"))
                    # Send connection successfull 004
                    print(f"{addr_header_send}:{user_details['hostname']} 004 {user_details['nick']} {user_details['hostname']} Group 7 IRC 1.0 :")
                    user_details['user'].send(f":{user_details['hostname']} 004 {user_details['nick']} {user_details['hostname']} Group 7 IRC 1.0\r\n".encode("ascii"))

                    #This needs to be updated with the proper number of users.
                    print(f"{addr_header_send}:{user_details['hostname']} 251 {user_details['nick']} :There are ____ users and 0 services on 1 server")
                    user_details['user'].send(f":{user_details['hostname']} 251 {user_details['nick']} :There are ____ users and 0 services on 1 server\r\n".encode("ascii"))

                    #this needs to be updated to not be hardcoded this will be done when you can set the Message of The Day
                    print(f"{addr_header_send}:{user_details['hostname']} 422 {user_details['nick']} :MOTD File is missing")
                    user_details['user'].send(f":{user_details['hostname']} 422 {user_details['nick']} :MOTD File is missing\r\n".encode("ascii"))
                    # Add user_details dictionary to the users list
                    this.users.append(user_details)

                    

                # Tell the que that the current task is done    
                user_queue.task_done()
        

# creates the new instance of the server, and launches it
server = Server(addr, port)
server.launch()