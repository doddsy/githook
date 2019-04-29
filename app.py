from flask import Flask, request, Response
# Using json rather than Flask's jsonify because I couldn't figure it out and it made me wish to un-alive
import json
import requests
from datetime import datetime
import sys


# Just wanted to try something new tbh
def configerror(type, key=None, extra=None):
    if type == "missing":
        print(f'You are missing the {key} key from your config.py. Please recreate the file.')
    if type == "default":
        print(f'You are using the default {key} value in your config.py. Please change this before running the program.')
    if type == "undefined":
        print(extra)


def checkwebhook(url):
    # Check if URL is a Discord URL
    if url.startswith("https://discordapp.com/api/webhooks/"):
        r = requests.get(url).text
        # Check if webhook is even active
        if all(keys in r for keys in ("name", "guild_id", "token")):
            return True


app = Flask(__name__)


@app.route('/', methods=['POST'])
def main():
    # If incoming request headers don't match Gitlab's headers or the token is not matching
    if ((not request.headers.get('X-Gitlab-Event')) or
            (not request.headers.get('X-Gitlab-Token')) or
            (request.headers.get('X-Gitlab-Token') != config.GITLAB_TOKEN)):
        # 401 unauthorised
        return Response(status=401)

    # Get incoming json data (GL will only POST JSON)
    content = request.get_json()
    commits = []
    numOfCommits = 0
    repo = content["repository"]["name"]
    for commit in content["commits"]:
        commitMessage = (commit['message'] if len(commit['message']) <= 50 else commit['message'][:47] + '...')
        commitMessage = commitMessage.split('\n')[0]
        numOfCommits += 1

        commits.append(
            f"`{commit['id'][:7]}` - {commitMessage}"
        )

    data = {"embeds": [{"description": '\n'.join(map(str, commits)),
                        "title": f"{numOfCommits} new commits on {repo}",
                        "color": 14423100,
                        "timestamp": datetime.now().isoformat()}]}

    r = requests.post(config.WEBHOOK_URL,
                      data=json.dumps(data),
                      headers={'Content-Type': 'application/json'})
    return (json.dumps(commits))


if __name__ == '__main__':
    # So. Many. Checks.

    # Check that the user isn't being stupid and has copied over the config sample
    try:
        import config
    except ImportError:
        print("You have not setup your config correctly. Please rename configexample.py to config.py and fill out the values in the file.")
        sys.exit(1)

    try:
        config.GITLAB_TOKEN
    # Check if the user (somehow) forgot to add a GITLAB_TOKEN key to the config
    except AttributeError:
        configerror("missing", "GITLAB_TOKEN")
        sys.exit(1)
    else:
        # No token is bad
        if config.GITLAB_TOKEN == '':
            configerror("missing", "GITLAB_TOKEN")
            sys.exit(1)
        # The equivalent of your password being password
        elif config.GITLAB_TOKEN == "DefaultValuePleaseChangeMe":
            configerror("default", "GITLAB_TOKEN")
            sys.exit(1)

    try:
        config.WEBHOOK_URL
    # Check if the user (somehow) forgot to add a WEBHOOK_URL key to the config
    except AttributeError:
        configerror("missing", "WEBHOOK_URL")
        sys.exit(1)
    else:
        # where tf it gon' send to buddy?
        if config.WEBHOOK_URL == "":
            configerror("default", "WEBHOOK_URL")
            sys.exit(1)
        # scroll up to see this magical function in all it's glory
        elif checkwebhook(config.WEBHOOK_URL) is not True:
            configerror("undefined", extra="Your webhook URL is invalid. Please check it is valid before running the program again.")
            sys.exit(1)

    try:
        config.PORT
    # Check if the user (somehow) forgot to add a PORT key to the config.
    # We'll still let them run if this is missing, it's not like it's gonna ruin everything. Unlike Karen. Please I just want my kids back
    except AttributeError:
        configerror("undefined", extra="You are missing a 'PORT' key in your config. Defaulting to port 5000.")
        config.PORT = 5000
    else:
        # Same as above. We'll just set the default port ourselves cause we're a strong, independent application who don't need no user input
        # to find the port. *sassy fingersnap*
        if config.PORT == "":
            configerror("undefined", extra="You are missing a 'PORT' value in your config. Defaulting to port 5000.")
            config.PORT = 5000

    app.run(host='0.0.0.0', port=config.PORT)
