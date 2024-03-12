import os
import datetime
import psycopg2
import psycopg2.extras
import flask
from flask import request, render_template, g, session, redirect, url_for
from functools import wraps

import utils


app = flask.Flask(__name__)
app.config["DEBUG"] = True

def connect_db():
    conn = psycopg2.connect(
        host = "localhost",
        database = os.environ['LOCAL_DB_NAME'],
        user = os.environ['LOCAL_DB_USER'],
        password = os.environ['LOCAL_DB_PASSWORD']
    )
    return conn

@app.before_request
def before_request():
    g.db = connect_db()
  
@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


## Primary Views ##

@app.route('/', methods=['GET', 'POST'])
def home():
    cur = g.db.cursor(cursor_factory = psycopg2.extras.DictCursor)

    sql = 'select * from browser_window where focused = true'
    cur.execute(sql)

    active_window = cur.fetchone()  # assuming only one

    sql = 'select * from browser_tab where window_object_id = %s'
    cur.execute(sql, (active_window['id'],))
    active_window_tabs = cur.fetchall()

    rv = {
        'active_window': active_window,
        'active_window_tabs': active_window_tabs
    }

    return render_template(
        'new_home_one.html',
        value = rv
    )


@app.route('/refresh_windows', methods=['POST'])
def refresh_window():
    print('json-data:', request.get_json())

    cur = g.db.cursor(cursor_factory = psycopg2.extras.DictCursor)

    sql = 'delete from browser_window'
    cur.execute(sql)
    g.db.commit()

    sql = 'delete from browser_tab'
    cur.execute(sql)
    g.db.commit()

    data = request.get_json()
    for mdict in data:
        window_data = mdict['window_data']
        tab_data_list = mdict['tab_info']
        num_tabs = mdict['num_of_tabs']
        
        sql = """insert into browser_window(
            google_id, focused, state, number_of_tabs
        ) values (%s, %s, %s, %s) RETURNING id"""
        cur.execute(sql, (
            window_data['id'],
            window_data['focused'],
            window_data['state'],
            num_tabs
        ))
        g.db.commit()

        last_inserted_row_id = cur.fetchone()[0]

        for tb_dict in tab_data_list:
            sql = """insert into browser_tab(
                google_id, title, url, favicon_url, is_active, window_object_id
            ) values (%s, %s, %s, %s, %s, %s)"""
            cur.execute(sql, (
                tb_dict['id'],
                tb_dict['title'],
                tb_dict['url'],
                tb_dict.get('favIconUrl', None),
                tb_dict['active'],
                last_inserted_row_id
            ))
            g.db.commit()

    return {'success': True}




if __name__ == "__main__":
  app.run(debug=True)

# export FLASK_APP=app.py
# export FLASK_ENV=development
# flask run --host 0.0.0.0 --port 5000

