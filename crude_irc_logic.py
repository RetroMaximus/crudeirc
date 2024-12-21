import socket
import ssl
import threading
import traceback

# Retro
class CrudeClientIRCLogic:
	def __init__(self, gui_callbacks):
		self.port = None
		self.server = None
		self.nickname = None
		self.irc_socket = None
		self.connected = gui_callbacks.connected
		self.gui_callbacks = gui_callbacks  # Callbacks for GUI updates
		self.details_manager = self.gui_callbacks.details_manager  # Access details manager from GUI
	
	def connect(self):
		if self.connected:
			return
		
		try:
			active_details = self.details_manager.get_active_details()
			if not active_details:
				self.gui_callbacks.status_label.config(text="No server details", fg="red")
				return
			self.server = active_details['server']
			self.port = active_details['port']
			use_ssl = active_details['ssl']
			self.nickname = active_details['nickname']
			username = active_details['username']
			realname = active_details['realname']
			auto_connect = active_details['auto_connect']
			
			if self.details_manager.is_proxy_enabled() is True:
				proxy_details = active_details['proxy_details']
				proxy_type = proxy_details.get('type', '').lower()
				proxy_host = proxy_details.get('host', '')
				proxy_port = int(proxy_details.get('port', 0))
				
				if proxy_type == 'socks5':
					import socks
					self.irc_socket = socks.socksocket()
					self.irc_socket.set_proxy(socks.SOCKS5, proxy_host, proxy_port)
				elif proxy_type == 'http':
					self.irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					proxy_connect_str = f'CONNECT {self.server}:{self.port} HTTP/1.1\r\n\r\n'
					self.irc_socket.connect((proxy_host, proxy_port))
					self.irc_socket.sendall(proxy_connect_str.encode('utf-8'))
					response = self.irc_socket.recv(4096)
					if b'200 Connection established' not in response:
						raise Exception('Failed to connect via HTTP proxy')
				else:
					self.irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			else:
				self.irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			
			self.irc_socket.connect((self.server, self.port))
			
			if use_ssl:
				context = ssl.create_default_context()
				self.irc_socket = context.wrap_socket(self.irc_socket, server_hostname=self.server)
			
			self.connected = True
			self.gui_callbacks.status_label.config(text="Connected", fg="green")
			self.gui_callbacks.connect_button.config(text="Disconnect")
			self.gui_callbacks.response_buffers["Status"] += f"server - Connected to {self.server}:{self.port}\n"
			# self.update_text_area()
			
			self.gui_callbacks.send_irc_message(f"NICK {self.nickname}")
			self.gui_callbacks.send_irc_message(f"USER {username} 0 * :{realname}")
			
			threading.Thread(target=self.gui_callbacks.receive_messages, daemon=True).start()
		
		except Exception as e:
			self.gui_callbacks.status_label.config(text=f"Connection failed: {e}", fg="red")
			self.gui_callbacks.response_buffers["Status"] += f"error - Connection failed: {e}\n"
			self.gui_callbacks.update_text_area()
			traceback.print_exc()
			self.connected = False
