from googleapiclient.discovery import build
import mysql.connector
import pandas as pd
import streamlit as st
from datetime import datetime
from dateutil import parser

#sql Connect
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="Arun@1989",
    database="GuviMDT33"
)
cursor = conn.cursor()

#API Key Connection

def Api_connect():
    Api_Id="AIzaSyBtZDZO8Rydxa17fckH1XEQpTE-aX8QVwo"

    api_service_name="youtube"
    api_version="v3"

    youtube=build(api_service_name,api_version,developerKey=Api_Id)

    return youtube

youtube=Api_connect()




#API Key Connection

def Api_connect():
    Api_Id="AIzaSyBtZDZO8Rydxa17fckH1XEQpTE-aX8QVwo"

    api_service_name="youtube"
    api_version="v3"

    youtube=build(api_service_name,api_version,developerKey=Api_Id)

    return youtube

youtube=Api_connect()


#get channels information 
def get_channel_details(channel_id):
    request=youtube.channels().list(
                    part="snippet,ContentDetails,statistics,status",
                    id=channel_id
    )
    response=request.execute()

    for i in response['items']:
        data=dict(channel_id=i["id"],
                channel_name=i["snippet"]["title"],
                sub_count=i['statistics']['subscriberCount'],
                view_count=i["statistics"]["viewCount"],
                videos_count=i["statistics"]["videoCount"],
                channel_description=i["snippet"]["description"],
                playlist_id=i["contentDetails"]["relatedPlaylists"]["uploads"],
                channel_status = i['status']['privacyStatus'])
    return data
    
    

#get videos ids
def get_video_ids(channel_id):
    channel_details = get_channel_details(channel_id)
    unique_playlist_id = channel_details['playlist_id']
    video_ids = []
    nextPageToken = None
    while True:
        response = youtube.playlistItems().list(
            playlistId = unique_playlist_id, 
            part = 'snippet,id',
            maxResults = 50,
            pageToken = nextPageToken
        ).execute()
        for item in response['items']:
            video_ids.append(item['snippet']['resourceId']['videoId'])
        nextPageToken = response.get('nextPageToken')
        if(nextPageToken is None):
            break
    return video_ids

                                

def durationInSeconds(duration):
    duration =list(duration)
    del duration[0:2]
    duration_seconds = 0
    for i,e in enumerate(duration):
        if(e == 'H'):
            duration_seconds += int(duration[i-1])* 60 * 60
        elif(e == 'M'):
            duration_seconds += int(duration[i-1])* 60
        elif(e == 'S'):
            duration_seconds += int(duration[i-1])
    return duration_seconds

#Changing Date format
def changeDateFormat(date_string):
    datetime_obj = parser.isoparse(date_string)
    format_datetime = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
    return format_datetime

#get video information
def get_video_details(video_ids):
    video_details = []  
 
    for i in range(0, len(video_ids), 50):
        response = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=','.join(video_ids[i:i + 50])).execute()
        
        for item in response['items']:
            data = dict(
                video_id = item.get('id'),
                channel_id = item['snippet'].get('channelId'), 
                video_name = item['snippet'].get('title'),
                video_description = item['snippet'].get('description'),
                published_date = item['snippet'].get('publishedAt'),
                view_count = item['statistics'].get('viewCount'),
                like_count = item['statistics'].get('likeCount'),
                favorite_count = item['statistics'].get('favoriteCount'),
                comment_count = item['statistics'].get('commentCount'),
                duration = item['contentDetails'].get('duration') ,                
                thumbnail = item['snippet']['thumbnails']['default']['url'],                
                caption_status = item['contentDetails'].get('caption')                
            )
            date_string = data['published_date'] 
            date_string = changeDateFormat(date_string)
            data['published_date'] = date_string
            duration = data['duration']
            duration = durationInSeconds(duration)
            data['duration'] = duration                
            video_details.append(data)
    return video_details


#get comment information
def get_comment_details(video_ids):
    try:        
        comment_details = []
        for video_id in video_ids:
            nextPageToken = None
            video_response = youtube.videos().list(part="snippet,statistics", id=video_id).execute()

            comments_enabled = int(video_response["items"][0]["statistics"]['commentCount'])
            comments_enabled
            if comments_enabled != 0:
                
                while True:
                
                       
                    response = youtube.commentThreads().list(
                        videoId = video_id,
                        part = 'snippet',
                        maxResults = 50,
                        pageToken = nextPageToken                        
                    ).execute()
                    if response['items']:
        
                        for item in response['items']:
                            data = dict(
                                comment_id = item.get('id'),
                                video_id = item['snippet'].get('videoId'),
                                comment_text = item['snippet']['topLevelComment']['snippet'].get('textDisplay'),
                                comment_author = item['snippet']['topLevelComment']['snippet'].get('authorDisplayName'),
                                comment_published_date =  item['snippet']['topLevelComment']['snippet'].get('publishedAt')
                            )
                            comment_details.append(data)
                    nextPageToken = response.get('nextPageToken')
                    if(nextPageToken is None):
                        break
                
    except Exception as err:
        print(err)
        pass
    return  comment_details

#Creating Tables in MYSQL
def create_tables():
    cursor.execute("Create Table IF NOT EXISTS Channel (channel_id varchar(255) PRIMARY KEY, channel_name varchar(255) NOT NULL, sub_count int, channel_views int, channel_description text,channel_status varchar(255))")
    cursor.execute("Create Table IF NOT EXISTS Video (video_id varchar(255) PRIMARY KEY, channel_id varchar(255) NOT NULL, video_name varchar(255), video_description text, published_date datetime, view_count int, like_count int, favorite_count int, comment_count int, duration int, thumbnail varchar(255), caption_status varchar(255), FOREIGN KEY (channel_id) REFERENCES Channel(channel_id))")
    cursor.execute("Create Table IF NOT EXISTS Comment (comment_id varchar(255) PRIMARY KEY, video_id varchar(255) NOT NULL,comment_text text, comment_author varchar(255),comment_published_date datetime,FOREIGN KEY (video_id) REFERENCES Video(video_id))")
    conn.commit()

#Viewing tables in Streamlit
def show_table(table):    
    if(table == ':blue[Channels]'):
        show_channel_table()        
    elif(table == ':blue[Videos]'):
        show_video_table()
    elif(table == ':blue[Comments]'):
        show_comment_table()

def show_channel_table():
    cursor.execute('Select * from Channel')
    myResult = cursor.fetchall()
    df = pd.DataFrame(data = myResult, columns = cursor.column_names)
    st.table(df)

def show_video_table():
    cursor.execute('Select * from Video')
    myResult = cursor.fetchall()
    df = pd.DataFrame(data = myResult, columns = cursor.column_names)
    st.table(df)

def show_comment_table():
    cursor.execute('Select * from Comment')
    myResult = cursor.fetchall()
    df = pd.DataFrame(data = myResult, columns = cursor.column_names)
    st.table(df)

def insert_channel_details(channel_id):
    channel_details = get_channel_details(channel_id) 
    channel_details = (channel_details['channel_id'],channel_details['channel_name'],channel_details['sub_count'],channel_details['view_count'],channel_details['channel_description'],channel_details['channel_status'],)
    insert_query = '''INSERT INTO Channel 
                    VALUES(%s,%s,%s,%s,%s,%s)''' 
    cursor.execute(insert_query,channel_details)
    conn.commit()
    print(cursor.rowcount,'rows inserted successfully')

def insert_video_details(channel_id):
    try:
        video_ids = get_video_ids(channel_id)        
        video_details = get_video_details(video_ids)        
        for video_detail in video_details:
            video_detail = (video_detail['video_id'],video_detail['channel_id'],video_detail['video_name'],video_detail['video_description'],video_detail['published_date'],video_detail['view_count'],video_detail['like_count'],video_detail['favorite_count'],video_detail['comment_count'],video_detail['duration'],video_detail['thumbnail'],video_detail['caption_status'])
            insert_query = '''INSERT INTO Video 
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
            cursor.execute(insert_query,video_detail)
            conn.commit()
    except Exception as err:
        print(err)

def insert_comment_details(channel_id):
    try:        
        video_ids = get_video_ids(channel_id)
        comment_details = get_comment_details(video_ids)
        for comment_detail in comment_details:
            date_string = comment_detail['comment_published_date'] 
            date_string = changeDateFormat(date_string)
            comment_detail['comment_published_date'] = date_string
            comment_detail = (comment_detail['comment_id'],comment_detail['video_id'],comment_detail['comment_text'],comment_detail['comment_author'],comment_detail['comment_published_date'])
            insert_query = '''INSERT INTO Comment 
            VALUES(%s,%s,%s,%s,%s)''' 
            cursor.execute(insert_query,comment_detail)
            conn.commit()
    except Exception as err:
        print(err) 
        pass

# Inserting data to MYSQL
def insert_all_table(channel_id):
    insert_channel_details(channel_id) 
    insert_video_details(channel_id) 
    insert_comment_details(channel_id)

# Navigation
with st.sidebar:
    option = st.selectbox('Select an option:', ("Home","Add Data to Database","View Tables","SQL Query"))

st.markdown(
    """
    <style>
    body {
        background-color: grey;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.write(":Green[Welcome to Youtube Harvesting]")  
if option == 'Home':
    st.subheader(":black[Provide Channel ID]")
    channel_id = st.text_input('Channel ID]"',label_visibility = 'collapsed')
    
    if st.button (' :Maroon[View Channel Details]'):
        try:
            df = get_channel_details(channel_id)
            st.dataframe(df)
        except:
            st.warning('Enter a valid Channel ID')

    if st.button(':green[View Video Details]'):
        try:
            with st.spinner('Getting Details...'):
                video_ids = get_video_ids(channel_id)
                df = get_video_details(video_ids)
                st.dataframe(df)
        except: 
            st.warning('Enter a valid Channel ID')

#Add Data to Database Streamlit
elif option == 'Add Data to Database':
    st.subheader(":black[Provide Channel ID]")
    channel_id = st.text_input(' Enter Channel Id', label_visibility = 'collapsed')
    if st.button(':green[Collect and Store Channel data]'):        
        create_tables()
        ch_ids = []
        cursor.execute('Select channel_id from Channel')
        myResult = cursor.fetchall()   
        
        for i in myResult:
            ch_ids.append(i[0])
        if(channel_id in ch_ids):
            st.success('Channel Data already Available in SQL')
        elif(channel_id == ''):
            st.warning('Invalid Channel Id')
        else:
            with st.spinner('Loading....'):
                try:
                    insert_all_table(channel_id)
                    st.success('Data has been inserted')
                except:
                    
                    st.warning('Invalid Channel Id')

# View Tables in Streamlit
elif option == 'View Tables':
    st.subheader(":black[Select the table to be viewed from SQL Database :sunglasses:]")
    view_table = st.radio('Select the table to view from MySql',
                          [':blue[Channels]',':blue[Videos]',':blue[Comments]'],
                          label_visibility = 'collapsed',horizontal = True)
    show_table(view_table)

#SQL Query to be displayed in Streamlit
elif option == 'SQL Query':
    st.subheader(" :black[Please select a query to execute]")
    questions = st.selectbox(':blue[Queries]',
                            ['1. What are the names of all the videos and their corresponding channels?',
                            '2. Which channels have the most number of videos, and how many videos do they have?',
                            '3. What are the top 10 most viewed videos and their respective channels?',
                            '4. How many comments were made on each video, and what are their corresponding video names?',
                            '5. Which videos have the highest number of likes, and what are their corresponding channel names?',
                            '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?',
                            '7. What is the total number of views for each channel, and what are their corresponding channel names?',
                            '8. What are the names of all the channels that have published videos in the year 2022?',
                            '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?',
                            '10. Which videos have the highest number of comments, and what are their corresponding channel names?'])

    if questions == '1. What are the names of all the videos and their corresponding channels?':
        cursor.execute('''SELECT Video.video_name AS Video_Title,Channel.channel_name AS Channel_Name FROM Video
                            LEFT JOIN Channel
                            ON Video.channel_id = Channel.channel_id;
                            ''')
        df = pd.DataFrame(cursor.fetchall(), columns=cursor.column_names)
        st.write(df)

    elif questions == '2. Which channels have the most number of videos, and how many videos do they have?':
        cursor.execute("""SELECT Channel.channel_name Channel_Name,COUNT(Video.video_id) AS Video_Count FROM Video
                            RIGHT JOIN Channel
                            ON Video.channel_id = Channel.channel_id
                            GROUP BY channel.channel_id
                            ORDER BY video_count DESC;
                            """)
        df = pd.DataFrame(cursor.fetchall(), columns=cursor.column_names)
        st.write(df)

    elif questions == '3. What are the top 10 most viewed videos and their respective channels?':
        cursor.execute("""SELECT  Channel.channel_name Channel_Name, Video.view_count View_Count, Video.video_name Video_Name FROM Video
                            RIGHT JOIN Channel
                            ON Video.channel_id = Channel.channel_id
                            ORDER BY view_count DESC
                            LIMIT 10;
                            """)
        df = pd.DataFrame(cursor.fetchall(), columns=cursor.column_names)
        st.write(df)

    elif questions == '4. How many comments were made on each video, and what are their corresponding video names?':
        cursor.execute("""SELECT Video.video_id Video_Id, video.video_name Video_Name,COUNT(comment_id) AS Comment_Count FROM Comment
                            LEFT JOIN Video
                            ON Comment.video_id = Video.video_id
                            GROUP BY Video.video_id
                            ORDER BY comment_count DESC;
                            """)
        df = pd.DataFrame(cursor.fetchall(), columns=cursor.column_names)
        st.write(df)

    elif questions == '5. Which videos have the highest number of likes, and what are their corresponding channel names?':
        cursor.execute("""SELECT  Channel.channel_name Channel_Name, Video.like_count Likes, Video.video_name Video_Name FROM Video
                            RIGHT JOIN Channel
                            ON Video.channel_id = Channel.channel_id
                            ORDER BY like_count DESC;
                            """)
        df = pd.DataFrame(cursor.fetchall(), columns=cursor.column_names)
        st.write(df)
    
    elif questions == '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?':
        cursor.execute("""SELECT video_name Video_Name, like_count Likes FROM Video
                            ORDER BY like_count DESC;
                            """)
        df = pd.DataFrame(cursor.fetchall(), columns=cursor.column_names)
        st.write(df)

    elif questions == '7. What is the total number of views for each channel, and what are their corresponding channel names?':
        cursor.execute("""SELECT channel_name Channel_Name, channel_views AS View_Count
                            FROM Channel
                            ORDER BY view_count DESC;""")
        df = pd.DataFrame(cursor.fetchall(), columns=cursor.column_names)
        st.write(df)

    elif questions == '8. What are the names of all the channels that have published videos in the year 2022?':
        cursor.execute("""SELECT  Channel.channel_name Channel_Name,Video.video_name Video_Name ,Video.published_date Published_Date FROM Video 
                            LEFT JOIN Channel 
                            ON Video.channel_id = Channel.channel_id
                            WHERE Video.published_date LIKE '2022%';
                            """)
        df = pd.DataFrame(cursor.fetchall(), columns=cursor.column_names)
        st.write(df)
    
    elif questions == '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?':
        cursor.execute("""SELECT Channel.channel_name Channel_Name ,ROUND(AVG(Video.duration)/ 60,2) as 'Duration in Minutes' FROM Video
                            RIGHT JOIN Channel
                            ON Video.channel_id = Channel.channel_id
                            GROUP BY channel.channel_id
                            ORDER BY 'Duration in Minutes' DESC;
                            """)
        df = pd.DataFrame(cursor.fetchall(), columns=cursor.column_names)
        st.write(df)
    
    elif questions == '10. Which videos have the highest number of comments, and what are their corresponding channel names?':
        cursor.execute("""SELECT Channel.channel_name Channel_Name,video.video_name Video_Name, COUNT(comment_id) AS Comment_Count FROM Comment
                            Left JOIN Video ON Comment.video_id = Video.video_id
                            inner JOIN CHANNEL ON Video.channel_id = Channel.channel_id
                            GROUP BY Video.video_id
                            ORDER BY comment_count DESC
                            """)
        df = pd.DataFrame(cursor.fetchall(), columns=cursor.column_names)
        st.write(df)
