#crueirc readme.md

CrudeIRC

CrudeIRC is a lightweight, Tkinter-based IRC client designed for minimalism and functionality. It supports multiple servers, proxy integration, and various UI customization options to enhance user experience.

This client is not complete by any means and very much a *WIP*


Features

Multi-Server Support: Connect to multiple IRC servers and switch between them seamlessly.

Proxy Integration: Utilize proxies for anonymity and security.

Configurable UI: Toggle menu visibility, nickname lists, and status frames.

Traceback Logging: Capture and display server responses and errors.

Launch Script Generation: Automatically generate launch scripts for ease of use.

Customizable Display: Adjust font sizes and message styles dynamically.

Key Bindings for Navigation: Navigate between chat buffers, adjust font sizes, and control UI elements with keyboard shortcuts.

Settings Window: Manage and configure client preferences conveniently.


Python Installation:

Clone the repository:

git clone https://github.com/RetroMaximus/crudeirc.git
cd crudeirc

Install dependencies:

pip install -r requirements.txt

Run the application:

python crudeirc.py


Build binary/executable:

Type: crudepybuild.py crudeirc crudeirc.py

Argument 1 = The new binary/executable name
Argument 2 = The entry script.

This will create a binary for linux or a execuable for window using pyinstaller.
the build will be stored in "/build" and "/dist". When finished you can simply call "crudeirc" anywhere in a terminal to launch
the IRC Client for the locally logged in user.


Usage:

Connecting to a Server

Click on Connect to establish a connection with a server.

Manage server details in the Settings menu.

Navigating Buffers

Use Ctrl + Right and Ctrl + Left to switch between chat buffers.

Use Ctrl + Up and Ctrl + Down to increase or decrease font size.


UI Customization

F1: Toggle menu visibility

F2: Open settings

F3: Move nickname list

F4: Show/hide nickname list

F5: Toggle distraction-free mode

F6: Open proxy bouncer settings - (WIP) not working!!!!


Logging and Debugging

Logs are stored in logs/logfile.log.

Errors and traceback messages are displayed in the terminal.

In case of crashes, the console window will appear to show error details.


Dependencies

Python 3.6+

tkinter for UI

requests for web interactions

Pillow for image handling


Development

To contribute to CrudeIRC:

Fork the repository.

Create a feature branch: git checkout -b feature-name

Commit your changes: git commit -m "Added new feature"

Push to your branch: git push origin feature-name

Open a Pull Request.


Known Bugs:

- When changing buffers sometimes only the last line that was recieved n the buffer will be displayed.
    (needs a bit more testing)

- When the a buffer get larger the client might lag (needs a bit more testing)

- Nickname colors are not being displayed in the chat buffer's. Colors will change when switching buffers.

- No settings will populate in the config window until a server is selected.


License

This project is licensed under the MIT License.

Credits

Developed by Reg "RetroMaximus" Finley aka Scr1ptAl1as
