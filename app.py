import sqlite3
from flask import Flask, render_template
from flask_httpauth import HTTPBasicAuth
import json
from flask_sqlite_admin_lcl.core import sqliteAdminBlueprint
import random
chars = '0123456789ABCDEF'

with open('config.json') as config_file:
    config = json.load(config_file)

auth = HTTPBasicAuth()

app = Flask(__name__,
            static_url_path='', 
            static_folder='public',)

def get_db_connection():
    conn = sqlite3.connect('database.sqlite')
    conn.row_factory = sqlite3.Row
    return conn

@auth.verify_password
def verify_password(username, password):
    if username == config['username'] and password == config['password']:
        return True
    return False

sqliteAdminBP = sqliteAdminBlueprint(dbPath = './database.sqlite',
                                     decorator=auth.login_required,)
app.register_blueprint(sqliteAdminBP, url_prefix='/db')	

@app.route('/win')
@auth.login_required
def index():
    conn = get_db_connection()
    teams = conn.execute('SELECT * FROM teams').fetchall()
    totalpoints = int(conn.execute('SELECT SUM(points) FROM teams').fetchone()[0] * 100)
    conn.close()
    stuff = {
        "numSegments": len(teams),
        "segments": [],
        'strokeStyle': None,
        'outerRadius' : 142,
    }
    teamsInfo = {}
    usedColors = []
    
    determinePointsArr = []
    
    for i in range(len(teams)):
        color = '#'+''.join(random.sample(chars,6))
        while color in usedColors:
            color = '#'+''.join(random.sample(chars,6))
        usedColors.append(color)
        text = teams[i][2]
        points = int(teams[i][1] * 100)
        teamsInfo[text] = {
            "id": teams[i][0],
            "points": points,
            "teamname": text,
            "builders": teams[i][3].split(','),
        }
        stuff['segments'].append({
                "fillStyle": color,
                "text": text,
                "size": 360 * (points/totalpoints)
        })
        for j in range(points):
            determinePointsArr.append(text)
            
    winnerInt = random.randint(0,len(determinePointsArr)-1)
    degree = 360 * (winnerInt/totalpoints)
    winner = determinePointsArr[winnerInt]
    
    conn = get_db_connection()
    conn.execute('INSERT INTO scores (winner) VALUES (?)', (teamsInfo[winner]['id'],)) #dont you dare remove the comma, it breaks the code
    conn.commit()
    conn.close()
    

    
    return render_template('win.html', stuff=json.dumps(stuff), winnerDeg=degree, winnerInfo=json.dumps(teamsInfo[winner]))

@app.route('/')
@auth.login_required
def base():
    return render_template('enter.html')

@app.route('/latest')
@auth.login_required
def latest():
    conn = get_db_connection()
    latestwinner = conn.execute('SELECT winner FROM scores ORDER BY created DESC;').fetchone()[0]
    winnerInfo = conn.execute('SELECT * FROM teams WHERE id = ?', (latestwinner,)).fetchone()
    conn.close()

    return {
            "id": winnerInfo[0],
            "points": int(winnerInfo[1] * 100),
            "teamname": winnerInfo[2].replace('\t',''),
            "builders": winnerInfo[3].split(','),
        }

app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.run(host='0.0.0.0', port=8809)