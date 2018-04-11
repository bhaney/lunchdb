#!/usr/bin/env python3.6
from flask import Flask,jsonify,request,render_template,redirect
from flask_cors import CORS, cross_origin
import psycopg2
import csv
from os import getenv,system

import project_lunch
from project_lunch.csv_helper import (getCsv, getLocationCsv)
from project_lunch.db_helper import connect
from project_lunch.plotting import histRatings
from project_lunch.config import config
from project_lunch.reviews import (getLocationNames, getLocationIds, getIdFromAlias, insertAlias, insertLocation, insertReview, checkAlias)

app = Flask(__name__)

@app.route('/get/reviews', methods=["GET"])
def makeCsv():
    results = getCsv()
    if results['success']:
        return redirect('https://bots.bijanhaney.com/csv_files/lunch_reviews.csv')
    else:
        return 'Could not generate lunch review CSV'

@app.route('/get/locations', methods=["GET"])
def makeLocationCsv():
    results = getLocationCsv()
    if results['success']:
        return redirect('https://bots.bijanhaney.com/csv_files/lunch_locations.csv')
    else:
        return 'Could not generate location CSV'

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
        review = data['context']['review']
        conn = connect()
        cur = conn.cursor()
        if getIdFromAlias(cur, alias):
            output['new_alias'] = False
            output['success'] = True
            output['update'] = { 'message': review + '\n\n Alias already exists'}
        else:
            name_id = getIdFromAlias(cur, name)
            output = insertAlias(cur, alias, name_id, name)
            output['update'] = { 'message': review + '\n\n' + output['text']}
            if output['success']:
                conn.commit()
                output['new_alias'] = True
            else:
                output['new_alias'] = False
        cur.close()
        conn.close()
        return jsonify(output)

@app.route('/newlocation')
def newLocation():
    return render_template('newlocation.html')

@app.route('/insert/location', methods=["GET","POST"])
def postLocation():
    if request.method == 'POST':
        output = {}
        data = request.form
        #check to see if name is just spaces
        name = data['name'].replace(' ','')
        if name == '':
            return render_template('locationthanks.html', 
                    success=False, text='Error: location name is empty')
        conn = connect()
        cur = conn.cursor()
        # check to see if location name is already in database
        if not checkAlias(cur, data['name']):
            output = insertLocation(cur, data)
            if output['success']:
                conn.commit()
                out1 = insertAlias(cur, output['name_id'], output['name_id'], output['name'])
                out2 = insertAlias(cur, output['name'], output['name_id'], output['name'])
                if out1['success'] and out2['success']:
                    conn.commit()
        else:
            output['success'] = False
            output['text'] = 'Location already exists in database.'
        cur.close()
        conn.close()
        return render_template('locationthanks.html', success=output['success'], text=output['text'])

@app.route('/unknown/location', methods=["GET","POST"])
def unknownLocation():
    if request.method == 'POST':
        output = {}
        data = request.get_json()
        review = data['context']['review']
        output['update'] = { 'message': review+'\n\n Add a new location with https://bots.bijanhaney.com/lunch/newlocation' }
        return jsonify(output)

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
