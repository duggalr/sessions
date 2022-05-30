import sqlite3
import datetime
import flask
from flask import request, render_template, g, session, redirect, url_for
from functools import wraps

import utils


app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config["DATABASE"] = '/Users/rahul/Documents/main/projects/personal_learning_projects/sessions/main.db'

def connect_db():
  sqlite_db = sqlite3.connect(app.config["DATABASE"])
  sqlite_db.row_factory = sqlite3.Row # to return dicts rather than tuples
  return sqlite_db

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
  window_ids = form_data['window_id_list']
  for wid in window_ids:
    sql = 'select title, url from current_windows where window_id = ?'
    cur = g.db.execute(sql, (wid,))
    window_tabs = cur.fetchall()
    for rw in window_tabs:
      sql = 'insert into sessions (session_title, window_id, tab_title, tab_url) values (?, ?, ?, ?)'
      g.db.execute(sql, (session_name, wid, rw['title'], rw['url']))
      g.db.commit()

  return redirect(url_for('home'))

# TODO: save in separate windows and refresh/redirect to home


@app.route('/', methods=['GET', 'POST'])
def home():
  # if request.method == 'POST':
  #   print(request.form)
    # session_name = request.form.get('session_name')
    # for key, val in request.form.items():
    #   if key.startswith("window"):
    #     sql = 'select title, url from current_windows where window_id = ?'
    #     cur = g.db.execute(sql, (val,))
    #     window_tabs = cur.fetchall()
    #     for rw in window_tabs:
    #       sql = 'insert into sessions (session_title, tab_title, tab_url) values (?, ?, ?)'
    #       g.db.execute(sql, (session_name, rw['title'], rw['url']))
    #       g.db.commit()


  sql = 'select * from current_windows where window_focused=1'
  cur = g.db.execute(sql)
  focused_window_tabs = cur.fetchall()
  focused_windows_list = []
  last_refreshed_timestamp = ''
  for rw in focused_window_tabs:
    # last_refreshed_timestamp = rw['t']
    db_timestamp = rw['t']  # 2022-05-30 15:31:12
    dt_timestamp = datetime.datetime.strptime(db_timestamp, '%Y-%m-%d %H:%M:%S')
    ct = datetime.datetime.now()
    td = ct - dt_timestamp
    td_mins = int(round(td.total_seconds() / 60))
    last_refreshed_timestamp = td_mins
    tab_dict = utils.create_tab_dict(rw)
    focused_windows_list.append(tab_dict)

  # sql = "select * from current_windows where window_state='minimized' "
  # cur = g.db.execute(sql)
  # minimized_window_tabs = cur.fetchall()
  # minimized_windows_dict = {}
  # for rw in minimized_window_tabs:
  #   tab_dict = utils.create_tab_dict(rw)
  #   if window_id in minimized_windows_dict:
  #     old_li = minimized_windows_dict[window_id]
  #     old_li.append(tab_dict)
  #     minimized_windows_dict[window_id] = old_li
  #   else: 
  #     minimized_windows_dict[window_id] = [tab_dict]

  sql = 'select * from current_windows where window_focused=0'
  cur = g.db.execute(sql)
  li = cur.fetchall()
  minimized_windows_dict = {}
  active_windows_dict = {}
  for rw in li:
    tab_dict = utils.create_tab_dict(rw)
    window_id = rw['window_id']
    if rw['window_state'] == 'minimized':
      if window_id in minimized_windows_dict:
        old_li = minimized_windows_dict[window_id]
        old_li.append(tab_dict)
        minimized_windows_dict[window_id] = old_li
      else: 
        minimized_windows_dict[window_id] = [tab_dict]
    
    else:
      if window_id in active_windows_dict:
        old_li = active_windows_dict[window_id]
        old_li.append(tab_dict)
        active_windows_dict[window_id] = old_li
      else: 
        active_windows_dict[window_id] = [tab_dict]

  # windows_dict = {}
  # for rw in li:
  #   window_id = rw['window_id']
  #   tab_id = rw['tab_id']
  #   tab_title = rw['title']
  #   tab_url = rw['url']
  #   fav_url = rw['fav_url']
  #   if window_id in windows_dict:
  #     old_li = windows_dict[window_id]
  #     old_li.append({'tab_id': tab_id, 'title': tab_title, 'url': tab_url, 'fav_url': fav_url, })
  #     windows_dict[window_id] = old_li
  #   else: 
  #     windows_dict[window_id] = [{'tab_id': tab_id, 'title': tab_title, 'url': tab_url, 'fav_url': fav_url}]
  
  sql = 'select * from sessions'
  cur = g.db.execute(sql)
  sessions_li = cur.fetchall()
  sessions_dict = {}
  for rw in sessions_li:
    session_title = rw['session_title']
    if session_title in sessions_dict:
      old_li = sessions_dict[session_title]
      old_li.append({'tab_title': rw['tab_title'], 'tab_url': rw['tab_url'], 'fav_url': rw['tab_fav_url']})
      sessions_dict[session_title] = old_li
    else:
      sessions_dict[session_title] = [{'tab_title': rw['tab_title'], 'tab_url': rw['tab_url'], 'fav_url': rw['tab_fav_url']}]


  return render_template(
    'new_home.html', 
    last_refreshed_timestamp=last_refreshed_timestamp,
    focused_window_id=focused_window_tabs[0]['window_id'],
    focused_tabs_list=focused_windows_list,
    minimized_windows_dict=minimized_windows_dict,
    active_windows_dict=active_windows_dict,
    sessions=sessions_dict
  )


@app.route('/refresh_windows', methods=['POST'])
def refresh_window():
  # print('json-data:', request.get_json())
  sql = 'delete from current_windows'
  g.db.execute(sql)
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

      sql = 'insert into current_windows (window_id, window_state, window_focused, tab_id, title, url, fav_url) values (?, ?, ?, ?, ?, ?, ?)'
      g.db.execute(sql, (window_id, window_state, window_focused, tab_id, title, url, fav_url,))
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
  app.run()

# export FLASK_APP=app.py
# export FLASK_ENV=development
# flask run --host 0.0.0.0 --port 5000





