# Group 7:
# Adam Smith (2449898)
# Celeste Artley (2600927)
# Daniel Niven (2481553)
# Stacy Onyango (2437819)
# Ross Mcbride (r.s.z.mcbride)


import socket
import random
import re
import argparse

parser = argparse.ArgumentParser(description='IRC bot for Networking')
parser.add_argument('--host', type=str, help='Specify the host address')
parser.add_argument('--port', type=int, help='Specify the port number')
parser.add_argument('--name', type=str, help='Specify the name of the bot')
parser.add_argument('--channel', type=str, help='Specify the channel for the bot')
args = parser.parse_args()

nick = args.name if args.name else 'SuperBot'
user = "ROBOT 0 * :Robot Junior"
cap = "CAP LS 302"
addr = args.host if args.host else '::1'
port = args.port if args.port else 6667
channel = args.channel if args.channel else '#Bot_Commands'

#creating a socket object
server = socket.socket()
# defines the botUsers class, in which the bot operations are executed
class botUsers:

    def __init__(bot,nick,cap,addr,port):
        # socket connection, using IPv6
        bot.server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

        # assigns the correct values to the nickname, addr, and port variables of the object
        bot.nick = nick
        bot.user = user
        bot.cap = cap
        bot.addr = addr
        bot.port = port
        bot.channel = channel
        bot.has_created_channel = False

        #opens a file and reads in content,then store it lines of text in a list
        with open('bot.txt', encoding='utf8') as f:
            bot.botTxts = [line.rstrip('\n') for line in f]
       
    def createBotChannel(server, message):
        bot.server.send(bytes(f"JOIN {bot.channel}\r\n", "ascii"))

    def listeningFor(bot, message):
        channel = f"{bot.channel}"
        # What commands the bot is listening in for in the default(#Bot_Commands) chat.
        if message.find(f'PRIVMSG {channel} :!hello') != -1 or message.find(f'PRIVMSG {channel} :!hello') > 5:
            bot.server.send(f'PRIVMSG {channel} :Hi, how are you?\r\n'.encode("ascii"))  

        if message.find(f'PRIVMSG {channel} :!list') != -1 or message.find(f'PRIVMSG {channel} :!list') > 5:
            bot.server.send(f'LIST\r\n'.encode('ascii'))
            message = bot.server.recv(1024).decode('ascii')
            parsedmessage = re.findall(r'#\w+', message)
            bot.server.send(f'PRIVMSG {channel} :{parsedmessage}\r\n'.encode("ascii"))
            bot.server.send(f'PRIVMSG {channel} :List of channels displayed!\r\n'.encode("ascii"))

        if message.find(f'PRIVMSG {channel} :!slap') != -1:
            sent_user = ''
             # Extract sender's username from the message
            colon_pos = message.find(':')
            exclamation_pos = message.find('!')
            if colon_pos != -1 and exclamation_pos != -1:
                sent_user = message[colon_pos+1:exclamation_pos]
            
            target_username = message.split('!slap')[1].strip() if '!slap' in message else None

            bot.server.send(f'NAMES\r\n'.encode('ascii'))
            list_response = bot.server.recv(1024).decode('ascii')

            nick_list = []

            lines = list_response.split('\r\n')

            for line in lines:
                print(f"line: {line}")
                # Only process lines that contain the '353' code as they contain usernames
                if ' 353 ' in line:
                    # Find the position of the last colon, which precedes the list of usernames
                    last_colon_pos = line.rfind(':')
                    
                    # Extract and split the usernames
                    usernames = line[last_colon_pos + 1:].strip().split(' ')
                    nick_list.extend(usernames)

            if target_username:
                bot.SlapUser(target_username)
            else:
                bot.SlapRandom(nick_list, sent_user)

        if message.find(f'PRIVMSG {bot.nick} :') != -1: 
            colon_pos = message.find(':')
            exclamation_pos = message.find('!')
            if colon_pos != -1 and exclamation_pos != -1:
                sent_user = message[colon_pos+1:exclamation_pos]
            
            bot.sendFacts(sent_user) 

    def sendFacts(bot,user):
        text = random.choice(bot.botTxts)
        print("sending fact to the user")
        bot.server.send(f'PRIVMSG {user} : {text}\r\n'.encode("ascii"))
        
    def removeUser(bot,nick,channel):
        nicks = []
        if nick in bot.nicks:
            nicks.remove(nick)

        bot.server.send(f"KICK {nick} from {channel} channel".encode())  

    def join(bot,nick,channel):
        try:
            nicks = []
            if nick not in bot.nicks:
                nicks.append(nick)
            bot.server.send(f"JOIN {channel}\r\n".encode())
        except:
            print("Cannot join the channel")

    def SlapRandom(bot, nick_list,sent_user):
        random_user = f"{bot.nick}"
        if len(nick_list) > 2:
            while random_user == sent_user or random_user == f"{bot.nick}":
                random_user = random.choice(nick_list)
            
            bot.server.send(f'PRIVMSG {bot.channel} : {bot.nick} slaps {random_user} around a bit with a large trout\r\n'.encode("ascii"))
        else:
            bot.server.send(f'PRIVMSG {bot.channel} : {bot.nick} slaps {sent_user} around a bit with a large trout. Next time make sure there is someone else to slap!\r\n'.encode("ascii"))
            
    def SlapUser(bot, targetname):
        bot.server.send(f'PRIVMSG {bot.channel} : {bot.nick} slaps {targetname} around a bit with a large trout\r\n'.encode("ascii"))

    def SlapSender(username):
        # username is the name of the user who sent the message
        data = "{bot.nick} slaps {} around a bit with a large trout".format(username)
        bot.server.send(data.encode())
 
    def launch(bot):

        # connects the socket object to the addr address and port
        bot.server.connect((bot.addr, bot.port))

        # displays that the bot is attempting to connect to the server
        print ("Looking up " + str(bot.addr))
        print ("Connecting to " + str(bot.addr) + ":" + str(bot.port))

        #sends the PASS USER and NICK and welcome message to the server
        bot.server.send(bytes(f"PASS Test1234\r\n", "ascii"))
        bot.server.send(bytes(f"USER {bot.nick} ThisPC ThisServer :{bot.nick}\r\n", "ascii"))
        bot.server.send(bytes(f"NICK {bot.nick}\r\n", "ascii"))
        
        #displays that the bot has connected, and maintains the connecion
        while True:
            message = bot.server.recv(1024).decode('ascii')
            print(f"Received: {message}")
            if message.startswith("PING"):
                pong_response = "PONG :" + message.split(":")[1] + "\r\n"
                bot.server.send(bytes(pong_response, "ascii"))
                
            # 004 is a common numeric for successful registration
            if "004" in message:  
                if not bot.has_created_channel:
                    print("Creating bot channel")
                    bot.createBotChannel(message)
                    bot.has_created_channel = True

            else:
                bot.listeningFor(message)

    def write(bot):
        while True:
            message = input("")
            bot.server.send(f'{bot.nick}: {message}'.encode('ascii'))

bot = botUsers(nick, cap, addr, port)
bot.launch()