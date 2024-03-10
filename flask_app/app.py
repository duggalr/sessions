import os
# import sqlite3
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
  # # Open a cursor to perform database operations
  # cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)
  # return cur
  return conn

@app.before_request
def before_request():
  g.db = connect_db()
  
@app.teardown_request
def teardown_request(exception):
  db = getattr(g, 'db', None)
  if db is not None:
    db.close()


@app.route('/save-session', methods=['POST'])
def save_session():
  print('data:', request.get_json())
  form_data = request.get_json()
  session_name = form_data['session_name']
  
  sql = 'select * from sessions where session_title = ?'
  cur = g.db.cursor(cursor_factory = psycopg2.extras.DictCursor)
  cur.execute(sql, (session_name,))
  existing_sessions = g.db.fetchall()

  print('length-sessions:', existing_sessions)
  if len(existing_sessions) == 0:
    window_dict = form_data['window_dict']
    for wid in window_dict:
      tab_ids = window_dict[wid]
      for tid in tab_ids:
        sql = 'select title, url from current_windows where window_id = ? and tab_id = ?'
        cur = g.db.execute(sql, (wid, tid,))
        tab_data = cur.fetchone()

        sql = 'insert into sessions (session_title, window_id, tab_title, tab_url) values (?, ?, ?, ?)'
        g.db.execute(sql, (session_name, wid, tab_data['title'], tab_data['url']))
        g.db.commit()

  #   window_ids = form_data['window_id_list']
  #   for wid in window_ids:
  #     sql = 'select title, url from current_windows where window_id = ?'
  #     cur = g.db.execute(sql, (wid,))
  #     window_tabs = cur.fetchall()
  #     for rw in window_tabs:
  #       sql = 'insert into sessions (session_title, window_id, tab_title, tab_url) values (?, ?, ?, ?)'
  #       g.db.execute(sql, (session_name, wid, rw['title'], rw['url']))
  #       g.db.commit()

    return {'success': True}

  else:
    return {'success': False, 'error_message': 'this session already exists...'}





@app.route('/', methods=['GET', 'POST'])
def home():

  cur = g.db.cursor(cursor_factory = psycopg2.extras.DictCursor)
  
  sql = 'select * from current_windows where window_focused=1'
  cur.execute(sql)
  focused_window_tabs = cur.fetchall()
  focused_windows_list = []
  last_refreshed_timestamp = ''
  for rw in focused_window_tabs:
    dt_timestamp = rw['created_at']
    ct = datetime.datetime.now()
    td = ct - dt_timestamp
    td_mins = int(round(td.total_seconds() / 60))
    last_refreshed_timestamp = td_mins
    tab_dict = utils.create_tab_dict(rw)
    focused_windows_list.append(tab_dict)

  print(focused_windows_list)

  return render_template(
    'new_home_one.html',
  )


# @app.route('/', methods=['GET', 'POST'])
# def home():

#   cur = g.db.cursor(cursor_factory = psycopg2.extras.DictCursor)

#   sql = 'select * from current_windows where window_focused=1'
#   cur.execute(sql)
#   focused_window_tabs = cur.fetchall()
#   focused_windows_list = []
#   last_refreshed_timestamp = ''
#   for rw in focused_window_tabs:
#     dt_timestamp = rw['created_at']  # 2022-05-30 15:31:12
#     # dt_timestamp = datetime.datetime.strptime(db_timestamp, '%Y-%m-%d %H:%M:%S')
#     ct = datetime.datetime.now()
#     td = ct - dt_timestamp
#     td_mins = int(round(td.total_seconds() / 60))
#     last_refreshed_timestamp = td_mins
#     tab_dict = utils.create_tab_dict(rw)
#     focused_windows_list.append(tab_dict)

#   sql = 'select * from current_windows where window_focused=0'
#   cur.execute(sql)
#   li = cur.fetchall()
#   minimized_windows_dict = {}
#   active_windows_dict = {}
#   for rw in li:
#     tab_dict = utils.create_tab_dict(rw)
#     window_id = rw['window_id']
#     if rw['window_state'] == 'minimized':
#       if window_id in minimized_windows_dict:
#         old_li = minimized_windows_dict[window_id]
#         old_li.append(tab_dict)
#         minimized_windows_dict[window_id] = old_li
#       else: 
#         minimized_windows_dict[window_id] = [tab_dict]
    
#     else:
#       if window_id in active_windows_dict:
#         old_li = active_windows_dict[window_id]
#         old_li.append(tab_dict)
#         active_windows_dict[window_id] = old_li
#       else: 
#         active_windows_dict[window_id] = [tab_dict]

#   sql = 'select session_title from sessions order by created_at desc'
#   cur.execute(sql)
#   sessions_li = cur.fetchall()
#   sessions_dict = {}
#   for rw in sessions_li:
#     session_title = rw['session_title']
#     # for each session_title, get all rows; create window-dict for each session and save in final sessions_dict
#       # display each session with window-blocks
#     all_windows_query = 'select * from sessions where session_title=?'
#     cur.execute(all_windows_query, (session_title,))
#     all_windows = cur.fetchall()
    
#     session_window_dict = {}
#     for rw in all_windows:
#       window_id = rw['window_id']
#       if window_id in session_window_dict:
#         old_li = session_window_dict[window_id]
#         tab_dict = {'tab_title': rw['tab_title'], 'tab_url': rw['tab_url'], 'fav_url': rw['tab_fav_url']}
#         old_li.append(tab_dict)
#         session_window_dict[window_id] = old_li
#       else:
#         session_window_dict[window_id] = [{'tab_title': rw['tab_title'], 'tab_url': rw['tab_url'], 'fav_url': rw['tab_fav_url']}]

#     sessions_dict[session_title] = session_window_dict


#   if len(focused_windows_list) > 0:
#     return render_template(
#       'new_home.html', 
#       last_refreshed_timestamp=last_refreshed_timestamp,
#       focused_window_id=focused_window_tabs[0]['window_id'],
#       focused_tabs_list=focused_windows_list,
#       minimized_windows_dict=minimized_windows_dict,
#       active_windows_dict=active_windows_dict,
#       sessions=sessions_dict
#     )
#   else:
#     return render_template(
#       'new_home.html', 
#       last_refreshed_timestamp=last_refreshed_timestamp,
#       focused_window_id='',
#       focused_tabs_list=focused_windows_list,
#       minimized_windows_dict=minimized_windows_dict,
#       active_windows_dict=active_windows_dict,
#       sessions=sessions_dict
#     )




@app.route('/refresh_windows', methods=['POST'])
def refresh_window():
  # print('json-data:', request.get_json())
  
  cur = g.db.cursor(cursor_factory = psycopg2.extras.DictCursor)
  sql = 'delete from current_windows'
  cur.execute(sql)
  g.db.commit()

  data = request.get_json()
  for li in data:
    window_dict = li[-1]
    window_id = window_dict['window_id']
    window_state = window_dict['window_state']
    window_focused = window_dict['window_focused']
    if window_focused:
      window_focused = 1
    else:
      window_focused = 0

    for di in li[:-1]:
      fav_url = di.get('favIconUrl', None)
      title = di['title']
      url = di['url']
      # window_id = di['windowId']
      tab_id = di['id']

      # print(window_id, window_state, window_focused, tab_id, title, url, fav_url)
      sql = 'insert into current_windows(window_id, window_state, window_focused, tab_id, title, url, fav_url) values (%s, %s, %s, %s, %s, %s, %s)'
      cur.execute(sql, (window_id, window_state, window_focused, tab_id, title, url, fav_url))
      g.db.commit()

  return {'success': True}
  # return redirect(url_for('home'))


@app.route('/delete_session/<name>', methods=['GET', 'POST'])
def delete_session(name):
  print('session-id:', name)
  sql = 'delete from sessions where session_title=?'
  g.db.execute(sql, (name,))
  g.db.commit()
  return redirect(url_for('home'))


@app.route('/update_session', methods=['POST'])
def update_session():
  data = request.get_json()
  print('data:', data)
  session_name = data['session_name']  

  sql = 'select * from sessions where session_title = ?'
  cur = g.db.execute(sql, (session_name,))
  existing_sessions = cur.fetchall()
  print('length-sessions:', existing_sessions)
  if len(existing_sessions) >= 1:
    window_dict = data['window_dict']
    for wid in window_dict:
      tab_ids = window_dict[wid]
      for tid in tab_ids:
        sql = 'select title, url from current_windows where window_id = ? and tab_id = ?'
        cur = g.db.execute(sql, (wid, tid,))
        tab_data = cur.fetchone()

        sql = 'insert into sessions (session_title, window_id, tab_title, tab_url) values (?, ?, ?, ?)'
        g.db.execute(sql, (session_name, wid, tab_data['title'], tab_data['url']))
        g.db.commit()


  # sql = 'select * from sessions where session_title = ?'
  # cur = g.db.execute(sql, (session_name,))
  # existing_sessions = cur.fetchall()
  # print('length-sessions:', existing_sessions)
  # if len(existing_sessions) >= 1:
  #   window_ids = data['window_id_list']
  #   tab_ids = data['tab_id_list']
  #   for wid in window_ids:
  #     sql = 'select title, url from current_windows where window_id = ?'
  #     cur = g.db.execute(sql, (wid,))
  #     window_tabs = cur.fetchall()
  #     for rw in window_tabs:
  #       sql = 'insert into sessions (session_title, window_id, tab_title, tab_url) values (?, ?, ?, ?)'
  #       g.db.execute(sql, (session_name, wid, rw['title'], rw['url']))
  #       g.db.commit()

  return {'success': True}


@app.route('/delete_session_window', methods=['POST'])
def delete_session_window():
  data = request.get_json()
  st = data['wid']
  li = st.split('wid')
  session_title = li[0].split('session_')[1].split('_')[0]
  window_id = li[1].split('_')[1]

  sql = 'select * from sessions where session_title=?'
  cur = g.db.execute(sql, (session_title,))
  li = cur.fetchall()
  if len(li) <= 1:
    sql = 'delete from sessions where session_title=?'
    g.db.execute(sql, (session_title,))
    g.db.commit()
  else:
    sql = 'delete from sessions where session_title=? and window_id=?'
    g.db.execute(sql, (session_title, window_id,))
    g.db.commit()

  return {'success': True}




@app.route('/open_session/<name>', methods=['GET'])
def open_session(name):
  print('session-name:', name)
  sql = 'select tab_url from sessions where session_title=?'
  cur = g.db.execute(sql, (name,))
  li = cur.fetchall()
  urls = [rw['tab_url'] for rw in li]
  utils.open_links(urls)
  return redirect(url_for('home'))
  


 


if __name__ == "__main__":
  app.run(debug=True)

# export FLASK_APP=app.py
# export FLASK_ENV=development
# flask run --host 0.0.0.0 --port 5000





