from flask import Flask, render_template, redirect, url_for, request, session
# from flask_socketio import SocketIO
import sqlite3 as sql
import requests
import json
import datetime

app = Flask(__name__)

relativeCountryQuery = ''

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

    cur.execute('select * from EquipmentDatabase')
    equipData = cur.fetchall()

    cur.execute('select distinct region from EquipmentDatabase')
    region = cur.fetchall()
    region = [ic['region'] for ic in region]
    
    cur.execute('select distinct country from EquipmentDatabase')
    country = cur.fetchall()
    country = [ic['country'] for ic in country]

    con.close() 
    return render_template('home.html', content=content, icao=icao, equipData=equipData, name=name, region=region, country=country)

@app.route('/searchRelativeCountries', methods=['POST'])
def searchRelativeCountries():
    global relativeCountryQuery

    req_data = request.get_data()
    req_data = json.loads(req_data)
    whereConditions = []
    for country in req_data['countries']:
        whereConditions.append("country = '{}'".format(country))
    whereConditions = " OR ".join(whereConditions)
    relativeCountryQuery = whereConditions
    sql2 = 'SELECT * FROM EquipmentDatabase WHERE ' + relativeCountryQuery

    con = sql.connect("airlines.db")
    con.row_factory = dict_factory
    cur = con.cursor()
    cur.execute(sql2)
    content = cur.fetchall()

    return json.dumps(content)

@app.route('/searchContent', methods=['POST'])
def searchContent():
    global relativeCountryQuery
    req_data = request.get_data()
    req_data = json.loads(req_data)
    whereConditions = []
    dateStart = ''
    dateEnd = ''

    for key,value in req_data['parameters'].items():
        if value is not '':
            if key == 'effectiveDateStart':
                dateStart = str(value)
            elif key == 'effectiveDateEnd':
                dateEnd = str(value)
            else:
                whereConditions.append("{} = '{}'".format(key, value))
    whereConditions = ' AND '.join(whereConditions)
    if whereConditions == '':
        sql2 = 'SELECT * FROM ' + req_data['flag']
        if dateStart != '':
            if dateEnd == '':
                sql2 += ' WHERE effectiveYear >= "' + dateStart + '"'
            else:
                sql2 += ' WHERE effectiveYear BETWEEN "' + dateStart + '" AND "' + dateEnd + '"'

            if relativeCountryQuery != '' and req_data['flag'] == "EquipmentDatabase":    
                sql2 += ' AND (' + relativeCountryQuery + ')'
        else:
            if relativeCountryQuery != '' and req_data['flag'] == "EquipmentDatabase":                
                sql2 += ' WHERE ' + relativeCountryQuery

    else:
        sql2 = 'SELECT * FROM ' + req_data['flag'] + ' WHERE ' + whereConditions
        if dateStart != '':
            if dateEnd == '':
                sql2 += ' AND effectiveYear >= ' + dateStart
            else:
                sql2 += ' AND effectiveYear BETWEEN ' + dateStart + ' AND ' + dateEnd
        if relativeCountryQuery != '' and req_data['flag'] == "EquipmentDatabase":
            sql2 += ' AND (' + relativeCountryQuery + ')'


    con = sql.connect("airlines.db")
    con.row_factory = dict_factory
    cur = con.cursor()
    cur.execute(sql2)
    content = cur.fetchall()
    con.close()

    return json.dumps(content)