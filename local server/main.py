from serverSock import *

class cSockHandler(clientSock):
	def __init__(self, clientId, sSock):
		clientSock.__init__(self, clientId, sSock)
		self.message = ['']
	def onMessage(self, msg):
		self.decodeMessage(msg)
	def decodeMessage(self, data):
		if len(self.message) != 3:
			self.message[0] += data
			data = self.message[0]
			lid = len(data)
			
			if ord(data[0]) == 136:
				self.close()
				return
			if lid < 6: # 1 + 1 + 4 (? + l_data + mask)
				return
			datalength = ord(data[1]) & 127
			mask_index = 2

			if datalength == 126:
				if lid < 8:
					return
				mask_index = 4
				datalength = struct.unpack(">H", data[2:4])[0]
			elif datalength == 127:	
				if lid < 14:
					return
				mask_index = 10
				datalength = struct.unpack(">Q", data[2:10])[0]
			self.message = [datalength, data[mask_index:mask_index+4], data[mask_index+4:]]
		else:
			self.message[2] += data
		
		if len(self.message[2]) < self.message[0]:
			return
		
		# Extract masks
		masks = [ord(m) for m in self.message[1]]
		msg = ''
		j = 0
		# Loop through each byte that was received
		for i in range(self.message[0]):
			# Unmask this byte and add to the decoded buffer
			msg += chr(ord(self.message[2][i]) ^ masks[j])
			j += 1
			if j == 4:
				j = 0
				
		self.onNewMessage(msg)
		if self.message[2][self.message[0]:] == '':
			self.message = ['']
		else:
			data = self.message[2][self.message[0]:]
			self.message = ['']
			self.decodeMessage(data)

	def sendMessage(self, s, binary = False):
		"""
		Encode and send a WebSocket message
		"""
		# Empty message to start with
		message = ""
		# always send an entire message as one frame (fin)
		# default text
		b1 = 0x81

		if binary:
			b1 = 0x02
		
		# in Python 2, strs are bytes and unicodes are strings
		if type(s) == unicode:
			payload = s.encode("UTF8")

		elif type(s) == str:
			payload = s
		# Append 'FIN' flag to the message
		message += chr(b1)
		# never mask frames from the server to the client
		b2 = 0

		# How long is our payload?
		length = len(payload)
		if length < 126:
			b2 |= length
			message += chr(b2)

		elif length < (2 ** 16):
			b2 |= 126
			message += chr(b2)
			l = struct.pack(">H", length)
			message += l

		else:
			l = struct.pack(">Q", length)
			b2 |= 127
			message += chr(b2)
			message += l
		# Append payload to message
		message += payload

		# Send to the client
		data = str(message)
		self.send(str(message))
	def onNewMessage(self, msg):
		print msg

if __name__ == "__main__":
	ws = serverSock('188.166.181.251', 5001, "ghuvronsgg104986")
	ws.setClientClass(cSockHandler)
	ws.run()
	ws.close()