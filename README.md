# githook
Githook is a small Python application designed to receive webhooks from GitLab and interpret them into Discord embeds (that look nicer than the default GitLab integrations.)

## How do I run it?
### Option A) :whale: Docker
Clone the repo then `docker build -t githook .`.    
Once that's done, run it like `docker run -d -p <your preferred port here>:5000 --name githook githook`.

### Option B) Public instance
I have a public instance running on `https://metrono.de/githook`. (don't depend on this, things may change someday!)

Specify your webhook at the end of this URL using the `?webhook=` parameter, add this entire URL to your GitLab integrations, and you're good to go. You'll know you've done it right if your URL matches something like `https://metrono.de/githook?webhook=https://discordapp.com/api/webhooks/1234567890123/iuhiuhiuygUYtbg8TBUYGgUYGUYGUYg876g87G87ghHUGUY8g87`, or you've tested it and you've received a webhook embed in the channel your webhook belongs to.

Further customisation *is* possible - see below for optional parameters.

### Option C) Self-hosted
As a prerequisite, you **must** have a public-facing server that can be accessed on either port(s) 80, 443 (standard HTTP(S) ports) or the port you set in either your [config.py](https://github.com/doddsy/githook/blob/master/configexample.py), your `PORT` environment variable, or using the `--port` flag when running the program. This application can be reverse proxy'd through your server application of choice. I recommend Caddy, however I'm sure this works with nginx and Apache too, although I can't help with setting up either of those.

Clone the repo, then run `pip install Flask requests`, wait for these packages to install, and then `python app.py`. Specify a port using `--port` - i.e `--port 5050`. Do note that you may have to run a different set of commands depending on your setup. This project also only supports Python 3.6, so you may need to `python3 app.py` instead.

To set it up in GitLab, follow the content of Option B, making sure to replace my URL with whatever your URL is, wherever necessary.

## Other features
- Automatic repository URL'ing based on private/public state
    - When an embed is sent, a hyperlink will be added to the message depending on whether or not a repo is public or private, which can allow for easy opening of that event in GitLab.
- `githook:ignore` or `gh:i`
    - Add this to an issue description, and the issue won't be sent to Discord. Add it to a commit message, and it won't be included in the list of commits.
- `githook:private` or `gh:p`
    - Add this to an issue description or a commit message and the content of the issue or the commit message won't be shown in the embed. It will be replaced with a different message explaining that that particular commit/issue has been marked as private.

### Optional Parameters
After the initial `?webhook=<your webhook URL>`, other parameters are supported but not required if default functionality is fine. These are listed here.

- `&hideAuthor` - Hides author from commit messages
- `&hideBranch` - Hides the commit branch from embed title
- `&color=` or `&colour=` - Yes, you can use either spelling! Specify a color in hexadecimal and the embed "pill" will have this colour. If it's incorrect, the colour defaults to `#da143c`.
    - Acceptable values for this are `fff`, `123`, `ff4500`, `000000` and any other hexadecimal color code you can think of. Just don't include a `#`.

