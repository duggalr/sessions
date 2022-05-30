import webbrowser


def open_links(url_list):
  for url in url_list: 
    webbrowser.open(url, new=1, autoraise=True)



def create_tab_dict(rw):
  window_id = rw['window_id']
  tab_id = rw['tab_id']
  tab_title = rw['title']
  tab_url = rw['url']
  fav_url = rw['fav_url']
  return {'window_id': window_id, 'tab_id': tab_id, 'title': tab_title, 'url': tab_url, 'fav_url': fav_url}
  # if window_id in windows_dict:
  #   old_li = windows_dict[window_id]
  #   old_li.append({'tab_id': tab_id, 'title': tab_title, 'url': tab_url, 'fav_url': fav_url, })
  #   windows_dict[window_id] = old_li
  # else: 
  #   windows_dict[window_id] = [{'tab_id': tab_id, 'title': tab_title, 'url': tab_url, 'fav_url': fav_url}]






