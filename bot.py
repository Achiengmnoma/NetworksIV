# Group 7:
# Adam Smith (2449898)
# Daniel Niven (2481553)
# Stacy Onyango (2437819)
# Ross Mcbride (r.s.z.mcbride)

import socket
from listening import createBotChannel, listeningFor

# set the correct values for the nickname, address, and port
nick = "SuperBot"
user = "ROBOT 0 * :Robot Junior"
cap = "CAP LS 302"
addr = "::1"
port = 6667

# a welcome message, that is displayed to all clients when the bot joins
bobWMsg = "A welcome message from Bob: Hello everyone, my name is Bot Bob. Please send me messages, and I will reply with utterly random nonsense!"
#creating a socket object
server = socket.socket()
# defines the botUsers class, in which the bot operations are executed
class botUsers:

    # creates the instance of the botUsers object, and instantiates the variables

    def __init__(bot,nick,cap,addr,port):


        # socket connection, using IPv6
        bot.server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        

        # assigns the correct values to the nickname, addr, and port variables of the object
        bot.nick = nick
        bot.user = user
        bot.cap = cap
        bot.addr = addr
        bot.port = port
        bot.has_created_channel = False
        


    def launch(bot):

        # connects the socket object to the addr address and port
        bot.server.connect((bot.addr, bot.port))

        # displays that the bot is attempting to connect to the server
        print ("Looking up " + str(bot.addr))
        print ("Connecting to " + str(bot.addr) + ":" + str(bot.port))

        # sends the nickname and welcome message to the server
        bot.server.sendall(bytes("PASS Test1234\r\n", "ascii"))
        bot.server.sendall(bytes("USER SuperBot SuperBot SuperBot :SuperBot\r\n", "ascii"))
        bot.server.sendall(bytes("NICK SuperBot\r\n", "ascii"))
        # bot.server.send(bot.cap.encode('ascii') + b"\r\n")
        # bot.server.send(bot.nick.encode('ascii')+ b"\r\n")
        # bot.server.send(bot.user.encode('ascii')+ b"\r\n")

        #bot.nick = ''.join(bot.nick.split("NICK")[1].split("USER")[0])
        
        #displays that the bot has connected, and maintains the connecion
        while True:
            message = bot.server.recv(1024).decode('ascii')
            print(f"Received: {message}")
            if message.startswith("PING"):
                pong_response = "PONG :" + message.split(":")[1] + "\r\n"
                bot.sendall(bytes(pong_response, "ascii"))

            if "004" in message:  # 004 is a common numeric for successful registration
                if not bot.has_created_channel:
                    print("Creating bot channel")
                    createBotChannel(bot.server, message)
                    bot.has_created_channel = True
            
            elif "some_other_condition" in message:  # Replace with other server messages you want to handle
                # Do something else
                pass
            
            else:
                # Default handling of received messages
                print("Connected. Now logging in")
                bot.server.send(f'{bot.nick}: {message}'.encode('ascii'))

  

    #sends the join channels
    def join(bot,nick,channel):
        try:
            nicks = []
            if nick not in bot.nicks:
                nicks.append(nick)
            bot.server.send(f"JOIN {channel}\r\n".encode())
        except:
            print("Cannot join the channel")

     #sends the KICK command to the server  
    def removeUser(bot,nick,channel):
        nicks = []
        if nick in bot.nicks:
            nicks.remove(nick)

        bot.server.send(f"KICK {nick} from {channel} channel".encode())  

        
    #COMMANDS THEY ARE INCOMPLETE JUST PROVIDING A TEMPLATE OF HANDLING THEM
    #used to handle the different commands 
    def commands(option):
        if option == "JOIN":
            channelJoin = ""
            nick = ""
            bot.join(nick,channelJoin)
            print("Joining channels")    #more should be done for it to join channels

        #used to remove nicknames(user) from channels
        elif option == "KICK":
            nickname = ""
            channelname = ""
            bot.removeUser(nickname,channelname)  


   
    # receive function, which receives messages from other clients and will (eventually) respond to these
    def receive(bot):
        first_message_received = False

        # starts an infinite loop, so that the bot is always accepitng messages from other clients
        while True:
            try:
                # receives a message from another client
                message = bot.server.recv(1024).decode('ascii')
                print(f"Received from server: {message}")
                if message:
                    if not first_message_received:
                        first_message_received = True
                        continue

                    if message.startswith("PING"):
                        bot.server.send(f"PONG {message.split(':')[1]}".encode('ascii'))

                    # Check if the message starts with the bot's nickname
                    elif message.startswith(bot.nick):
                        print(message)  # Print bot's messages
                    else:
                        print(f"Server: {message}\n")  # Print server messages

                #listens for messages from the client and then does something respectivly
                listeningFor(bot.server, message)
            except Exception as e:
                print(f"An error occurred: {e}")
                bot.server.close()
                break

    # the write function, which enables the bot to send messages to other clients
    # still a work in progress, as the bot does not currently reply to clients messages
    def write(bot):
        while True:
            message = input("")
            bot.server.send(f'{bot.nick}: {message}'.encode('ascii'))

# creates the new instance of the bot, and launches it
bot = botUsers(nick, cap, addr, port)
bot.launch()