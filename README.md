Youtube-Harvesting-
YouTube harvesting is the process of collecting data from YouTube using the YouTube Data API. This data can include video details, channel information, comments, and more. The harvested data can be used for analysis, reporting or any other purposes. I used it as to collect the data's and display it in streamlit.

Topic: Youtube Data Harvesting and Warehousing Using MySql and Streamlit in Python

requirements: mysql.connector, stremlit, pandas, google-api_client, parser from dateutil, Datetime

step 1: gets api_key in developer console and Collect the youtube channel_details using channel_id, video_ids using playlist_id, video_details using video_ids, using video_ids to get comment_details and using channel_id to get playlist_details.

step 2: connecting Mysql into python using mysql.connector create table for channel,video,comment,playlist & insert all data's.

step 3: write query for 10 question and display it on streamlit.
