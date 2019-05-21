from datetime import datetime

EVENT = 'Issue Hook'


def run(request, color, *args):
    content = request.get_json()

    repo = content["project"]["name"]
    isPrivate = content["project"]["visibility_level"]
    issueEditor = content["user"]["username"]
    issueEditorAvatar = content["user"]["avatar_url"]
    issueID = content["object_attributes"]["iid"]
    issueTitle = '*' + content["object_attributes"]["title"] + '*'
    if "githook:ignore" in content["object_attributes"]["description"]:
        return "empty"
    elif "githook:private" in content["object_attributes"]["description"]:
        issueTitle = ''
        issueDescription = "This issue has been marked as private, and as such the issue description will not be shown."
    else:
        issueDescription = (
            content["object_attributes"]["description"]
            if len(content["object_attributes"]["description"]) <= 255
            else content["object_attributes"]["description"][:252] + '...'
        )
    state = content["object_attributes"]["state"]
    issueURL = content["object_attributes"]["url"] if isPrivate != 0 else None

    wasEdited = content["object_attributes"]["last_edited_at"]

    # Issue opened or edited
    if state == "opened":

        # Issue reopened. Doesn't have to be too fancy
        if content["object_attributes"]["action"] == "reopen":
            if color != 14423100:
                color = color
            else:
                color = 3272007
            data = {
                "embeds": [
                    {
                        "author": {"name": issueEditor, "icon_url": issueEditorAvatar},
                        "title": f"Issue {issueID} of {repo} was reopened.",
                        "url": issueURL,
                        "color": color,
                        "timestamp": datetime.now().isoformat(),
                    }
                ]
            }
            return data
        # Issue opened
        if wasEdited == None:
            # Overwriting the default color to "green"
            if color != 14423100:
                color = color
            else:
                color = 3272007
            data = {
                "embeds": [
                    {
                        "author": {"name": issueEditor, "icon_url": issueEditorAvatar},
                        "description": issueDescription,
                        "title": f"New issue ({issueID}) on {repo}: {issueTitle}",
                        "url": issueURL,
                        "color": color,
                        "timestamp": datetime.now().isoformat(),
                    }
                ]
            }
            return data
        # Issue edited
        else:
            edits = []
            if "title" in content["changes"]:
                edits.append('title')
            if "description" in content["changes"]:
                edits.append('description')
            # Don't show edits that don't change the content of the issue, i.e hide "assigned" or "labelled" actions
            if edits == []:
                return "empty"
            if color != 14423100:
                color = color
            else:
                color = 15133997
            data = {
                "embeds": [
                    {
                        "author": {"name": issueEditor, "icon_url": issueEditorAvatar},
                        "description": issueDescription,
                        "title": f"{' and '.join(edits).capitalize()} was edited on issue {issueID} of {repo}: {issueTitle}",
                        "url": issueURL,
                        "color": color,
                        "timestamp": datetime.now().isoformat(),
                    }
                ]
            }
            return data
    # Issue closed
    else:
        if color != 14423100:
            color = color
        else:
            color = 14030101
        data = {
            "embeds": [
                {
                    "author": {"name": issueEditor, "icon_url": issueEditorAvatar},
                    "title": f"Issue {issueID} of {repo} was closed.",
                    "url": issueURL,
                    "color": color,
                    "timestamp": datetime.now().isoformat(),
                }
            ]
        }
        return data
