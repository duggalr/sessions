create table current_windows(
  id int primary key,
  window_id int,
  tab_id int,
  title text, 
  url text, 
  fav_url text
);

create table sessions(
  id int primary key,
  session_title text, 
  tab_title text, 
  tab_url text,
  tab_fav_url text,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
);


  
