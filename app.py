#!/usr/bin/env python3.6
from flask import Flask,jsonify,request,render_template
from flask_cors import CORS, cross_origin
from config import config
import psycopg2
import csv
from os import getenv,system

from .csv_helper import getCsv
from .db_helper import connect
from .plotting import histRatings

app = Flask(__name__)

@app.route('/getcsv', methods=["GET"])
def makeCsv():
    results = getCsv()
    return jsonify(results)

@app.route('/insert', methods=["GET","POST"])
def insertLunch():
    output = {}
    sql = """INSERT INTO lunch_reviews(timestamp, suggested_lunch, weather,
             temperature_f, username, actual_lunch, rating, comment) 
             VALUES(to_timestamp(%(time)s / 1000.0), %(suggest)s, %(weather)s, %(temp)s, 
             %(user)s, %(actual)s, %(rating)s, %(comment)s); """
    if request.method == 'POST':
        session = connect()
        cur = session.cursor()
        data = request.get_json()
        if data['token'] == getenv("LUNCH_TOKEN"):
            try:
                cur.execute(sql, data)
                session.commit()
                output['success'] = True
                output['text'] = 'OK'
            except (Exception, psycopg2.Error) as error:
                output['success'] = False
                output['text'] = error.pgerror
        else:
           output['success'] = False
           output['text'] = 'API token is not valid.'
        cur.close()
        session.close()
        return jsonify(output)

@app.route('/plot/ratings', methods=["GET"])
def plotRatings():
    output = {}
    output['success'] = False
    username = request.args.get('username')
    sql = "SELECT rating FROM lunch_reviews WHERE username = %s"
    #try:
    session = connect()
    cur = session.cursor()
    cur.execute(sql, (username,))
    rows = cur.fetchall()
    ratings_list = [ i[0] for i in rows ]
    histRatings(username, ratings_list)
    output['success'] = True
    output['text'] = 'https://bots.bijanhaney.com/plots/'+username+'_ratings.png'
    #except(Exception, psycopg2.Error) as error:
    #output['success'] = False
    #output['text'] = error.pgerror
    cur.close()
    session.close()
    return jsonify(output)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run()
