# Welcome to IGNoteIntegration
## A simple DiscordLike Game integration to your Instagram Notes.

### How to use it ?

### Exe version :   
**Some antiviruses like windows defender can consider this as a false positive. You can check the code if you don't trust, but it's not. Authorize the folder you'll put your app in (because when it updates it re-downloads the exe) in your antivirus exclusion or disable it in order to work**  
  
Download the latest release .zip and extract it  
Create a creds.txt in the .exe folder and put your username on 1st line and password on 2nd  
Start the IGNoteIntegration.exe  
  
**You're all set !**  
  
If you want to add games or IDEs, navigate to _internal/list.txt and add your games/ide as :
```
game_executable.exe - Game Name
---
ide_executable.exe - Ide Name
```
(if you add an IDE, put it after the "---" located down in the file)  
  
To change the language of the sended note or add a time update on your note every 10 mins, go to _internal/config.txt and change the settings :
```
time_update: True/False
language: FR/EN/DE/NL/ES
```
**BE CAREFUL** !! Enabling the time update can upset instagram (like really).
  
### Python Version  
Download the source code,  
Install **Python 3**,  
Install all requirements by using (in the folder it's in)
```
pip install -r requirements.txt
```
Create a **creds.txt** and put your username on first line then password on second line  
  
Start **main.py**
  
## You're all set !  
You can create a shortcut of **main.py** or **IGNoteIntegration.exe** in your `C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup` to start it when you boot your PC.
