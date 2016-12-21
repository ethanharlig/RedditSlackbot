from __future__ import print_function
from slackclient import SlackClient
from twilio.rest import TwilioRestClient
import praw
import random
import time
import re
import credentials

slack_client = SlackClient(credentials.SLACK_BOT_TOKEN)

reddit = praw.Reddit(user_agent = credentials.r_user_agent, client_id = credentials.r_client_id, client_secret = credentials.r_client_secret)

AT_BOT = "<@" + credentials.BOT_ID + ">"

def get_reddit_stuff(subreddit):
    title = ""
    image = ""
    subreddit = reddit.subreddit(subreddit)
    if (subreddit == None):
        return "No subreddit provided", ""
    try:
        for submission in subreddit.hot():
            if submission.stickied:
                continue
            title += submission.title
            image += submission.url
            break
    except Exception:
        return "Invalid/unsupported subreddit", ""
    return title, image

def handle_command(command, channel):
    title, image = get_reddit_stuff(command)
    response = title + "\n" + image
    slack_client.api_call("chat.postMessage", 
            channel=channel, text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                first = output['text'].split(AT_BOT)[1].strip().lower()
                if ':' in first and len(first) > 1:
                    text = first.split(': ', 1)[1]
                else:
                    text = first
                if text==' ' or text==None:
                    return None, None
                texts = re.match('[a-zA-Z0-9_]*', text).group()
                print(texts)
                return texts, output['channel']
    return None, None

if __name__ == '__main__':
    READ_WEBSOCKET_DELAY = 1
    if slack_client.rtm_connect():
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID.")
