import socket
import thread
import threading
import struct

class serverHandler(threading.Thread):
	def __init__(self, mom, sock, serverid):
		threading.Thread.__init__(self)
		self.mom = mom
		self.sock = sock
		self.serverid = serverid
		self.clients = {}
		self.message = ['']
		self.sendMessage(0,'asdqwe12');
		self.freeId = []
		self.maxId = 1
		
	def sendMessage(self, cmd, sender, msg = None):
		message = ''
		message += chr(cmd)
		message += sender
		if cmd != 212:
			try:
				self.sock.send(message)
			except Exception:
				return
			return
		
		length = len(msg)
		if length < 255:
			message += chr(length)
		else:
			message += chr(255)
			l = struct.pack(">H", length)
			message += l
		message += msg
		try:
			self.sock.send(message)
		except Exception:
			return

	def addClient(self, cHandler):
		#create id
		print "processing...\n"
		cid = 0;
		if len(self.freeId) == 0:
			cid = self.maxId
			self.maxId += 1
		else:
			cid = self.freeId[0]
			self.freeId.remove(cid)
		if cid > 65535:
			return False
		cid = struct.pack(">H", cid)
		cHandler.clientId = cid
		self.clients[cid] = cHandler
		self.sendMessage(12, cid)
		return True
	
	def onMessage(self, reciver, msg):
		if self.clients.has_key(reciver):
			try:
				self.clients[reciver].sendMessage(msg);
			except Exception:
				return

	def decodeMsg(self, data):
		if len(self.message) != 3:
			self.message[0] += data
			data = self.message[0]
			lid = len(data)
			if lid < 3: # data => cmd(1byte) + addr(2byte)
				return
			
			cmd = ord(data[0])
			addr = data[1:3]
			
			if cmd == 136: # close its self
				self.close()
				self.message = ['']
				return
			elif cmd == 12: # add client
				#do somethings
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

	def removeClient(self, clientId):
		print 'removing'
		del self.clients[clientId]
		self.sendMessage(21, clientId)
	
	def close(self):
		for c_t in self.clients.values():
			c_t.sock.close()
		self.sock.close()
		del self.mom.servers[self.serverid]
	
	def run(self):
		while True:
			try:
				data = self.sock.recv(1024)
				if data:
					self.decodeMsg(data)
				else:
					self.close()
					print "closing"
					break
			except Exception:
				print "some thing error"
				self.close()
				break

class clientHandler (threading.Thread):
	def __init__(self, sock, sHandler):
		threading.Thread.__init__(self)
		self.sock = sock
		self.sHandler = sHandler
		self.clientId = None
	def onMessage(self, msg):
		self.sHandler.sendMessage(212, self.clientId, msg)
	
	def sendMessage(self, msg):
		self.sock.send(msg)
	
	def close(self):
		self.sHandler.removeClient(self.clientId)
		self.sock.close()
	
	def run(self):
		while True:
			try:
				data = self.sock.recv(1024)
				if data:
					self.onMessage(data)
				else:
					self.close()
					print "client closing"
					break
			except Exception:
				print "client error"
				self.close()
				break

class motherSVR:
	def __init__(self, ip, port):
		self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.server_socket.bind((ip, port))
		self.server_socket.listen(10)
		self.servers = {}
		self.listAPI = {'ghuvrons':['gg104986', 'ppmttphq']}
		
	def handsacking(self, sock):
		try:
			req = sock.recv(1024)
			sock.setblocking(1)
			serverid = req[:8]
			key = req[8:16]
			if self.listAPI.has_key(serverid):
				if key == self.listAPI[serverid][0] and not self.servers.has_key(serverid):
					thread = serverHandler(self, sock, serverid)
					self.servers[serverid] = thread
					thread.start()
					print "new server"
					return True
				elif key == self.listAPI[serverid][1]:
					if self.servers.has_key(serverid):
						thread = clientHandler(sock, self.servers[serverid])
						if self.servers[serverid].addClient(thread):
							
							print "new client"
							thread.start()
						return True
					else:
						return False
		except socket.timeout, e:
			print e
		sock.close()
		return False
	def run(self):
		while True:
			sock, addr = self.server_socket.accept()
			thread.start_new_thread( self.handsacking, (sock, ) )
			
	def close(self):
		self.server_socket.close()

if __name__ == "__main__":
    ws = motherSVR("0.0.0.0",5001)
    ws.run()
    ws.close()