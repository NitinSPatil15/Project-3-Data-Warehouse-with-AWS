# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events;"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs;"
songplay_table_drop = "DROP TABLE IF EXISTS songplays;"
user_table_drop = "DROP TABLE IF EXISTS users;"
song_table_drop = "DROP TABLE IF EXISTS songs;"
artist_table_drop = "DROP TABLE IF EXISTS artists;"
time_table_drop = "DROP TABLE IF EXISTS time;"


# CREATE TABLES

staging_events_table_create= ("""
CREATE TABLE IF NOT EXISTS staging_events(
artist text,
auth text,
firstName text,
gender char,
itemInSession int,
lastName text,
length real,
level text,
location text,
method text,
page text,
registration real,
sessionId int,
song text,
status int,
ts bigint,
userAgent text, 
userId int 
);
""")

staging_songs_table_create = ("""
CREATE TABLE IF NOT EXISTS staging_songs(
num_songs int,
artist_id varchar,
artist_latitude real,
artist_longitude real,
artist_location text,
artist_name text not null,
song_id varchar,
title varchar,
duration real,
year int
);
""")

songplay_table_create = ("""
CREATE TABLE IF NOT EXISTS songplays(
start_time bigint, 
user_id int not null, 
level text, 
song_id varchar, 
artist_id varchar, 
session_id int, 
location text, 
user_agent varchar
);
""")

user_table_create = ("""
CREATE TABLE IF NOT EXISTS users(
user_id int primary key, 
first_name text not null, 
last_name text not null, 
gender char, 
level text);
""")

song_table_create = ("""
CREATE TABLE IF NOT EXISTS songs(
song_id varchar primary key, 
title text not null, 
artist_id varchar, 
year int, 
duration real);
""")

artist_table_create = ("""
CREATE TABLE IF NOT EXISTS artists(
artist_id varchar primary key, 
artist_name text not null, 
artist_location text, 
artist_latitude real, 
artist_longitude real);
""")

time_table_create = ("""
CREATE TABLE IF NOT EXISTS time(
ts timestamp not null, 
hour int, 
day int, 
week int, 
month int, 
year int, 
weekday int);
""")


# STAGING TABLES

staging_events_copy = ("""
copy staging_events from {}
credentials 'aws_iam_role={}' 
format as json {};
""").format(config['S3']['LOG_DATA'], config['IAM_ROLE']['ARN'], config['S3']['LOG_JSONPATH'])

staging_songs_copy = ("""
copy staging_songs from {}
credentials 'aws_iam_role={}' 
json 'auto';
""").format(config['S3']['SONG_DATA'], config['IAM_ROLE']['ARN'])


# FINAL TABLES

songplay_table_insert = ("""
INSERT INTO songplays 
SELECT ts,
       se.userId,
       se.level,
       ss.song_id,
       ss.artist_id,
       se.sessionId,
       se.location,
       se.userAgent
FROM staging_events se, staging_songs ss
WHERE se.page = 'NextSong'
AND se.song = ss.title
AND se.artist = ss.artist_name
AND se.length = ss.duration;
""")

user_table_insert = ("""
INSERT INTO users 
SELECT userid, 
       firstName, 
       lastName, 
       gender, 
       level
FROM staging_events
WHERE page = 'NextSong';
""")

song_table_insert = ("""
INSERT INTO songs
SELECT song_id, 
       title, 
       artist_id, 
       year,        
       duration
FROM staging_songs;
""")

artist_table_insert = ("""
INSERT INTO artists
SELECT artist_id, 
       artist_name, 
       artist_location, 
       artist_latitude, 
       artist_longitude
FROM staging_songs;
""")

time_table_insert = ("""
INSERT INTO time 
SELECT a.start_time,
EXTRACT (HOUR FROM a.start_time), EXTRACT (DAY FROM a.start_time),
EXTRACT (WEEK FROM a.start_time), EXTRACT (MONTH FROM a.start_time),
EXTRACT (YEAR FROM a.start_time), EXTRACT (WEEKDAY FROM a.start_time) FROM
(SELECT TIMESTAMP 'epoch' + start_time/1000 *INTERVAL '1 second' as start_time FROM songplays) a;
""")


# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]
