#!/usr/bin/env python3.6
from flask import Flask,jsonify,request,render_template
from flask_cors import CORS, cross_origin
import psycopg2
import csv
from os import getenv,system

import project_lunch
from project_lunch.csv_helper import getCsv
from project_lunch.db_helper import connect
from project_lunch.plotting import histRatings
from project_lunch.config import config
from project_lunch.reviews import (getLocationNames, getLocationIds, getIdFromAlias, insertAlias, insertLocation, insertReview)

app = Flask(__name__)

@app.route('/getcsv', methods=["GET"])
def makeCsv():
    results = getCsv()
    return jsonify(results)

@app.route('/insert/review', methods=["GET","POST"])
def postLunch():
    if request.method == 'POST':
        output = {}
        data = request.get_json()
        location = data['actual']
        output['location'] = location
        if data['token'] == getenv("LUNCH_TOKEN"):
            conn = connect()
            cur = conn.cursor()
            output = insertReview(cur, data)
            if output['success']:
                conn.commit()
                if not getIdFromAlias(cur, location):
                    output['list'] = getLocationNames(cur)
            cur.close()
            conn.close()
        else:
            output['success'] = False
            output['text'] = 'API token is not valid.'
            output['location'] = location
        return jsonify(output)

@app.route('/insert/alias', methods=["GET","POST"])
def postAlias():
    if request.method == 'POST':
        output = {}
        data = request.get_json()
        alias = data['context']['alias']
        name = data['context']['name']
        conn = connect()
        cur = conn.cursor()
        if getIdFromAlias(cur, alias):
            output['new_alias'] = False
            output['success'] = True
            output['update'] = { 'message': 'No need to update. Alias already exists.' }
        else:
            name_id = getIdFromAlias(cur, name)
            output = insertAlias(cur, alias, name_id, name)
            output['update'] = { 'message': output['text'] }
            if output['success']:
                conn.commit()
                output['new_alias'] = True
            else:
                output['new_alias'] = False
        cur.close()
        conn.close()
        return jsonify(output)

@app.route('/insert/location', methods=["GET","POST"])
def postLocation():
    if request.method == 'POST':
        output = {}
        output['update'] = { 'message': 'TODO: A form to add a new location.'}
        return jsonify(output)
'''
        data = request.get_json()
        if data['token'] == getenv("LUNCH_TOKEN"):
            conn = connect()
            cur = conn.cursor()
            location_exists = data['exists']
            location_name = data['exists']
            output = insertReview(cur, data)
            if output['success']:
                conn.commit()
            output['location'] = checkLocation(cur, location)
        else:
            output['success'] = False
            output['text'] = 'API token is not valid.'
            output['location'] = True
        cur.close()
        conn.close()
        return jsonify(output)
'''

@app.route('/plot/ratings', methods=["GET"])
def plotRatings():
    output = {}
    output['success'] = False
    username = request.args.get('username')
    conn = connect()
    cur = conn.cursor()
    if username == 'everyone':
        sql = "SELECT rating FROM lunch_reviews"
        cur.execute(sql)
    else:
        sql = "SELECT rating FROM lunch_reviews WHERE username = %s"
        cur.execute(sql, (username,))
    rows = cur.fetchall()
    ratings_list = [ i[0] for i in rows ]
    if len(ratings_list) != 0:
    	histRatings(username, ratings_list)
    	output['success'] = True
    	output['text'] = 'https://bots.bijanhaney.com/plots/'+username+'_ratings.png'
    else:
        output['success'] = False
        output['text'] = 'User has submitted no reviews to the database.'
    cur.close()
    conn.close()
    return jsonify(output)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run()
