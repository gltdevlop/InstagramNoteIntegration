# Welcome to IGNoteIntegration
## A simple DiscordLike Game integration to your Instagram Notes.

### How to use it ?

### Exe version :   
Download the latest release .zip and extract it  
Put your username and password in the creds file  
Start the IGNoteIntegration.exe  
  
**You're all set !**  
  
If you want to add games or IDEs, navigate to list.txt and add your games as :
```
game_executable.exe - Game Name
---
ide_executable.exe - Ide Name
```
To change the language of the sended note or add a time update on your note every 10 mins, go to config.txt and change the settings :
```
time_update: True/False
language: FR/EN/DE/NL/ES
```
**BE CAREFUL** !! Enabling the time update can upset instagram.
  
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
