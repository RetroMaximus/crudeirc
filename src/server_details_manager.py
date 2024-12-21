# server_details_manager.py
import json
import os.path


class ServerDetailsManager:
    def __init__(self, gui_callbacks):
        self.gui_callbacks = gui_callbacks
        self.server_details = {
            'servers': {}
        }
        self.proxy_details = {
            'proxies': {}
        }
        self.load_server_details()
        self.load_proxy_details()
    
    def open_proxy_bouncer(self):
        self.gui_callbacks(self.gui_callbacks, self.gui_callbacks.details_manager).open_proxy_bouncer()
    
    @staticmethod
    def get_project_dir():
        return os.path.dirname(os.path.abspath(__file__))
    
    def load_server_details(self):
        #print("Did I start loading servers?", f"{self.get_project_dir()}\\crude_server_details.json")
        if os.path.exists(f"{self.get_project_dir()}\\crude_server_details.json"):
            try:
                with open(f"{self.get_project_dir()}\\crude_server_details.json", 'r') as f:
                    self.server_details = json.load(f)
                #print("loading servers",self.server_details)
            except FileNotFoundError as e:
                print("File not found", e)
                pass  # Handle file not found error or initialize with default empty server dictionary
        else:
            with open(f"{self.get_project_dir()}\\crude_server_details.json", 'w') as f:
                json.dump(self.server_details, f, indent=4)
                
    def load_proxy_details(self):
        #print("Did I start loading proxies?")
        if os.path.exists(f"{self.get_project_dir()}\\crude_proxy_details.json"):
            try:
                with open(f"{self.get_project_dir()}\\crude_proxy_details.json", 'r') as f:
                    self.proxy_details = json.load(f)
                #print("loading proxies?", self.proxy_details)
            except FileNotFoundError:
                pass  # Handle file not found error or initialize with default empty proxy dictionary
        else:
            with open(f"{self.get_project_dir()}\\crude_proxy_details.json", 'w') as f:
                json.dump(self.proxy_details, f, indent=4)
                
    def save_proxy_details(self):
        with open(f"{self.get_project_dir()}\\crude_proxy_details.json", 'w') as f:
            json.dump(self.proxy_details, f, indent=4)
    
    def save_server_details(self):
        with open(f"{self.get_project_dir()}\\crude_proxy_details.json", 'w') as f:
            json.dump(self.server_details, f, indent=4)

    def get_server_details(self, selected_server):
        return self.server_details.get('servers', {}).get(selected_server, {})
    
    def get_proxy_details(self, selected_proxy):
        return self.proxy_details.get('proxies', {}).get(selected_proxy, {})
   
    def get_server_list(self):
        return self.server_details.get('servers', {})
    
    def get_proxy_list(self):
        return self.proxy_details.get('proxies', {})
    
    def get_active_details(self):
        return self.server_details.get('active_details', {})
    
    def get_active_proxy_details(self):
        return self.server_details.get('active_details', {}).get('proxy_details', {})
    
    def is_proxy_enabled(self):
        print(self.server_details.get('active_details', {}).get('proxy_details', {}).get('type', '') != "")
        return self.server_details.get('active_details', {}).get('proxy_details', {}).get('type', '') != ""
    
    def set_proxy_details(self, proxy_name, details):
        if 'proxies' not in self.proxy_details:
            self.proxy_details['proxies'] = {}
        self.proxy_details['proxies'][proxy_name] = details
        self.proxy_details['active_details'] = details
        self.save_proxy_details()
        
    def remove_proxy_details(self, proxy_name):
        if 'proxies' in self.proxy_details and proxy_name in self.proxy_details['proxies']:
            del self.proxy_details['proxies'][proxy_name]
            self.save_proxy_details()
    
    def set_server_details(self, server_name, details):
        if 'servers' not in self.server_details:
            self.server_details['servers'] = {}
        self.server_details['servers'][server_name] = details
        self.server_details['active_details'] = details
        self.save_server_details()

    def remove_server_details(self, server_name):
        if 'servers' in self.server_details and server_name in self.server_details['servers']:
            del self.server_details['servers'][server_name]
            self.save_server_details()
