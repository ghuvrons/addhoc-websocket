from motherSVR import *
from hashlib import sha1
import base64

class momServer(motherSVR):
	def hashKey(self, key):
		guid = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
		combined = key + guid
		hashed = sha1(combined).digest()
		result = base64.b64encode(hashed)
		return result
	
	def handsacking(self, sock):
		req = sock.recv(1024)
		header_end = req.find("\r\n\r\n")
		if header_end != -1:
			header = req[:header_end]
			header_lines = header.split("\r\n")
			headers = {}
			for line in header_lines[1:]:
				key, value = line.split(": ")
				headers[key] = value
			
			serverid = headers["Sec-WebSocket-Protocol"][:8]
			key = headers["Sec-WebSocket-Protocol"][8:16]
			print serverid
			print key
			if self.listAPI.has_key(serverid) and key == self.listAPI[serverid][1] and self.servers.has_key(serverid):
				sock.send("HTTP/1.1 101 Web Socket Protocol Handshake\r\n")
				sock.send("Upgrade: WebSocket\r\n")
				sock.send("Connection: Upgrade\r\n")
				sock.send("Sec-WebSocket-Accept: %s\r\n" % self.hashKey(headers["Sec-WebSocket-Key"]))
				if headers.has_key("Sec-WebSocket-Protocol"):
					sock.send("Sec-WebSocket-Protocol: "+headers["Sec-WebSocket-Protocol"]+"\r\n")
				sock.send("Server: TestTest\r\n")
				sock.send("origin: http://localhost\r\n")
				sock.send("Access-Control-Allow-Credentials: true\r\n")
				sock.send("\r\n")
				
				thread = clientHandler(sock, self.servers[serverid])
				if self.servers[serverid].addClient(thread):
					print "new client"
					thread.start()
				return True
			else:
				sock.send("HTTP/1.1 400 Web Socket Protocol Handshake\r\n")
				sock.send("\r\n")
				sock.close()
				return False
		else:
			serverid = req[:8]
			key = req[8:16]
			if self.listAPI.has_key(serverid) and key == self.listAPI[serverid][0] and not self.servers.has_key(serverid):
				thread = serverHandler(self, sock, serverid)
				self.servers[serverid] = thread
				thread.start()
				print "new server"
				return True

if __name__ == "__main__":
	ws = momServer("0.0.0.0",5001)
	ws.run()
	ws.close()