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

def start_app(port='5000'):
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    # Check if a system argument of port was provided
    if '--port' in sys.argv:
        try:
            # Try and run with port argument
            start_app(sys.argv[2])
        except: 
            # Run on default port
            start_app()
    elif 'PORT' in os.environ:
        try:
            # Try and run with ENV port
            start_app(os.environ['PORT'])
        except:
            # Run on default port
            start_app()
    else: 
        # Run on default port
        start_app()
