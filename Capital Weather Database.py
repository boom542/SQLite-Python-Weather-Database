import sqlite3 as SQL # SQLite3 is fine enough for this. Built into python so we use it here. Also just change it so it says SQL in things like commands.
import os # Gonna need this for ensuring things stay in the same folder as the program.
import requests # Need this to do things such as request the api for retrieving place weather.
from datetime import datetime # Need this to get the date and time for our forecasts table.
from pymenu import Menu, select_menu # Pymenu in not in python by default. pip install pymenu-console should do the trick on most systems. Its basic but it does the trick and saves me making one myself.

API_KEY = "e0fc1abd3382817e1dc217bd3bd0b3b4" # Needed to use the API for OpenWeatherMap. This is limited to 1000 requests a day but we should be fine with our country list.

# Set capital and date to all cause we wanna show everything even if the user doesnt select that by default and not calculate averages by default.
capital = "All"
date = "All"
average = "No"

# The code below is gonna be needed to set a bunch of critical stuff involving the databases.
script_path = os.path.dirname(__file__) # Get the path of where the program is stored
file = os.path.join(script_path, "database.db") # Join the path with the file name for use within the program. It can simply be used in place of the file name.
# make a database if it does not exist or connect an existing one.
database = SQL.connect(file)
# Create a cursor object to interact with the database
edit = database.cursor()
edit.execute("PRAGMA foreign_keys = on") # PRAGMA is basically the command to change any database settings. This is specific to SQLite unlike some other SQL commands which work across other SQL databases.

def create_country_list():
    # A good chunk of the code underneath is made by AI to just generate a database containing a ton of capital cities and the countries they belong to. I am not willing to manually add every single country I want. I am editing this code though because i plan to maybe use some of it again later or integrate this file into other programs. I will also be adding comments on the code.

    # List of countries and their capitals. This is all written by AI. Just call it capitals for now. This list is infinitely expandible. If you add something and run the program it should be added. I don't know how well this works because i do not fancy testing it but for 100% chance of success if it does fail just delete the database.db file
    capitals = [
        ("Egypt", "Cairo", "Africa"),
        ("Democratic Republic of the Congo", "Kinshasa", "Africa"),
        ("Kenya", "Nairobi", "Africa"),
        ("Nigeria", "Abuja", "Africa"),
        ("Tanzania", "Dar es Salaam", "Africa"),
        ("Bangladesh", "Dhaka", "Asia"),
        ("China", "Beijing", "Asia"),
        ("India", "New Delhi", "Asia"),
        ("Indonesia", "Jakarta", "Asia"),
        ("Iran", "Tehran", "Asia"),
        ("Iraq", "Baghdad", "Asia"),
        ("Japan", "Tokyo", "Asia"),
        ("Pakistan", "Islamabad", "Asia"),
        ("Philippines", "Manila", "Asia"),
        ("Saudi Arabia", "Riyadh", "Asia"),
        ("South Korea", "Seoul", "Asia"),
        ("Thailand", "Bangkok", "Asia"),
        ("Turkey", "Ankara", "Asia"),
        ("Vietnam", "Hanoi", "Asia"),
        ("United Kingdom", "London", "Europe"),
        ("France", "Paris", "Europe"),
        ("Germany", "Berlin", "Europe"),
        ("Italy", "Rome", "Europe"),
        ("Russia", "Moscow", "Europe"),
        ("Spain", "Madrid", "Europe"),
        ("Ukraine", "Kyiv", "Europe"),
        ("Iceland", "Reykjavik", "Europe"),
        ("Mexico", "Mexico City", "North America"),
        ("United States", "Washington, D.C.", "North America"),
        ("Argentina", "Buenos Aires", "South America"),
        ("Brazil", "Brasília", "South America"),
        ("Colombia", "Bogotá", "South America"),
        ("Peru", "Lima", "South America"),
        ("Australia", "Canberra", "Oceania")
    ]



    # Create a table that will store the countries and their capitals
    edit.execute("CREATE TABLE IF NOT EXISTS capitals (place_id INTEGER PRIMARY KEY, country TEXT UNIQUE, capital TEXT UNIQUE, continent TEXT)") # Will only be made if the table does not exist. INTEGER PRIMARY KEY is basically our id for each place. TEXT ensures the data is a string. Ensure all entries are unique with UNIQUE to ensure no entry can be a duplicate. (Also dont do this for continents lol)

    # Insert the countries done earlier into the capitals+countries database.
    edit.executemany("INSERT OR IGNORE INTO capitals (country, capital, continent) VALUES (?, ?, ?)", capitals) # Should ensure that all the countries are inserted as it should keep adding each one until they are all added. INSERT OR IGNORE would be used to ignore anything that will cause an error or crash, in this case duplicates.



    # Commit the changes and close the connection
    database.commit() # Save everything. Else it will remain in RAM.
    print("Database created and data inserted successfully!")

    # create_country_list() ends here. Also any AI code included as part of the list i was too lazy to make ends here (Though AI is a very powerful google alternative so it is still used for research.)

# The following code just needs to add another table to the existing database that will store all of our forecast data.
def create_forecast_list():
    edit.execute("CREATE TABLE IF NOT EXISTS forecasts (forecast_id INTEGER PRIMARY KEY, place_id INTEGER, conditions TEXT, temperature float, date DATE, FOREIGN KEY (place_id) REFERENCES capitals(place_id) ON DELETE CASCADE)") # Foreign key will be referencing things that are in another table, in this case the place_id in the capitals table. ON DELETE CASCADE will delete anything that used a place_id that is no longer in the database file. This should never occur unless the database is messed with.
    database.commit()



# We should now check how many entries there are as that is the amount of IDs we have. This means we can grab all the IDs here and use them to query
def update_forecast_list(): # Update the forecast list
    edit.execute("SELECT COUNT(*) FROM capitals")
    city_amount = edit.fetchone()[0] # Ensure there is () after fetchone else it will not work. [0] ensures it is formatted correctly.
    for count in range(1, city_amount+1): # Ensure that the fully occurs. Add 1 to ensure the last one is included. 
        edit.execute(f"SELECT capital FROM capitals WHERE place_id = {count}")
        city = edit.fetchone()[0]
        URL = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric" # Insets the API key and city we want to find into the link
        status = requests.get(URL) # Check status.
        date = datetime.today().strftime('%Y-%m-%d') # We just need the current date, not time. use strftime to format it. You can see the format used next to it. YYYY-MM-DD.
        if status.status_code == 200: # Should check that the status is the status for ok
            weather_data = status.json() # JSON Stores data.
            weather = weather_data["weather"][0]["description"] # This will get our description of current weather conditions. Weather is like a list and we want to pull what is in that list. In this example its description, which is the first item in the list, so we use [0].
            temperature = weather_data["main"]["temp"] # Get the current temperature. Pulling the temp part from the main part of the data.
            print(f"Weather in {city}: The current conditions are described as {weather} and the temperature is {temperature}°C.") # Combine all the data gathered into an output.
            edit.execute("INSERT OR IGNORE INTO forecasts (place_id, conditions, temperature, date) VALUES (?, ?, ?, ?)", (count, weather, temperature, date)) # Insert each value into the correct area in the SQL table
        else: # If any status other that 200 for ok is returned
            print(f"Error code {status}") # Print the status for troubleshooting
    database.commit() # Save everything. Do this after fetching all data.


def combine_tables():
    edit.execute("CREATE TABLE IF NOT EXISTS combined (entry_id INTEGER PRIMARY KEY, forecast_id INTEGER UNIQUE, place_id INTEGER, country TEXT, capital TEXT, continent TEXT, conditions TEXT, temperature float, date DATE, FOREIGN KEY (forecast_id) REFERENCES forecasts(forecast_id) ON DELETE CASCADE, FOREIGN KEY (place_id) REFERENCES capitals(place_id) ON DELETE CASCADE)") # Makes a table, this time with two foreign keys. Not much that needs to be said here.
    edit.execute("INSERT OR IGNORE INTO combined (forecast_id, place_id, country, capital, continent, conditions, temperature, date) SELECT forecasts.forecast_id, capitals.place_id, capitals.country, capitals.capital, capitals.continent, forecasts.conditions, forecasts.temperature, forecasts.date FROM capitals INNER JOIN forecasts ON capitals.place_id = forecasts.place_id ORDER BY capitals.capital") # Combine the forecasts and capitals tables together based on the place ID. We need to list everything we wanna combine it seems. Put it into the new table i called combined. INNER JOIN is the combine type used here. It ports all listed values over.
    database.commit()

 # MENU SYSTEM
def menu():
    menu = Menu("Choose what you want to do")
    menu.add_option("Get weather data", lambda: selectionmenu())
    menu.add_option("Update Forecast", lambda: update_forecast_list())
    menu.add_option("Create lists.", lambda: createlists())
    menu.add_option("Exit", lambda: print("test"))
    menu.show()

def selectionmenu():
    selectionmenu =  Menu("How do you want to filter your output?")
    selectionmenu.add_option("Select a capital to see data for", lambda: capitalfilter())
    selectionmenu.add_option("Filter by date.", lambda: datefilter())
    selectionmenu.add_option("Show data", lambda: printdata())
    selectionmenu.add_option("Add averages toggle", lambda: averagetoggle())
    selectionmenu.show()

def averagetoggle():
    global average
    print("Do you want to calculate the average temperature for the selected data? (Yes / No)")
    average = input()

def capitalfilter():
    global capital
    edit.execute("SELECT capital, country FROM capitals") # Get both the capital and country columns from capitals and combine them
    templist = edit.fetchall() # Ugly list with a bunch of junk we dont want
    clean_list = [f"{item[0]}, {item[1]}" for item in templist] + ["All"] # Get both the country and capitals and combine them with a " ," in the middle and put them into their own list entry. Do this for each entry. Also add "All" as an option for them to select everything
    capitalmenu = select_menu.create_select_menu(clean_list, "Select a country to see results for") # Put all the results into a menu, run the menu and return what the user selected
    if capitalmenu != "Washington, D.C., United States" and capitalmenu != "All": # Error with splitting with Washington, D.C. due to the ,  in its name. Also fails to split All.
        capital, country = capitalmenu.split(", ") # Because the output will have both the capital and country in 1 string. We need to split that. We will use the capital variable. split will split at a certain point we define (", ") and remove the part we defined (", ")
    else: # If it is Washington.
        capital = "Washington, D.C." # Just do it manually its not worth my time if someone else adds a place with a ", " they can fix it themselves.


def datefilter():
    global date
    print("Enter the date you want to filter by (YYYY-MM-DD) or All:") # TODO: Impliment showing all at some point
    date = input()

def printdata():
    if capital == "All" and date == "All": # If the user wanted to select everything 
        where = ""
    elif capital != "All" and date == "All": # If the user wanted to select a capital but not dates
        where = f" WHERE capital = '{capital}'"
    elif capital == "All" and date != "All": # If the user wanted to select dates but not a capital
        where = f" WHERE date = '{date}'"
    else: # If the user wanted to select both
        where = f" WHERE capital = '{capital}' AND date = '{date}'"
    if average == "Yes": # If the user has set calc temp average to true
        edit.execute(f"SELECT temperature FROM combined{where}") # Should attach the string containing instructions if it exists.
        result = edit.fetchall()
        edit.execute(f"SELECT count(temperature) FROM combined{where}")
        amount = edit.fetchone()[0]
        currentavg = 0
        for count in range(0, amount): # Go from the first forecast entry to the last forecast entry defined by amount
            currentavg = currentavg + int(result[count][0]) # Get the temp from the result, convert to int and add the the current avg
        currentavg = currentavg / amount
        print("Average temperature:", currentavg)
    else:
        edit.execute(f"SELECT * FROM combined{where}") # Should attach the string containing instructions if it exists.
        result = edit.fetchall()
        edit.execute(f"SELECT count(*) FROM combined{where}")
        amount = edit.fetchone()[0]
        for count in range(0, amount): # Go from the first forecast entry to the last forecast entry defined by amount
            print("Country:", result[count][3])
            print("Capital:", result[count][4])
            print("Continent:", result[count][5]) # Just print the forecast we are on and then each part of it. 
            print("Weather:", result[count][6])
            print("Temperature", result[count][7])
            print("Forecast Date:", result[count][8])
            print("\n") # Add new line for better formatting
    input("Press enter to exit") # Turns out the loop means things exit almost instantly due to no user conformation to continue. Add that here.

def createlists():
    create_country_list()
    create_forecast_list()

createlists()
#update_forecast_list() #FIXME: ENABLE AGAIN LATER
combine_tables()
while True:
    menu()

# TODO: Make user input more advanced
# TODO: Ensure the program is able to get data (Such as all countries on a certain day, period or in a certain continent) and be able to do things like list all known data for it or to try calculate averages such as the common weather conditions or most likely a median/ Average TEMP
# TODO: Figure out someway to have parts of the program run automatically skipping any UI such as adding new forecasts. Potentially or ideally implement some sort of system with flags such as running program.py --update-forecast to just run a forecast update.
# TODO: Have the system it is running on run the forecast update function on schedule automatically (Such as every few hours or every day at 6:00). Not really involved with the actual program itself but might as well put it here why not.

# TODO: Complete Menu.

# TODO: ADD CODE COMMENTS TO SOME SECTIONS