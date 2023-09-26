import socket
import threading

nickname = "Bot Bob"
bobWMsg = "A welcome message from Bob: Hello everyone, my name is Bot Bob. Please send me messages, and I will reply with utterly random nonsense!"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))

# Send the bot's nickname and greeting message when it connects
client.send(nickname.encode('ascii'))

def receive():
    first_message_received = False
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            if message:
                if not first_message_received:
                    first_message_received = True
                    continue
                # Check if the message starts with the bot's nickname
                if message.startswith(nickname):
                    print(message)  # Print bot's messages
                else:
                    print(f"Server: {message}\n")  # Print server messages
        except:
            client.close()
            break
        break


def write():
    while True:
        message = input("")
        client.send(f'{nickname}: {message}'.encode('ascii'))


receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()

client.send(bobWMsg.encode('ascii') + b'\n')
