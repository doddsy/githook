from datetime import datetime

EVENT = 'Push Hook'

def run(request,
        color,
        authorHidden,
        branchHidden):
    content = request.get_json()
    commits = []
    numOfCommits = 0
    repo = content["repository"]["name"]
    isPrivate = content["repository"]["visibility_level"]
    branch = (":" + content["ref"].split("/")[2]) if branchHidden == False else ""
    commitUser = content['user_username']

    for commit in content["commits"]:
        if any(x in commit['message'] for x in ("githook:ignore", "gh:i")):
            continue
        if any(x in commit['message'] for x in ("githook:private", "gh:p")):
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

        return data