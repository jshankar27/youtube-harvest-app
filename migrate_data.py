import mysql.connector
from datetime import datetime
import re
import os

class SqlConnection:

    date_format = '%Y-%m-%dT%H:%M:%SZ'
    MYSQL_USERNAME = os.environ["MYSQL_USERNAME"]
    MYSQL_PASSWORD = os.environ["MYSQL_PASSWORD"]
   
    def __init__(self):
        sql_conn = mysql.connector.connect(
                host="localhost",
                user=f"{self.MYSQL_USERNAME}",
                password=f"{self.MYSQL_PASSWORD}")
        self.sql_cursor = sql_conn.cursor()
        self.sql_cursor.execute('CREATE DATABASE if not exists youtube_db')
        self.sql_cursor.execute('use youtube_db ')
        self.sql_cursor.execute('''create table if not exists channel (
                           channel_id varchar(255) not null primary key, channel_name varchar(255), channel_type varchar(255),
                           channel_views int, channel_description text, channel_status varchar(255))
                           ''')
        self.sql_cursor.execute('''create table if not exists playlist (
                           playlist_id varchar(255) unique, channel_id varchar(255) , playlist_name varchar(255),
                           primary key (playlist_id), constraint FK_channel_playlist foreign key(channel_id)
                           references channel(channel_id))
                           ''')
        self.sql_cursor.execute('''create table if not exists video (
                           video_id varchar(255) unique, playlist_id varchar(255) , video_name varchar(255),
                           video_description text, plublished_date datetime, view_count int, like_count int,
                           dislike_count int, favorite_count int, comment_count int, duration int, thumbnail varchar(255),
                           caption_status varchar(255), primary key (video_id), 
                           constraint FK_playlist_video foreign key(playlist_id)
                           references playlist(playlist_id))
                           ''')
        self.sql_cursor.execute('''create table if not exists comment (
                    comment_id varchar(255) unique, video_id varchar(255), comment_text text,
                    comment_author varchar(255), comment_published_date datetime, primary key (comment_id),
                    constraint FK_video_comment foreign key(video_id) references video(video_id))
                    ''')
        
    def insert_into_sql_tables(self, data):
        sql_conn = mysql.connector.connect(
            host = "localhost",
            user = f"{self.MYSQL_USERNAME}",
            password = f"{self.MYSQL_PASSWORD}")
        self.sql_cursor = sql_conn.cursor()
        self.sql_cursor.execute('use youtube_db ')
        playlist_id = data['channel']['playlist_id']
        channel_sql = '''REPLACE INTO channel (channel_id, channel_name, channel_type,
                                 channel_views, channel_description, channel_status) values (%s, %s,  %s, %s, %s, %s)'''
        channel_val = (data['channel']['channel_id'], data['channel']['channel_name'], 'null', int(data['channel']['channel_views']),
               data['channel']['channel_description'], 'null')
        self.sql_cursor.execute(channel_sql, channel_val)

        playlist_sql = '''REPLACE INTO playlist (playlist_id, channel_id, playlist_name) 
                                    values (%s, %s, %s)'''
        playlist_val = (playlist_id, data['channel']['channel_id'], 'null')
        self.sql_cursor.execute(playlist_sql, playlist_val)


        for video in data['videos']:
            video_sql = '''REPLACE INTO video (video_id, playlist_id, video_name,
                           video_description, plublished_date, view_count, like_count,
                           dislike_count, favorite_count, comment_count, duration, thumbnail) 
                           values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
            video_val = (video['video_id'], playlist_id, video['video_title'], video['video_description'], 
                            datetime.strptime(video['published_date'], self.date_format),
                            video['view_count'], video['like_count'], 0, video['favorite_count'], video['comment_count'], 
                            int(re.search(r'\d+', video['duration']).group()), video['thumbnail'])
            self.sql_cursor.execute(video_sql, video_val)

            if 'comments' in video:
                for comment in video['comments']:
                    comment_sql = '''REPLACE INTO comment (comment_id, video_id, comment_text,
                                        comment_author, comment_published_date) values (%s, %s, %s, %s, %s)'''    
                    comment_val = (comment['comment_id'], video['video_id'], comment['comment_text'],
                                    comment['comment_author'], datetime.strptime(comment['comment_published'], self.date_format))
                    self.sql_cursor.execute(comment_sql, comment_val)
        sql_conn.commit()

    def get_video_names_with_channel_name(self):
        sql_conn = mysql.connector.connect(
            host = "localhost",
            user = f"{self.MYSQL_USERNAME}",
            password = f"{self.MYSQL_PASSWORD}")
        self.sql_cursor = sql_conn.cursor()
        self.sql_cursor.execute('use youtube_db ')

        select_sql = '''select c.channel_name, v.video_name from video v inner join playlist p on p.playlist_id=v.playlist_id
		                    inner join channel c on c.channel_id=p.channel_id'''
        self.sql_cursor.execute(select_sql)
        return self.sql_cursor.fetchall()
    
    def get_most_video_count_with_channel_name(self):
        sql_conn = mysql.connector.connect(
            host = "localhost",
            user = f"{self.MYSQL_USERNAME}",
            password = f"{self.MYSQL_PASSWORD}")
        self.sql_cursor = sql_conn.cursor()
        self.sql_cursor.execute('use youtube_db ')
        select_sql = '''select c.channel_name, count(v.video_id),v.playlist_id from video v  inner join playlist p on p.playlist_id=v.playlist_id
		inner join channel c on c.channel_id=p.channel_id group by playlist_id'''
        self.sql_cursor.execute(select_sql)
        return self.sql_cursor.fetchall()
    
    def get_top_10_most_watched_videos_with_channel_name(self):
        sql_conn = mysql.connector.connect(
            host = "localhost",
            user = f"{self.MYSQL_USERNAME}",
            password = f"{self.MYSQL_PASSWORD}")
        self.sql_cursor = sql_conn.cursor()
        self.sql_cursor.execute('use youtube_db ')
        select_sql = '''select v.video_name, v.view_count, c.channel_name from video v inner join playlist p on p.playlist_id=v.playlist_id
                            inner join channel c on c.channel_id=p.channel_id where 10 >= (select count(v.view_count) from video v1 
                                    where v1.view_count >= v.view_count) order by v.view_count desc;'''
        self.sql_cursor.execute(select_sql)
        return self.sql_cursor.fetchall()
    
    def get_video_comment_count_With_channel_name(self):
        sql_conn = mysql.connector.connect(
            host = "localhost",
            user = f"{self.MYSQL_USERNAME}",
            password = f"{self.MYSQL_PASSWORD}")
        self.sql_cursor = sql_conn.cursor()
        self.sql_cursor.execute('use youtube_db ')
        select_sql = '''select c.channel_name, v.video_name, v.comment_count from video v inner join playlist p on p.playlist_id=v.playlist_id
		                    inner join channel c on c.channel_id=p.channel_id'''
        self.sql_cursor.execute(select_sql)
        return self.sql_cursor.fetchall()
    
    def get_highest_liked_video_With_channel_name(self):
        sql_conn = mysql.connector.connect(
            host = "localhost",
            user = f"{self.MYSQL_USERNAME}",
            password = f"{self.MYSQL_PASSWORD}")
        self.sql_cursor = sql_conn.cursor()
        self.sql_cursor.execute('use youtube_db ')
        select_sql = '''select c.channel_name, v.video_name, v.like_count from video v inner join playlist p on p.playlist_id=v.playlist_id
                    inner join channel c on c.channel_id=p.channel_id
                    where 1 >= (select count(v.like_count) from video v1 
                    where v1.like_count >= v.like_count)'''
        self.sql_cursor.execute(select_sql)
        return self.sql_cursor.fetchall()
    
    def get_videos_like_count_with_channel_name(self):
        sql_conn = mysql.connector.connect(
            host = "localhost",
            user = f"{self.MYSQL_USERNAME}",
            password = f"{self.MYSQL_PASSWORD}")
        self.sql_cursor = sql_conn.cursor()
        self.sql_cursor.execute('use youtube_db ')
        select_sql = '''select c.channel_name, v.video_name, v.like_count from video v inner join playlist p on p.playlist_id=v.playlist_id
		                    inner join channel c on c.channel_id=p.channel_id'''
        self.sql_cursor.execute(select_sql)
        return self.sql_cursor.fetchall()
    
    def get_total_views_with_channel_name(self):
        sql_conn = mysql.connector.connect(
            host = "localhost",
            user = f"{self.MYSQL_USERNAME}",
            password = f"{self.MYSQL_PASSWORD}")
        self.sql_cursor = sql_conn.cursor()
        self.sql_cursor.execute('use youtube_db ')
        select_sql = '''select c.channel_name, c.channel_views from channel c'''
        self.sql_cursor.execute(select_sql)
        return self.sql_cursor.fetchall()
    
    def get_channels_published_in_2022(self):
        sql_conn = mysql.connector.connect(
            host = "localhost",
            user = f"{self.MYSQL_USERNAME}",
            password = f"{self.MYSQL_PASSWORD}")
        self.sql_cursor = sql_conn.cursor()
        self.sql_cursor.execute('use youtube_db ')
        select_sql = '''select c.channel_name from video v inner join playlist p on p.playlist_id=v.playlist_id
		                    inner join channel c on c.channel_id=p.channel_id where year(v.plublished_date) = "2022"'''
        self.sql_cursor.execute(select_sql)
        return self.sql_cursor.fetchall()
    
    def get_avg_video_duration_for_channels(self):
        sql_conn = mysql.connector.connect(
            host = "localhost",
            user = f"{self.MYSQL_USERNAME}",
            password = f"{self.MYSQL_PASSWORD}")
        self.sql_cursor = sql_conn.cursor()
        self.sql_cursor.execute('use youtube_db ')
        select_sql = '''select c.channel_name, avg(v.duration) from video v inner join playlist p on p.playlist_id=v.playlist_id
                            inner join channel c on c.channel_id=p.channel_id group by v.playlist_id'''
        self.sql_cursor.execute(select_sql)
        return self.sql_cursor.fetchall()
    
    def get_max_comment_count_videos_with_channel_name(self):
        sql_conn = mysql.connector.connect(
            host = "localhost",
            user = f"{self.MYSQL_USERNAME}",
            password = f"{self.MYSQL_PASSWORD}")
        self.sql_cursor = sql_conn.cursor()
        self.sql_cursor.execute('use youtube_db ')
        select_sql = '''SELECT c.channel_name, v.video_name
                        FROM video v
                        INNER JOIN playlist p ON p.playlist_id = v.playlist_id
                        INNER JOIN channel c ON c.channel_id = p.channel_id
                        INNER JOIN (
                            SELECT v.playlist_id, MAX(v.comment_count) AS max_comment_count
                            FROM video v
                            INNER JOIN playlist p ON p.playlist_id = v.playlist_id
                            GROUP BY v.playlist_id
                        ) max_count ON v.playlist_id = max_count.playlist_id AND v.comment_count = max_count.max_comment_count'''
        self.sql_cursor.execute(select_sql)
        return self.sql_cursor.fetchall()