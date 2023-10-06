def createBotChannel(server, message):
    channel = "#Bot_Commands"
    server.send(bytes(f"JOIN {channel}\r\n", "ascii"))

def listeningFor(server, message):
    channel = "#Bot_Commands"
    if message.find(f'PRIVMSG {channel} :!hello') != -1 or message.find(f'PRIVMSG {channel} :!hello') > 5:
        server.send(f'PRIVMSG {channel} :Hi, how are you?\r\n'.encode("ascii"))


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