Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "F:\cloude ai\profit-matrix-bot"
WshShell.Run """C:\Users\User\AppData\Local\Microsoft\WindowsApps\py.exe"" ""F:\cloude ai\profit-matrix-bot\bot.py""", 0, False
Set WshShell = Nothing
