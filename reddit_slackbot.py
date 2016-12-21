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

BLOCKED_IDS = [] # any user ID in here will get no response from bot


def get_reddit_stuff(subreddit, options):
    title = ""
    image = ""
    subreddit = reddit.subreddit(subreddit)
    print(subreddit)

    if subreddit is None:
        return "No subreddit provided", ""

    sub = None

    if options is None or options[0] == "h":
        sub = subreddit.hot()
    elif options[0] == "d":
        sub = subreddit.top('day')
    elif options[0] == "w":
        sub = subreddit.top('week')
    elif options[0] == "m":
        sub = subreddit.top('month')
    elif options[0] == "y":
        sub = subreddit.top('year')
    elif options[0] == "a":
        sub = subreddit.top('all')

    count = 1
    str_count = ''
    if options is not None and len(options) > 1:
        for item in options[1:]:
            str_count += item
        count = int(str_count)
        if count < 1:
            count = 1
    print(count)

    cur = 0

    try:
        for submission in sub:
            if submission.stickied:
                continue
            cur += 1
            if cur != count:
                continue
            title += submission.title
            image += submission.url
            break
    except Exception:
        return "Invalid/unsupported subreddit", ""
    return title, image


def handle_command(command, channel, options):
    title, image = get_reddit_stuff(command, options)
    response = title + "\n" + image
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                if output['user'] in BLOCKED_IDS:
                    return None, None, None

                first = output['text'].split(AT_BOT)[1].strip().lower()

                if ':' in first and len(first) > 1:
                    text = first.split(': ', 1)[1]
                else:
                    text = first
                optional = text.split(' ')

                options = None
                if len(optional) > 1:
                    options = optional[1]

                if text is None or text == ' ' or text == ':':
                    return None, None, None

                emojis = slack_client.api_call("emoji.list")

                texts = re.match('[a-zA-Z0-9_]*', text).group()
                return texts, output['channel'], options
    return None, None, None


if __name__ == '__main__':
    READ_WEBSOCKET_DELAY = 1
    if slack_client.rtm_connect():
        while True:
            command, channel, options = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel, options)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID.")


# BELOW IS AN EXAMPLE API CALL SINCE I KEEP FORGETTING
# users = slack_client.api_call("users.list")
