from __future__ import print_function
from slackclient import SlackClient
import praw
import random
import time
import re
import credentials
import datetime

slack_client = SlackClient(credentials.SLACK_BOT_TOKEN)

reddit = praw.Reddit(user_agent = credentials.r_user_agent, client_id = credentials.r_client_id, client_secret = credentials.r_client_secret)

AT_BOT = "<@" + credentials.BOT_ID + ">"

LOL_IDS = []
BLACKLISTED_IDS = [] # any user ID in here will get no response from bot
WHITELISTED_IDS = ['U0XS9BU3V'] # any user ID in here will be able to request as many times as they want per day

RANDOM_CHANNEL = credentials.random_channel
REDDIT_CHANNEL = credentials.reddit_channel

RANDOM_CAP = 1
REDDIT_CAP = 50

def get_reddit_stuff(subreddit, options):
    title = ""
    image = ""
    subreddit = reddit.subreddit(subreddit)

    if subreddit is None:
        return "No subreddit provided", ""

    sub = subreddit.hot()

    # determine which "links from" option to get
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

    # determine which post number to get
    if options is not None and len(options) > 1:
        for item in options[1:]:
            str_count += item
        try:
            count = int(str_count)
        except Exception:
            count = 1
        if count < 1 or count > 100:
            count = 1

    cur = 0

    # ensure that invalid subreddits are handled
    try:
        # loop over posts until the post number that is requested has been found
        for submission in sub:
            # ignore stickied posts
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
    response = ""

    # if options is exceeded, the user is told that they have exceeded their requests
    if options == 'exceed':
        response = "User " + command + " has exceeded their " 
        if channel == RANDOM_CHANNEL:
            response += "1 request for the day."
        else:
            response += "10 requests for the day."

    else:
        title, image = get_reddit_stuff(command, options)
        response = title + "\n" + image
        if title == "Invalid/unsupported subreddit":
            if channel == RANDOM_CHANNEL:
                users.get(curr_id)[1] -= 1
            elif channel == REDDIT_CHANNEL:
                users.get(curr_id)[2] -= 1
    # post the reponse message into the requested channel with the appropriate response
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    global curr_id

    output_list = slack_rtm_output

    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                curr_id = output['user']
                if curr_id in BLACKLISTED_IDS:
                    print(users.get(curr_id)[0] + " is a blocked user")
                    return None, None, None

                # if user is whitelisted, do not increment their request count
                if curr_id in WHITELISTED_IDS:
                    print(users.get(curr_id)[0] + " is a whitelisted user")

                # check if user has surpassed their alloted amount of requests per channel
                else:
                    if output['channel'] == RANDOM_CHANNEL:
                        # if user has called the bot 10 times, give the appropriate response
                        if users.get(curr_id)[1] == RANDOM_CAP: 
                            users.get(curr_id)[1] += 1
                            print(users.get(curr_id)[0] + " has exceeded their random requests for the day")
                            return users.get(curr_id)[0], output['channel'], 'exceed'
                    # if user has called the bot more than 10 times, give nothing
                        elif users.get(curr_id)[1] > RANDOM_CAP:
                            return None, None, None
                        else:
                            users.get(curr_id)[1] += 1
                            times = " times" if users.get(curr_id)[1] > 1 else " time"
                            print(users.get(curr_id)[0] + " has called the bot " + str(users.get(curr_id)[1]) + times + " today from #random")

                    if output['channel'] == REDDIT_CHANNEL:
                        # if user has called the bot 10 times, give the appropriate response
                        if users.get(curr_id)[2] == REDDIT_CAP:
                            users.get(curr_id)[2] += 1
                            print(users.get(curr_id)[0] + " has exceeded their reddit requests for the day")
                            return users.get(curr_id)[0], output['channel'], 'exceed'
                        # if user has called the bot more than 10 times, give nothing
                        elif users.get(curr_id)[2] > REDDIT_CAP:
                            return None, None, None
                        else:
                            users.get(curr_id)[2] += 1
                            times = " times" if users.get(curr_id)[2] > 1 else " time"
                            print(users.get(curr_id)[0] + " has called the bot " + str(users.get(curr_id)[2]) + times + " today from #reddit")

                # get text right after the bot is called
                first = output['text'].split(AT_BOT)[1].strip().lower()

                # string parsing so that just the subreddit is retrieved from the user request
                if ':' in first and len(first) > 1:
                    text = first.split(': ', 1)[1]
                else:
                    text = first

                optional = text.split(' ')
                options = None

                # check if user gives any options after subreddit
                if len(optional) > 1:
                    options = optional[1]

                if text is None or text == ' ' or text.lower() == 'watchpeopledie':
                    return None, None, None

                # ensure that subreddit is valid and only contains a-z, A-Z, 0-9, _
                texts = re.match('[a-zA-Z0-9_]*', text).group()

                # any user in LOL_IDS always requests the subreddit below
                if curr_id in LOL_IDS:
                    texts = 'history'

                return texts, output['channel'], options
    return None, None, None


def reset_count():
    print("COUNT RESET: " + str(datetime.datetime.now()))
    
    # reset each user's count to 0
    for curr_id in users:
        users.get(curr_id)[1] = 0
        users.get(curr_id)[2] = 0


if __name__ == '__main__':
    global users

    READ_WEBSOCKET_DELAY = 1

    today = datetime.date.today()
    tomorrow = datetime.date.today() + datetime.timedelta(days = 1)

    users = {}
    all_users = slack_client.api_call("users.list").get('members')
    # for user in all_users:
        # print(user)
    for channel in slack_client.api_call('channels.list').get('channels'):
        print(channel)

    # fill users dictionary with all users names and an initial count of 0
    for user in all_users:
        users[user.get('id')] = [user.get('name'), 0, 0] # first 0 is in #random second 0 is in #reddit

    count = 0

    if slack_client.rtm_connect():
        while True:
            count += READ_WEBSOCKET_DELAY

            command, channel, options = parse_slack_output(slack_client.rtm_read())
            print(command, channel, options)
            if command and channel:
                handle_command(command, channel, options)
            time.sleep(READ_WEBSOCKET_DELAY)

            # reset count of how many times each user has called bot that day
            if today == tomorrow:
                reset_count()
                today = datetime.date.today()
                tomorrow = datetime.date.today() + datetime.timedelta(days = 1)

            # if it has been a minute
            if count == 60:
                today = datetime.date.today()
                count = 0
    else:
        print("Connection failed. Invalid Slack token or bot ID.")

