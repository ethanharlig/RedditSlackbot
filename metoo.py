from __future__ import print_function
from slackclient import SlackClient
import credentials


BOT_NAME = 'redditbot'

slack_client = SlackClient(credentials.SLACK_BOT_TOKEN)
api_call = "emoji.list"


if __name__ == "__main__":
    api_call = slack_client.api_call(api_call)
    if api_call.get('ok'):
        print(api_call)
    else:
        print("could not find bot user with the name " + BOT_NAME)
