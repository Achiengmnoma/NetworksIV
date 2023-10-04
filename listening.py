def createBotChannel(server):
    channel = "Bot_Commands"
    server.send(f"JOIN #{channel}\r\n".encode("ascii"))

def listeningFor(server, message):
    channel = "Bot_Commands"
    if message.find(f'PRIVMSG {channel} :!hello') != -1 or message.find(f'PRIVMSG {channel} :!hello') > 5:
        server.send(f'PRIVMSG {channel} :Hi, how are you?\r\n'.encode("ascii"))
