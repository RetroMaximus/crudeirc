import json
import tkinter as tk
from tkinter import ttk, messagebox
from src.server_details_manager import ServerDetailsManager


class SettingsWindow:
	_instance = None
	def __init__(self, root, details_manager, server_details, proxy_details):
		
		self.server_details = server_details
		self.proxy_details = proxy_details

		self.proxy_list_dropdown = None
		if SettingsWindow._instance is not None:
			# Bring existing window to the top
			SettingsWindow._instance.window.lift()
			SettingsWindow._instance.window.focus_set()
			return
		
		self.server_details_manager = ServerDetailsManager(root, server_details, proxy_details)
		
		self.details_manager = details_manager
		self.window = root
		
		# if SettingsWindow._instance is not None:
		# 	SettingsWindow._instance.window.resizable(False, False)
		# 	SettingsWindow._instance.window.title("Settings")
			
		self.show_server_addresses_check = None
		self.show_server_addresses_var = None
		self.show_username_addresses_check = None
		self.show_traceback_results_check = None
		self.proxy_name_entry = None
		self.proxy_port_entry = None
		self.proxy_host_entry = None
		self.proxy_enabled_check = None
		self.proxy_enabled_var = None
		self.show_server_response_type_var = None
		self.show_username_addresses_var = None
		self.show_traceback_results_var = None
		self.proxy_type_entry = None
		self.auto_connect_check = None
		self.auto_connect_var = None
		self.realname_entry = None
		self.username_entry = None
		self.nickname_entry = None
		self.ssl_check = None
		self.ssl_var = None
		self.port_entry = None
		self.server_name_entry = None
		self.server_entry = None
		self.server_list_dropdown = None
		self.debug_frame = None
		self.firewall_frame = None
		self.identd_frame = None
		self.options_frame = None
		self.local_info_frame = None
		self.appearance_frame = None
		self.script_editor_frame = None
		self.proxy_frame = None
		self.server_frame = None
		self.notebook = None
		self.show_server_response_type_check = None
		
		self.window = tk.Toplevel(root)
		self.window.protocol("WM_DELETE_WINDOW", self.on_close)
		self.window.focus_set()
		self.window.attributes('-topmost', True)
		
		SettingsWindow._instance = self
		
		# Bind to the focus in event
		self.window.bind("<<FocusIn>>", self.on_focus_in)
		
		self.create_widgets()
	
	def on_focus_in(self, event):
		_ = event
		self.window.focus_set()
		
	def on_close(self):
		SettingsWindow._instance = None
		self.window.resizable(True, True)
		self.window.destroy()
		
	def create_widgets(self):
		# Create notebook
		self.notebook = ttk.Notebook(self.window)
		self.notebook.pack(expand=True, fill='both')
		
		# Create frames for each tab
		self.server_frame = ttk.Frame(self.notebook)
		self.proxy_frame = ttk.Frame(self.notebook)
		self.script_editor_frame = ttk.Frame(self.notebook)
		self.appearance_frame = ttk.Frame(self.notebook)
		self.local_info_frame = ttk.Frame(self.notebook)
		self.options_frame = ttk.Frame(self.notebook)
		self.identd_frame = ttk.Frame(self.notebook)
		self.firewall_frame = ttk.Frame(self.notebook)
		self.debug_frame = ttk.Frame(self.notebook)
		
		# Add frames to notebook
		self.notebook.add(self.server_frame, text='Server')
		self.notebook.add(self.proxy_frame, text='Proxy')
		#self.notebook.add(self.script_editor_frame, text='Script Editor')
		#self.notebook.add(self.appearance_frame, text='Appearance')
		#self.notebook.add(self.local_info_frame, text='Local Info')
		#self.notebook.add(self.options_frame, text='Options')
		#self.notebook.add(self.identd_frame, text='Identd')
		#self.notebook.add(self.firewall_frame, text='Firewall')
		self.notebook.add(self.debug_frame, text='Debug')
		
		# Populate the frames
		self.create_server_tab()
		self.create_proxy_tab()
		self.create_debug_tab()
		
		# Apply Changes button
		apply_button = tk.Button(self.window, text="Apply Settings", command=self.apply_changes)
		apply_button.pack(pady=10)
	
	def create_server_tab(self):
		# Server settings on the first tab
		server_list_label = tk.Label(self.server_frame, text="Server List:")
		server_list_label.grid(row=0, column=0, padx=10, pady=5)
		
		if 'servers' in self.server_details_manager.server_details.keys():
			server_names = list(self.server_details_manager.server_details['servers'].keys())
		else:
			server_names = []
		
		self.server_list_dropdown = ttk.Combobox(self.server_frame, values=server_names, state="readonly")
		#print(server_names)
		self.server_list_dropdown.grid(row=0, column=1, padx=10, pady=5)
		self.server_list_dropdown.bind("<<ComboboxSelected>>", self.populate_server_details)
		
		server_name_label = tk.Label(self.server_frame, text="Server Name:")
		server_name_label.grid(row=1, column=0, padx=10, pady=5)
		self.server_name_entry = tk.Entry(self.server_frame)
		self.server_name_entry.grid(row=1, column=1, padx=10, pady=5)
		
		server_label = tk.Label(self.server_frame, text="Server:")
		server_label.grid(row=2, column=0, padx=10, pady=5)
		self.server_entry = tk.Entry(self.server_frame)
		self.server_entry.grid(row=2, column=1, padx=10, pady=5)
		
		port_label = tk.Label(self.server_frame, text="Port:")
		port_label.grid(row=3, column=0, padx=10, pady=5)
		self.port_entry = tk.Entry(self.server_frame)
		self.port_entry.grid(row=3, column=1, padx=10, pady=5)
		
		ssl_label = tk.Label(self.server_frame, text="SSL:")
		ssl_label.grid(row=4, column=0, padx=10, pady=5)
		self.ssl_var = tk.BooleanVar()
		self.ssl_check = tk.Checkbutton(self.server_frame, variable=self.ssl_var)
		self.ssl_check.grid(row=4, column=1, padx=10, pady=5)
		
		nickname_label = tk.Label(self.server_frame, text="Nickname:")
		nickname_label.grid(row=5, column=0, padx=10, pady=5)
		self.nickname_entry = tk.Entry(self.server_frame)
		self.nickname_entry.grid(row=5, column=1, padx=10, pady=5)
		
		username_label = tk.Label(self.server_frame, text="Username:")
		username_label.grid(row=6, column=0, padx=10, pady=5)
		self.username_entry = tk.Entry(self.server_frame)
		self.username_entry.grid(row=6, column=1, padx=10, pady=5)
		
		realname_label = tk.Label(self.server_frame, text="Realname:")
		realname_label.grid(row=7, column=0, padx=10, pady=5)
		self.realname_entry = tk.Entry(self.server_frame)
		self.realname_entry.grid(row=7, column=1, padx=10, pady=5)
		
		auto_connect_label = tk.Label(self.server_frame, text="Auto Connect:")
		auto_connect_label.grid(row=8, column=0, padx=10, pady=5)
		self.auto_connect_var = tk.BooleanVar()
		self.auto_connect_check = tk.Checkbutton(self.server_frame, variable=self.auto_connect_var)
		self.auto_connect_check.grid(row=8, column=1, padx=10, pady=5)
		
		new_button = tk.Button(self.server_frame, text="Add New Server", command=self.new_server_details)
		new_button.grid(row=9, column=0, padx=10, pady=10)
		
		remove_button = tk.Button(self.server_frame, text="Remove Selected Server", command=self.remove_server_details)
		remove_button.grid(row=9, column=1, padx=10, pady=10)
		# Apply Changes button
		save_button = tk.Button(self.server_frame, text="Save Changes", command=self.apply_server_changes   )
		save_button.grid(row=10, column=0, columnspan=2,padx=10, pady=10)
	
	def create_proxy_tab(self):
		# Proxy settings on the proxy tab
		if 'proxies' in self.server_details_manager.server_details.keys():
			proxy_list = list(self.server_details_manager.server_details['proxies'].keys())
		else:
			proxy_list = []
		
		server_label = tk.Label(self.proxy_frame, text="Proxy List:")
		server_label.grid(row=0, column=0, padx=10, pady=5)
		
		self.proxy_list_dropdown = ttk.Combobox(self.proxy_frame, values=proxy_list, state="readonly")
		self.proxy_list_dropdown.grid(row=0, column=1, padx=10, pady=5)
		self.proxy_list_dropdown.bind("<<ComboboxSelected>>", self.populate_proxy_details)
		
		proxy_name_label = tk.Label(self.proxy_frame, text="Proxy Name:")
		proxy_name_label.grid(row=1, column=0, padx=10, pady=5)
		self.proxy_name_entry = tk.Entry(self.proxy_frame)
		self.proxy_name_entry.grid(row=1, column=1, padx=10, pady=5)
		
		proxy_host_label = tk.Label(self.proxy_frame, text="Proxy Host:")
		proxy_host_label.grid(row=2, column=0, padx=10, pady=5)
		self.proxy_host_entry = tk.Entry(self.proxy_frame)
		self.proxy_host_entry.grid(row=2, column=1, padx=10, pady=5)
		
		proxy_type_label = tk.Label(self.proxy_frame, text="Proxy Type (socks4, socks5, http):")
		proxy_type_label.grid(row=3, column=0, padx=10, pady=5)
		self.proxy_type_entry = tk.Entry(self.proxy_frame)
		self.proxy_type_entry.grid(row=3, column=1, padx=10, pady=5)
		
		proxy_port_label = tk.Label(self.proxy_frame, text="Proxy Port:")
		proxy_port_label.grid(row=4, column=0, padx=10, pady=5)
		self.proxy_port_entry = tk.Entry(self.proxy_frame)
		self.proxy_port_entry.grid(row=4, column=1, padx=10, pady=5)
		
		proxy_enabled_label = tk.Label(self.proxy_frame, text="Enable Proxy:")
		proxy_enabled_label.grid(row=5, column=0, padx=10, pady=5)
		self.proxy_enabled_var = tk.BooleanVar()
		self.proxy_enabled_check = tk.Checkbutton(self.proxy_frame, variable=self.proxy_enabled_var, command=self.toggle_proxy_settings)
		self.proxy_enabled_check.grid(row=5, column=1, padx=10, pady=5)
		
		add_proxy_button = tk.Button(self.proxy_frame, text="Add New Proxy", command=self.new_proxy_details)
		add_proxy_button.grid(row=6, column=0, padx=10, pady=5)
		
		remove_proxy_button = tk.Button(self.proxy_frame, text="Remove Selected Proxy", command=self.remove_proxy)
		remove_proxy_button.grid(row=6, column=1, padx=10, pady=5)
		
		save_button = tk.Button(self.proxy_frame, text="Save Changes", command=self.apply_proxy_changes)
		save_button.grid(row=7, column=0, columnspan=2, padx=10, pady=10)
		
	
	def create_debug_tab(self):
		# Move the debug settings to the Debug tab
		tracback_errors_label = tk.Label(self.debug_frame, text="Show Traceback Errors:")
		tracback_errors_label.grid(row=0, column=0, padx=10, pady=5)
		self.show_traceback_results_var = tk.BooleanVar()
		self.show_traceback_results_check = tk.Checkbutton(self.debug_frame, variable=self.show_traceback_results_var)
		self.show_traceback_results_check.grid(row=0, column=1, padx=10, pady=5)
		
		username_address_label = tk.Label(self.debug_frame, text="Show Username Addresses:")
		username_address_label.grid(row=1, column=0, padx=10, pady=5)
		self.show_username_addresses_var = tk.BooleanVar()
		self.show_username_addresses_check = tk.Checkbutton(self.debug_frame, variable=self.show_username_addresses_var)
		self.show_username_addresses_check.grid(row=1, column=1, padx=10, pady=5)
		
		server_address_label = tk.Label(self.debug_frame, text="Show Server Addresses:")
		server_address_label.grid(row=2, column=0, padx=10, pady=5)
		self.show_server_addresses_var = tk.BooleanVar()
		self.show_server_addresses_check = tk.Checkbutton(self.debug_frame, variable=self.show_server_addresses_var)
		self.show_server_addresses_check.grid(row=2, column=1, padx=10, pady=5)
		
		server_response_type_label = tk.Label(self.debug_frame, text="Show Server Response Type:")
		server_response_type_label.grid(row=3, column=0, padx=10, pady=5)
		self.show_server_response_type_var = tk.BooleanVar()
		self.show_server_response_type_check = tk.Checkbutton(self.debug_frame, variable=self.show_server_response_type_var)
		self.show_server_response_type_check.grid(row=3, column=1, padx=10, pady=5)
	
	def populate_server_details(self, event=None):
		_ = event
		selected_server = self.server_list_dropdown.get()
		server_details = self.server_details_manager.get_server_details(selected_server)
		
		if server_details:
			# Populate main server details
			self.server_name_entry.delete(0, tk.END)
			self.server_name_entry.insert(0, server_details.get('name', ''))
			self.server_entry.delete(0, tk.END)
			self.server_entry.insert(0, server_details.get('server', ''))
			self.port_entry.delete(0, tk.END)
			self.port_entry.insert(0, server_details.get('port', ''))
			self.ssl_var.set(server_details.get('ssl', False))
			self.nickname_entry.delete(0, tk.END)
			self.nickname_entry.insert(0, server_details.get('nickname', ''))
			self.username_entry.delete(0, tk.END)
			self.username_entry.insert(0, server_details.get('username', ''))
			self.realname_entry.delete(0, tk.END)
			self.realname_entry.insert(0, server_details.get('realname', ''))
			self.auto_connect_var.set(server_details.get('auto_connect', False))
			
			# Populate additional settings
			self.show_traceback_results_var.set(server_details.get('show_traceback_results', False))
			self.show_username_addresses_var.set(server_details.get('show_username_addresses', False))
			self.show_server_addresses_var.set(server_details.get('show_server_addresses', False))
			self.show_server_response_type_var.set(server_details.get('show_server_response_type', False))
			
			# Populate proxy details
			proxy_details = server_details.get('proxy_details', {})
			self.proxy_enabled_var.set(bool(proxy_details))
			self.proxy_host_entry.delete(0, tk.END)
			self.proxy_host_entry.insert(0, proxy_details.get('host', ''))
			self.proxy_type_entry.delete(0, tk.END)
			self.proxy_type_entry.insert(0, proxy_details.get('type', ''))
			self.proxy_port_entry.delete(0, tk.END)
			self.proxy_port_entry.insert(0, proxy_details.get('port', ''))
			
			# Toggle proxy settings based on whether proxy is enabled
			self.toggle_proxy_settings()
	
	def populate_proxy_details(self, event=None):
		_ = event
		selected_proxy = self.proxy_list_dropdown.get()
		proxy_details = self.server_details_manager.get_proxy_details(selected_proxy)
		
		if proxy_details:
			
			# Populate proxy details
			proxy_details = proxy_details.get('proxy_details', {})
			self.proxy_name_entry.delete(0, tk.END)
			self.proxy_name_entry.insert(0, proxy_details.get('name', ''))
			self.proxy_enabled_var.set(bool(proxy_details))
			self.proxy_host_entry.delete(0, tk.END)
			self.proxy_host_entry.insert(0, proxy_details.get('host', ''))
			self.proxy_type_entry.delete(0, tk.END)
			self.proxy_type_entry.insert(0, proxy_details.get('type', ''))
			self.proxy_port_entry.delete(0, tk.END)
			self.proxy_port_entry.insert(0, proxy_details.get('port', ''))
			
			# Toggle proxy settings based on whether proxy is enabled
			self.toggle_proxy_settings()
	
	def toggle_proxy_settings(self):
		state = "normal" if self.proxy_enabled_var.get() else "disabled"
		self.proxy_type_entry.config(state=state)
		self.proxy_host_entry.config(state=state)
		self.proxy_port_entry.config(state=state)
	
	def new_proxy_details(self):
		proxy_name = self.proxy_name_entry.get().strip()
		if proxy_name:
			if proxy_name in self.server_details_manager.proxy_details.get('proxies', {}):
				user_input = tk.messagebox.askquestion("Proxy Exists", "This proxy already exists. Do you want to overwrite it?")
				if user_input.lower() not in ['yes', 'y']:
					return
			details = self.collect_proxy_details()
			self.server_details_manager.set_proxy_details(proxy_name, details)
			self.proxy_list_dropdown.configure(values=list(self.server_details_manager.proxy_details.get('proxies', {}).keys()))
			self.proxy_list_dropdown.set(proxy_name)
	
	def remove_proxy(self):
		server_name = self.server_list_dropdown.get()
		if server_name:
			self.server_details_manager.remove_proxy_details(server_name)
			self.proxy_list_dropdown.configure(values=list(self.server_details_manager.proxy_details.get('proxies', {}).keys()))
			self.populate_proxy_details()
	
	
	@staticmethod
	def save_proxies(proxies):
		with open('crude_proxy_settings.json', 'w') as file:
			json.dump(proxies, file)
	
	def new_server_details(self):
		server_name = self.server_name_entry.get().strip()
		if server_name:
			if server_name in self.server_details_manager.server_details.get('servers', {}):
				user_input = tk.messagebox.askquestion("Server Exists", "This server already exists. Do you want to overwrite it?")
				if user_input.lower() not in ['yes', 'y']:
					return
			details = self.collect_server_details()
			self.server_details_manager.set_server_details(server_name, details)
			self.server_list_dropdown.configure(values=list(self.server_details_manager.server_details.get('servers', {}).keys()))
			self.server_list_dropdown.set(server_name)
	
	def remove_server_details(self):
		server_name = self.server_list_dropdown.get()
		if server_name:
			self.server_details_manager.remove_server_details(server_name)
			self.server_list_dropdown.configure(values=list(self.server_details_manager.server_details.get('servers', {}).keys()))
			self.populate_server_details()
	
	def collect_server_details(self):
		details = {
			'show_traceback_results'   : self.show_traceback_results_var.get(),
			'show_username_addresses'  : self.show_username_addresses_var.get(),
			'show_server_addresses'    : self.show_server_addresses_var.get(),
			'show_server_response_type': self.show_server_response_type_var.get(),
			'name'                     : self.server_name_entry.get(),
			'server'                   : self.server_entry.get(),
			'port'                     : self.port_entry.get(),
			'ssl'                      : self.ssl_var.get(),
			'nickname'                 : self.nickname_entry.get(),
			'username'                 : self.username_entry.get(),
			'realname'                 : self.realname_entry.get(),
			'auto_connect'             : self.auto_connect_var.get(),
			'proxy_details'            : {
				'name': self.proxy_name_entry.get(),
				'host': self.proxy_host_entry.get(),
				'type': self.proxy_type_entry.get(),
				'port': self.proxy_port_entry.get()
			} if self.proxy_enabled_var.get() else {}
		}
		return details
	
	def collect_proxy_details(self):
		details = {
				'name': self.proxy_name_entry.get() if self.proxy_enabled_var.get() else {},
				'host': self.proxy_host_entry.get() if self.proxy_enabled_var.get() else {},
				'type': self.proxy_type_entry.get() if self.proxy_enabled_var.get() else {},
				'port': self.proxy_port_entry.get() if self.proxy_enabled_var.get() else {}
		}
		return details
	
	def apply_changes(self):
		server_name = self.server_list_dropdown.get()
		details = self.collect_server_details()
		self.server_details_manager.set_server_details(server_name, details)
		self.server_list_dropdown.configure(values=list(self.server_details_manager.server_details.get('servers', {}).keys()))

		
	
	def apply_server_changes(self):
		server_name = self.server_list_dropdown.get()
		details = self.collect_server_details()
		self.server_details_manager.set_server_details(server_name, details)
		self.server_list_dropdown.configure(values=list(self.server_details_manager.server_details.get('servers', {}).keys()))
	
	def apply_proxy_changes(self):
		proxy_name = self.proxy_list_dropdown.get()
		details = self.collect_proxy_details()
		self.server_details_manager.set_proxy_details(proxy_name, details)
		self.proxy_list_dropdown.configure(values=list(self.server_details_manager.proxy_details.get('proxies', {}).keys()))
	
	def save_settings(self):
		self.details_manager.set('show_traceback_results', self.show_traceback_results_var.get())
		self.details_manager.set('show_username_addresses', self.show_username_addresses_var.get())
		self.details_manager.set('show_server_addresses', self.show_server_addresses_var.get())
		self.details_manager.set('show_server_response_type', self.show_server_response_type_var.get())
		self.details_manager.set('name', self.server_name_entry.get())
		self.details_manager.set('server', self.server_entry.get())
		self.details_manager.set('port', int(self.port_entry.get()))
		self.details_manager.set('ssl', self.ssl_var.get())
		self.details_manager.set('nickname', self.nickname_entry.get())
		self.details_manager.set('username', self.username_entry.get())
		self.details_manager.set('realname', self.realname_entry.get())
		self.details_manager.set('auto_connect', self.auto_connect_var.get())
		if self.proxy_enabled_var.get():
			self.details_manager["proxy_details"].set('name', self.proxy_host_entry.get())
			self.details_manager["proxy_details"].set('host', self.proxy_host_entry.get())
			self.details_manager["proxy_details"].set('type', self.proxy_type_entry.get())
			self.details_manager["proxy_details"].set('port', self.proxy_port_entry.get())
		else:
			self.details_manager["proxy_details"].clear()
		
		self.window.destroy()
