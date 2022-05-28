import sqlite3
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


@app.route('/', methods=['GET', 'POST'])
def home():
  if request.method == 'POST':
    print(request.form)
    session_name = request.form.get('session_name')
    for key, val in request.form.items():
      if key.startswith("window"):
        sql = 'select title, url from current_windows where window_id = ?'
        cur = g.db.execute(sql, (val,))
        window_tabs = cur.fetchall()
        for rw in window_tabs:
          sql = 'insert into sessions (session_title, tab_title, tab_url) values (?, ?, ?)'
          g.db.execute(sql, (session_name, rw['title'], rw['url']))
          g.db.commit()


  sql = 'select * from current_windows'
  cur = g.db.execute(sql)
  li = cur.fetchall()

  windows_dict = {}
  for rw in li:
    window_id = rw['window_id']
    tab_title = rw['title']
    tab_url = rw['url']
    fav_url = rw['fav_url']
    if window_id in windows_dict:
      old_li = windows_dict[window_id]
      old_li.append({'title': tab_title, 'url': tab_url, 'fav_url': fav_url})
      windows_dict[window_id] = old_li
    else: 
      windows_dict[window_id] = [{'title': tab_title, 'url': tab_url, 'fav_url': fav_url}]
  
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


  return render_template('home.html', windows=windows_dict, sessions=sessions_dict)


@app.route('/refresh_windows', methods=['POST'])
def refresh_window():
  print('json-data:', request.get_json())
  # sql = 'delete from current_windows'
  # g.db.execute(sql)
  # g.db.commit()
  # data = request.get_json()
  # for li in data:
  #   for di in li:
  #     fav_url = di.get('favIconUrl', None)
  #     title = di['title']
  #     url = di['url']
  #     window_id = di['windowId']
  #     sql = 'insert into current_windows (window_id, title, url, fav_url) values (?, ?, ?, ?)'
  #     g.db.execute(sql, (window_id, title, url, fav_url,))
  #     g.db.commit()

  return {'success': True}


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





