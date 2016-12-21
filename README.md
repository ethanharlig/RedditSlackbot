# RedditSlackbot

This program is a bot for Slack. When the program is running, any user in your slack channel may say "@memebot meirl" with meirl being any given subreddit on Reddit.

You will need to provide a "credentials.py" file that contains (REDDIT): "r_user_agent=xxx", "r_client_id=yyy", "r_client_secret=zzz", (SLACK): "BOT_ID=xyz", "SLACK_BOT_TOKEN=yzx"

The bot only supports valid subreddits and will give a message stating that the subreddit is invalid or unsupported if it is not valid.
