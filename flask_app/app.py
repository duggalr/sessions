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

    sql = 'select * from current_windows where window_focused=1'
    cur.execute(sql)
    focused_window_tabs = cur.fetchall()
    focused_window_tab_list = []
    last_refreshed_timestamp = ''
    for rw in focused_window_tabs:
        dt_timestamp = rw['created_at']
        ct = datetime.datetime.now()
        td = ct - dt_timestamp
        td_mins = int(round(td.total_seconds() / 60))
        last_refreshed_timestamp = td_mins
        tab_dict = utils.create_tab_dict(rw)
        focused_window_tab_list.append(tab_dict)

    print(focused_window_tab_list)

    return render_template(
    'new_home_one.html',
    )


@app.route('/refresh_windows', methods=['POST'])
def refresh_window():
    print('json-data:', request.get_json())

    cur = g.db.cursor(cursor_factory = psycopg2.extras.DictCursor)

    # TODO: create new schema and run below; show in UI and finalize the UI 

    sql = 'delete from window'
    cur.execute(sql)
    g.db.commit()

    sql = 'delete from tab'
    cur.execute(sql)
    g.db.commit()

    data = request.get_json()
    for mdict in data:
        window_data = mdict['window_data']
        tab_data_list = mdict['tab_info']
        num_tabs = mdict['num_of_tabs']
        
        sql = """insert into window(
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
            sql = """insert into tab(
                google_id, title, url, favicon_url, is_active, window_object_id
            ) values (%s, %s, %s, %s, %s)"""
            cur.execute(sql, (
                tb_dict['id'],
                tb_dict['title'],
                tb_dict['url'],
                tb_dict['favIconUrl'],
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

