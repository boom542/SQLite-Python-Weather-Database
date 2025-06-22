import sqlite3 as SQL # SQLite3 is fine enough for this. Built into python so we use it here. Also just change it so it says SQL in things like commands.
import os # Gonna need this for ensuring things stay in the same folder as the program.
import requests # Need this to do things such as request the api for retrieving place weather. Not installed by default on windows for some reason it seems.
from datetime import datetime # Need this to get the date and time for our forecasts table.
from pymenu import Menu, select_menu # Pymenu in not in python by default. pip install pymenu-console should do the trick on most systems. Its basic but it does the trick and saves me making one myself.
import argparse # Used to get commandline arguments. Not included by default. 
from dotenv import load_dotenv # Not installed by default
from flask import Flask, request, jsonify, render_template # Not installed by default. 

# Set capital and date to all cause we wanna show everything even if the user doesnt select that by default and not calculate averages by default. Also set the API key.
load_dotenv() # load .env
API_KEY = os.getenv("API_KEY") # Get the API key from the .env. This requires OS.
capital = "All"
date = "All"
average = "No"

# The code below is gonna be needed to set a bunch of critical stuff involving the databases.
def crit(): # This is done to open this in different places depending on what the user is doing to avoid a crashing bug related to running in different instances or cores i think idk this just fixed it
    global database, edit, script_path
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
        elif status.status_code == 401: # If there is no API key in .env, or it is invalid, it should return a 401 status. It could also be some other error.
            print("Error status 401: It is likely you have either an invalid or non existent API key in the .env file.")
            print("Do you want to create a .env with an API key? (Y/N)")
            print("PLEASE ENSURE .ENV IS DELETED IF EXISTENT")
            key_creation = input()
            if key_creation == "Y":
                env_loc = os.path.join(script_path, ".env") # Make sure .env is put into the same folder as the program and not where it is being ran.
                env_file = open(env_loc, "a") # Open for appending. Wil create if not existent.
                print("Please get a valid OpenWeatherMap API key from https://openweathermap.org/api and paste it here.")
                print("Please enter your OpenWeatherMap API key:")
                api_key = input()
                env_file.write(f"API_KEY={api_key}") #Write the API key to the .env
                env_file.close()
                print("Please reload the program.")
                break
            elif key_creation == "N":
                print("Ok, exiting.")
                break
            else:
                print("Invalid. Exiting")
                input("Press enter to exit") # Give the user a chance to read the invalid input message before closing.
                break
        else: # If any status other that 200 for ok / 401 for is returned
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
    menu.add_option("Exit", lambda: quit())
    menu.show()

def selectionmenu():
    selectionmenu =  Menu("How do you want to filter your output?")
    selectionmenu.add_option("Select a capital to see data for", lambda: capitalfilter())
    selectionmenu.add_option("Filter by date.", lambda: datefilter())
    selectionmenu.add_option("Add averages toggle", lambda: averagetoggle())
    selectionmenu.add_option("Show data", lambda: tuiprintdata())
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

def tuiprintdata(): # Since the menu generally instantly reloads we need to just add a pause to show the user using terminal the results first. This should allow me to do that only if done in the TUI
    printdata()
    input("Press Enter to continue.")

def printdata():
    if capital == "All" and date == "All": # If the user wanted to select everything 
        where = ""
    elif capital != "All" and date == "All": # If the user wanted to select a capital but not dates
        where = f" WHERE capital = '{capital}'"
    elif capital == "All" and date != "All": # If the user wanted to select dates but not a capital
        where = f" WHERE date = '{date}'"
    else: # If the user wanted to select both
        where = f" WHERE capital = '{capital}' AND date = '{date}'"
    if average == "Yes" or average == True: # If the user has set calc temp average to true
        edit.execute(f"SELECT temperature FROM combined{where}") # Should attach the string containing instructions if it exists.
        result = edit.fetchall()
        edit.execute(f"SELECT count(temperature) FROM combined{where}")
        amount = edit.fetchone()[0]
        currentavg = 0
        for count in range(0, amount): # Go from the first forecast entry to the last forecast entry defined by amount
            currentavg = currentavg + float(result[count][0]) # Get the temp from the result, convert to int and add the the current avg
        currentavg = round(currentavg / amount, 5)
        currentavg = str(currentavg) # Calc the average by taking the final total and dividing it by total entries
        output = "Average temperature to 5 d.p: " +  currentavg.replace(",","")
        print(output)
        return output
    else:
        edit.execute(f"SELECT * FROM combined{where}") # Should attach the string containing instructions if it exists.
        result = edit.fetchall()
        edit.execute(f"SELECT count(*) FROM combined{where}")
        amount = edit.fetchone()[0]
        output = ""
        for count in range(0, amount): # Go from the first forecast entry to the last forecast entry defined by amount
            sqlouput = str(result[count][3]) # Set the variable to the stringed version of the selected tuple.
            output = output + "Country: " + sqlouput + "\n" # For some reason stringing the tuple here and adding it didn't work??? Anyway doing this fixes it so idc
            sqlouput = str(result[count][4])
            output = output + "Capital: " + sqlouput +"\n"
            sqlouput = str(result[count][5])
            output = output + "Continent: " + sqlouput + "\n"
            sqlouput = str(result[count][6])
            output = output + "Weather:" + sqlouput + "\n"
            sqlouput = str(result[count][7])
            output = output + "Temperature: " + sqlouput + "\n"
            sqlouput = str(result[count][8])
            output = output + "Forecast Date: " + sqlouput + "\n"
            output = output + "\n" # Add new line for better formatting
        print(output)
        return output
    #input("Press enter to exit") # Turns out the loop means things exit almost instantly due to no user conformation to continue. Add that here.

def createlists():
    create_country_list()
    create_forecast_list()

#Web server junk

def flasksetup():
    print("NOTE: This should probably not be exposed to the public internet.")
    print("Use -tui to use the terminal")
    print("Use -update to update the databases")
    server = Flask(__name__) # Create a flask server.
    @server.route("/")
    def index(): # The main page that will show if the user goes to the IP.
        return render_template("index.html")
    @server.route("/process", methods = ["POST"]) # /Recieving and sending page data on the main page
    def process():
        crit()
        global capital, date, average
        data = request.get_json() # Get the data from the javascript sending user input from the page
        capital = data.get("city")
        date = data.get("date")
        if date == "": # If the user entered no date on the site then date should return blank
            date = "All" # Set it to all for later
        average = data.get("average")
        print(capital, date, average)
        return jsonify({"message": printdata()}) # Change to actual output later
    if __name__ == "__main__":
        server.run(debug = False, host="0.0.0.0", port=5000)

arguments = argparse.ArgumentParser() # Create a thing that looks for arguments.
arguments.add_argument("-update", action="store_true", help="Create (If not existent), update and combine all the weather databases") # Create a valid argument for the user. action="store_true" just means it will set to true if the user adds it and therefore will activate the updating of the lists if used in the if statement below
arguments.add_argument("-tui", action="store_true", help="Will open a terminal menu")
selectedarguments = arguments.parse_args() # Get whatever arguments the user used
if selectedarguments.update: # If the user decided to use the update argument
    crit() # Crit opens the database
    createlists()
    update_forecast_list()
    combine_tables()
elif selectedarguments.tui: # If the user decided to use the terminal interface
    while True:
        crit()
        menu()
else: # If the user started it normally (Use the web GUI)
    flasksetup() # Starts the flask web server stuff

# LEGACY CODE BELOW TO USE FOR DEBUGGING OR TESTING
#createlists()
#update_forecast_list()
#combine_tables()
#while True:
#    menu()