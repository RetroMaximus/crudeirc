Set WshShell = WScript.CreateObject("WScript.Shell")

' Get the current working directory
currentDir = WshShell.CurrentDirectory
parentDir = Left(currentDir, InStrRev(currentDir, "\") - 1)

' Define the path to the batch file using the current directory
batPath = currentDir & "\crude_bat_launch_no_log.bat"

' Define the path to the shortcut
shortcutPath = parentDIR & "\Crude Bat Launch No Log Batch.lnk"

' Define the path to the icon file (you can use SHELL32.dll for system icons)
iconPath = "%SystemRoot%\System32\SHELL32.dll"

' Create the shortcut
Set shortcut = WshShell.CreateShortcut(shortcutPath)
shortcut.TargetPath = batPath
shortcut.IconLocation = iconPath & ", 89" ' Index of the icon in SHELL32.dll
shortcut.Save

batPath = currentDir & "\crude_bat_launch_with_log.bat"

' Define the path to the shortcut
shortcutPath = parentDIR & "\Crude Launch With Log Batch.lnk"

' Define the path to the icon file (you can use SHELL32.dll for system icons)
iconPath = "%SystemRoot%\System32\SHELL32.dll"

' Create the shortcut
Set shortcut = WshShell.CreateShortcut(shortcutPath)
shortcut.TargetPath = batPath
shortcut.IconLocation = iconPath & ", 88" ' Index of the icon in SHELL32.dll
shortcut.Save
