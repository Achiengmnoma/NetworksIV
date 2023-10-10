# Group 7:
# Adam Smith (2449898)
# Celeste Artley (2600927)
# Daniel Niven (2481553)
# Stacy Onyango (2437819)
# Ross Mcbride (r.s.z.mcbride)


import socket
import random

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

        #opens a file and reads in content,then store it lines of text in a list
        with open('bot.txt', encoding='utf8') as f:
            bot.botTxts = [line.rstrip('\n') for line in f]
       
    def createBotChannel(server, message):
        channel = "#Bot_Commands"
        bot.server.send(bytes(f"JOIN {channel}\r\n", "ascii"))

    def listeningFor(message):
        channel = "#Bot_Commands"
        # What commands the bot is listening in for in the #Bot_Commands chat.
        if message.find(f'PRIVMSG {channel} :!hello') != -1 or message.find(f'PRIVMSG {channel} :!hello') > 5:
            bot.server.send(f'PRIVMSG {channel} :Hi, how are you?\r\n'.encode("ascii"))
    

    #send random facts to a user
    def sendFacts(bot,user):
       bot.PRIVMSG(user,random.choice(bot.botTxts))
        
    #sends the KICK command to the server  
    def removeUser(bot,nick,channel):
        nicks = []
        if nick in bot.nicks:
            nicks.remove(nick)

        bot.server.send(f"KICK {nick} from {channel} channel".encode())  

    #sends the join channels
    def join(bot,nick,channel):
        try:
            nicks = []
            if nick not in bot.nicks:
                nicks.append(nick)
            bot.server.send(f"JOIN {channel}\r\n".encode())
        except:
            print("Cannot join the channel")


    # !slap (slapping a random user in the channel with a trout excluding the bot and the user sending it)
    def SlapRandom(bot,username,nick):
        # nicks = []
        x = len(nick)
        # username is the name of the user who sent the message
        if x == 0:
        # checks the length of the array of nicknames and stores it in x
        # x = len(nicks)
        # y = random.randrange(0, x)
        # if x == 1:
            print("Error do not have a person")
        # error message
        else:
            y = random.randrange(0,x)
            if nick[y] == username:
                print("Cannot slap user(self)")
            else:
                data = "SuperBot slaps {} around a bit with a large trout".format(nick[y])
                bot.server.send(data.encode())
        # elif nicks[y] == username:
        #     SlapRandom(bot,username) the recursive function was giving not defined
        

    # !slap (slap a specific user)
    def SlapUser(targetname):
        # targetname is the name of the user to be slapped
        data = "SuperBot slaps {} around a bit with a large trout".format(targetname)
        bot.server.send(data.encode())


    # !slap (slapping the user sending it if that user is not in the channel)
    def SlapSender(username):
        # username is the name of the user who sent the message
        data = "SuperBot slaps {} around a bit with a large trout".format(username)
        bot.server.send(data.encode())
 
    def launch(bot):

        # connects the socket object to the addr address and port
        bot.server.connect((bot.addr, bot.port))

        # displays that the bot is attempting to connect to the server
        print ("Looking up " + str(bot.addr))
        print ("Connecting to " + str(bot.addr) + ":" + str(bot.port))

        # sends the PASS USER and NICK and welcome message to the server
        bot.server.send(bytes("PASS Test1234\r\n", "ascii"))
        bot.server.send(bytes("USER SuperBot ThisPC ThisServer :SuperBot\r\n", "ascii"))
        bot.server.send(bytes("NICK SuperBot\r\n", "ascii"))
        
        #displays that the bot has connected, and maintains the connecion
        while True:
            message = bot.server.recv(1024).decode('ascii')
            print(f"Received: {message}")
            if message.startswith("PING"):
                pong_response = "PONG :" + message.split(":")[1] + "\r\n"
                bot.server.send(bytes(pong_response, "ascii"))

            if "004" in message:  # 004 is a common numeric for successful registration
                print(bot.has_created_channel)
                if not bot.has_created_channel:
                    print("Creating bot channel")
                    bot.createBotChannel(message)
                    bot.has_created_channel = True
   
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
                bot.listeningFor(message)
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