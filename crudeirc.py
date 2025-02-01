import os
import atexit
import ctypes
import hashlib
import random
import re
import socket
import ssl
import sys
import tkinter as tk
from tkinter import Menu
import webbrowser
from io import BytesIO
import requests
from src.settings_window import SettingsWindow
import threading
from src.server_details_manager import ServerDetailsManager
from crude_irc_logic import CrudeClientIRCLogic
from src.crude_proxy_bouncer import CrudeProxyBouncer
from src.crude_launch_writer import CrudeLaunchWriter
import traceback
import logging
import PIL
from PIL import Image, ImageTk

def hide_console():
    if sys.platform == "win32":
        print(ctypes.windll.kernel32.GetConsoleWindow())
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

def show_console():
    if sys.platform == "win32":
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 1)

def handle_exception(exc_type, exc_value, exc_traceback):
    show_console()
    # Print the exception details to the console
    if not issubclass(exc_type, KeyboardInterrupt):
        traceback.print_exception(exc_type, exc_value, exc_traceback)
    sys.__excepthook__(exc_type, exc_value, exc_traceback)
    # Exit the application after showing the console
    sys.exit(1)

def initialize_application(self):
    if self.hide_terminal_on_init:
        hide_console()
        # Register exception handler to show console on error
        sys.excepthook = handle_exception
        # Register exit handler to show console on application exit
        atexit.register(show_console)
        
class CrudeIRC:
    def __init__(self, main_app):
        self.logpath = self.get_project_dir()
        self.logger = logging.basicConfig(filename=f"'{self.logpath}/logs/logfile.log", level=logging.DEBUG, format="")
        self.colors = None
        
        self.hide_terminal_on_init = True  # Set this based on your configuration
        
        initialize_application(self)
        self.last_line = ""
        self.part_len = 0

        self.server_name = None
        self.new_nickname_side = 0
        self.no_distractions_state = True
        self.zen_mode_state = False
        self.showing_entry_frame = True
        self.showing_status_frame = True
        self.showing_menu = True
        self.root_frame = None
        self.root = main_app
        current_width = 200
        current_height = 100
        self.root.geometry(f"{current_width}x{current_height}")
        self.nerd_font = ("TkDefaultFont", 12) 
        # self.nerd_font = ("JetBrainsMono Nerd Font", 12)
        self.text_container = None
        self.text_area_menu = None
        self.nickname_list_menu = None
        self.chanserv_menu = None
        self.nickserv_menu = None
        self.port = None
        self.server = None
        self.nickname = None
        self.status_buffer_label = None
        self.viewing_buffer_index = 0
        self.response_buffer_labels = []
        self.response_buffers = {
            "Status": "",
        }
        self.nickname_buffers = {
            "Status": [],
        }
        self.nickname_colors = {
            "colors": [],
        }
        self.send_button = None
        self.entry = None
        self.entry_frame = None
        self.nickname_listbox = None
        self.text_area = None
        self.text_frame = None
        self.connect_button = None
        self.status_label = None
        self.status_frame = None
        self.window_menu = None
        self.file_menu = None
        self.menu_bar = None
        self.server_var = tk.StringVar()
        
        # current_width = self.root.winfo_width()
        # current_height = self.root.winfo_height()
        current_width = 800
        current_height = 400
        self.root.geometry(f"{current_width}x{current_height}")
        self.connected = False
        self.server_details = {
            'servers': {}
        }
        self.proxy_details = {
            'proxies': {}
        }
        self.details_manager = ServerDetailsManager(self, self.server_details, self.proxy_details)
        self.crude_launch_writer = CrudeLaunchWriter
        self.crude_proxy_bouncer = CrudeProxyBouncer
        self.settings_window = SettingsWindow
        
        self.make_buffer_display_labels()
        self.create_gui()
        self.irc_socket = None
        self.details_manager.load_server_details()
        self.details_manager.load_proxy_details()
        
        self.active_details = self.details_manager.get_active_details()
        # print("active details:",self.active_details)

        self.active_proxy_details = self.details_manager.get_active_proxy_details()
        
        #print(self.details_manager.get_active_details())
        self.show_tracback_results = self.active_details["show_traceback_results"]
        self.show_username_addresses = self.active_details["show_username_addresses"]
        self.show_server_addresses = self.active_details["show_server_addresses"]
        self.show_server_response_type = self.active_details["show_server_response_type"]
        
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)
        
    def generate_launch_scripts(self):
        self.crude_launch_writer(self.root, self.details_manager).write_bat_no_log()
        self.crude_launch_writer(self.root, self.details_manager).write_bat_with_log()
        self.crude_launch_writer(self.root, self.details_manager).write_sh_no_log()
        self.crude_launch_writer(self.root, self.details_manager).write_sh_with_log()
        self.crude_launch_writer(self.root, self.details_manager).write_create_shortcut()
    
    def open_proxy_bouncer(self):
        self.crude_proxy_bouncer.open_proxy_bouncer(self.crude_proxy_bouncer(self))
    
    def view_next_buffer(self):
        buffer_keys = list(self.response_buffers.keys())
        self.viewing_buffer_index = (self.viewing_buffer_index + 1) % len(buffer_keys)
        channel = buffer_keys[self.viewing_buffer_index]
        self.request_nicklist(channel)
        self.text_area.delete(1.0, tk.END)
        self.populate_text_area()

    def view_prior_buffer(self):
        buffer_keys = list(self.response_buffers.keys())
        self.viewing_buffer_index = (self.viewing_buffer_index - 1) % len(buffer_keys)
        channel = buffer_keys[self.viewing_buffer_index]
        self.request_nicklist(channel)
        self.text_area.delete(1.0, tk.END)
        self.populate_text_area()
    
    def create_gui(self):
        self.root.title("CrudeIRC")
        
        self.menu_bar = tk.Menu(self.root)
        #self.menu_bar.configure(background="#36454f", borderwidth=-1)
        self.root.config(menu=self.menu_bar)
        self.root.config(background="#36454f", borderwidth=0)
        
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Settings", command=self.open_settings)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)
        
        self.window_menu = tk.Menu(self.menu_bar, tearoff=0, font=self.nerd_font)
        self.menu_bar.add_cascade(label="Window", menu=self.window_menu)
        self.window_menu.add_command(label="Show Nickname List", command=self.show_nickname_list)
        self.window_menu.add_command(label="Hide Nickname List", command=self.hide_nickname_list)
        self.window_menu.add_command(label="Move Nickname List to Left", command=lambda: self.move_nickname_list(0))
        self.window_menu.add_command(label="Move Nickname List to Right", command=lambda: self.move_nickname_list(1))
        
        self.window_menu.configure(font=self.nerd_font, background="#36454f", foreground="#eeeeee", borderwidth=0)
        self.file_menu.configure(font=self.nerd_font, background="#36454f", foreground="#eeeeee", borderwidth=0)
        self.menu_bar.configure(font=self.nerd_font, background="#36454f", foreground="#eeeeee", borderwidth=0)
        
        # Window Setup
        self.status_frame = tk.Frame(self.root)
        self.status_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.status_frame.config(background="#36454f", borderwidth=-1, relief="flat")
        
        self.status_label = tk.Label(self.status_frame, text="Disconnected", fg="red")
        self.status_label.grid(row=0, column=1, sticky="w")
        self.status_label.configure(background="#36454f", foreground="#eeeeee", borderwidth=-1, relief="flat")
        self.make_buffer_display_labels()
        
        self.connect_button = tk.Button(self.status_frame, text="Connect", command=self.toggle_connection)
        self.connect_button.grid(row=0, column=0, sticky="e")
        self.connect_button.config(background="#36454f", foreground="#eeeeee", activebackground="#36454f", activeforeground="#eeeeee")
        
        self.text_area = tk.Text(self.root, state=tk.DISABLED, width=1, height=1)
        self.text_area.grid(row=1, column=0, sticky="nsew", padx=(5,0), pady=5)
        self.text_area.configure(font=self.nerd_font, wrap="word", background="#36454f", foreground="#eeeeee")
        
        
        self.nickname_listbox = tk.Listbox(self.root)
        self.nickname_listbox.grid(row=1, column=1, sticky="ns", padx=5, pady=5)
        self.nickname_listbox.configure(font=self.nerd_font, background="#36454f", foreground="#eeeeee", borderwidth=0, relief="flat")
        
        self.entry_frame = tk.Frame(self.root)
        self.entry_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=0)
        self.entry_frame.configure(background="#36454f", borderwidth=0, relief="flat")
        
        self.entry = tk.Entry(self.entry_frame)
        self.entry.grid(row=0, column=0, sticky="ew", padx=(5,0),pady=(0,5))
        self.entry.bind("<Return>", self.send_message)
        self.entry.configure(font=self.nerd_font, background="#36454f", foreground="#eeeeee", borderwidth=0, relief="flat")
        
        self.send_button = tk.Button(self.entry_frame, text="Send", command=self.send_message)
        self.send_button.grid(row=0, column=1, sticky="e", padx=(0,5), pady=(0,5))
        self.send_button.config(background="#36454f", foreground="#eeeeee", activebackground="#36454f", activeforeground="#eeeeee")
        
        self.entry_frame.grid_rowconfigure(0, weight=1)
        self.entry_frame.grid_columnconfigure(0, weight=1)
        
        # Define styles for different message types
        self.text_area.tag_configure("bold", font="TkDefaultFont 9 bold")
        self.text_area.tag_configure("ping", foreground="red")
        self.text_area.tag_configure("nickserv", foreground="magenta", background="lightgray", font="TkDefaultFont 9 bold")
        self.text_area.tag_configure("chanserv", foreground="green", background="lightgray", font="TkDefaultFont 9 bold")
        self.text_area.tag_configure("notice", foreground="purple", font="TkDefaultFont 9 italic")
        self.text_area.tag_configure("error", foreground="red", font="TkDefaultFont 9 bold")
        self.text_area.tag_configure("channel", foreground="black")
        self.text_area.tag_configure("private", foreground="white")
        self.text_area.tag_configure("join", foreground="green")
        self.text_area.tag_configure("part", foreground="orange")
        self.text_area.tag_configure("quit", foreground="red")
        self.text_area.tag_configure("kick", foreground="red", font="TkDefaultFont 9 bold")
        self.text_area.tag_configure("mode", foreground="blue")
        self.text_area.tag_configure("topic", foreground="cyan")
        self.text_area.tag_configure("nick", foreground="darkgreen")
        self.text_area.tag_configure("server", foreground="gray")
        
        # Bind keys for buffer navigation
        self.root.bind("<Control-Right>", lambda e: self.view_next_buffer())
        self.root.bind("<Control-Left>", lambda e: self.view_prior_buffer())
        
        # Bind scroll up +1
        self.root.bind("<Control-Up>", lambda e: self.increment_font(1))
        self.root.bind("<Control-Down>", lambda e: self.increment_font(-1))
        
        self.root.bind("<Up>", lambda e: self.increment_scroll_wheel(1))
        self.root.bind("<Down>", lambda e: self.increment_scroll_wheel(-1))
        
        # Bind F-keys
        self.root.bind("<F1>", lambda e: self.toggle_menu_visibility())
        self.root.bind("<F2>", lambda e: self.open_settings())
        self.root.bind("<F3>", lambda e: self.toggle_nickname_list_position())
        self.root.bind("<F4>", lambda e: self.toggle_nickname_list_visibility())
        # self.root.bind("<F5>", lambda e: self.toggle_status_bar())
        self.root.bind("<F5>", lambda e: self.no_distractions())
        self.root.bind("<F6>", lambda e: self.open_proxy_bouncer())
        # open_proxy_bouncer
        # Create context menus
        self.create_context_menus()
        
        # Configure grid weights to ensure resizing works correctly
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)
    
    
    def toggle_menu_visibility(self):
        #print(self.showing_menu)
        if  self.showing_menu is True:
            
            self.showing_menu = False
            self.root.config(menu="")
            self.root.update_idletasks()
        else:
            self.root.config(menu=self.menu_bar)
            self.showing_menu = not self.showing_menu
            
    def toggle_nickname_list_position(self):
        if self.nickname_listbox.winfo_ismapped() and self.nickname_listbox.grid_info()['column'] == 1:
            self.move_nickname_list(0)
        else:
            self.move_nickname_list(1)
    
    def toggle_nickname_list_visibility(self):
        if self.nickname_listbox.winfo_ismapped():
            self.hide_nickname_list()
        else:
            self.show_nickname_list()
    
    
    def no_distractions(self):
        if self.no_distractions_state is True:
            self.no_distractions_state = False
            self.showing_menu = self.no_distractions_state
            
            # self.status_frame.pack(side=tk.TOP, fill=tk.X)
            self.nickname_listbox.pack(side=tk.RIGHT, fill=tk.Y)
            self.entry_frame.pack(side=tk.LEFT, expand=True,fill=tk.X)
            self.root.config(menu=self.menu_bar)
            self.root.update_idletasks()
        else:
            
            self.no_distractions_state = True
            self.showing_menu = not self.showing_menu
            
            # self.status_frame.pack_forget()
            self.nickname_listbox.pack_forget()
            self.root.config(menu="")
            
            self.entry_frame.pack_forget()
            
            self.showing_status_frame = self.no_distractions_state

    def increment_font(self, direction):
        # Get current font size
        current_width = self.root.winfo_width()
        current_height = self.root.winfo_height()
        self.root.geometry(f"{current_width}x{current_height}")
        old_font = self.text_area.cget("font")
        tmp_args = old_font.split(" ")
        if direction == 1:
            new_size = int(tmp_args[-1]) + 1
        else:
            new_size = int(tmp_args[-1]) - 1
        new_font = " ".join(tmp_args[:-1]).replace(f'{chr(92)}','')
        self.text_area.configure(font=(new_font, new_size))
        self.root.geometry(f"{current_width}x{current_height}")
    
    def increment_scroll_wheel(self, direction):
        # Increment if the scroll wheel is moved up or down.
        if direction == 1:
            self.text_area.yview_scroll(1, 'units')
        else:
            self.text_area.yview_scroll(-1, 'units')
        pass
        
    def scroll_to_bottom(self):
        self.text_area.see(tk.END)
        
    def create_context_menus(self):
        # Create context menus
        self.text_area_menu = tk.Menu(self.text_area, tearoff=0)
        self.text_area_menu.add_command(label="Copy", command=self.copy_text)
        self.text_area_menu.add_separator()
        
        self.text_area_menu.add_command(label="Kick", command=self.kick_user)
        self.text_area_menu.add_command(label="Ban", command=self.ban_user)
        self.text_area_menu.add_command(label="Whois", command=self.whois_user)
        self.text_area_menu.add_command(label="Send File", command=self.send_file)
        
        self.nickname_list_menu = tk.Menu(self.nickname_listbox, tearoff=0)
        self.nickname_list_menu.add_command(label="Kick", command=self.kick_user)
        self.nickname_list_menu.add_command(label="Ban", command=self.ban_user)
        self.nickname_list_menu.add_command(label="Whois", command=self.whois_user)
        self.nickname_list_menu.add_command(label="Send File", command=self.send_file)
        
        # ChanServ commands
        self.chanserv_menu = tk.Menu(self.text_area_menu, tearoff=0)
        self.chanserv_menu.add_command(label="Register Channel", command=self.chanserv_register)
        self.chanserv_menu.add_command(label="Identify Channel", command=self.chanserv_identify)
        self.chanserv_menu.add_command(label="Set Channel", command=self.chanserv_set)
        self.chanserv_menu.add_command(label="Ban Channel", command=self.chanserv_ban)
        self.chanserv_menu.add_command(label="Kick Channel", command=self.chanserv_kick)
        self.chanserv_menu.add_command(label="Unban Channel", command=self.chanserv_unban)
        self.chanserv_menu.add_command(label="Invite Channel", command=self.chanserv_invite)
        
        # NickServ commands
        self.nickserv_menu = tk.Menu(self.text_area_menu, tearoff=0)
        self.nickserv_menu.add_command(label="Register Nickname", command=self.nickserv_register)
        self.nickserv_menu.add_command(label="Identify Nickname", command=self.nickserv_identify)
        self.nickserv_menu.add_command(label="Set Nickname", command=self.nickserv_set)
        self.nickserv_menu.add_command(label="Ghost Nickname", command=self.nickserv_ghost)
        self.nickserv_menu.add_command(label="Recover Nickname", command=self.nickserv_recover)
        self.nickserv_menu.add_command(label="Group Nickname", command=self.nickserv_group)
        
        # Add ChanServ and NickServ menus to text area menu
        self.text_area_menu.add_cascade(label="ChanServ", menu=self.chanserv_menu)
        self.text_area_menu.add_cascade(label="NickServ", menu=self.nickserv_menu)
        
        # Bind right-click events to show context menus
        self.text_area.bind("<Button-3>", self.show_text_area_menu)
        self.nickname_listbox.bind("<Button-3>", self.show_nickname_list_menu)
        
        old_font = self.text_area.cget("font")
        
        self.text_area_menu.configure(font=old_font, background="#36454f", foreground="#eeeeee", borderwidth=0)
        self.nickname_list_menu.configure(font=old_font, background="#36454f", foreground="#eeeeee", borderwidth=0)
        self.chanserv_menu.configure(font=old_font, background="#36454f", foreground="#eeeeee", borderwidth=0)
        self.nickserv_menu.configure(font=old_font, background="#36454f", foreground="#eeeeee", borderwidth=0)
    
    def show_text_area_menu(self, event):
        try:
            self.text_area_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.text_area_menu.grab_release()
    
    def show_nickname_list_menu(self, event):
        try:
            self.nickname_list_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.nickname_list_menu.grab_release()
    
    @staticmethod
    def copy_text():
        print("Copy text")
    
    @staticmethod
    def kick_user():
        print("Kick user")
    
    @staticmethod
    def ban_user():
        print("Ban user")
    
    @staticmethod
    def whois_user():
        print("Whois user")
    @staticmethod
    def send_file():
        print("Send file")
    
    @staticmethod
    def chanserv_register():
        print("ChanServ: Register Channel")
    
    @staticmethod
    def chanserv_identify():
        print("ChanServ: Identify Channel")
    
    @staticmethod
    def chanserv_set():
        print("ChanServ: Set Channel")
    
    @staticmethod
    def chanserv_ban():
        print("ChanServ: Ban Channel")
    
    @staticmethod
    def chanserv_kick():
        print("ChanServ: Kick Channel")
    
    @staticmethod
    def chanserv_unban():
        print("ChanServ: Unban Channel")
    
    @staticmethod
    def chanserv_invite():
        print("ChanServ: Invite Channel")
    
    @staticmethod
    def nickserv_register():
        print("NickServ: Register Nickname")
    
    @staticmethod
    def nickserv_identify():
        print("NickServ: Identify Nickname")
    
    @staticmethod
    def nickserv_set():
        print("NickServ: Set Nickname")
    
    @staticmethod
    def nickserv_ghost():
        print("NickServ: Ghost Nickname")
    
    @staticmethod
    def nickserv_recover():
        print("NickServ: Recover Nickname")
    
    @staticmethod
    def nickserv_group():
        print("NickServ: Group Nickname")
        
    def download_and_display_image(self, url):
        if not url:
            return
        response = requests.get(url)
        image_data = BytesIO(response.content)
        image = Image.open(image_data)
        tk_image = ImageTk.PhotoImage(image)
        self.text_area.image_create(tk.END, image=tk_image)
        self.text_area.insert(tk.END, "\n")
        print(f"Downloaded and displayed image: {url}")
        
    def make_buffer_display_labels(self):
        # Clear any existing labels
        for label in self.response_buffer_labels:
            label.destroy()
        self.response_buffer_labels = []
        i = 0
        for buffer_name in self.response_buffers:
            label = tk.Label(
                self.status_frame,
                text=buffer_name,
                bd=1,
                relief=tk.SUNKEN,
                padx=5,
                pady=2,
            )
            if i == self.viewing_buffer_index:
                label.config(bg="lightblue")
            else:
                label.config(bg="lightgray")
            label.grid(row=0, column=i+2, sticky=tk.W, padx=5, pady=5)
            self.response_buffer_labels.append(label)
            i += 1
            
    def update_buffer_display_labels(self):
        self.make_buffer_display_labels()

    def open_settings(self):
        self.settings_window(self.root, self.details_manager, self.server_details, self.proxy_details)

    def update_settings_with_selected_server(self, event):
        _ = event
        selected_server = self.server_var.get()
        for server in self.details_manager.get_server_list():
            if server["server"] == selected_server:
                self.details_manager.set_server_details(server)
                break

    def toggle_connection(self):
        if self.connected:
            self.disconnect()
        else:
            self.active_details = self.details_manager.get_active_details()
            if self.active_details is not None:
                
                self.connect()
            else:
                print("Manage your settings and try again. No active details found.")
                return

    def configure_status_label(self, text, fg):
        self.status_label.config(text=text, fg=fg)

    def configure_connect_button(self, text):
        self.connect_button.config(text=text)

    def connect(self):
        if self.connected:
            return
        try:
            active_details = self.details_manager.get_active_details()
            if active_details is None:
                self.status_label.config(text="No server details", fg="red")
                return
            self.server_name = active_details["server"]
            self.server = active_details["server"]
            self.port = int(active_details["port"])
            use_ssl = active_details["ssl"]
            self.nickname = active_details["nickname"]
            username = active_details["username"]
            realname = active_details["realname"]
            auto_connect = active_details["auto_connect"]
            
            #print(f"Connecting to {self.server} on port {self.port}")
            
            #self.irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #self.irc_socket.connect((self.server, self.port))
            
            if self.details_manager.is_proxy_enabled() is True:
                # Set up proxy if enabled
                proxy_details = active_details["proxy_details"]
                proxy_type = proxy_details.get("type", "").lower()
                proxy_host = proxy_details.get("host", "")
                proxy_port = int(proxy_details.get("port", 0))
                if proxy_type == "socks5":
                    import socks
                    self.irc_socket = socks.socksocket()
                    self.irc_socket.set_proxy(socks.SOCKS5, proxy_host, proxy_port)
                elif proxy_type == "http":
                    self.irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    proxy_connect_str = f"CONNECT {self.server}:{self.port} HTTP/1.1\r\n\r\n"
                    self.irc_socket.connect((proxy_host, proxy_port))
                    self.irc_socket.sendall(proxy_connect_str.encode("utf-8"))
                    response = self.irc_socket.recv(4096)
                    if b"200 Connection established" not in response:
                        raise Exception("Failed to connect via HTTP proxy")
                else:
                    self.irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            else:
                # Connect without proxy
                self.irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
                print(self.server, self.port)
                self.irc_socket.connect((self.server, int(self.port)))

            # Wrap socket if SSL is enabled
            if use_ssl:
                context = ssl.create_default_context()
                self.irc_socket = context.wrap_socket(
                    self.irc_socket, server_hostname=self.server
                )
            self.connected = True
            self.status_label.config(text="Connected", fg="green")
            self.connect_button.config(text="Disconnect")
            self.response_buffers["Status"] += f"server - Connected to {self.server}:{self.port}\n"
            self.send_irc_message(f"NICK {self.nickname}")
            self.send_irc_message(f"USER {username} 0 * :{realname}")
            threading.Thread(target=self.receive_messages, daemon=True).start()
        except Exception as e:
            self.status_label.config(text=f"Connection failed: {e}", fg="red")
            if self.show_tracback_results is False:
                self.response_buffers["Status"] += f"error - Connection failed: {e}\n"
            else:
                self.response_buffers["Status"] += f"error - Connection failed: {e}\n{traceback.print_exc(e)}\n"
            
            traceback.print_exc(e)
            self.update_text_area()
            self.connected = False

    @staticmethod
    def get_project_dir():
        root_path = os.path.dirname(os.path.abspath(__file__))
        
        #root_path = root_path.replace("/src","")
        #print(root_path)
        logging.info("Dir: {root_path}")
        #return os.path.dirname(os.path.abspath(root_path))
        return root_path
    

    def disconnect(self):
        if not self.connected:
            return
        try:
            self.send_irc_message("QUIT :Client disconnected")
            self.irc_socket.close()
        except Exception as e:
            self.response_buffers["Status"] += f"server - Error during disconnection: {e}\n"
        finally:
            self.connected = False
            self.status_label.config(text="Disconnected", fg="red")
            self.connect_button.config(text="Connect")
            if self.show_tracback_results is False:
                self.response_buffers["Status"] += "server - Disconnected from server\n"
            else:
                self.response_buffers["Status"] += f"server - Disconnected from server\n{traceback.print_exc()}\n"
            traceback.print_exc()
            self.update_text_area()

    def send_irc_message(self, message):
        if self.connected:
            try:
                try:
                    self.irc_socket.send((message + "\r\n").encode("utf-8"))
                except ConnectionError as e:
                    if self.show_tracback_results is False:
                        self.response_buffers["Status"] += f"error - Failed to send message connection error: {e}\n"
                    else:
                        self.response_buffers["Status"] += f"error - Failed to send message connection error: {e}\n{traceback.print_exc()}\n"
                    traceback.print_exc()
                    self.update_text_area()
            except Exception as e:
                if self.show_tracback_results is False:
                    self.response_buffers["Status"] += f"error - Failed to send message: {e}\n"
                else:
                    self.response_buffers["Status"] += f"error - Failed to send message: {e}\n{traceback.print_exc()}\n"
                traceback.print_exc()
                self.update_text_area()

    def receive_messages(self):
        while self.connected:
            try:
                response = self.irc_socket.recv(4096).decode("utf-8")
                if not response:
                    break
                self.handle_irc_response(response)
            except Exception as e:
                if self.show_tracback_results is False:
                    self.response_buffers["Status"] += f"error - Error receiving message: {e}\n"
                else:
                    self.response_buffers["Status"] += f"error - Error receiving message: {e}\n{traceback.print_exc()}\n"
                traceback.print_exc()
                self.update_text_area()
                break
        self.disconnect()

    def handle_irc_response(self, response):
        lines = response.split("\r\n")
        for line in lines:
            if line:
                # self.response_buffers["Status"] += line + "\n"
                # self.update_text_area()
                self.parse_irc_message(line)

    def parse_irc_message(self, message):
        if message.startswith("PING"):
            self.send_irc_message("PONG " + message.split()[1])
            tag = "ping"
            self.response_buffers["Status"] += f"{tag} - PING PONG\n"
            buffer_keys = list(self.response_buffers.keys())
            buffer_name = buffer_keys[self.viewing_buffer_index]
            if buffer_name == "Status":
                self.update_text_area()   
            return
        else:
            if self.show_username_addresses is False:
                prefix = f"{message.split('!')[0]}"
                command = message.split()[1]
                params = message.split()[2:]

            else:
                prefix, command, params = self.split_irc_message(message)
                
            if command == "PRIVMSG":
                target = params[0]
                msg = " ".join(params[1:])
                buffer_keys = list(self.response_buffers.keys())
                buffer_name = buffer_keys[self.viewing_buffer_index]
                if target.startswith("#"):
                    tag = "channel"
                    
                    if f"discord @ #{buffer_name.replace('#', '')}:" in message or 'channel - discord!~u@' in message:
                        youtube_match = re.search(r'https://www.youtube.com/watch\?v=\S+', message)
                        youtube_match_two = re.search(r'https://www.youtube.com/embed/\S+', message)
                        
                        if youtube_match:
                            url = youtube_match.group(0)
                            self.generate_youtube_embedded_code(url)
                        
                        if youtube_match_two:
                            url = youtube_match_two.group(0)
                            self.generate_youtube_embedded_code(url)
                    
                    if f"discord @ #{buffer_name.replace('#', '')}:" in message or 'channel - discord!~u@' in message:
                        match = re.search(r'https://media.discordapp.net/stickers/\S+', message)
                        
                        # match = re.search(r'https://media.discordapp.net/stickers/[^\s]+', message)
                        # [^\s]
                        if match:
                            url = match.group(0)
                            self.download_and_display_image(url)
                    self.response_buffers[target.replace("#", "")] += f"{tag} - {prefix}: {msg}\n"
                else:
                    tag = "private"
                    if f"discord @ #{buffer_name.replace('#', '')}:" in message or 'channel - discord!~u@' in message:
                        youtube_match = re.search(r'https://www.youtube.com/watch\?v=\S+', message)
                        youtube_match_two = re.search(r'https://www.youtube.com/embed/\S+', message)
                        
                        if youtube_match:
                            url = youtube_match.group(0)
                            self.generate_youtube_embedded_code(url)
                        
                        if youtube_match_two:
                            url = youtube_match_two.group(0)
                            self.generate_youtube_embedded_code(url)
                    
                    if f"discord @ #{buffer_name.replace('#', '')}:" in message or 'channel - discord!~u@' in message:
                        match = re.search(r'https://media.discordapp.net/stickers/\S+', message)
                        
                        # match = re.search(r'https://media.discordapp.net/stickers/[^\s]+', message)
                        # [^\s]
                        if match:
                            url = match.group(0)
                            self.download_and_display_image(url)

                    self.response_buffers[target.replace("#", "")] += f"{tag} - {prefix} (private): {msg}\n"

            elif command == "NOTICE":
                target = params[0]
                msg = " ".join(params)
                tag = "notice"
                self.response_buffers[target.replace("#", "")] += f"{tag} - {prefix}: {msg}\n"

            elif command == "JOIN":
                channel = params[0][1:]
                if channel not in self.response_buffers:
                    self.response_buffers[channel.replace("#", "")] = ""
                    self.viewing_buffer_index = len(self.response_buffers) - 1
                tag = "join"
                self.response_buffers[channel.replace("#", "")] += f"{tag} - {prefix} has joined {channel}\n"
                self.update_buffer_display_labels()

            elif command == "PART":
                buffer_keys = list(self.response_buffers.keys())
                buffer_name = buffer_keys[self.viewing_buffer_index]
                channel = params[0][1:]
                tag = "part"

                if self.response_buffers[buffer_name]:
                    self.response_buffers[buffer_name] += f"{tag} - {prefix} has left {channel}\n"

            elif command == "QUIT":
                buffer_keys = list(self.response_buffers.keys())
                buffer_name = buffer_keys[self.viewing_buffer_index]
                msg = " ".join(params)
                tag = "quit"
                self.response_buffers[buffer_name] += f"{tag} - {prefix} has quit: {msg}\n"

            elif command == "KICK":
                channel = params[0][1:]
                target = params[1]
                msg = " ".join(params[2:])
                tag = "kick"
                self.response_buffers[channel.replace("#", "")] += f"{tag} - {prefix} has kicked {target} from {channel}: {msg}\n"

            elif command == "MODE":
                target = params[0]
                mode = " ".join(params[1:])
                tag = "mode"
                self.response_buffers[target.replace("#", "")] += f"{tag} - {prefix} set mode {mode} on {target}\n"

            elif command == "TOPIC":
                channel = params[0][1:]
                topic = " ".join(params[1:])
                tag = "topic"
                self.response_buffers[channel.replace("#", "")] += f"{tag} - {prefix} has changed the topic of {channel} to: {topic}\n"

            elif command == "NICK":
                buffer_keys = list(self.response_buffers.keys())
                buffer_name = buffer_keys[self.viewing_buffer_index]
                new_nick = params[0][1:]
                tag = "nick"
                self.response_buffers[buffer_name] += f"{tag} - {prefix} is now known as {new_nick}\n"

            elif command == "433":
                buffer_keys = list(self.response_buffers.keys())
                buffer_name = buffer_keys[self.viewing_buffer_index]
                tag = "error"
                self.response_buffers[buffer_name] += f"{tag} - Error: Nickname is already in use\n"

            else:
                tag = "server"
                # channel = params[0][0:].replace("#", "")
                buffer_keys = list(self.response_buffers.keys())
                buffer_name = buffer_keys[self.viewing_buffer_index]
                parsed_msg = message
                if self.show_server_addresses is False:
                    # TODO fix if this the set to true nickname list cannot load.
                    if message.startswith(f":{self.server}"):
                        # remove everything before the second :
                        # if more then one : exists in the message, remove everything before the second :
                        if message.count(":") > 1:
                            parsed_msg = message.split(":", 2)[2]
                            #print(self.show_server_addresses, "parsed", parsed_msg)
                        else:
                            parsed_msg = message
                    else:
                        parsed_msg = message
                    
                if buffer_name != "Status":
                    self.response_buffers["Status"] += f"{tag} - {parsed_msg}\n"
                    self.update_nickname_list_from_buffer("Status")
                    self.update_buffer_display_labels()
                    self.update_text_area()
                    return
                else:
                    self.response_buffers["Status"] += f"{tag} - {parsed_msg}\n"
                    self.update_nickname_list_from_buffer("Status")
                    

        self.update_buffer_display_labels()
        self.update_text_area()
    
    def generate_youtube_embedded_code(self, url):
        video_id = self.extract_youtube_video_id(url)
        if video_id:
            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
            self.display_thumbnail(thumbnail_url, url)

    @staticmethod
    def extract_youtube_video_id(url):
        pattern = re.compile(r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^\s&]+)')
        match = pattern.search(url)
        if match:
            return match.group(1)
        return None

    def display_thumbnail(self, thumbnail_url, video_url):
        response = requests.get(thumbnail_url)
        img_data = response.content
        image = Image.open(BytesIO(img_data))
        image.thumbnail((120, 90))  # Adjust thumbnail size if necessary
        photo = ImageTk.PhotoImage(image)

        self.text_area.image_create(tk.END, image=photo)
        self.text_area.insert(tk.END, "\n")
        self.text_area.image = photo  # Keep a reference to avoid garbage collection

        self.text_area.tag_bind(photo, '<Button-1>', lambda e: webbrowser.open(video_url))

    def update_nickname_list_from_buffer(self, buffer_name):
        # Retrieve the nickname list from the response buffer
        buffer_content = self.response_buffers[buffer_name]
        lines = buffer_content.split("\n")
        nicklist_line = []
        for line in lines:
            buffer_keys = list(self.response_buffers.keys())
            current_buffer = buffer_keys[self.viewing_buffer_index]
            if current_buffer == buffer_name:
                #print("Skipping status buffer? clearing visible nicklist gui item")
                self.nickname_listbox.delete(0, tk.END)
                break
            
            if (line.startswith(f":{self.server} 353 {self.nickname} = #{current_buffer} :") or
                    line.startswith(f"server - :{self.server} 353 {self.nickname} = #{current_buffer} :") or
                    line.startswith(f":{self.server} 353 {self.nickname} = #{current_buffer} ") or
                    line.startswith(f"server - :{self.server} 353 {self.nickname} = #{current_buffer} ")):
                nicklist_line.append(line)
                break

            if line.endswith(f"End of NAMES list"):
                break
                
        if nicklist_line is not None and len(nicklist_line) > 0:
            if nicklist_line[len(nicklist_line) - 1] != "":
                nicknames = nicklist_line[len(nicklist_line) - 1].split(":")[2].split()
                self.nickname_buffers[buffer_name] = []
                for nickname in nicknames:
                    self.nickname_buffers[buffer_name].append(nickname)
                self.populate_from_nickname_buffer(buffer_name)
    
    def populate_from_nickname_buffer(self, buffer_name):
        self.nickname_listbox.delete(0, tk.END)
        self.nickname_colors[buffer_name] = []
        
        # use a 8 bit color to assign colors to the self.nickname_colors list.
        # then apply the color to the font of the self.nickname_listbox nickname items
        # self.nickname_listbox is a tk.Listbox
        
        for buffer in self.nickname_buffers:
            for nickname in self.nickname_buffers[buffer]:
                nick_color = self.get_color_for_nickname()
                self.nickname_colors[buffer_name].append(nick_color)
                self.nickname_listbox.insert(tk.END, nickname)
                self.nickname_listbox.itemconfig(tk.END, foreground=f"{nick_color}")
                self.nickname_listbox.see(tk.END)
                
    @staticmethod
    def get_color_for_nickname():
        # Generate a random 8-bit color (0 to 255)
        random_color = "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        return random_color
    
    @staticmethod
    def split_irc_message(message):
        prefix = ""
        trailing = []
        if not message:
            raise Exception("Empty line.")
        if message[0] == ":":
            prefix, message = message[1:].split(" ", 1)
        if message.find(" :") != -1:
            message, trailing = message.split(" :", 1)
            args = message.split()
            args.append(trailing)
        else:
            args = message.split()
        command = args.pop(0)
        return prefix, command, args

    def send_message(self, event=None):
        # Send a message to the server
        _ = event
        message = self.entry.get().strip()
        if message and self.connected:
            buffer_name = list(self.response_buffers.keys())[self.viewing_buffer_index]

            if message.startswith("/join "):
                channel = message.split(" ")[1]
                if not channel.startswith("#"):
                    channel = f"#{channel}"
                
                self.send_irc_message(f'JOIN #{channel.replace("#", "")}')
            elif message == "/close":
                self.close_current_buffer()
            elif message.startswith("/nick "):
                nickname = message.split(" ")[1]
                self.send_irc_message(f"NICK {nickname}")
            elif message.startswith("/topic "):
                topic = message.split(" ")[1]
                self.send_irc_message(f"TOPIC #{buffer_name} :{topic}")
            elif message.startswith("/mode "):
                mode = message.split(" ")[1]
                self.send_irc_message(f"MODE #{buffer_name} {mode}")
            elif message.startswith("/nickserv "):
                nickserv = message.split(" ")[1]
                self.send_irc_message(f"NICKSERV {nickserv}")
            elif message.startswith("/chanserv "):
                chanserv = message.split(" ")[1]
                self.send_irc_message(f"CHANSERV {chanserv}")
            elif message.startswith("/whois "):
                whois = message.split(" ")[1]
                self.send_irc_message(f"WHOIS {whois}")
            elif message.startswith("/who "):
                who = message.split(" ")[1]
                self.send_irc_message(f"WHO {who}")
            elif message.startswith("/away "):
                away = message.split(" ")[1]
                self.send_irc_message(f"AWAY :{away}")
            elif message == "/quit":
                self.send_irc_message("QUIT")
            elif message == "/help":
                self.response_buffers[buffer_name] += f"private - {self.nickname} - #{buffer_name}: {message}\n"
                self.send_irc_message(f"PRIVMSG #{buffer_name} :/help")
            elif message == "/whoami":
                self.response_buffers[buffer_name] += f"private - {self.nickname} - #{buffer_name}: {message}\n"
                self.send_irc_message(f"PRIVMSG #{buffer_name} :/whoami")
            else:
                self.response_buffers[buffer_name] += f"private - {self.nickname} - #{buffer_name}: {message}\n"
                self.send_irc_message(f"PRIVMSG #{buffer_name} :{message}")

            self.update_text_area()
            self.entry.delete(0, tk.END)
    
    def update_text_area1(self):
        # Update from buffer to add colors to self.text_area
        buffer_name = list(self.response_buffers.keys())[self.viewing_buffer_index].replace("#", "")
        
        text_content = self.response_buffers[buffer_name]
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        
        # Split the content and apply tags
        for line in text_content.split("\n"):
            if line:
                parts = line.split(" - ", 1)
                if len(parts) == 2:
                    current_tag, message = parts
                    self.text_area.insert(tk.END, f'{line.replace("channel - :", "").replace("server - :", "")}\n', current_tag, )
                else:
                    self.text_area.insert(tk.END, f'{line.replace("channel - :", "").replace("server - :", "")}\n', )  # No tag applied for this line
                    
        for index, nickname in enumerate(self.nickname_listbox.get(0, tk.END)):
            if re.match(r'^' + re.escape(nickname) + r'', self.text_area.get("1.0", tk.END)):
                # color from the stat of the nickname to the length of only the nickname
                text_color = self.nickname_colors[buffer_name][index]
                self.text_area.tag_add(text_color, f"{index + 1}.0", f"{index + 1}.{len(nickname)}")
            else:
                random_color = self.get_color_for_nickname()
                self.text_area.tag_add(random_color, f"{index + 1}.0", f"{index + 1}.{len(nickname)}")
            
        self.text_area.update_idletasks()
        self.text_area.config(state=tk.DISABLED)
        self.text_area.yview(tk.END)
    
    def update_text_area2(self):
        # Update from buffer to add colors to self.text_area
        buffer_name = list(self.response_buffers.keys())[self.viewing_buffer_index].replace("#", "")
        text_content = self.response_buffers[buffer_name]
        current_content = self.text_area.get("1.0", tk.END).splitlines()
        new_lines = text_content.split("\n")
        # self.text_area.delete(1.0, tk.END)
        
        
        # Find the difference and update only the new lines
        if len(current_content) < len(new_lines):
            self.text_area.config(state=tk.NORMAL)
            for line in new_lines[len(current_content):]:
                if line:
                    parts = line.split(" - ", 1)
                    if len(parts) == 2:
                        current_tag, message = parts
                        self.text_area.insert(tk.END, f'{line.replace("channel - :", "").replace("server - :", "")}\n', current_tag)
                    else:
                        self.text_area.insert(tk.END, f'{line.replace("channel - :", "").replace("server - :", "")}\n')  # No tag applied for this line
            self.text_area.config(state=tk.DISABLED)
            self.text_area.yview(tk.END)
    
    def populate_text_area(self):
        # Update from buffer to add colors to self.text_area
        buffer_name = list(self.response_buffers.keys())[self.viewing_buffer_index].replace("#", "")
        text_content = self.response_buffers[buffer_name]
        
        self.nickname_listbox.delete(1.0, tk.END)
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        # Split the content and apply tags
        for line in text_content.split("\n"):
            if line:
                parts = line.split(" - ", 1)
                                
                if len(parts) == 2:
                    if parts[0] == "channel - :" and parts[1] not in self.nickname_listbox.get(0, tk.END):
                        self.nickname_listbox.insert(tk.END, parts[0])
                        #self.text_area.insert(tk.END, f'{self.line.replace("channel - :", "").replace("server - :", "")}\n', self.nick_tag,)
                    
                    self.part_len = len(parts)
                    self.nick_tag, message = parts
                    #print("two part:", parts[0])
                    if parts[0] == "channel":
                        self.last_line = line
                        self.text_area.insert(tk.END, f'{self.last_line.replace("channel - :", "").replace("server - :", "")}\n', self.nick_tag,)
                        print("NICAK TAG:",self.nick_tag)
                    elif parts[0] == "server":
                        self.last_line = line
                        self.text_area.insert(tk.END, f'{self.last_line.replace("server - :", "").replace("server - :", "")}\n', self.nick_tag,)
                    elif parts[0] == "ping":
                        self.last_line = line
                        self.text_area.insert(tk.END, f'{self.last_line.replace("ping - :", "").replace("server - :", "")}\n', self.nick_tag,)
                    elif parts[0] == None or parts[0] == "None" or parts[0] == "error":
                        
                        self.last_line = line
                        self.text_area.insert(tk.END, f'{self.last_line.replace("ping - :", "").replace("server - :", "")}\n', self.nick_tag,)

                else:
                    #print("populate line:", line)
                    self.part_len = len(parts)
                    #print("not two parts", parts[0])
                    if parts[0] == None or parts[0] == "None" or parts[0] == "error":
                        self.last_line = line
                    else:
                        self.last_line = line
                    
                    self.text_area.insert(tk.END, f'{self.last_line.replace("channel - :", "").replace("server - :", "")}\n', self.nick_tag,)


                # iterate self.nickname_listbox get the text color of each item. match the nickname to the color and apply the color to
                # the font of the matching text for the self.text_line
                text_color = ""
#                for index, nickname in enumerate(self.nickname_listbox.get(0, tk.END)):
#                    
#                    if len(parts) > 2:
#                        if nickname == parts[0] or nickname == parts[1]:
#                            text_color = self.nickname_colors[buffer_name][index]
#                            self.nickname_buffers[buffer_name].append(nickname)
#                            self.populate_from_nickname_buffer(buffer_name)
#                        else:
#                            text_color = self.nickname_colors[buffer_name][index]
#                            self.nickname_buffers[buffer_name].append(nickname)
#                            self.populate_from_nickname_buffer(buffer_name)
#                    else:
#                        if nickname == parts[0]:
#                            text_color = self.nickname_colors[buffer_name][index]
#                            self.nickname_buffers[buffer_name].append(nickname)
#                            self.populate_from_nickname_buffer(buffer_name)
#                        else:
#                            text_color = self.nickname_colors[buffer_name][index]
#                            self.nickname_buffers[buffer_name].append(nickname)
#                            self.populate_from_nickname_buffer(buffer_name)
#
#
#                    # Get the content of the text widget as a string
#                    # text_content = self.text_area.get("1.0", tk.END)
#                    match = re.search(r'\b' + re.escape(nickname) + r'\b', text_content)
#                    print("matching:", match)
#                    if match:
#                        start_index = match.start()
#                        end_index = match.end()
#                        start_line = text_content.count("\n", 0, start_index) + 1
#                        start_column = start_index - text_content.rfind("\n", 0, start_index)
#                        end_line = text_content.count("\n", 0, end_index) + 1
#                        end_column = end_index - text_content.rfind("\n", 0, end_index)
#                        
#                        self.text_area.tag_add(text_color, f"{start_line}.{start_column}", f"{end_line}.{end_column}")
#                    else:
#                        random_color = self.get_color_for_nickname()
#                        self.text_area.tag_add(random_color, f"{index + 1}.0", f"{index + 1}.{len(nickname)}")
#
#                if len(parts) == 2:
#                    self.part_len = len(parts)
#                    self.nick_tag, message = parts
#                    print("two part:", parts[0])
#                    if parts[0] == "channel":
#                        self.last_line = line
#                        self.text_area.insert(tk.END, f'{self.last_line.replace("channel - :", "").replace("server - :", "")}\n', self.nick_tag,)
#                        print(self.nick_tag)
#                    elif parts[0] == "server":
#                        self.last_line = line
#                        self.text_area.insert(tk.END, f'{self.last_line.replace("server - :", "").replace("server - :", "")}\n', self.nick_tag,)
#                    elif parts[0] == "ping":
#                        self.last_line = line
#                        self.text_area.insert(tk.END, f'{self.last_line.replace("ping - :", "").replace("server - :", "")}\n', self.nick_tag,)
#                    elif parts[0] == None or parts[0] == "None" or parts[0] == "error":
#                        
#                        self.last_line = line
#                        self.text_area.insert(tk.END, f'{self.last_line.replace("ping - :", "").replace("server - :", "")}\n', self.nick_tag,)
#
#                else:
#                    print("populate line:", line)
#                    self.part_len = len(parts)
#                    #print("not two parts", parts[0])
#                    if parts[0] == None or parts[0] == "None" or parts[0] == "error":
#                        self.last_line = line
#                    else:
#                        self.last_line = line
#                    
#                    self.text_area.insert(tk.END, f'{self.last_line.replace("channel - :", "").replace("server - :", "")}\n', self.nick_tag,)
       
        self.text_area.config(state=tk.DISABLED)
        self.text_area.yview(tk.END)

    def update_text_area(self):
        # Update from buffer to add colors to self.text_area
        buffer_name = list(self.response_buffers.keys())[self.viewing_buffer_index].replace("#", "")
        text_content = self.response_buffers[buffer_name]
        self.text_area.config(state=tk.NORMAL)
        # self.text_area.delete(1.0, tk.END)
        # Split the content and apply tags
        for line in text_content.split("\n"):
            if line:
                parts = line.split(" - ", 1)

                if parts[0] == "channel - :" and parts[1] not in self.nickname_listbox.get(0, tk.END):
                    self.nickname_listbox.insert(tk.END, parts[0])

                # iterate self.nickname_listbox get the text color of each item. match the nickname to the color and apply the color to
                # the font of the matching text for the self.text_line
                text_color = ""
                if self.nickname_listbox:
                    for index, nickname in enumerate(self.nickname_listbox.get(0, tk.END)):
                        
                        if len(parts) >= 2:
                            if nickname == parts[0] or nickname == parts[1]:
                                text_color = self.nickname_colors[buffer_name][index]
                                self.nickname_buffers[buffer_name].append(nickname)
                                self.populate_from_nickname_buffer(buffer_name)
                        else:
                            if nickname == parts[0]:
                                text_color = self.nickname_colors[buffer_name][index]
                                self.nickname_buffers[buffer_name].append(nickname)
                                self.populate_from_nickname_buffer(buffer_name)


                        # Get the content of the text widget as a string
                        # text_content = self.text_area.get("1.0", tk.END)
                        match = re.search(r'\b' + re.escape(nickname) + r'\b', text_content)
                    
                        if match:
                            start_index = match.start()
                            end_index = match.end()
                            start_line = text_content.count("\n", 0, start_index) + 1
                            start_column = start_index - text_content.rfind("\n", 0, start_index)
                            end_line = text_content.count("\n", 0, end_index) + 1
                            end_column = end_index - text_content.rfind("\n", 0, end_index)
                        
                            self.text_area.tag_add(text_color, f"{start_line}.{start_column}", f"{end_line}.{end_column}")
                        else:
                            random_color = self.get_color_for_nickname()
                            self.text_area.tag_add(random_color, f"{index + 1}.0", f"{index + 1}.{len(nickname)}")

                if len(parts) == 2:
                    self.part_len = len(parts)
                    self.nick_tag, message = parts
                    #print("two part:", parts[0], line)
                    self.last_line = line
                else:
                    self.part_len = len(parts)
                    #print("not two parts", parts[0])
                    self.last_line = line
        
        if self.part_len == 2:

            self.text_area.insert(tk.END, f'{self.last_line.replace("channel - :", "").replace("server - :", "")}\n', self.nick_tag,)
        else:

            self.text_area.insert(tk.END, f'{self.last_line.replace("channel - :", "").replace("server - :", "")}\n',)  # No tag applied for this line

        self.text_area.config(state=tk.DISABLED)
        self.text_area.yview(tk.END)
    
    def close_current_buffer(self):
        if len(self.response_buffers) > 1:
            buffer_keys = list(self.response_buffers.keys())
            removed_buffer = buffer_keys[self.viewing_buffer_index]

            self.send_irc_message(f"PART #{removed_buffer}")
            del self.response_buffers[removed_buffer]
            if self.viewing_buffer_index >= len(self.response_buffers):
                self.viewing_buffer_index = len(self.response_buffers) - 1

            self.update_text_area()
        else:
            self.text_area.config(text="")

    def request_nicklist(self, channel):
        self.send_irc_message(f"NAMES {channel}")

    def show_nickname_list(self):
        if self.new_nickname_side == 0:
            self.text_area.grid(row=1, column=1, sticky=tk.NSEW)
            self.nickname_listbox.grid(row=1, column=0, sticky=tk.NS)
            self.root.grid_columnconfigure(0, weight=0)
            self.root.grid_columnconfigure(1, weight=1)
        elif self.new_nickname_side == 1:
            self.text_area.grid(row=1, column=0, sticky=tk.NSEW)
            self.nickname_listbox.grid(row=1, column=1, sticky=tk.NS)
            self.root.grid_columnconfigure(0, weight=1)
            self.root.grid_columnconfigure(1, weight=0)
            
    def hide_nickname_list(self):
        self.nickname_listbox.grid_forget()
    
    def move_nickname_list(self, side):
        # Forget current grid positions
        self.text_area.grid_forget()
        self.nickname_listbox.grid_forget()
        
        # 0 == left side, 1 == right side
        
        if side == 0:
            self.text_area.grid(row=1, column=1, sticky=tk.NSEW)
            self.nickname_listbox.grid(row=1, column=0, sticky=tk.NS)
            self.root.grid_columnconfigure(0, weight=0)
            self.root.grid_columnconfigure(1, weight=1)
            self.new_nickname_side = 0
        elif side == 1:
            self.text_area.grid(row=1, column=0, sticky=tk.NSEW)
            self.nickname_listbox.grid(row=1, column=1, sticky=tk.NS)
            self.root.grid_columnconfigure(0, weight=1)
            self.root.grid_columnconfigure(1, weight=0)
            self.new_nickname_side = 1
            
            
if __name__ == "__main__":
    root = tk.Tk()
    app = CrudeIRC(root)
    root.mainloop()import os
import atexit
import ctypes
import hashlib
import random
import re
import socket
import ssl
import sys
import tkinter as tk
from tkinter import Menu
import webbrowser
from io import BytesIO
import requests
from src.settings_window import SettingsWindow
import threading
from src.server_details_manager import ServerDetailsManager
from crude_irc_logic import CrudeClientIRCLogic
from src.crude_proxy_bouncer import CrudeProxyBouncer
from src.crude_launch_writer import CrudeLaunchWriter
import traceback
import logging
import PIL
from PIL import Image, ImageTk

def hide_console():
    if sys.platform == "win32":
        print(ctypes.windll.kernel32.GetConsoleWindow())
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

def show_console():
    if sys.platform == "win32":
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 1)

def handle_exception(exc_type, exc_value, exc_traceback):
    show_console()
    # Print the exception details to the console
    if not issubclass(exc_type, KeyboardInterrupt):
        traceback.print_exception(exc_type, exc_value, exc_traceback)
    sys.__excepthook__(exc_type, exc_value, exc_traceback)
    # Exit the application after showing the console
    sys.exit(1)

def initialize_application(self):
    if self.hide_terminal_on_init:
        hide_console()
        # Register exception handler to show console on error
        sys.excepthook = handle_exception
        # Register exit handler to show console on application exit
        atexit.register(show_console)
        
class CrudeIRC:
    def __init__(self, main_app):
        self.logpath = self.get_project_dir()
        self.logger = logging.basicConfig(filename=f"'{self.logpath}/logs/logfile.log", level=logging.DEBUG, format="")
        self.colors = None
        
        self.hide_terminal_on_init = True  # Set this based on your configuration
        
        initialize_application(self)
        self.last_line = ""
        self.part_len = 0

        self.server_name = None
        self.new_nickname_side = 0
        self.no_distractions_state = True
        self.zen_mode_state = False
        self.showing_entry_frame = True
        self.showing_status_frame = True
        self.showing_menu = True
        self.root_frame = None
        self.root = main_app
        current_width = 200
        current_height = 100
        self.root.geometry(f"{current_width}x{current_height}")
        self.nerd_font = ("TkDefaultFont", 12) 
        # self.nerd_font = ("JetBrainsMono Nerd Font", 12)
        self.text_container = None
        self.text_area_menu = None
        self.nickname_list_menu = None
        self.chanserv_menu = None
        self.nickserv_menu = None
        self.port = None
        self.server = None
        self.nickname = None
        self.status_buffer_label = None
        self.viewing_buffer_index = 0
        self.response_buffer_labels = []
        self.response_buffers = {
            "Status": "",
        }
        self.nickname_buffers = {
            "Status": [],
        }
        self.nickname_colors = {
            "colors": [],
        }
        self.send_button = None
        self.entry = None
        self.entry_frame = None
        self.nickname_listbox = None
        self.text_area = None
        self.text_frame = None
        self.connect_button = None
        self.status_label = None
        self.status_frame = None
        self.window_menu = None
        self.file_menu = None
        self.menu_bar = None
        self.server_var = tk.StringVar()
        
        # current_width = self.root.winfo_width()
        # current_height = self.root.winfo_height()
        current_width = 800
        current_height = 400
        self.root.geometry(f"{current_width}x{current_height}")
        self.connected = False
        self.server_details = {
            'servers': {}
        }
        self.proxy_details = {
            'proxies': {}
        }
        self.details_manager = ServerDetailsManager(self, self.server_details, self.proxy_details)
        self.crude_launch_writer = CrudeLaunchWriter
        self.crude_proxy_bouncer = CrudeProxyBouncer
        self.settings_window = SettingsWindow
        
        self.make_buffer_display_labels()
        self.create_gui()
        self.irc_socket = None
        self.details_manager.load_server_details()
        self.details_manager.load_proxy_details()
        
        self.active_details = self.details_manager.get_active_details()
        # print("active details:",self.active_details)

        self.active_proxy_details = self.details_manager.get_active_proxy_details()
        
        #print(self.details_manager.get_active_details())
        self.show_tracback_results = self.active_details["show_traceback_results"]
        self.show_username_addresses = self.active_details["show_username_addresses"]
        self.show_server_addresses = self.active_details["show_server_addresses"]
        self.show_server_response_type = self.active_details["show_server_response_type"]
        
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)
        
    def generate_launch_scripts(self):
        self.crude_launch_writer(self.root, self.details_manager).write_bat_no_log()
        self.crude_launch_writer(self.root, self.details_manager).write_bat_with_log()
        self.crude_launch_writer(self.root, self.details_manager).write_sh_no_log()
        self.crude_launch_writer(self.root, self.details_manager).write_sh_with_log()
        self.crude_launch_writer(self.root, self.details_manager).write_create_shortcut()
    
    def open_proxy_bouncer(self):
        self.crude_proxy_bouncer.open_proxy_bouncer(self.crude_proxy_bouncer(self))
    
    def view_next_buffer(self):
        buffer_keys = list(self.response_buffers.keys())
        self.viewing_buffer_index = (self.viewing_buffer_index + 1) % len(buffer_keys)
        channel = buffer_keys[self.viewing_buffer_index]
        self.request_nicklist(channel)
        self.text_area.delete(1.0, tk.END)
        self.populate_text_area()

    def view_prior_buffer(self):
        buffer_keys = list(self.response_buffers.keys())
        self.viewing_buffer_index = (self.viewing_buffer_index - 1) % len(buffer_keys)
        channel = buffer_keys[self.viewing_buffer_index]
        self.request_nicklist(channel)
        self.text_area.delete(1.0, tk.END)
        self.populate_text_area()
    
    def create_gui(self):
        self.root.title("CrudeIRC")
        
        self.menu_bar = tk.Menu(self.root)
        #self.menu_bar.configure(background="#36454f", borderwidth=-1)
        self.root.config(menu=self.menu_bar)
        self.root.config(background="#36454f", borderwidth=0)
        
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Settings", command=self.open_settings)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)
        
        self.window_menu = tk.Menu(self.menu_bar, tearoff=0, font=self.nerd_font)
        self.menu_bar.add_cascade(label="Window", menu=self.window_menu)
        self.window_menu.add_command(label="Show Nickname List", command=self.show_nickname_list)
        self.window_menu.add_command(label="Hide Nickname List", command=self.hide_nickname_list)
        self.window_menu.add_command(label="Move Nickname List to Left", command=lambda: self.move_nickname_list(0))
        self.window_menu.add_command(label="Move Nickname List to Right", command=lambda: self.move_nickname_list(1))
        
        self.window_menu.configure(font=self.nerd_font, background="#36454f", foreground="#eeeeee", borderwidth=0)
        self.file_menu.configure(font=self.nerd_font, background="#36454f", foreground="#eeeeee", borderwidth=0)
        self.menu_bar.configure(font=self.nerd_font, background="#36454f", foreground="#eeeeee", borderwidth=0)
        
        # Window Setup
        self.status_frame = tk.Frame(self.root)
        self.status_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.status_frame.config(background="#36454f", borderwidth=-1, relief="flat")
        
        self.status_label = tk.Label(self.status_frame, text="Disconnected", fg="red")
        self.status_label.grid(row=0, column=1, sticky="w")
        self.status_label.configure(background="#36454f", foreground="#eeeeee", borderwidth=-1, relief="flat")
        self.make_buffer_display_labels()
        
        self.connect_button = tk.Button(self.status_frame, text="Connect", command=self.toggle_connection)
        self.connect_button.grid(row=0, column=0, sticky="e")
        self.connect_button.config(background="#36454f", foreground="#eeeeee", activebackground="#36454f", activeforeground="#eeeeee")
        
        self.text_area = tk.Text(self.root, state=tk.DISABLED, width=1, height=1)
        self.text_area.grid(row=1, column=0, sticky="nsew", padx=(5,0), pady=5)
        self.text_area.configure(font=self.nerd_font, wrap="word", background="#36454f", foreground="#eeeeee")
        
        
        self.nickname_listbox = tk.Listbox(self.root)
        self.nickname_listbox.grid(row=1, column=1, sticky="ns", padx=5, pady=5)
        self.nickname_listbox.configure(font=self.nerd_font, background="#36454f", foreground="#eeeeee", borderwidth=0, relief="flat")
        
        self.entry_frame = tk.Frame(self.root)
        self.entry_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=0)
        self.entry_frame.configure(background="#36454f", borderwidth=0, relief="flat")
        
        self.entry = tk.Entry(self.entry_frame)
        self.entry.grid(row=0, column=0, sticky="ew", padx=(5,0),pady=(0,5))
        self.entry.bind("<Return>", self.send_message)
        self.entry.configure(font=self.nerd_font, background="#36454f", foreground="#eeeeee", borderwidth=0, relief="flat")
        
        self.send_button = tk.Button(self.entry_frame, text="Send", command=self.send_message)
        self.send_button.grid(row=0, column=1, sticky="e", padx=(0,5), pady=(0,5))
        self.send_button.config(background="#36454f", foreground="#eeeeee", activebackground="#36454f", activeforeground="#eeeeee")
        
        self.entry_frame.grid_rowconfigure(0, weight=1)
        self.entry_frame.grid_columnconfigure(0, weight=1)
        
        # Define styles for different message types
        self.text_area.tag_configure("bold", font="TkDefaultFont 9 bold")
        self.text_area.tag_configure("ping", foreground="red")
        self.text_area.tag_configure("nickserv", foreground="magenta", background="lightgray", font="TkDefaultFont 9 bold")
        self.text_area.tag_configure("chanserv", foreground="green", background="lightgray", font="TkDefaultFont 9 bold")
        self.text_area.tag_configure("notice", foreground="purple", font="TkDefaultFont 9 italic")
        self.text_area.tag_configure("error", foreground="red", font="TkDefaultFont 9 bold")
        self.text_area.tag_configure("channel", foreground="black")
        self.text_area.tag_configure("private", foreground="white")
        self.text_area.tag_configure("join", foreground="green")
        self.text_area.tag_configure("part", foreground="orange")
        self.text_area.tag_configure("quit", foreground="red")
        self.text_area.tag_configure("kick", foreground="red", font="TkDefaultFont 9 bold")
        self.text_area.tag_configure("mode", foreground="blue")
        self.text_area.tag_configure("topic", foreground="cyan")
        self.text_area.tag_configure("nick", foreground="darkgreen")
        self.text_area.tag_configure("server", foreground="gray")
        
        # Bind keys for buffer navigation
        self.root.bind("<Control-Right>", lambda e: self.view_next_buffer())
        self.root.bind("<Control-Left>", lambda e: self.view_prior_buffer())
        
        # Bind scroll up +1
        self.root.bind("<Control-Up>", lambda e: self.increment_font(1))
        self.root.bind("<Control-Down>", lambda e: self.increment_font(-1))
        
        self.root.bind("<Up>", lambda e: self.increment_scroll_wheel(1))
        self.root.bind("<Down>", lambda e: self.increment_scroll_wheel(-1))
        
        # Bind F-keys
        self.root.bind("<F1>", lambda e: self.toggle_menu_visibility())
        self.root.bind("<F2>", lambda e: self.open_settings())
        self.root.bind("<F3>", lambda e: self.toggle_nickname_list_position())
        self.root.bind("<F4>", lambda e: self.toggle_nickname_list_visibility())
        # self.root.bind("<F5>", lambda e: self.toggle_status_bar())
        self.root.bind("<F5>", lambda e: self.no_distractions())
        self.root.bind("<F6>", lambda e: self.open_proxy_bouncer())
        # open_proxy_bouncer
        # Create context menus
        self.create_context_menus()
        
        # Configure grid weights to ensure resizing works correctly
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)
    
    
    def toggle_menu_visibility(self):
        #print(self.showing_menu)
        if  self.showing_menu is True:
            
            self.showing_menu = False
            self.root.config(menu="")
            self.root.update_idletasks()
        else:
            self.root.config(menu=self.menu_bar)
            self.showing_menu = not self.showing_menu
            
    def toggle_nickname_list_position(self):
        if self.nickname_listbox.winfo_ismapped() and self.nickname_listbox.grid_info()['column'] == 1:
            self.move_nickname_list(0)
        else:
            self.move_nickname_list(1)
    
    def toggle_nickname_list_visibility(self):
        if self.nickname_listbox.winfo_ismapped():
            self.hide_nickname_list()
        else:
            self.show_nickname_list()
    
    
    def no_distractions(self):
        if self.no_distractions_state is True:
            self.no_distractions_state = False
            self.showing_menu = self.no_distractions_state
            
            # self.status_frame.pack(side=tk.TOP, fill=tk.X)
            self.nickname_listbox.pack(side=tk.RIGHT, fill=tk.Y)
            self.entry_frame.pack(side=tk.LEFT, expand=True,fill=tk.X)
            self.root.config(menu=self.menu_bar)
            self.root.update_idletasks()
        else:
            
            self.no_distractions_state = True
            self.showing_menu = not self.showing_menu
            
            # self.status_frame.pack_forget()
            self.nickname_listbox.pack_forget()
            self.root.config(menu="")
            
            self.entry_frame.pack_forget()
            
            self.showing_status_frame = self.no_distractions_state

    def increment_font(self, direction):
        # Get current font size
        current_width = self.root.winfo_width()
        current_height = self.root.winfo_height()
        self.root.geometry(f"{current_width}x{current_height}")
        old_font = self.text_area.cget("font")
        tmp_args = old_font.split(" ")
        if direction == 1:
            new_size = int(tmp_args[-1]) + 1
        else:
            new_size = int(tmp_args[-1]) - 1
        new_font = " ".join(tmp_args[:-1]).replace(f'{chr(92)}','')
        self.text_area.configure(font=(new_font, new_size))
        self.root.geometry(f"{current_width}x{current_height}")
    
    def increment_scroll_wheel(self, direction):
        # Increment if the scroll wheel is moved up or down.
        if direction == 1:
            self.text_area.yview_scroll(1, 'units')
        else:
            self.text_area.yview_scroll(-1, 'units')
        pass
        
    def scroll_to_bottom(self):
        self.text_area.see(tk.END)
        
    def create_context_menus(self):
        # Create context menus
        self.text_area_menu = tk.Menu(self.text_area, tearoff=0)
        self.text_area_menu.add_command(label="Copy", command=self.copy_text)
        self.text_area_menu.add_separator()
        
        self.text_area_menu.add_command(label="Kick", command=self.kick_user)
        self.text_area_menu.add_command(label="Ban", command=self.ban_user)
        self.text_area_menu.add_command(label="Whois", command=self.whois_user)
        self.text_area_menu.add_command(label="Send File", command=self.send_file)
        
        self.nickname_list_menu = tk.Menu(self.nickname_listbox, tearoff=0)
        self.nickname_list_menu.add_command(label="Kick", command=self.kick_user)
        self.nickname_list_menu.add_command(label="Ban", command=self.ban_user)
        self.nickname_list_menu.add_command(label="Whois", command=self.whois_user)
        self.nickname_list_menu.add_command(label="Send File", command=self.send_file)
        
        # ChanServ commands
        self.chanserv_menu = tk.Menu(self.text_area_menu, tearoff=0)
        self.chanserv_menu.add_command(label="Register Channel", command=self.chanserv_register)
        self.chanserv_menu.add_command(label="Identify Channel", command=self.chanserv_identify)
        self.chanserv_menu.add_command(label="Set Channel", command=self.chanserv_set)
        self.chanserv_menu.add_command(label="Ban Channel", command=self.chanserv_ban)
        self.chanserv_menu.add_command(label="Kick Channel", command=self.chanserv_kick)
        self.chanserv_menu.add_command(label="Unban Channel", command=self.chanserv_unban)
        self.chanserv_menu.add_command(label="Invite Channel", command=self.chanserv_invite)
        
        # NickServ commands
        self.nickserv_menu = tk.Menu(self.text_area_menu, tearoff=0)
        self.nickserv_menu.add_command(label="Register Nickname", command=self.nickserv_register)
        self.nickserv_menu.add_command(label="Identify Nickname", command=self.nickserv_identify)
        self.nickserv_menu.add_command(label="Set Nickname", command=self.nickserv_set)
        self.nickserv_menu.add_command(label="Ghost Nickname", command=self.nickserv_ghost)
        self.nickserv_menu.add_command(label="Recover Nickname", command=self.nickserv_recover)
        self.nickserv_menu.add_command(label="Group Nickname", command=self.nickserv_group)
        
        # Add ChanServ and NickServ menus to text area menu
        self.text_area_menu.add_cascade(label="ChanServ", menu=self.chanserv_menu)
        self.text_area_menu.add_cascade(label="NickServ", menu=self.nickserv_menu)
        
        # Bind right-click events to show context menus
        self.text_area.bind("<Button-3>", self.show_text_area_menu)
        self.nickname_listbox.bind("<Button-3>", self.show_nickname_list_menu)
        
        old_font = self.text_area.cget("font")
        
        self.text_area_menu.configure(font=old_font, background="#36454f", foreground="#eeeeee", borderwidth=0)
        self.nickname_list_menu.configure(font=old_font, background="#36454f", foreground="#eeeeee", borderwidth=0)
        self.chanserv_menu.configure(font=old_font, background="#36454f", foreground="#eeeeee", borderwidth=0)
        self.nickserv_menu.configure(font=old_font, background="#36454f", foreground="#eeeeee", borderwidth=0)
    
    def show_text_area_menu(self, event):
        try:
            self.text_area_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.text_area_menu.grab_release()
    
    def show_nickname_list_menu(self, event):
        try:
            self.nickname_list_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.nickname_list_menu.grab_release()
    
    @staticmethod
    def copy_text():
        print("Copy text")
    
    @staticmethod
    def kick_user():
        print("Kick user")
    
    @staticmethod
    def ban_user():
        print("Ban user")
    
    @staticmethod
    def whois_user():
        print("Whois user")
    @staticmethod
    def send_file():
        print("Send file")
    
    @staticmethod
    def chanserv_register():
        print("ChanServ: Register Channel")
    
    @staticmethod
    def chanserv_identify():
        print("ChanServ: Identify Channel")
    
    @staticmethod
    def chanserv_set():
        print("ChanServ: Set Channel")
    
    @staticmethod
    def chanserv_ban():
        print("ChanServ: Ban Channel")
    
    @staticmethod
    def chanserv_kick():
        print("ChanServ: Kick Channel")
    
    @staticmethod
    def chanserv_unban():
        print("ChanServ: Unban Channel")
    
    @staticmethod
    def chanserv_invite():
        print("ChanServ: Invite Channel")
    
    @staticmethod
    def nickserv_register():
        print("NickServ: Register Nickname")
    
    @staticmethod
    def nickserv_identify():
        print("NickServ: Identify Nickname")
    
    @staticmethod
    def nickserv_set():
        print("NickServ: Set Nickname")
    
    @staticmethod
    def nickserv_ghost():
        print("NickServ: Ghost Nickname")
    
    @staticmethod
    def nickserv_recover():
        print("NickServ: Recover Nickname")
    
    @staticmethod
    def nickserv_group():
        print("NickServ: Group Nickname")
        
    def download_and_display_image(self, url):
        if not url:
            return
        response = requests.get(url)
        image_data = BytesIO(response.content)
        image = Image.open(image_data)
        tk_image = ImageTk.PhotoImage(image)
        self.text_area.image_create(tk.END, image=tk_image)
        self.text_area.insert(tk.END, "\n")
        print(f"Downloaded and displayed image: {url}")
        
    def make_buffer_display_labels(self):
        # Clear any existing labels
        for label in self.response_buffer_labels:
            label.destroy()
        self.response_buffer_labels = []
        i = 0
        for buffer_name in self.response_buffers:
            label = tk.Label(
                self.status_frame,
                text=buffer_name,
                bd=1,
                relief=tk.SUNKEN,
                padx=5,
                pady=2,
            )
            if i == self.viewing_buffer_index:
                label.config(bg="lightblue")
            else:
                label.config(bg="lightgray")
            label.grid(row=0, column=i+2, sticky=tk.W, padx=5, pady=5)
            self.response_buffer_labels.append(label)
            i += 1
            
    def update_buffer_display_labels(self):
        self.make_buffer_display_labels()

    def open_settings(self):
        self.settings_window(self.root, self.details_manager, self.server_details, self.proxy_details)

    def update_settings_with_selected_server(self, event):
        _ = event
        selected_server = self.server_var.get()
        for server in self.details_manager.get_server_list():
            if server["server"] == selected_server:
                self.details_manager.set_server_details(server)
                break

    def toggle_connection(self):
        if self.connected:
            self.disconnect()
        else:
            self.active_details = self.details_manager.get_active_details()
            if self.active_details is not None:
                
                self.connect()
            else:
                print("Manage your settings and try again. No active details found.")
                return

    def configure_status_label(self, text, fg):
        self.status_label.config(text=text, fg=fg)

    def configure_connect_button(self, text):
        self.connect_button.config(text=text)

    def connect(self):
        if self.connected:
            return
        try:
            active_details = self.details_manager.get_active_details()
            if active_details is None:
                self.status_label.config(text="No server details", fg="red")
                return
            self.server_name = active_details["server"]
            self.server = active_details["server"]
            self.port = int(active_details["port"])
            use_ssl = active_details["ssl"]
            self.nickname = active_details["nickname"]
            username = active_details["username"]
            realname = active_details["realname"]
            auto_connect = active_details["auto_connect"]
            
            #print(f"Connecting to {self.server} on port {self.port}")
            
            #self.irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #self.irc_socket.connect((self.server, self.port))
            
            if self.details_manager.is_proxy_enabled() is True:
                # Set up proxy if enabled
                proxy_details = active_details["proxy_details"]
                proxy_type = proxy_details.get("type", "").lower()
                proxy_host = proxy_details.get("host", "")
                proxy_port = int(proxy_details.get("port", 0))
                if proxy_type == "socks5":
                    import socks
                    self.irc_socket = socks.socksocket()
                    self.irc_socket.set_proxy(socks.SOCKS5, proxy_host, proxy_port)
                elif proxy_type == "http":
                    self.irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    proxy_connect_str = f"CONNECT {self.server}:{self.port} HTTP/1.1\r\n\r\n"
                    self.irc_socket.connect((proxy_host, proxy_port))
                    self.irc_socket.sendall(proxy_connect_str.encode("utf-8"))
                    response = self.irc_socket.recv(4096)
                    if b"200 Connection established" not in response:
                        raise Exception("Failed to connect via HTTP proxy")
                else:
                    self.irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            else:
                # Connect without proxy
                self.irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
                print(self.server, self.port)
                self.irc_socket.connect((self.server, int(self.port)))

            # Wrap socket if SSL is enabled
            if use_ssl:
                context = ssl.create_default_context()
                self.irc_socket = context.wrap_socket(
                    self.irc_socket, server_hostname=self.server
                )
            self.connected = True
            self.status_label.config(text="Connected", fg="green")
            self.connect_button.config(text="Disconnect")
            self.response_buffers["Status"] += f"server - Connected to {self.server}:{self.port}\n"
            self.send_irc_message(f"NICK {self.nickname}")
            self.send_irc_message(f"USER {username} 0 * :{realname}")
            threading.Thread(target=self.receive_messages, daemon=True).start()
        except Exception as e:
            self.status_label.config(text=f"Connection failed: {e}", fg="red")
            if self.show_tracback_results is False:
                self.response_buffers["Status"] += f"error - Connection failed: {e}\n"
            else:
                self.response_buffers["Status"] += f"error - Connection failed: {e}\n{traceback.print_exc(e)}\n"
            
            traceback.print_exc(e)
            self.update_text_area()
            self.connected = False

    @staticmethod
    def get_project_dir():
        root_path = os.path.dirname(os.path.abspath(__file__))
        
        #root_path = root_path.replace("/src","")
        #print(root_path)
        logging.info("Dir: {root_path}")
        #return os.path.dirname(os.path.abspath(root_path))
        return root_path
    

    def disconnect(self):
        if not self.connected:
            return
        try:
            self.send_irc_message("QUIT :Client disconnected")
            self.irc_socket.close()
        except Exception as e:
            self.response_buffers["Status"] += f"server - Error during disconnection: {e}\n"
        finally:
            self.connected = False
            self.status_label.config(text="Disconnected", fg="red")
            self.connect_button.config(text="Connect")
            if self.show_tracback_results is False:
                self.response_buffers["Status"] += "server - Disconnected from server\n"
            else:
                self.response_buffers["Status"] += f"server - Disconnected from server\n{traceback.print_exc()}\n"
            traceback.print_exc()
            self.update_text_area()

    def send_irc_message(self, message):
        if self.connected:
            try:
                try:
                    self.irc_socket.send((message + "\r\n").encode("utf-8"))
                except ConnectionError as e:
                    if self.show_tracback_results is False:
                        self.response_buffers["Status"] += f"error - Failed to send message connection error: {e}\n"
                    else:
                        self.response_buffers["Status"] += f"error - Failed to send message connection error: {e}\n{traceback.print_exc()}\n"
                    traceback.print_exc()
                    self.update_text_area()
            except Exception as e:
                if self.show_tracback_results is False:
                    self.response_buffers["Status"] += f"error - Failed to send message: {e}\n"
                else:
                    self.response_buffers["Status"] += f"error - Failed to send message: {e}\n{traceback.print_exc()}\n"
                traceback.print_exc()
                self.update_text_area()

    def receive_messages(self):
        while self.connected:
            try:
                response = self.irc_socket.recv(4096).decode("utf-8")
                if not response:
                    break
                self.handle_irc_response(response)
            except Exception as e:
                if self.show_tracback_results is False:
                    self.response_buffers["Status"] += f"error - Error receiving message: {e}\n"
                else:
                    self.response_buffers["Status"] += f"error - Error receiving message: {e}\n{traceback.print_exc()}\n"
                traceback.print_exc()
                self.update_text_area()
                break
        self.disconnect()

    def handle_irc_response(self, response):
        lines = response.split("\r\n")
        for line in lines:
            if line:
                # self.response_buffers["Status"] += line + "\n"
                # self.update_text_area()
                self.parse_irc_message(line)

    def parse_irc_message(self, message):
        if message.startswith("PING"):
            self.send_irc_message("PONG " + message.split()[1])
            tag = "ping"
            self.response_buffers["Status"] += f"{tag} - PING PONG\n"
            buffer_keys = list(self.response_buffers.keys())
            buffer_name = buffer_keys[self.viewing_buffer_index]
            if buffer_name == "Status":
                self.update_text_area()   
            return
        else:
            if self.show_username_addresses is False:
                prefix = f"{message.split('!')[0]}"
                command = message.split()[1]
                params = message.split()[2:]

            else:
                prefix, command, params = self.split_irc_message(message)
                
            if command == "PRIVMSG":
                target = params[0]
                msg = " ".join(params[1:])
                buffer_keys = list(self.response_buffers.keys())
                buffer_name = buffer_keys[self.viewing_buffer_index]
                if target.startswith("#"):
                    tag = "channel"
                    
                    if f"discord @ #{buffer_name.replace('#', '')}:" in message or 'channel - discord!~u@' in message:
                        youtube_match = re.search(r'https://www.youtube.com/watch\?v=\S+', message)
                        youtube_match_two = re.search(r'https://www.youtube.com/embed/\S+', message)
                        
                        if youtube_match:
                            url = youtube_match.group(0)
                            self.generate_youtube_embedded_code(url)
                        
                        if youtube_match_two:
                            url = youtube_match_two.group(0)
                            self.generate_youtube_embedded_code(url)
                    
                    if f"discord @ #{buffer_name.replace('#', '')}:" in message or 'channel - discord!~u@' in message:
                        match = re.search(r'https://media.discordapp.net/stickers/\S+', message)
                        
                        # match = re.search(r'https://media.discordapp.net/stickers/[^\s]+', message)
                        # [^\s]
                        if match:
                            url = match.group(0)
                            self.download_and_display_image(url)
                    self.response_buffers[target.replace("#", "")] += f"{tag} - {prefix}: {msg}\n"
                else:
                    tag = "private"
                    if f"discord @ #{buffer_name.replace('#', '')}:" in message or 'channel - discord!~u@' in message:
                        youtube_match = re.search(r'https://www.youtube.com/watch\?v=\S+', message)
                        youtube_match_two = re.search(r'https://www.youtube.com/embed/\S+', message)
                        
                        if youtube_match:
                            url = youtube_match.group(0)
                            self.generate_youtube_embedded_code(url)
                        
                        if youtube_match_two:
                            url = youtube_match_two.group(0)
                            self.generate_youtube_embedded_code(url)
                    
                    if f"discord @ #{buffer_name.replace('#', '')}:" in message or 'channel - discord!~u@' in message:
                        match = re.search(r'https://media.discordapp.net/stickers/\S+', message)
                        
                        # match = re.search(r'https://media.discordapp.net/stickers/[^\s]+', message)
                        # [^\s]
                        if match:
                            url = match.group(0)
                            self.download_and_display_image(url)

                    self.response_buffers[target.replace("#", "")] += f"{tag} - {prefix} (private): {msg}\n"

            elif command == "NOTICE":
                target = params[0]
                msg = " ".join(params)
                tag = "notice"
                self.response_buffers[target.replace("#", "")] += f"{tag} - {prefix}: {msg}\n"

            elif command == "JOIN":
                channel = params[0][1:]
                if channel not in self.response_buffers:
                    self.response_buffers[channel.replace("#", "")] = ""
                    self.viewing_buffer_index = len(self.response_buffers) - 1
                tag = "join"
                self.response_buffers[channel.replace("#", "")] += f"{tag} - {prefix} has joined {channel}\n"
                self.update_buffer_display_labels()

            elif command == "PART":
                buffer_keys = list(self.response_buffers.keys())
                buffer_name = buffer_keys[self.viewing_buffer_index]
                channel = params[0][1:]
                tag = "part"

                if self.response_buffers[buffer_name]:
                    self.response_buffers[buffer_name] += f"{tag} - {prefix} has left {channel}\n"

            elif command == "QUIT":
                buffer_keys = list(self.response_buffers.keys())
                buffer_name = buffer_keys[self.viewing_buffer_index]
                msg = " ".join(params)
                tag = "quit"
                self.response_buffers[buffer_name] += f"{tag} - {prefix} has quit: {msg}\n"

            elif command == "KICK":
                channel = params[0][1:]
                target = params[1]
                msg = " ".join(params[2:])
                tag = "kick"
                self.response_buffers[channel.replace("#", "")] += f"{tag} - {prefix} has kicked {target} from {channel}: {msg}\n"

            elif command == "MODE":
                target = params[0]
                mode = " ".join(params[1:])
                tag = "mode"
                self.response_buffers[target.replace("#", "")] += f"{tag} - {prefix} set mode {mode} on {target}\n"

            elif command == "TOPIC":
                channel = params[0][1:]
                topic = " ".join(params[1:])
                tag = "topic"
                self.response_buffers[channel.replace("#", "")] += f"{tag} - {prefix} has changed the topic of {channel} to: {topic}\n"

            elif command == "NICK":
                buffer_keys = list(self.response_buffers.keys())
                buffer_name = buffer_keys[self.viewing_buffer_index]
                new_nick = params[0][1:]
                tag = "nick"
                self.response_buffers[buffer_name] += f"{tag} - {prefix} is now known as {new_nick}\n"

            elif command == "433":
                buffer_keys = list(self.response_buffers.keys())
                buffer_name = buffer_keys[self.viewing_buffer_index]
                tag = "error"
                self.response_buffers[buffer_name] += f"{tag} - Error: Nickname is already in use\n"

            else:
                tag = "server"
                # channel = params[0][0:].replace("#", "")
                buffer_keys = list(self.response_buffers.keys())
                buffer_name = buffer_keys[self.viewing_buffer_index]
                parsed_msg = message
                if self.show_server_addresses is False:
                    # TODO fix if this the set to true nickname list cannot load.
                    if message.startswith(f":{self.server}"):
                        # remove everything before the second :
                        # if more then one : exists in the message, remove everything before the second :
                        if message.count(":") > 1:
                            parsed_msg = message.split(":", 2)[2]
                            #print(self.show_server_addresses, "parsed", parsed_msg)
                        else:
                            parsed_msg = message
                    else:
                        parsed_msg = message
                    
                if buffer_name != "Status":
                    self.response_buffers["Status"] += f"{tag} - {parsed_msg}\n"
                    self.update_nickname_list_from_buffer("Status")
                    self.update_buffer_display_labels()
                    self.update_text_area()
                    return
                else:
                    self.response_buffers["Status"] += f"{tag} - {parsed_msg}\n"
                    self.update_nickname_list_from_buffer("Status")
                    

        self.update_buffer_display_labels()
        self.update_text_area()
    
    def generate_youtube_embedded_code(self, url):
        video_id = self.extract_youtube_video_id(url)
        if video_id:
            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
            self.display_thumbnail(thumbnail_url, url)

    @staticmethod
    def extract_youtube_video_id(url):
        pattern = re.compile(r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^\s&]+)')
        match = pattern.search(url)
        if match:
            return match.group(1)
        return None

    def display_thumbnail(self, thumbnail_url, video_url):
        response = requests.get(thumbnail_url)
        img_data = response.content
        image = Image.open(BytesIO(img_data))
        image.thumbnail((120, 90))  # Adjust thumbnail size if necessary
        photo = ImageTk.PhotoImage(image)

        self.text_area.image_create(tk.END, image=photo)
        self.text_area.insert(tk.END, "\n")
        self.text_area.image = photo  # Keep a reference to avoid garbage collection

        self.text_area.tag_bind(photo, '<Button-1>', lambda e: webbrowser.open(video_url))

    def update_nickname_list_from_buffer(self, buffer_name):
        # Retrieve the nickname list from the response buffer
        buffer_content = self.response_buffers[buffer_name]
        lines = buffer_content.split("\n")
        nicklist_line = []
        for line in lines:
            buffer_keys = list(self.response_buffers.keys())
            current_buffer = buffer_keys[self.viewing_buffer_index]
            if current_buffer == buffer_name:
                #print("Skipping status buffer? clearing visible nicklist gui item")
                self.nickname_listbox.delete(0, tk.END)
                break
            
            if (line.startswith(f":{self.server} 353 {self.nickname} = #{current_buffer} :") or
                    line.startswith(f"server - :{self.server} 353 {self.nickname} = #{current_buffer} :") or
                    line.startswith(f":{self.server} 353 {self.nickname} = #{current_buffer} ") or
                    line.startswith(f"server - :{self.server} 353 {self.nickname} = #{current_buffer} ")):
                nicklist_line.append(line)
                break

            if line.endswith(f"End of NAMES list"):
                break
                
        if nicklist_line is not None and len(nicklist_line) > 0:
            if nicklist_line[len(nicklist_line) - 1] != "":
                nicknames = nicklist_line[len(nicklist_line) - 1].split(":")[2].split()
                self.nickname_buffers[buffer_name] = []
                for nickname in nicknames:
                    self.nickname_buffers[buffer_name].append(nickname)
                self.populate_from_nickname_buffer(buffer_name)
    
    def populate_from_nickname_buffer(self, buffer_name):
        self.nickname_listbox.delete(0, tk.END)
        self.nickname_colors[buffer_name] = []
        
        # use a 8 bit color to assign colors to the self.nickname_colors list.
        # then apply the color to the font of the self.nickname_listbox nickname items
        # self.nickname_listbox is a tk.Listbox
        
        for buffer in self.nickname_buffers:
            for nickname in self.nickname_buffers[buffer]:
                nick_color = self.get_color_for_nickname()
                self.nickname_colors[buffer_name].append(nick_color)
                self.nickname_listbox.insert(tk.END, nickname)
                self.nickname_listbox.itemconfig(tk.END, foreground=f"{nick_color}")
                self.nickname_listbox.see(tk.END)
                
    @staticmethod
    def get_color_for_nickname():
        # Generate a random 8-bit color (0 to 255)
        random_color = "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        return random_color
    
    @staticmethod
    def split_irc_message(message):
        prefix = ""
        trailing = []
        if not message:
            raise Exception("Empty line.")
        if message[0] == ":":
            prefix, message = message[1:].split(" ", 1)
        if message.find(" :") != -1:
            message, trailing = message.split(" :", 1)
            args = message.split()
            args.append(trailing)
        else:
            args = message.split()
        command = args.pop(0)
        return prefix, command, args

    def send_message(self, event=None):
        # Send a message to the server
        _ = event
        message = self.entry.get().strip()
        if message and self.connected:
            buffer_name = list(self.response_buffers.keys())[self.viewing_buffer_index]

            if message.startswith("/join "):
                channel = message.split(" ")[1]
                if not channel.startswith("#"):
                    channel = f"#{channel}"
                
                self.send_irc_message(f'JOIN #{channel.replace("#", "")}')
            elif message == "/close":
                self.close_current_buffer()
            elif message.startswith("/nick "):
                nickname = message.split(" ")[1]
                self.send_irc_message(f"NICK {nickname}")
            elif message.startswith("/topic "):
                topic = message.split(" ")[1]
                self.send_irc_message(f"TOPIC #{buffer_name} :{topic}")
            elif message.startswith("/mode "):
                mode = message.split(" ")[1]
                self.send_irc_message(f"MODE #{buffer_name} {mode}")
            elif message.startswith("/nickserv "):
                nickserv = message.split(" ")[1]
                self.send_irc_message(f"NICKSERV {nickserv}")
            elif message.startswith("/chanserv "):
                chanserv = message.split(" ")[1]
                self.send_irc_message(f"CHANSERV {chanserv}")
            elif message.startswith("/whois "):
                whois = message.split(" ")[1]
                self.send_irc_message(f"WHOIS {whois}")
            elif message.startswith("/who "):
                who = message.split(" ")[1]
                self.send_irc_message(f"WHO {who}")
            elif message.startswith("/away "):
                away = message.split(" ")[1]
                self.send_irc_message(f"AWAY :{away}")
            elif message == "/quit":
                self.send_irc_message("QUIT")
            elif message == "/help":
                self.response_buffers[buffer_name] += f"private - {self.nickname} - #{buffer_name}: {message}\n"
                self.send_irc_message(f"PRIVMSG #{buffer_name} :/help")
            elif message == "/whoami":
                self.response_buffers[buffer_name] += f"private - {self.nickname} - #{buffer_name}: {message}\n"
                self.send_irc_message(f"PRIVMSG #{buffer_name} :/whoami")
            else:
                self.response_buffers[buffer_name] += f"private - {self.nickname} - #{buffer_name}: {message}\n"
                self.send_irc_message(f"PRIVMSG #{buffer_name} :{message}")

            self.update_text_area()
            self.entry.delete(0, tk.END)
    
    def update_text_area1(self):
        # Update from buffer to add colors to self.text_area
        buffer_name = list(self.response_buffers.keys())[self.viewing_buffer_index].replace("#", "")
        
        text_content = self.response_buffers[buffer_name]
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        
        # Split the content and apply tags
        for line in text_content.split("\n"):
            if line:
                parts = line.split(" - ", 1)
                if len(parts) == 2:
                    current_tag, message = parts
                    self.text_area.insert(tk.END, f'{line.replace("channel - :", "").replace("server - :", "")}\n', current_tag, )
                else:
                    self.text_area.insert(tk.END, f'{line.replace("channel - :", "").replace("server - :", "")}\n', )  # No tag applied for this line
                    
        for index, nickname in enumerate(self.nickname_listbox.get(0, tk.END)):
            if re.match(r'^' + re.escape(nickname) + r'', self.text_area.get("1.0", tk.END)):
                # color from the stat of the nickname to the length of only the nickname
                text_color = self.nickname_colors[buffer_name][index]
                self.text_area.tag_add(text_color, f"{index + 1}.0", f"{index + 1}.{len(nickname)}")
            else:
                random_color = self.get_color_for_nickname()
                self.text_area.tag_add(random_color, f"{index + 1}.0", f"{index + 1}.{len(nickname)}")
            
        self.text_area.update_idletasks()
        self.text_area.config(state=tk.DISABLED)
        self.text_area.yview(tk.END)
    
    def update_text_area2(self):
        # Update from buffer to add colors to self.text_area
        buffer_name = list(self.response_buffers.keys())[self.viewing_buffer_index].replace("#", "")
        text_content = self.response_buffers[buffer_name]
        current_content = self.text_area.get("1.0", tk.END).splitlines()
        new_lines = text_content.split("\n")
        # self.text_area.delete(1.0, tk.END)
        
        
        # Find the difference and update only the new lines
        if len(current_content) < len(new_lines):
            self.text_area.config(state=tk.NORMAL)
            for line in new_lines[len(current_content):]:
                if line:
                    parts = line.split(" - ", 1)
                    if len(parts) == 2:
                        current_tag, message = parts
                        self.text_area.insert(tk.END, f'{line.replace("channel - :", "").replace("server - :", "")}\n', current_tag)
                    else:
                        self.text_area.insert(tk.END, f'{line.replace("channel - :", "").replace("server - :", "")}\n')  # No tag applied for this line
            self.text_area.config(state=tk.DISABLED)
            self.text_area.yview(tk.END)
    
    def populate_text_area(self):
        # Update from buffer to add colors to self.text_area
        buffer_name = list(self.response_buffers.keys())[self.viewing_buffer_index].replace("#", "")
        text_content = self.response_buffers[buffer_name]
        
        self.nickname_listbox.delete(1.0, tk.END)
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        # Split the content and apply tags
        for line in text_content.split("\n"):
            if line:
                parts = line.split(" - ", 1)
                                
                if len(parts) == 2:
                    if parts[0] == "channel - :" and parts[1] not in self.nickname_listbox.get(0, tk.END):
                        self.nickname_listbox.insert(tk.END, parts[0])
                        #self.text_area.insert(tk.END, f'{self.line.replace("channel - :", "").replace("server - :", "")}\n', self.nick_tag,)
                    
                    self.part_len = len(parts)
                    self.nick_tag, message = parts
                    #print("two part:", parts[0])
                    if parts[0] == "channel":
                        self.last_line = line
                        self.text_area.insert(tk.END, f'{self.last_line.replace("channel - :", "").replace("server - :", "")}\n', self.nick_tag,)
                        print("NICAK TAG:",self.nick_tag)
                    elif parts[0] == "server":
                        self.last_line = line
                        self.text_area.insert(tk.END, f'{self.last_line.replace("server - :", "").replace("server - :", "")}\n', self.nick_tag,)
                    elif parts[0] == "ping":
                        self.last_line = line
                        self.text_area.insert(tk.END, f'{self.last_line.replace("ping - :", "").replace("server - :", "")}\n', self.nick_tag,)
                    elif parts[0] == None or parts[0] == "None" or parts[0] == "error":
                        
                        self.last_line = line
                        self.text_area.insert(tk.END, f'{self.last_line.replace("ping - :", "").replace("server - :", "")}\n', self.nick_tag,)

                else:
                    #print("populate line:", line)
                    self.part_len = len(parts)
                    #print("not two parts", parts[0])
                    if parts[0] == None or parts[0] == "None" or parts[0] == "error":
                        self.last_line = line
                    else:
                        self.last_line = line
                    
                    self.text_area.insert(tk.END, f'{self.last_line.replace("channel - :", "").replace("server - :", "")}\n', self.nick_tag,)


                # iterate self.nickname_listbox get the text color of each item. match the nickname to the color and apply the color to
                # the font of the matching text for the self.text_line
                text_color = ""
#                for index, nickname in enumerate(self.nickname_listbox.get(0, tk.END)):
#                    
#                    if len(parts) > 2:
#                        if nickname == parts[0] or nickname == parts[1]:
#                            text_color = self.nickname_colors[buffer_name][index]
#                            self.nickname_buffers[buffer_name].append(nickname)
#                            self.populate_from_nickname_buffer(buffer_name)
#                        else:
#                            text_color = self.nickname_colors[buffer_name][index]
#                            self.nickname_buffers[buffer_name].append(nickname)
#                            self.populate_from_nickname_buffer(buffer_name)
#                    else:
#                        if nickname == parts[0]:
#                            text_color = self.nickname_colors[buffer_name][index]
#                            self.nickname_buffers[buffer_name].append(nickname)
#                            self.populate_from_nickname_buffer(buffer_name)
#                        else:
#                            text_color = self.nickname_colors[buffer_name][index]
#                            self.nickname_buffers[buffer_name].append(nickname)
#                            self.populate_from_nickname_buffer(buffer_name)
#
#
#                    # Get the content of the text widget as a string
#                    # text_content = self.text_area.get("1.0", tk.END)
#                    match = re.search(r'\b' + re.escape(nickname) + r'\b', text_content)
#                    print("matching:", match)
#                    if match:
#                        start_index = match.start()
#                        end_index = match.end()
#                        start_line = text_content.count("\n", 0, start_index) + 1
#                        start_column = start_index - text_content.rfind("\n", 0, start_index)
#                        end_line = text_content.count("\n", 0, end_index) + 1
#                        end_column = end_index - text_content.rfind("\n", 0, end_index)
#                        
#                        self.text_area.tag_add(text_color, f"{start_line}.{start_column}", f"{end_line}.{end_column}")
#                    else:
#                        random_color = self.get_color_for_nickname()
#                        self.text_area.tag_add(random_color, f"{index + 1}.0", f"{index + 1}.{len(nickname)}")
#
#                if len(parts) == 2:
#                    self.part_len = len(parts)
#                    self.nick_tag, message = parts
#                    print("two part:", parts[0])
#                    if parts[0] == "channel":
#                        self.last_line = line
#                        self.text_area.insert(tk.END, f'{self.last_line.replace("channel - :", "").replace("server - :", "")}\n', self.nick_tag,)
#                        print(self.nick_tag)
#                    elif parts[0] == "server":
#                        self.last_line = line
#                        self.text_area.insert(tk.END, f'{self.last_line.replace("server - :", "").replace("server - :", "")}\n', self.nick_tag,)
#                    elif parts[0] == "ping":
#                        self.last_line = line
#                        self.text_area.insert(tk.END, f'{self.last_line.replace("ping - :", "").replace("server - :", "")}\n', self.nick_tag,)
#                    elif parts[0] == None or parts[0] == "None" or parts[0] == "error":
#                        
#                        self.last_line = line
#                        self.text_area.insert(tk.END, f'{self.last_line.replace("ping - :", "").replace("server - :", "")}\n', self.nick_tag,)
#
#                else:
#                    print("populate line:", line)
#                    self.part_len = len(parts)
#                    #print("not two parts", parts[0])
#                    if parts[0] == None or parts[0] == "None" or parts[0] == "error":
#                        self.last_line = line
#                    else:
#                        self.last_line = line
#                    
#                    self.text_area.insert(tk.END, f'{self.last_line.replace("channel - :", "").replace("server - :", "")}\n', self.nick_tag,)
       
        self.text_area.config(state=tk.DISABLED)
        self.text_area.yview(tk.END)

    def update_text_area(self):
        # Update from buffer to add colors to self.text_area
        buffer_name = list(self.response_buffers.keys())[self.viewing_buffer_index].replace("#", "")
        text_content = self.response_buffers[buffer_name]
        self.text_area.config(state=tk.NORMAL)
        # self.text_area.delete(1.0, tk.END)
        # Split the content and apply tags
        for line in text_content.split("\n"):
            if line:
                parts = line.split(" - ", 1)

                if parts[0] == "channel - :" and parts[1] not in self.nickname_listbox.get(0, tk.END):
                    self.nickname_listbox.insert(tk.END, parts[0])

                # iterate self.nickname_listbox get the text color of each item. match the nickname to the color and apply the color to
                # the font of the matching text for the self.text_line
                text_color = ""
                if self.nickname_listbox:
                    for index, nickname in enumerate(self.nickname_listbox.get(0, tk.END)):
                        
                        if len(parts) >= 2:
                            if nickname == parts[0] or nickname == parts[1]:
                                text_color = self.nickname_colors[buffer_name][index]
                                self.nickname_buffers[buffer_name].append(nickname)
                                self.populate_from_nickname_buffer(buffer_name)
                        else:
                            if nickname == parts[0]:
                                text_color = self.nickname_colors[buffer_name][index]
                                self.nickname_buffers[buffer_name].append(nickname)
                                self.populate_from_nickname_buffer(buffer_name)


                        # Get the content of the text widget as a string
                        # text_content = self.text_area.get("1.0", tk.END)
                        match = re.search(r'\b' + re.escape(nickname) + r'\b', text_content)
                    
                        if match:
                            start_index = match.start()
                            end_index = match.end()
                            start_line = text_content.count("\n", 0, start_index) + 1
                            start_column = start_index - text_content.rfind("\n", 0, start_index)
                            end_line = text_content.count("\n", 0, end_index) + 1
                            end_column = end_index - text_content.rfind("\n", 0, end_index)
                        
                            self.text_area.tag_add(text_color, f"{start_line}.{start_column}", f"{end_line}.{end_column}")
                        else:
                            random_color = self.get_color_for_nickname()
                            self.text_area.tag_add(random_color, f"{index + 1}.0", f"{index + 1}.{len(nickname)}")

                if len(parts) == 2:
                    self.part_len = len(parts)
                    self.nick_tag, message = parts
                    #print("two part:", parts[0], line)
                    self.last_line = line
                else:
                    self.part_len = len(parts)
                    #print("not two parts", parts[0])
                    self.last_line = line
        
        if self.part_len == 2:

            self.text_area.insert(tk.END, f'{self.last_line.replace("channel - :", "").replace("server - :", "")}\n', self.nick_tag,)
        else:

            self.text_area.insert(tk.END, f'{self.last_line.replace("channel - :", "").replace("server - :", "")}\n',)  # No tag applied for this line

        self.text_area.config(state=tk.DISABLED)
        self.text_area.yview(tk.END)
    
    def close_current_buffer(self):
        if len(self.response_buffers) > 1:
            buffer_keys = list(self.response_buffers.keys())
            removed_buffer = buffer_keys[self.viewing_buffer_index]

            self.send_irc_message(f"PART #{removed_buffer}")
            del self.response_buffers[removed_buffer]
            if self.viewing_buffer_index >= len(self.response_buffers):
                self.viewing_buffer_index = len(self.response_buffers) - 1

            self.update_text_area()
        else:
            self.text_area.config(text="")

    def request_nicklist(self, channel):
        self.send_irc_message(f"NAMES {channel}")

    def show_nickname_list(self):
        if self.new_nickname_side == 0:
            self.text_area.grid(row=1, column=1, sticky=tk.NSEW)
            self.nickname_listbox.grid(row=1, column=0, sticky=tk.NS)
            self.root.grid_columnconfigure(0, weight=0)
            self.root.grid_columnconfigure(1, weight=1)
        elif self.new_nickname_side == 1:
            self.text_area.grid(row=1, column=0, sticky=tk.NSEW)
            self.nickname_listbox.grid(row=1, column=1, sticky=tk.NS)
            self.root.grid_columnconfigure(0, weight=1)
            self.root.grid_columnconfigure(1, weight=0)
            
    def hide_nickname_list(self):
        self.nickname_listbox.grid_forget()
    
    def move_nickname_list(self, side):
        # Forget current grid positions
        self.text_area.grid_forget()
        self.nickname_listbox.grid_forget()
        
        # 0 == left side, 1 == right side
        
        if side == 0:
            self.text_area.grid(row=1, column=1, sticky=tk.NSEW)
            self.nickname_listbox.grid(row=1, column=0, sticky=tk.NS)
            self.root.grid_columnconfigure(0, weight=0)
            self.root.grid_columnconfigure(1, weight=1)
            self.new_nickname_side = 0
        elif side == 1:
            self.text_area.grid(row=1, column=0, sticky=tk.NSEW)
            self.nickname_listbox.grid(row=1, column=1, sticky=tk.NS)
            self.root.grid_columnconfigure(0, weight=1)
            self.root.grid_columnconfigure(1, weight=0)
            self.new_nickname_side = 1
            
            
if __name__ == "__main__":
    root = tk.Tk()
    app = CrudeIRC(root)
    root.mainloop()
