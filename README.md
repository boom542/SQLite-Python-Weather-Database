<h1>SQLite Weather Database using Python</h1> 
This is a work in progress and probably very bad.

Creates and updates an SQL database for capital countries’ weather using OpenWeatherMap.
Allows the User to do basic filtering for weather and calculate the average temperature of those filtered options.

This has Menus and Terminal flags. It also has a basic web interface.


![image](https://github.com/user-attachments/assets/80f9be81-3c2d-4256-a154-c85577de6f2f)

![image](https://github.com/user-attachments/assets/33dc2d4f-bb7a-496d-b44d-2afadb01b951)


Menu Example:
```
Choose what you want to do 

1) Get weather data
2) Update Forecast
3) Create lists.
4) Exit 
```
Available flags:
```
-update: Create and update the database.
-tui: Use the terminal instead of the web interface.
```

Example of the flag in use: `python "Capital Weather Database.py" -update`

<h2>Requirements and info</h2>

Requires a Recent version of Python. Written for 3.11 but should work for anything similar.

Tested mainly on Linux. Confirmed working on Windows. Should work with most other systems with python support.

Requires PyMenu: `pip3 install pymenu-console`

Requires dotenv: `pip3 install python-dotenv`

Requires Flask: `pip3 install flask`

Requires Waitress: `pip3 install waitress`

Requires Requests: `pip3 install requests` (Found this was installed by default on my linux distro but not on windows)

Menu Requires around 40 lines of vertical terminal space.