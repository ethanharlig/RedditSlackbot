# RedditSlackbot

This program is a bot for Slack. When the program is running, any user in your slack channel may say "@memebot meirl" with meirl being any given subreddit on Reddit.

You will need to provide a "credentials.py" file that contains (REDDIT): "r_user_agent=xxx", "r_client_id=yyy", "r_client_secret=zzz", (SLACK): "BOT_ID=xyz", "SLACK_BOT_TOKEN=yzx"

The bot allows users to make requests 10 times per day and resets that count at midnight. If a user exceeds their allowed requests, they are given a message telling them so. 

Users can be blocked (not allowed to make requests) and whitelisted (allowed to make as many requests as they want per day) by putting their user IDs into the arrays at the top of the main file.
