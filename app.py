from flask import Flask, request, Response
import json
import requests
from datetime import datetime
import sys


def configerror(type, key=None, extra=None):
    if type == "missing":
        print(f'You are missing the {key} key from your config.py. Please recreate the file.')
    if type == "default":
        print(f'You are using the default {key} value in your config.py. Please change this before running the program.')
    if type == "undefined":
        print(extra)


def checkwebhook(url):
    if url.startswith("https://discordapp.com/api/webhooks/"):
        r = requests.get(url).text
        if all(keys in r for keys in ("name", "guild_id", "token")):
            return True


app = Flask(__name__)


@app.route('/', methods=['POST'])
def main():
    if ((not request.headers.get('X-Gitlab-Event')) or
        (not request.headers.get('X-Gitlab-Token')) or
        (request.headers.get('X-Gitlab-Token') != config.GITLAB_TOKEN)):
        return Response(status=401)
    content = request.get_json()
    commits = []
    numOfCommits = 0
    repo = content["repository"]["name"]
    for commit in content["commits"]:
        numOfCommits += 1

        commits.append(
            f"`{commit['id'][:7]}` - {commit['message'] if len(commit['message']) <= 50 else commit['message'][:47] + '...'}"
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
    try:
        import config
    except ImportError:
        print("You have not setup your config correctly. Please rename configexample.py to config.py and fill out the values in the file.")
        sys.exit(1)

    try:
        config.GITLAB_TOKEN
    except AttributeError:
        configerror("missing", "GITLAB_TOKEN")
        sys.exit(1)
    else:
        if config.GITLAB_TOKEN == '':
            configerror("missing", "GITLAB_TOKEN")
            sys.exit(1)
        elif config.GITLAB_TOKEN == "DefaultValuePleaseChangeMe":
            configerror("default", "GITLAB_TOKEN")
            sys.exit(1)

    try:
        config.WEBHOOK_URL
    except AttributeError:
        configerror("missing", "WEBHOOK_URL")
        sys.exit(1)
    else:
        if config.WEBHOOK_URL == "":
            configerror("default", "WEBHOOK_URL")
            sys.exit(1)
        elif checkwebhook(config.WEBHOOK_URL) is not True:
            configerror("undefined", extra="Your webhook URL is invalid. Please check it is valid before running the program again.")
            sys.exit(1)

    try:
        config.PORT
    except AttributeError:
        configerror("undefined", extra="You are missing a 'PORT' key in your config. Defaulting to port 5000.")
        config.PORT = 5000
    else:
        if config.PORT == "":
            configerror("undefined", extra="You are missing a 'PORT' value in your config. Defaulting to port 5000.")
            config.PORT = 5000

    app.run(host='0.0.0.0', port=config.PORT)
