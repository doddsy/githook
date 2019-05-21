from flask import Flask, request, Response

import requests
from dispatch import dispatch
import sys
import importlib as imp
import os


def checkwebhook(url):
    r = requests.get(url).text
    # Check if webhook is even active
    if all(keys in r for keys in ("name", "guild_id", "token")):
        return True


file_names = os.listdir(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plugins', '')
)
module_names = [
    f"plugins.{file_name[:-3]}"
    for file_name in file_names
    if os.path.isfile(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'plugins', '', file_name
        )
    )
]
modules = [imp.import_module(module_name) for module_name in module_names]
list_of_plugins = [module for module in modules if hasattr(module, 'EVENT')]

plugins = {}
for plugin in list_of_plugins:
    plugins[plugin.EVENT] = plugin

app = Flask(__name__)


@app.route('/', methods=['POST'])
def main():
    # If incoming request doesn't contain a '?webhook=' parameter
    if 'webhook' in request.args:
        webhook_url = request.args.get('webhook')
        if checkwebhook(webhook_url) is not True:
            return Response(
                status=400,
                response="Your webhook URL is incorrect. Are you sure you entered it correctly?",
            )
    else:
        return Response(status=400, response="You're missing a webhook URL!")
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
    try:
        plugin = plugins[request.headers.get('X-Gitlab-Event')]
        data = plugin.run(request, color, authorHidden, branchHidden)
        if data == "empty":
            return Response(status=204)
        else:
            status = dispatch(data, webhook_url)
            return Response(status=status)
    except KeyError:
        return Response(
            status=405, response="That event isn't supported by Githook (yet)."
        )
    except Exception:
        return Response(status=401)


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
        print("You are missing a 'PORT' key in your config. Defaulting to port 5000.")
        config.PORT = 5000
    else:
        # Same as above. We'll just set the default port ourselves cause we're a strong, independent application who don't need no user input
        # to find the port. *sassy fingersnap*
        if config.PORT == "":
            print(
                "You are missing a 'PORT' value in your config. Defaulting to port 5000."
            )
            config.PORT = 5000
    app.run(host='0.0.0.0', port=config.PORT)
