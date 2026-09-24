# Import the necessary modules from Flask and sqlite3
from flask import Flask, render_template, request, redirect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import sqlite3

# Create the Flask app
app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    storage_uri="memory://",
)

VALIDREALMS = {'thequizgame', 'securitydefender', 'bugblaster', 'datasorter'} # whitelist for the valid realms

# Name of the database file (don't change this unless you also update it below)
DB_NAME = 'scores.db'


# This function sets up the database if it doesn't already exist
def init_db():
    # Connect to the SQLite database (it will be created if it doesn't exist)
    with sqlite3.connect(DB_NAME) as conn:
        # Create the 'scores' table with four columns:
        # - id: an auto-incrementing number (primary key)
        # - name: the player's name
        # - score: the player's score
        # and a lastname 
        conn.execute('''
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                lastname TEXT NOT NULL,
                score INTEGER NOT NULL
            )
        ''')
        #Realms completion table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS realms (
                realm TEXT PRIMARY KEY,
                count INTEGER NOT NULL
            )
        ''')

        # Default values for realm table
        conn.execute('INSERT OR IGNORE INTO realms (realm, count) VALUES ("thequizgame", 0)')
        conn.execute('INSERT OR IGNORE INTO realms (realm, count) VALUES ("securitydefender", 0)')
        conn.execute('INSERT OR IGNORE INTO realms (realm, count) VALUES ("bugblaster", 0)')
        conn.execute('INSERT OR IGNORE INTO realms (realm, count) VALUES ("datasorter", 0)')

#This specifies that the following function will run whenever there's any actions taken on the web page
@app.route('/', methods=['GET', 'POST'])
@limiter.limit("1 per minute", methods=["POST"]) # Allows 1 post request per minute


# This function handles both displaying the leaderboard and submitting scores
def leaderboard():
    # If someone has submitted the form (POST request), save their data
    if request.method == 'POST':
        # Get the names and score that the player entered in the form
        name = request.form['name'] #Grabs user data that was submitted in the form
        lastname = request.form['lastname']
        score = request.form['score']
        
        # Save the new score into the database
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute('INSERT INTO scores (name, lastname, score) VALUES (?, ?, ?)', (name, lastname, score))
        
        # Redirect the user back to the main page after submitting
        return redirect('/')
    
    
    # If it's a normal page load (GET request), show the leaderboard
    query = request.args.get('q', '').strip()
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        # Get  name and score entries from the database that fit hall of fame criteria
        # Hall of fame
        cur.execute('SELECT name, lastname, score FROM scores ORDER BY score DESC LIMIT 5')

        halloffame = cur.fetchall() 

        #Stats section
        cur.execute('SELECT AVG(score) FROM scores')
        avgresult = cur.fetchone()

        # Fastest time (lowest score)
        cur.execute('SELECT MIN(score) FROM scores')
        minresult = cur.fetchone()

        # Slowest time (highest score)
        cur.execute('SELECT MAX(score) FROM scores')
        maxresult = cur.fetchone()

        sort = request.args.get('sort', 'score')  # default is score
        sort_order = request.args.get('order', 'asc')

        #Sorting ascending, descending, score/ name
        if sort == 'name' and sort_order == 'asc':
            cur.execute('SELECT name, lastname, score FROM scores WHERE name LIKE ? OR lastname LIKE ? ORDER BY name ASC LIMIT 15', (f'%{query}%', f'%{query}%')) #the (f%`query`) checks for scores that contain what the user entered in searchbar. The reason there is two is because it checks both firstname and lastname, for example, searching "bob" , it would filter out scores that have either or both firstnae/lastname container bob
        elif sort == 'name' and sort_order == 'desc':
            cur.execute('SELECT name, lastname, score FROM scores WHERE name LIKE ? OR lastname LIKE ? ORDER BY name DESC LIMIT 15', (f'%{query}%', f'%{query}%'))
        elif sort == 'score' and sort_order == 'asc':
            cur.execute('SELECT name, lastname, score FROM scores WHERE name LIKE ? OR lastname LIKE ? ORDER BY score ASC LIMIT 15', (f'%{query}%', f'%{query}%'))
        else:
            cur.execute('SELECT name, lastname, score FROM scores WHERE name LIKE ? OR lastname LIKE ? ORDER BY score DESC LIMIT 15', (f'%{query}%', f'%{query}%'))


        entries = cur.fetchall()

        cur.execute('SELECT realm, count FROM realms') #Realm completion
        realm_data = dict(cur.fetchall()) # dict makes the data spit out as a "dictionary" in brackets like ("thequizgame", 5), ("securitydefender", 2) etc 

        avgscore = int(avgresult[0]) if avgresult and avgresult[0] is not None else None # Add fallback for when scores.db is deleted
        minscore = int(minresult[0]) if minresult and minresult[0] is not None else None
        maxscore = int(maxresult[0]) if maxresult and maxresult[0] is not None else None

        

        # Send the HTML page with the most recent leaderboard and renders everything  
        return render_template(
            'index.html', 
            halloffame=halloffame, 
            entries=entries, query=query, 
            average=avgscore, 
            highest=maxscore, 
            lowest=minscore, 
            thequizgame=realm_data["thequizgame"],
            securitydefender=realm_data["securitydefender"],
            bugblaster=realm_data["bugblaster"],
            datasorter=realm_data["datasorter"])

@app.route('/complete/<realm>', methods=['POST']) #Uses dynamic routing to prevent me from routing 4 times
@limiter.limit("4 per minute", methods=["POST"]) # Allows 4 post request per minute
def complete_realm(realm): #(realm is defined in <realm>)
    if realm not in VALIDREALMS:
        return redirect('/')  # ignore unknown realm url
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('UPDATE realms SET count = count + 1 WHERE realm = ?', (realm,))
    return redirect('/') #Redirects back to / (home)


@app.errorhandler(429) #What happens when you get rate limited
def ratelimit_handler(e):
    return render_template('429.html'), 429 #Renders 429.html

@app.errorhandler(405)
def method_not_allowed(e):
    return redirect('/')

#----- Mainline program: This code executes when we run this file.-----#

init_db()  # Set up the database before starting the web app

# Start the Flask server for local testing (Comment the version not being used)
if __name__ == "__main__":
    app.run(debug=True)

# Use this version when testing on your computer only

    #app.run(debug=True, host='0.0.0.0') 
# Use this version if you want to test it on a phone/tablet connected to the same Wi-Fi