<h1>SQLite Weather Database using Python</h1> 
This is a work in progress and probably very bad.

Creates and updates an SQL database for capital countries’ weather using OpenWeatherMap.
Allows the User to do basic filtering for weather and calculate the average temperature of those filtered options.

This has Menus and Terminal flags.

Menu Example:
```
Choose what you want to do 

1) Get weather data
2) Update Forecast
3) Create lists.
4) Exit 
```

Example of the flag in use: `python "Capital Weather Database.py" -update`

<h2>Requirements and info</h2>

Requires a Recent version of Python. Written for 3.11 but should work for anything similar
Tested on Linux. Should work with most other systems with python support.
Requires PyMenu: `pip3 install pymenu-console`
Requires dotenv: `pip3 install python-dotenv`
Menu Requires around 40 lines of text

Rename .env-contents to .env and enter your API key if you are not going to edit the code to just contain your API key.