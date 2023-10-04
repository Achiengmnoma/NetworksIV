def messages():
    if message.find(f'PRIVMSG {channel} :!hello') != -1 or message.find(f'PRIVMSG {channel} :!hello') > 5:
        bot.server.send(bytes(f'PRIVMSG {channel} :Hi, how are you?\n', "ascii"))
