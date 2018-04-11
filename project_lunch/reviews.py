from .db_helper import connect
import csv
import psycopg2
from os import getenv

def getLocationNames(cur):
    sql = "SELECT name from locations;"
    cur.execute(sql)
    rows = cur.fetchall()
    lunch_list = [i[0] for i in rows]
    return lunch_list

def getLocationIds(cur):
    sql = "SELECT name_id from locations;"
    cur.execute(sql)
    rows = cur.fetchall()
    lunch_list = [i[0] for i in rows]
    return lunch_list

def getIdFromAlias(cur, location):
    sql = "SELECT name_id FROM aliases WHERE alias=%s;"
    cur.execute(sql, (location,))
    rows = cur.fetchone()
    if rows == None:
        return False
    else:
        return rows[0]

def insertAlias(cur, alias, nameid, name):
    sql = "INSERT INTO aliases (alias, name_id) VALUES (%s, %s);"
    data = (alias, nameid)
    output = insertDatabase(cur, sql, data)
    output['text'] = '**'+alias+'** registered as alias for **'+name+'**'
    return output

def insertLocation(cur, data):
    sql = """INSERT INTO locations(name_id, name, type, description,
             price, walk_time_min, location) VALUES (LOWER(REPLACE(%(name)s,' ', '_')),
             %(name)s, %(type)s, %(desc)s, %(price)s, %(walk_time)s, %(location)s); """
    output = insertDatabase(cur, sql, data)
    output['name_id'] = data['name'].lower().replace(" ", "_")
    output['name'] = data['name']
    return output

def insertReview(cur, data):
    sql = """INSERT INTO lunch_reviews(timestamp, suggested_lunch, weather,
             temperature_f, username, actual_lunch, rating, comment) 
             VALUES(to_timestamp(%(time)s / 1000.0), %(suggest)s, %(weather)s,
             %(temp)s, %(user)s, %(actual)s, %(rating)s, %(comment)s); """
    output = insertDatabase(cur, sql, data)
    return output

def insertDatabase(cur, sql, data):
    output = {}
    try:
        cur.execute(sql, data)
        output['success'] = True
        output['text'] = 'OK'
    except (Exception, psycopg2.Error) as error:
        output['success'] = False
        output['text'] = error.pgerror
    return output
