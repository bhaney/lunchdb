from .db_helper import connect
import csv
import psycopg2

def getCsv():
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
    return output
