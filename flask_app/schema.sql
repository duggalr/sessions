-- create table current_windows(
--   id int primary key,
--   window_id int,
--   window_state text, 
--   window_focused int,
--   tab_id int,
--   title text, 
--   url text, 
--   fav_url text,
--   t TIMESTAMP DEFAULT (datetime('now','localtime'))
-- );

-- create table sessions(
--   id int primary key,
--   session_title text, 
--   window_id int,
--   tab_title text, 
--   tab_url text,
--   tab_fav_url text,
--   timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
-- );


create table window(
  id serial primary key,
  google_id integer,
  focused boolean,
  state text,
  number_of_tabs integer,
  fetched_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL

  -- title text,
  -- url text,
  -- favicon_url text,
  -- is_active boolean,
  -- last_accessed_ts float,
  -- number_of_tabs int
  -- fetched_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
)

create table tab(
  id serial primary key,
  google_id integer,
  title text,
  url text,
  favicon_url text,
  is_active boolean,
  fetched_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
  window_object_id integer not null,
  FOREIGN KEY (window_object_id) REFERENCES window(id)
)


-- create table saved_windows(
-- -- user saved created windows
-- )

