import os
import datetime
import json
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

    sql = 'select * from browser_window order by focused desc'
    cur.execute(sql)
    all_windows = cur.fetchall()

    final_window_tab_list = []
    final_window_id_list = []
    c = 1
    for wdi in all_windows:
        sql = 'select * from browser_tab where window_object_id = %s'
        cur.execute(sql, (wdi['id'],))
        c_wd_tabs = cur.fetchall()
        final_window_tab_list.append({
            'window_object_id': wdi['id'],
            'current_count': c,
            'window_title': f'Window {c}',
            'window': wdi,
            'tabs': c_wd_tabs
        })
        final_window_id_list.append(f"window_{ wdi['id'] }")
        c += 1


    # Fetching saved user sessions
    sql = 'select * from saved_session order by created_timestamp desc'
    cur.execute(sql)
    user_sessions = cur.fetchall()

    c = 1
    final_sessions_list = []
    final_sessions_id_list = []
    for sdict in user_sessions:
        sql = 'select * from saved_session_url where session_object_id = %s'
        cur.execute(sql, (sdict['id'],))
        session_tab_urls = cur.fetchall()
        final_sessions_list.append({
            'session_object_id': sdict['id'],
            'current_count': c,
            'session': sdict,
            'tabs': session_tab_urls    
        })
        final_sessions_id_list.append(f"session_{sdict['id']}")
        c += 1

    rv = {
        'final_window_id_list': json.dumps(final_window_id_list),
        'final_window_tab_list': final_window_tab_list,
        'final_sessions_id_list': final_sessions_id_list,
        'final_sessions_list': final_sessions_list
    }

    if request.method == 'POST':
        pass

    return render_template(
        # 'new_home_one.html',
        'new_home_two.html',
        value = rv
    )

    # sql = 'select * from browser_window where focused = true'
    # cur.execute(sql)

    # active_window = cur.fetchone()  # assuming only one

    # sql = 'select * from browser_tab where window_object_id = %s'
    # cur.execute(sql, (active_window['id'],))
    # active_window_tabs = cur.fetchall()

    # sql = 'select * from browser_window where focused = false'
    # cur.execute(sql)    
    # non_active_windows = cur.fetchall()

    # non_active_window_tab_list = []
    # for n_act_wd in non_active_windows:
    #     sql = 'select * from browser_tab where window_object_id = %s'
    #     cur.execute(sql, (n_act_wd['id'],))
    #     c_wd_tabs = cur.fetchall()
    #     non_active_window_tab_list.append({
    #         'window_dict': n_act_wd,
    #         'tabs': c_wd_tabs
    #     })

    # rv = {
    #     'active_window': active_window,
    #     'active_window_tabs': active_window_tabs,
    #     'non_active_windows': non_active_window_tab_list
    # }

    # return render_template(
    #     'new_home_one.html',
    #     value = rv
    # )


@app.route('/sessions', methods=['GET', 'POST'])
def saved_sessions():
    cur = g.db.cursor(cursor_factory = psycopg2.extras.DictCursor)

    sql = 'select * from saved_session order by created_timestamp desc'
    cur.execute(sql)
    user_sessions = cur.fetchall()

    c = 1
    final_sessions_list = []
    final_sessions_id_list = []
    for sdict in user_sessions:
        sql = 'select * from saved_session_url where session_object_id = %s'
        cur.execute(sql, (sdict['id'],))
        session_tab_urls = cur.fetchall()
        final_sessions_list.append({
            'session_object_id': sdict['id'],
            'current_count': c,
            'session': sdict,
            'tabs': session_tab_urls    
        })
        final_sessions_id_list.append(f"session_{sdict['id']}")
        c += 1

    rv = {
        'final_sessions_id_list': final_sessions_id_list,
        'final_sessions_list': final_sessions_list
    }

    return render_template('saved_sessions.html', value = rv)




@app.route('/refresh_windows', methods=['POST'])
def refresh_window():
    print('json-data:', request.get_json())

    cur = g.db.cursor(cursor_factory = psycopg2.extras.DictCursor)

    sql = 'delete from browser_tab'
    cur.execute(sql)
    g.db.commit()

    sql = 'delete from browser_window'
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



@app.route('/create_session', methods=['POST'])
def create_session():
    print('post-data:', request.json)

    session_name = request.json['session_name']
    requested_tab_data = request.json['requested_tabs']
    
    cur = g.db.cursor(cursor_factory = psycopg2.extras.DictCursor)
    
    sql = 'INSERT INTO saved_session(session_name) values (%s) RETURNING id;'
    cur.execute(sql, (session_name,))
    g.db.commit()
    
    saved_session_object_id = cur.fetchone()['id']

    for tb_dict in requested_tab_data:
        tb_url = tb_dict['url']
        tb_title = tb_dict['title']
        tb_favicon_url = tb_dict['favicon_url']

        sql = 'insert into saved_session_url(title, url, favicon_url, session_object_id) values (%s, %s, %s, %s)'
        cur.execute(sql, (tb_title, tb_url, tb_favicon_url, saved_session_object_id,))
        g.db.commit()

    return {'success': True}



@app.route('/delete_session', methods=['POST'])
def delete_session():
    print('post-data:', request.json)

    session_id = request.json['session_id']
    cur = g.db.cursor(cursor_factory = psycopg2.extras.DictCursor)
    
    sql = 'DELETE FROM saved_session_url where session_object_id = %s'
    cur.execute(sql, (session_id,))
    g.db.commit()
    
    sql = 'DELETE FROM saved_session where id = %s'
    cur.execute(sql, (session_id,))
    g.db.commit()

    return {'success': True}




if __name__ == "__main__":
  app.run(debug=True)

# export FLASK_APP=app.py
# export FLASK_ENV=development
# flask run --host 0.0.0.0 --port 5000

