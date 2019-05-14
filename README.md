# githook
Githook is a small Python application designed to receive webhooks from GitLab and interpret them into Discord embeds (that look nicer than the default GitLab integrations.)

## How do I run it?
### Option A) Docker
:whale: Docker coming soon (maybe?)

### Option B) Public instance
I have a public instance running on `https://metrono.de/githook`. (don't depend on this, things may change someday!)

Specify your webhook at the end of this URL using the `?webhook=` parameter, add this entire URL to your GitLab integrations (**only push events are supported right now!**), and you're good to go. You'll know you've done it right if your URL matches something like `https://metrono.de/githook?webhook=https://discordapp.com/api/webhooks/1234567890123/iuhiuhiuygUYtbg8TBUYGgUYGUYGUYg876g87G87ghHUGUY8g87`, or you've tested it and you've received a webhook embed in the channel your webhook belongs to.

Further customisation *is* possible - see below for optional parameters.

### Option C) Self-hosted
As a prerequisite, you **must** have a public-facing server that can be accessed on either port(s) 80, 443 (standard HTTP(S) ports) or the port you set in your [config.py](https://github.com/doddsy/githook/blob/master/configexample.py). This application can be reverse proxy'd through your server application of choice. I recommend Caddy, however I'm sure this works with nginx and Apache too, although I can't help with setting up either of those.

Clone the repo and rename/move `configeexample.py` to `config.py`. Feel free to hide branches by setting SHOW_BRANCHES to 'FALSE', or feel free to change the port here. If you have nothing running on port 5000 and you don't mind branches being shown in commit embeds, feel free to leave these as their default values.

After that, run `pip install Flask requests`, wait for these packages to install, and then `python app.py`. Do note that you may have to run a different set of commands depending on your setup. This project also only supports Python 3, so you may need to `python3 app.py` instead.

To set it up in GitLab, follow the content of Option B, making sure to replace my URL with whatever your URL is, wherever necessary.

## Other features
- Add `githook:ignore` to a commit message, and it will be hidden in the list of commits and not counted towards commits in that push event.
- Add `githook:private` to a commit message, and the message will be replaced with "**This commit has been marked as private.**" in the webhook message.

### Optional Parameters
After the initial `?webhook=<your webhook URL>`, other parameters are supported but not required if default functionality is fine. These are listed here.

- `&hideAuthor` - Hides author from commit messages
- `&hideBranch` - Hides the commit branch from embed title
- `&color=` or `&colour=` - Yes, you can use either spelling! Specify a color in hexadecimal and the embed "pill" will have this colour. If it's incorrect, the colour defaults to `#da143c`.
    - Acceptable values for this are `fff`, `123`, `ff4500`, `000000` and any other hexadecimal color code you can think of. Just don't include a `#`.

