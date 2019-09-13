from flask import Flask, render_template, redirect, url_for, request, session
# from flask_socketio import SocketIO
import sqlite3 as sql
import requests
import json
app = Flask(__name__)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@app.route('/')
def home():
    con = sql.connect("airlines.db")
    con.row_factory = dict_factory
    cur = con.cursor()
    cur.execute('select * from AirlineRoute')
    content = cur.fetchall()

    cur.execute('select distinct icao from AirlineRoute') 
    icao = cur.fetchall()
    icao = [ic['icao'] for ic in icao]
    
    cur.execute('select distinct name from AirlineRoute') 
    name = cur.fetchall()
    name = [ic['name'] for ic in name]

    con.close() 
    return render_template('home.html', content=content, icao=icao, name=name)

@app.route('/searchAirlineRoute', methods=['POST'])
def searchAirlineRoute():
    req_data = request.get_data()
    req_data = json.loads(req_data)
    whereConditions = []
    for key,value in req_data.items():
        if value is not '':
            whereConditions.append("{} = '{}'".format(key, value))
    whereConditions = ' AND '.join(whereConditions)
    if whereConditions == '':
        sql2 = 'SELECT * FROM AirlineRoute'
    else:
        sql2 = 'SELECT * FROM AirlineRoute WHERE ' + whereConditions
    
    con = sql.connect("airlines.db")
    con.row_factory = dict_factory
    cur = con.cursor()
    cur.execute(sql2)
    content = cur.fetchall()

    return json.dumps(content)