from streamlit_option_menu import option_menu
import streamlit as st
import pandas as pd
import api

from save_data import MongoConnection
from migrate_data import SqlConnection

with st.sidebar:
    selected = option_menu(
        menu_title="Menu",
        options = ["Home", "Search Channel", "Migrate", "Analyse"],
        icons = ["house-heart-fill", "search", "database-fill-add", "card-list"],
        menu_icon = "menu-button",
        default_index=0
    )

if selected=="Home":
    st.title("Youtube channel Harvest App")

    st.markdown(''' 
                
                :blue[The Youtue Data Harvesting and Warehousing is an application built on streamlit  
                framework that allows users to access and analyse data from multiple 
                YouTube channels.]
                
                ''')
    
    st.markdown('''### :red[Search:]''')
    st.markdown('''Channel details of the channel id enetered will be stored in MONGO Database''')
    st.markdown('''### :red[Migrate:]''')
    st.markdown('''Channel details will be migrated from MONGO database to MYSQL database''')
    st.markdown('''### :red[Analyse:]''')
    st.markdown('''Anaytical data will be populated based on selection''')

if selected=="Search Channel":
    st.title(f"Channel Details - Data Collection")
    
    channel_id = st.text_input('Enter Channel Id:', value = "", type = "default",
         autocomplete = None, placeholder = None, disabled = False, label_visibility = "visible")
    submitted = st.button('Search and Collect Channel Details')
    
    if submitted:
        with st.spinner("Running operation..."):
            channel_result = api.fetch_channel_details(channel_id)
            
            if 'channel' not in channel_result:
                st.error(channel_result)
            
            mongo_connection = MongoConnection()
            conn_result = mongo_connection.connect_mongo_database()
            
            result = mongo_connection.insert_into_mongodb(channel_result)
            if result.acknowledged:       
                st.success('Data collected successfully!', icon="✅")
            else:
                st.error('Failed to collect Data! Please try again later', icon="🚨")


if selected == "Migrate":
    st.title(f"Migrate to SQL from Data Lake")
    sql_connection = SqlConnection()
    mongo_connection = MongoConnection()
    mongo_connection.connect_mongo_database()
    channel_names = [] 

    result = mongo_connection.list_channel_names()
    
    for item in result:
        channel_names.append(item['channel']['channel_name']) 

    #Display only the channels that are not migrated yet
    if len(channel_names) == 0: 
        st.error("All the saved channels are migrated already! Please search a channel and store to migrate!")        
    
    else:
        option = st.selectbox('Select the channel to migrate to SQL Database',
                 options = channel_names, key = 'channel_names',
                 placeholder = "Select channel")
        
        if option != "Select one":
            migrate = st.button('Migrate')
            print(sql_connection.sql_cursor)

            if migrate:
                with st.spinner("Running operation..."):
                    result = mongo_connection.find_selected_channel(option)
                    sql_result = sql_connection.insert_into_sql_tables(result)
                    result['isMigrated'] = True;
                    mongo_connection.upsert_into_mongodb(result)
                st.success("Channel migrated successfully!")    

if selected == "Analyse":
    st.title("Analyse Channel Data")
    analysis_questions = ["What are the names of all the videos and their corresponding channels?",
                           "Which channels have the most number of videos, and how many videos do they have?",
                           "What are the top 10 most viewed videos and their respective channels?",
                           "How many comments were made on each video, and what are their corresponding video names?",
                           "Which videos have the highest number of likes, and what are their corresponding channel names?",
                           "What is the total number of likes and dislikes for each video, and what are their corresponding video names?",
                           "What is the total number of views for each channel, and what are their corresponding channel names?",
                           "What are the names of all the channels that have published videos in the year 2022?",
                           "What is the average duration of all videos in each channel, and what are their corresponding channel names?",
                           "Which videos have the highest number of comments, and what are their corresponding channel names?"]
    option = st.selectbox('Select a analysis qustion', options = analysis_questions, 
                            key = 'analysis_questions',
                            placeholder = "Select to analyse")
    
    sql_connection = SqlConnection()
    if option == "What are the names of all the videos and their corresponding channels?":
        result = sql_connection.get_video_names_with_channel_name()
        df = pd.DataFrame(result)
        print("What are the names of all the videos and their corresponding channels? --> ", df)
        df.columns = ['Channel Name', 'Video Name']
        st.dataframe(df, hide_index=True)

    if option == "Which channels have the most number of videos, and how many videos do they have?":
        result = sql_connection.get_most_video_count_with_channel_name()
        df = pd.DataFrame(result)
        df.drop(df.columns[[2]], axis=1, inplace=True)
        df.columns = ['Channel Name', 'Video Count']
        st.dataframe(df, hide_index=True)

    if option == "What are the top 10 most viewed videos and their respective channels?":
        result = sql_connection.get_top_10_most_watched_videos_with_channel_name()
        df = pd.DataFrame(result)
        df.drop(df.columns[[1]], axis=1, inplace=True)
        df.columns = ['Channel Name', 'Video Name']
        st.dataframe(df, hide_index=True)

    if option == "How many comments were made on each video, and what are their corresponding video names?":
        result = sql_connection.get_video_comment_count_With_channel_name()
        df = pd.DataFrame(result)
        df.columns = ['Channel Name', 'Video Name', 'Comment Count']
        st.dataframe(df, hide_index=True)  

    if option == "Which videos have the highest number of likes, and what are their corresponding channel names?":
        result = sql_connection.get_highest_liked_video_With_channel_name()
        df = pd.DataFrame(result)
        df.drop(df.columns[[2]], axis=1, inplace=True)
        df.columns = ['Channel Name', 'Video Name']
        st.dataframe(df, hide_index=True)

    if option == "What is the total number of likes and dislikes for each video, and what are their corresponding video names?":
        result = sql_connection.get_videos_like_count_with_channel_name()
        df = pd.DataFrame(result)
        df.columns = ['Channel Name', 'Video Name', 'Like & Dislike count']
        st.dataframe(df, hide_index=True)

    if option == "What is the total number of views for each channel, and what are their corresponding channel names?":
        result = sql_connection.get_total_views_with_channel_name()
        df = pd.DataFrame(result)
        df.columns = ['Channel Name', 'Channel views']
        st.dataframe(df, hide_index=True)

    if option == "What are the names of all the channels that have published videos in the year 2022?":
        result = sql_connection.get_channels_published_in_2022()
        df = pd.DataFrame(result)
        df.columns = ['Channel Name']
        st.dataframe(df, hide_index=True)

    if option == "What is the average duration of all videos in each channel, and what are their corresponding channel names?":
        result = sql_connection.get_avg_video_duration_for_channels()
        df = pd.DataFrame(result)
        df.columns = ['Channel Name', 'Average Video duration']
        st.dataframe(df, hide_index=True)

    if option == "Which videos have the highest number of comments, and what are their corresponding channel names?":
        result = sql_connection.get_max_comment_count_videos_with_channel_name()
        df = pd.DataFrame(result)
        df.columns = ['Channel Name', 'Video Name']
        st.dataframe(df, hide_index=True)