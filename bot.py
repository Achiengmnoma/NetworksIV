from time import sleep
import socket
import random
from datetime import datetime
import atexit

botServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#defin
class botUsers:
    def __init__(self,channel,nicknames,host,port):
        self.channel = channel(channel)
        self.nicknames = nicknames
        self.host = host
        self.port = port


#Initiate a connection to the server
    def connect_bot_server(self):
        try:
            botServer.connect((self.host,self.port))    
        except:
            print("Server connection error")    

#Requesting for a coonnection to the server
    def server_response(self):
        try:
            response = botServer.recv(1024)
            if not response:
                    raise Exception("No data received")
            print("Response received:", response.decode("utf-8"))
        except Exception as e:
            print("Error receiving data:", e)
    
#this is incomplete 
    def joinChannel(self):
        self.channel.channelName = ""
        
        #a new channel is created here

    def commands(self,command):
        try:
            if command == "JOIN" :
                self.joinChannel()
            # # if command == "" :
            # #     self.arguments = ""   

        except:
            print("Argument cannnot be retrieved at this time")




class channel:
    def __init__(self,channelName,channelTopic):
        self.channelName = [] 


