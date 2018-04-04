from flask import Flask,jsonify,request,render_template
from flask_cors import CORS, cross_origin
from config import config
import psycopg2
import csv
from os import getenv,system

def connect():
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

app = Flask(__name__)

@app.route('/getcsv', methods=["GET"])
def makeCsv():
    output = {}
    session = connect()
    cur = session.cursor()
    csv_path = getenv("CSV_PATH")+'/lunch_reviews.csv'
    try:
        with open(csv_path, 'w') as csvfile:
            cw = csv.writer(csvfile)
            cur.execute('SELECT * FROM lunch_reviews')
            rows = cur.fetchall()
            cw.writerow([i[0] for i in cur.description])
            cw.writerows(rows)
        output['success'] = True
        output['text'] = 'https://bots.bijanhaney.com/csv_files/lunch_reviews.csv'
    except (Exception, psycopg2.Error) as error:
        output['success'] = False
        output['text'] = error.pgerror
    cur.close()
    session.close()
    return jsonify(output)

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

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run()
