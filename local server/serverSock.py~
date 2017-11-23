import socket
import sys
import struct

class clientSock():
	def __init__(self, clientId, sSock):
		self.clientId = clientId
		self.sSock = sSock
	def send(self, msg):
		self.sSock.sendMessage(212, self.clientId, msg)
	def onMessage(self, msg):
		print msg
	def close(self):
		self.sSock.sendMessage(21, self.clientId)
		del self.sSock.clients[self.clientId]
		
class serverSock():
	def __init__(self, serverIP, serverPort, serverId):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_address = (serverIP, serverPort)
		self.sock.connect(server_address)
		self.sock.send(serverId)
		print self.sock.recv(45)
		self.message = ['']
		self.clients = {}
		self.clientClass = clientSock
	def setClientClass(self, clientClass):
		self.clientClass = clientClass
	def sendMessage(self, cmd, addr, msg):
		message = ''
		message += chr(cmd)
		message += addr
		if cmd != 212:
			self.sock.send(message)
			return
		
		length = len(msg)
		if length < 255:
			message += chr(length)
		else:
			message += chr(255)
			l = struct.pack(">H", length)
			message += l
		message += msg
		self.sock.send(message)
	def addClient(self, clientID):
		print "new client"
		cSock = self.clientClass(clientID, self)
		self.clients[clientID] = cSock

	def removeClient(self, addr):
		print "close client"
		cSock = self.clients[addr]
		del self.clients[addr]
		del cSock
		
	def onMessage(self, addr, msg):
		if self.clients.has_key(addr):
			cSock = self.clients[addr]
			cSock.onMessage(msg)
	
	def decodeMsg(self, data):
		if len(self.message) != 3:
			self.message[0] += data
			data = self.message[0]
			lid = len(data)
			if lid < 3: # data => cmd(1byte) + addr(2byte)
				return
			
			cmd = ord(data[0])
			addr = data[1:3]
			#print [ord(m) for m in data]
			
			if cmd == 136: # close its self
				self.close()
				self.message = ['']
				return
			elif cmd == 12: # add client
				#do somethings
				self.addClient(addr)
				self.message = ['']
				return
			elif cmd == 21: # close client
				self.removeClient(addr)
				self.message = ['']
				return
			elif cmd == 212: # message to client
				pass

			if lid < 4: 
				return
			datalength = ord(data[3])

			data_index = 4
			if datalength == 255:
				if lid < 6:
					return
				data_index = 6
				datalength = struct.unpack(">H", data[4:6])[0]
			self.message = [datalength, addr, data[data_index:]]
		else:
			self.message[2] += data
		
		if len(self.message[2]) < self.message[0]:
			return
		
		self.onMessage(self.message[1], self.message[2][:self.message[0]])
		if self.message[2][self.message[0]:] == '':
			self.message = ['']
		else:
			data = self.message[2][self.message[0]:]
			self.message = ['']
			self.decodeMsg(data)
	
	def run(self):
		while True:
			data = self.sock.recv(1024)
			if data:
				self.decodeMsg(data)
			else:
				self.close()
				print "closing"
				break
	
	def close(self):
		self.sock.close()
		