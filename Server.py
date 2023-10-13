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
import time
import argparse
import select

parser = argparse.ArgumentParser(description='IRC Server for Networking')
parser.add_argument('--host', type=str, help='Specify the host address')
parser.add_argument('--port', type=int, help='Specify the port number')
args = parser.parse_args()


addr = args.host if args.host else '::1'
port = args.port if args.port else 6667

class Server:

    def __init__(this, addr, port):

        # socket connection, using IPv6
        this.server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

        # an array of user dictionaries that contain all info needed to manage connections
        this.users = []

        # dictionary for channels that include users and the topics for each associated channel
        this.channels = {}

        # assigns the correct values to the addr and port variables of the object
        this.addr = addr
        this.port = port
        
        # prevents accessing data at the same time with multi threads by locking it
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

            #This is a queue for the messages sent to register the users
            user_queue = queue.Queue()
            # Create a new thread to allow for multiple users to send and recieve data at the same time.
            threading.Thread(target=this.handle_Client, args=(user, addr, user_queue)).start()
            threading.Thread(target=this.process_Client_Messages, args=(user, addr, user_queue)).start()
            threading.Thread(target=this.keep_Users_Active).start()

    def keep_Users_Active(this):
        while True:
            current_time = time.time()
            for user_details in this.users:
                # If the user has not sent a message in the last 60 seconds, send a PING
                if current_time - user_details['last_msg_timestamp'] > 60:
                    this.safe_Send(user_details['user'], f"PING :{user_details['hostname']}\r\n")

                # If the user has not sent a message in the last 120 seconds, remove them
                if current_time - user_details['last_msg_timestamp'] > 120:
                    # Remove the user
                    print(f"Removing {user_details['nick']} due to timeout.")
                    this.users.remove(user_details)
                    user_details['user'].close()

            # Wait for 5 seconds before checking again
            time.sleep(5)
    
    def handle_Client(this, user, addr, user_queue):
        # Initialize user_details to None before the for loop
        user_details = None

        #checks to see if the user already exist in the this.users library
        for existing_user_details in this.users:
            if existing_user_details['user'] == user:
                user_details = existing_user_details
                break
        #If not we need to make one so we do here.
        if user_details is None:
            user_details = {"addr": addr, "user": user, "nick": "", "username": "", "registered": False, "last_msg_timestamp": time.time()}
            this.users.append(user_details)

        buffer = ""
        #Need an if statement here to check to see if the connection is active before trying to read data from them. populates and exception when discconnecting
        while True:
            if not user_details.get('is_connected', True):
                break
            try:
                data = user.recv(1024).decode('ascii')
            except Exception as e:
                print(f"Error in handle_Client: {e}")
                this.users.remove(user_details)
                break
            if not data:
                break

            buffer += data

            while "\r\n" in buffer:
                line, buffer = buffer.split("\r\n", 1)
                user_queue.put(line)

    def process_Client_Messages(this, user, addr, user_queue):
        user_details = None
        #checks to see if the user already exist in the this.users library
        for existing_user_details in this.users:
            if existing_user_details['user'] == user:
                user_details = existing_user_details
                break
        #If not we need to make one so we do here.
        if user_details is None:
            user_details = {"addr": addr, "user": user, "nick": "", "username": "", "registered": False, "last_msg_timestamp": time.time()}
            this.users.append(user_details)
        while True:
            if not user_queue.empty():
                #uses the queue to get the next message
                message = user_queue.get()
                words = message.split()
                #received message log into the server
                this.print_To_Server(user_details, f"{message}", "recieve")
                
                
                # Parse the message by spliting and then pulling out the all caps word to run the if statement on.
                if len(words) >= 1:
                    command = words[0].upper()
                
                if command == 'PASS':
                    user_details["password"] = words[1].strip()

                elif command == 'NICK':
                    user_details["nick"] = words[1].strip()

                elif command == 'USER':
                    this.run_USER_Command(words, user_details, message)

                elif command == 'CAP':
                    this.print_To_Server(user_details, "user set the permisions", "sent")

                elif command == 'JOIN':
                    this.run_JOIN_Command(words, user_details)
                    
                elif command == 'PART':
                    this.print_To_Server(user_details, "user left channel ____", "sent")
                
                elif command == 'QUIT':
                    this.run_QUIT_Command(words, user_details, message)
                    #breaks listening for the specific user  (thread)
                    break
                            
                elif command == 'LIST':
                    this.run_LIST_Command(user_details)

                elif command == 'NAMES':
                    this.run_NAMES_Command(words, user_details)

                elif command == 'PRIVMSG':
                    this.run_PRIVMSG_Command(words, user_details, message, addr)
                
                elif command == 'TOPIC':
                    this.run_TOPIC_Command(user_details, message)
                
                elif command == 'PONG':
                    this.run_PONG_Command(user_details, message) 

                elif command == 'PING':
                    this.run_PING_Command(user_details, message)

                elif command == "WHO":
                    this.run_WHO_Command(user_details, message)

                elif command == "MODE":
                    this.run_MODE_Command(user_details, message)
                
                else:
                    this.print_To_Server(user_details, f"{message}", "recieve")
                    message_text = f"invalid command sent please use from this list of commands (PASS, NICK, USER, CAP, JOIN, PART, QUIT, LIST, NAMES, PRIVMSG, TOPIC, PONG, PING, WHO, MODE)"
                    this.print_To_Server(user_details, message_text, "recieve")
                    this.safe_Send(user_details['user'], f":{user_details['nick']}!{user_details['username']}@{addr[0]} PRIVMSG {user_details['nick']} :{message_text}\r\n")
                
                # Checks that the user info is enough to be registered to the users list.
                # Has the user_details stored in a local dictionary but not with the full details guaraneteed and should make sure all data is verified before finish.
                if user_details["nick"] and user_details["username"] and not user_details["registered"]:
                    this.register_User(user_details)
                # Tell the que that the current task is done    
                user_queue.task_done()

    def run_USER_Command(this, words, user_details, message):
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
    
    def run_PING_Command(this, user_details, message):
        # Current time when PING is received
        received_time = time.time()
        
        command, *parameters = message.split()
        if command.upper() != "PING":
            return
        
        # Extract the LAG identifier if present
        lag_identifier = parameters[0] if parameters else None
        
        pong_response = f'PONG {lag_identifier}\r\n' if lag_identifier else 'PONG\r\n'
        this.safe_Send(user_details['user'], pong_response)     

    def run_WHO_Command(this, user_details, message):
        parameters = message.split()[1:]
        channel = parameters[0] if parameters else '*'
        
        user_list = []  
        for username in this.users:
            user_list.append(username)
        
        for user in user_list:
            who_response = f"352 {user_details['nick']} {channel} {user_details['username']} {user_details['hostname']} {user_details['servername']} {user_details['nick']} H :0 {user_details['realname']}"
            this.safe_Send(user_details['user'],who_response + '\r\n' )
        
        end_response = f"315 {user_details['nick']} {channel} :End of WHO list"
        this.safe_Send(user_details['user'], end_response + '\r\n')
    
    def run_MODE_Command(this, user_details, message):
        params = message.split()[1:]
        target = params[0]
        modes = params[1] if len(params) > 1 else None
        mode_params = params[2:] if len(params) > 2 else None
        
        if target.startswith("#"):
            #this is where we would do channel modes
            pass
        elif target == user_details['nick']:
            # this is where you would do user modes
            pass
        
        #detailed response based on what mode was sent and if there were perams sent needs the if then because params are not always send in MODE commands
        mode_response = f":{user_details['nick']}!{user_details['username']}@{user_details['hostname']} MODE {target} {modes} {' '.join(mode_params) if mode_params else ''}"
        this.safe_Send(user_details['user'], mode_response + '\r\n')
    
    def run_TOPIC_Command(this, user_details, message):
        params = message.split()[1:]
        channel_name = params[0]
        new_topic = ' '.join(params[1:])

        if channel_name in this.channels:
            this.channels[channel_name]["topic"] = new_topic
            topic_response = f":{user_details['nick']}!{user_details['username']}@{user_details['hostname']} TOPIC {channel_name} :{new_topic}"
            this.safe_Send(user_details['user'], topic_response)
        else:
            # there might be an IRC code to let the sender know this
            this.safe_Send(user_details['user'], "That channel does not exist so you can't set the topic")

    def run_JOIN_Command(this, words, user_details):
        channel_name = words[1].strip()
        # Create the channel if it does not exist
        if channel_name not in this.channels:
            this.channels[channel_name] = {"users": [], "topic": ""}
        
        # Add the user to the channel
        this.channels[channel_name]["users"].append(user_details)

        this.print_To_Server(user_details, f"User {user_details['nick']} joined channel {channel_name}" , "sent")

        #Building the names list for the 353 command to be sent to each user
        names_list = " ".join([u['nick'] for u in this.channels[channel_name]["users"]])

        # Broadcast to the other users of that server that the client has JOINed
        # This happens regularly and needs to be able to be sent more often using the LIST command I think
        for channel_user in this.channels[channel_name]["users"]:
            this.safe_Send(channel_user['user'], f":{user_details['nick']}!{user_details['username']}@{addr[0]} JOIN {channel_name}\r\n")

            this.safe_Send(channel_user['user'], f":{user_details['hostname']} 331 {user_details['nick']} {channel_name} :No Topic is set\r\n")
            #This is where you send the name list info
            this.safe_Send(channel_user['user'], f":{user_details['hostname']} 353 {user_details['nick']} = {channel_name} :{names_list}\r\n")
            #This is where you tell the client that you are at the end of the names list
            this.safe_Send(channel_user['user'], f":{user_details['hostname']} 366 {user_details['nick']} {channel_name} :End of names list\r\n")

    def run_QUIT_Command(this, words, user_details, message):
        # Parse optional quit message then split it from the command word
        optional_message = ''
        if len(words) > 1:
            optional_message = message.split(" ", 1)[1].strip()

        # Broadcast quit message to all the users channels
        for channel_name, channel_info in this.channels.items():
            channel_users = channel_info["users"]
            if user_details in channel_users:
                for channel_user in channel_users:
                    this.safe_Send(channel_user['user'], f":{user_details['nick']}!{user_details['username']}@{addr[0]} QUIT :{optional_message}\r\n")
                # Remove the user from this channel
                channel_users.remove(user_details)

        # Remove user from the users list
        this.users.remove(user_details)

        # Close the socket
        user_details['user'].close()
        this.print_To_Server(user_details, f"user has quit. Message: {optional_message}", "sent")
    
    def run_LIST_Command(this, user_details):
        # To hold the number of users in each channel
        num_users_in_channel = 0
        
        # Loop through each channel in the 'this.channels' dictionary
        for channel_name, channel_info in this.channels.items():
            channel_users = channel_info["users"]
            # Count the number of users in the channel
            num_users_in_channel = len(channel_users)
            
            # Send the 322 numeric reply back to the client for each channel
            this.safe_Send(user_details['user'], f":{user_details['hostname']} 322 {user_details['nick']} {channel_name} {num_users_in_channel} :\r\n")
            this.print_To_Server(user_details, f":{user_details['hostname']} 322 {user_details['nick']} {channel_name} {num_users_in_channel} :", "sent")

        # Send the 'End of LIST' 323 numeric reply to the client
        this.safe_Send(user_details['user'], f":{user_details['hostname']} 323 {user_details['nick']} :End of LIST\r\n")
        this.print_To_Server(user_details, f":{user_details['hostname']} 323 {user_details['nick']} :End of LIST\r\n", "sent")
    
    def run_NAMES_Command(this, words, user_details):
        # If there is a channel name
        if len(words) > 1:
            channel_name = words[1].strip()
            
            # check to see if it exist
            if channel_name in this.channels:
                # find the names
                names_list = ""
                for u in this.channels[channel_name]["users"]:
                    if names_list:  # if names_list is not empty, add a space before the next nickname
                        names_list += " "
                    names_list += u['nick']
                
                
                # Send the 353 send the info to the client
                this.safe_Send(user_details['user'], f":{user_details['hostname']} 353 {user_details['nick']} = {channel_name} :{names_list}\r\n")
                
                # Send the 366 send end of names to the client
                this.safe_Send(user_details['user'], f":{user_details['hostname']} 366 {user_details['nick']} {channel_name} :End of NAMES list\r\n")
                
        else:  # If no channel name is provided, list names for all channels
            for channel_name, channel_info in this.channels.items():
                channel_users = channel_info["users"]
                # Build the names list
                names_list = " ".join([u['nick'] for u in channel_users])
                
                
                # Send the 353 numeric reply
                this.safe_Send(user_details['user'], f":{user_details['hostname']} 353 {user_details['nick']} = {channel_name} :{names_list}\r\n")
                
                # Send the 366 numeric reply to indicate the end of the list
                this.safe_Send(user_details['user'], f":{user_details['hostname']} 366 {user_details['nick']} {channel_name} :End of NAMES list\r\n")

    def run_PRIVMSG_Command(this, words, user_details, message, addr):
        # Takes the target, which could be a  channel or a nickname to be used to send to the right client
        target = words[1]  
        #Gets the message from the split using the : and then strips the info after it
        message_text = message.split(":", 1)[1].strip()  

        # Check to see if it's a channel
        if target.startswith("#"):
            if target in this.channels:  # Make sure channel exists
                # Send the message to all users in the channel
                for channel_user in this.channels[target]["users"]:
                    # however you don't want to send the message twice so you need to exclude yourself as a channel_user from the channels list
                    if channel_user['addr'] != addr:
                        this.safe_Send(channel_user['user'], f":{user_details['nick']}!{user_details['username']}@{addr[0]} PRIVMSG {target} :{message_text}\r\n")
                    
        # If the target is a nickname
        else:
            # Send the message to the user with the target nickname
            for user in this.users:
                if user['nick'] == target:
                    this.safe_Send(user['user'], f":{user_details['nick']}!{user_details['username']}@{addr[0]} PRIVMSG {target} :{message_text}\r\n")
                    break 
        #Logs the message to the Server in the correct way
        this.print_To_Server(user_details, f"Message sent to {target}", "sent")

    def run_PONG_Command(this, user_details, message):
        user_details['last_msg_timestamp'] = time.time()

        this.print_To_Server(user_details, f"Received: {message}", "received")
        outgoing_message = f"PONG : 0\r\n"
        this.print_To_Server(user_details, f"Sending: {outgoing_message}", "sent")
        this.safe_Send(user_details['user'], outgoing_message)

    def print_To_Server(this, user_details, message, dir):
        addr_header_send = f"[{user_details['addr'][0]}:{user_details['addr'][1]}] <- b'"
        addr_header_recieve = f"[{user_details['addr'][0]}:{user_details['addr'][1]}] -> b'"
        if (dir == "sent"):
            print(f"{addr_header_send} {message}")
        else:
            print(f"{addr_header_recieve} {message}")

    def register_User(this, user_details):
        # Update registered = True
        user_details["registered"] = True
        # Send welcome message etc. as per IRC 002
        this.print_To_Server(user_details, f":{user_details['hostname']} 001 {user_details['nick']} :Hi, welcome to IRC.", "sent")
        this.safe_Send(user_details['user'], f":{user_details['hostname']} 001 {user_details['nick']} :Hi, welcome to IRC.\r\n")
        # Send version number per 002
        this.print_To_Server(user_details, f"{user_details['hostname']} 002 {user_details['nick']} :Your host is {user_details['hostname']} running version Group 7 IRC 1.0", "sent")
        this.safe_Send(user_details['user'], f":{user_details['hostname']} 002 {user_details['nick']} :Your host is {user_details['hostname']} running version Group 7 IRC 1.0\r\n")
        # Send Server created time per 003
        this.print_To_Server(user_details, f":{user_details['hostname']} 003 {user_details['nick']} :This server was created sometime", "sent")
        this.safe_Send(user_details['user'], f":{user_details['hostname']} 003 {user_details['nick']} :This server was created sometime\r\n")
        # Send connection successfull 004
        this.print_To_Server(user_details, f":{user_details['hostname']} 004 {user_details['nick']} {user_details['hostname']} Group 7 IRC 1.0 :", "sent")
        this.safe_Send(user_details['user'], f":{user_details['hostname']} 004 {user_details['nick']} {user_details['hostname']} Group 7 IRC 1.0\r\n")
        count = 0
        for user_details in this.users:
            count += 1
        #This needs to be updated with the proper number of users.
        this.print_To_Server(user_details, f":{user_details['hostname']} 251 {user_details['nick']} :There are {count} users and 0 services on 1 server", "sent")
        this.safe_Send(user_details['user'], f":{user_details['hostname']} 251 {user_details['nick']} :There are {count} users and 0 services on 1 server\r\n")

        #this needs to be updated to not be hardcoded this will be done when you can set the Message of The Day
        this.print_To_Server(user_details, f":{user_details['hostname']} 422 {user_details['nick']} :MOTD File is missing", "sent")
        this.safe_Send(user_details['user'], f":{user_details['hostname']} 422 {user_details['nick']} :MOTD File is missing\r\n")

    def safe_Send(this, socket, message):
        try:
            if isinstance(message, str):
                message = message.encode('ascii')
            socket.send(message)
        except (BrokenPipeError, ConnectionResetError, OSError):
            print("Client disconnected unexpectedly.")
# creates the new instance of the server, and launches it
server = Server(addr, port)
server.launch()