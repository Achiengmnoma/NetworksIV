def createBotChannel(server, message):
    channel = "#Bot_Commands"
    server.send(bytes(f"JOIN {channel}\r\n", "ascii"))

def listeningFor(server, message):
    channel = "#Bot_Commands"
    if message.find(f'PRIVMSG {channel} :!hello') != -1 or message.find(f'PRIVMSG {channel} :!hello') > 5:
        server.send(f'PRIVMSG {channel} :Hi, how are you?\r\n'.encode("ascii"))
