from flask import Flask, request, Response

# Using json rather than Flask's jsonify because I couldn't figure it out and it made me wish to un-alive
import json
import requests
from datetime import datetime
import sys

# Just wanted to try something new tbh
def configerror(type, key=None, extra=None):
    if type == "missing":
        print(
            f'You are missing the {key} key from your config.py. Please recreate the file.'
        )
    if type == "default":
        print(
            f'You are using the default {key} value in your config.py. Please change this before running the program.'
        )
    if type == "undefined":
        print(extra)


def checkwebhook(url):
    r = requests.get(url).text
    # Check if webhook is even active
    if all(keys in r for keys in ("name", "guild_id", "token")):
        return True


app = Flask(__name__)


@app.route('/', methods=['POST'])
def main():
    # If incoming request doesn't contain a '?webhook=' parameter
    if 'webhook' in request.args:
        webhook_url = request.args.get('webhook')
        if checkwebhook(webhook_url) is not True:
            return Response(status=400)
    else:
        return Response(status=400)
    # optional parameters
    # hideAuthor
    if 'hideAuthor' in request.args:
        authorHidden = True
    else:
        authorHidden = False
    # hideBranch
    if 'hideBranch' in request.args:
        branchHidden = True
    else:
        branchHidden = False
    # color
    # set default fallback color
    color = 14423100
    for args in request.args:
        if any(spelling in args for spelling in ('color', 'colour')):
            color = request.args.get(args)
            if (len(color) == 3) or (len(color) == 6):
                if len(color) == 3:
                    color = ''.join([letter * 2 for letter in color])
                try:
                    color = int(color, 16)
                except:
                    color = 14423100
            else:
                color = 14423100
    # If incoming request headers don't match Gitlab's headers
    if not request.headers.get('X-Gitlab-Event'):
        # 401 unauthorised
        return Response(status=401)
    # Get incoming json data (GL will only POST JSON)
    content = request.get_json()
    commits = []
    numOfCommits = 0
    repo = content["repository"]["name"]
    isPrivate = content["repository"]["visibility_level"]
    branch = (":" + content["ref"].split("/")[2]) if branchHidden == False else ""
    commitUser = content['user_username']

    for commit in content["commits"]:
        if "githook:ignore" in commit['message']:
            continue
        if "githook:private" in commit['message']:
            commitMessage = "**This commit has been marked as private.**"
        else:
            commitMessage = (
                commit['message']
                if len(commit['message']) <= 50
                else commit['message'][:47] + '...'
            )
        commitMessage = commitMessage.split('\n')[0]
        if authorHidden == False:
            commitMessage += " - **" + commitUser + "**"
        commitUrl = commit['url']
        numOfCommits += 1

        if isPrivate != 0:
            commits.append(f"[`{commit['id'][:7]}`]({commitUrl}) - {commitMessage}")
        else:
            commits.append(f"`{commit['id'][:7]}` - {commitMessage}")
    if numOfCommits > 0:
        data = {
            "embeds": [
                {
                    "description": '\n'.join(map(str, commits)),
                    "title": f"{numOfCommits} new commits on {repo}{branch}",
                    "color": color,
                    "timestamp": datetime.now().isoformat(),
                }
            ]
        }

        r = requests.post(
            webhook_url,
            data=json.dumps(data),
            headers={'Content-Type': 'application/json'},
        )
    return json.dumps(commits)


if __name__ == '__main__':
    # So. Many. Checks.

    # Check that the user isn't being stupid and has copied over the config sample
    try:
        import config
    except ImportError:
        print(
            "You have not setup your config correctly. Please rename configexample.py to config.py and fill out the values in the file."
        )
        sys.exit(1)
    try:
        config.PORT
    # Check if the user (somehow) forgot to add a PORT key to the config.
    # We'll still let them run if this is missing, it's not like it's gonna ruin everything. Unlike Karen. Please I just want my kids back
    except AttributeError:
        configerror(
            "undefined",
            extra="You are missing a 'PORT' key in your config. Defaulting to port 5000.",
        )
        config.PORT = 5000
    else:
        # Same as above. We'll just set the default port ourselves cause we're a strong, independent application who don't need no user input
        # to find the port. *sassy fingersnap*
        if config.PORT == "":
            configerror(
                "undefined",
                extra="You are missing a 'PORT' value in your config. Defaulting to port 5000.",
            )
            config.PORT = 5000
    app.run(host='0.0.0.0', port=config.PORT)
