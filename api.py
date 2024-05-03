from googleapiclient import discovery
from googleapiclient.errors import HttpError
import os;
import pandas as pd;

'''
This module is used to connect to youtube data API and access multiple API's that are supported
'''

'''
This method
takes input parameter of channel_id and youtube
internally calls 'youtube channels list'
and returns channel data
'''    
def get_channel_details_by_id(channel_id, youtube) :
    try:
        channel_id = channel_id
        request = youtube.channels().list(
            part="snippet,contentDetails,statistics,brandingSettings",
            id=channel_id)
        response = request.execute();

        if 'items' not in response:
            return None
        if response:
            for items in response.get('items', []):
                data = {'channel_id': channel_id,
                        'channel_name': items['snippet']['title'],
                        'channel_description': items['snippet']['description'],
                        'subscription_count':items['statistics']['subscriberCount'],
                        'channel_views': items['statistics']['viewCount'],
                        'playlist_id': items['contentDetails']['relatedPlaylists']['uploads']}
                return data     
    
    except HttpError as e:
        print(f'An HTTP error occurred while fetching channel details: {e}')
        return 'Server error (or) Check your internet connection (or) Please Try again after a few minutes'
    except:
        return 'You have exceeded your YouTube API quota. Please try again tomorrow.'                     

'''
This method
takes input parameter of playlist_id and youtube
internally calls 'youtube playlistItems list'
and returns playlist data
''' 
def get_videos_by_playlist_id(playlist_id, youtube):
    try:
        video_ids = []
        next_page_token = None
        while True:
            request = youtube.playlistItems().list(
                    part = "contentDetails,snippet",
                    playlistId = playlist_id,
                    maxResults = 50,
                    pageToken = next_page_token
                 )
            response = request.execute()

            if 'items' in response:
                for items in response.get('items', []):
                    video_ids.append(items['contentDetails']['videoId'])
                
                if 'nextPageToken' in response:    
                    next_page_token = response.get('nextPageToken')
                else:
                    break
         
        return video_ids  
    except HttpError as e:
        print(f'An HTTP error occurred while fetching videos by playlist id: {e}')
        return 'Server error (or) Check your internet connection (or) Please Try again after a few minutes'
    except:
        return 'You have exceeded your YouTube API quota. Please try again tomorrow.'

'''
This method
takes input parameter of playlist_id and youtube
internally calls 'youtube playlistItems list'
and returns playlist data
''' 
def get_video_details_by_video_id(video_ids, youtube):
    try:
        video_data=[]
        for video_id in video_ids:
            request=youtube.videos().list(
                part = "contentDetails,snippet,statistics",
                id = video_id
            )
            response = request.execute()
            if 'items' not in response:
                return video_data
        
            else:
                for items in response.get('items', []):
                    like_count = 0
                    if 'statistics' in items and 'likeCount' in items['statistics']:
                        like_count = items['statistics']['likeCount']
                    data = {'video_id': items['id'],
                            'video_title': items['snippet']['title'],
                            'video_description': items['snippet']['description'],
                            'thumbnail': items['snippet']['thumbnails']['default']['url'],
                            'view_count': items['statistics']['viewCount'],
                            'like_count': like_count,
                            'comment_count': items['statistics']['commentCount'],
                            'favorite_count': items['statistics']['favoriteCount'],
                            'published_date':items['snippet']['publishedAt'],
                            'caption_status':items['contentDetails']['caption'],
                            'duration':items['contentDetails']['duration']}
                    video_data.append(data)
            
        return video_data 
    except HttpError as e:
         print(f'An HTTP error occurred while fetching videos by video id: {e}')
         return 'Server error (or) Check your internet connection (or) Please Try again after a few minutes'
    
'''
This method
takes input parameter of video_ids and youtube
internally calls 'youtube commentThreads list'
and returns comments of the video
'''
def get_comment_threads_by_video_id(video_ids, youtube):
    try:
        comment_data = []
        for id in video_ids:
            request = youtube.commentThreads().list(
                part ='snippet,replies,id',
                videoId = id
            )
            response = request.execute()

            if 'items' not in response:
                return comment_data;
            
            else:
                for items in response.get('items', []):
                    comment = {'comment_id':items['snippet']['topLevelComment']['id'],
                            'comment_text':items['snippet']['topLevelComment']['snippet']['textOriginal'],
                            'comment_author':items['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                            'comment_published':items['snippet']['topLevelComment']['snippet']['publishedAt']}
                    data = {'video_id':id,
                            'comments': comment}
                    comment_data.append(data)
        return comment_data
    except HttpError as e:
        print(f'An HTTP error occurred while fetching comment threads by video id: {e}')  
        return comment_data
    except Exception as e:
        print(f'An error occurred while fetching comment threads by video id: {e}')     

'''
This method
takes input parameter of channel_id
internally calls 'youtube v3 API'
and 
returns channel data     
'''
def fetch_channel_details(channel_id):
    try:
        API_KEY = os.environ["API_KEY"]

        if API_KEY is None:
            return "Please set your API Key as environment variable!"

        youtube = discovery.build("youtube", "v3", developerKey = API_KEY)

        channel_result = get_channel_details_by_id(channel_id, youtube)
        if channel_result is None:
            return "Invalid channel id. Please enter correct channel id"
        if 'channel_id' not in channel_result:
            return channel_result

        video_ids = get_videos_by_playlist_id(channel_result['playlist_id'], youtube)
        video_data = []
        if video_ids is not None and len(video_ids) > 0:
            video_data = get_video_details_by_video_id(video_ids, youtube)

            comment_data = get_comment_threads_by_video_id(video_ids, youtube)

            if len(video_data) > 0:
                for v_data in video_data:
                    comments = []
                    if comment_data is not None:
                        for c_data in comment_data:
                            if v_data['video_id'] == c_data['video_id']:
                                comments.append(c_data['comments'])
                        if comments:
                            v_data['comments'] = comments  

        return {'channel':channel_result,
                             'videos': video_data,
                             'isMigrated': False
                            }              
    except HttpError as e:
        print(f'An HTTP error occurred: {e}')
        return 'Server error (or) Check your internet connection (or) Please Try again after a few minutes'      