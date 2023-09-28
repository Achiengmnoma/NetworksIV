import socket

class Server:
    def __init__(self, address, port):
        self.server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.users = []
        self.nicknames = []
        self.address = address
        self.port = port

    def start(self):
        self.server.bind((self.address, self.port))
        self.server.listen()
        print(f"Server is listening on {self.address}:{self.port}...")

        while True:
            user, address = self.server.accept()
            print(f"Connected with {str(address)}")

            user.send('NICK'.encode('ascii'))
            nickname = user.recv(1024).decode('ascii')

            if nickname in self.nicknames:
                user.send("Please choose a unique username".encode('ascii'))
                user.close()
                continue

            self.nicknames.append(nickname)
            self.users.append(user)

            print(f'User nickname is {nickname}!')
            self.broadcast(f'{nickname} joined the chat!'.encode('ascii'))
            user.send('Connected!'.encode('ascii'))

    def broadcast(self, message):
        for user in self.users:
            user.send(message)

    def handle(self, user):
        while True:
            try:
                message = user.recv(1024)
                if not message:
                    index = self.users.index(user)
                    nickname = self.nicknames[index]
                    self.broadcast(f'{nickname} left the chat!'.encode('ascii'))
                    self.nicknames.remove(nickname)
                    self.users.remove(user)
                    user.close()
                    break
                self.broadcast(message)
            except Exception as e:
                print(f"An error occurred :(): {str(e)}")
                break

if __name__ == "__main__":
    address = '::1'
    port = 6667
    server = Server(address, port)
    server.start()