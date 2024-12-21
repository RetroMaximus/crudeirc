

class CrudeLaunchWriter:
	_instance = None
	def __init__(self, root, details_manager):
		self.root = root
		self.details_manager = details_manager
		
		self.write_bat_no_log()
		self.write_bat_with_log()
		self.write_sh_no_log()
		self.write_sh_with_log()
		self.write_create_shortcut()
		
	@staticmethod
	def write_create_shortcut():
		with open("create_crude_shortcut.vbs", "w") as f:
			f.write("Set shell = WScript.CreateObject(\"WScript.Shell\")\n")
			f.write("Set shortcut = shell.CreateShortcut(\"%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Crude\\Crude.lnk\")\n")
			f.write("shortcut.TargetPath = WScript.ScriptFullName\n")
			f.write("shortcut.IconLocation = \"%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Crude\\crude.ico\"\n")
	
	@staticmethod
	def write_bat_no_log():
		with open("crude_bat_launch_no_log.bat", "w") as f:
			f.write("@echo off\n")
			f.write("python main.py\n")
	
	@staticmethod
	def write_bat_with_log():
		with open("crude_bat_launch_with_log.bat", "w") as f:
			f.write("@echo off\n")
			f.write("python main.py\n")
	
	@staticmethod
	def write_sh_no_log():
		with open("crude_sh_launch_no_log.sh", "w") as f:
			f.write("#!/bin/bash\n")
			f.write("python main.py\n")
	
	@staticmethod
	def write_sh_with_log():
		with open("crude_sh_launch_with_log.sh", "w") as f:
			f.write("#!/bin/bash\n")
			f.write("python main.py\n")
