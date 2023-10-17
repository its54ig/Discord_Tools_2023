from flask import Flask, render_template, request
from markupsafe import Markup
from datetime import datetime
import time
import requests

app = Flask(__name__)

token = "MTA5ODExNzA5NTM1NjY0MTMwMQ.GLTKEL.rmw__2HSj5kD_gsAA_bVWwUX14Cw7zfm5RSuyY"


@app.route("/")
def redirect():
    return render_template("redirect.html")


@app.route("/home")
def home():
    guilds = requests.get(
        url="https://discord.com/api/v9/users/@me/guilds",
        headers={
            "Authorization": token
        }
    ).json()

    html_data = ""

    for i in guilds:
        html_data += f"<button onclick=\"window.location.replace(\'/guild?id={i['id']}\')\" class=\"guild-button\"><img src=\"https://cdn.discordapp.com/icons/{i['id']}/{i['icon']}?size=512\" width=\"256\" height=\"256\"><h3>{i['name']}</h3></button>"

    return render_template("homepage.html", data=Markup(html_data))


@app.route("/guild")
def guild():
    guild = requests.get(
        url=f"https://discord.com/api/v9/guilds/{request.args['id']}",
        headers={
            "Authorization": token
        }
    ).json()
    
    owner = requests.get(
        url=f"https://discord.com/api/v9/users/{guild['owner_id']}",
        headers={
            "Authorization": token
        }
    ).json()

    data = {
        "name": guild["name"],
        "server_icon": f"https://cdn.discordapp.com/icons/{guild['id']}/{guild['icon']}?size=1024",
        "owner_avatar": f"https://cdn.discordapp.com/avatars/{owner['id']}/{owner['avatar']}?size1024",
        "guild": guild,
        "owner": owner,
    }

    return render_template("guild.html", plain_text=data)


@app.route("/channels")
def channels():
    channels = requests.get(
        url=f"https://discord.com/api/v9/guilds/{request.args['id']}/channels",
        headers={
            "Authorization": token
        }
    ).json()

    guild = requests.get(
        url=f"https://discord.com/api/v9/guilds/{request.args['id']}",
        headers={
            "Authorization": token
        }
    ).json()

    channel_list = ""

    for i in channels:
        if i['type'] == 4:
            channel_list += f"<h2>{i['name']}<button onclick=\"navigator.clipboard.writeText('{i['id']}')\">Copy ID</button></h2><br>"
            for j in channels:
                if j['parent_id'] == i['id']:
                    channel_list += f"<a href=\"/channel?guild={guild['id']}&channel={j['id']}&gn={guild['name']}&cn={j['name']}\"><b>{j['name']} ({j['id']})</b></a><button onclick=\"navigator.clipboard.writeText('{j['id']}')\">Copy ID</button><br><br>"

    data = {
        "channel_list": channel_list,
        "guild": guild
    }

    return render_template("channels.html", data=data)


@app.route("/channel")
def channel():
    content = requests.get(
        url=f"https://discord.com/api/v9/channels/{request.args['channel']}/messages?limit=100",
        headers={
            "Authorization": token
        }
    )

    guild = requests.get(
        url=f"https://discord.com/api/v9/guilds/{request.args['guild']}",
        headers={
            "Authorization": token
        }
    ).json()

    all_content = []

    print(content.status_code)

    if content.status_code == 200:
        data = {
            "guild": guild,
            "title": f"{request.args['gn']} | {request.args['cn']}",
            "messages": ""
        }
        while True:
            if len(content.json()) < 1:
                break
            
            all_content.append(content.json())

            for i in content.json():
                latest_message_id = i['id']

            content = requests.get(
                url=f"https://discord.com/api/v9/channels/{request.args['channel']}/messages?before={latest_message_id}&limit=100",
                headers={
                    "Authorization": token
                }
            )

        sorted_content = []

        all_msg = len(all_content) - 1

        print(all_msg)

        while all_msg > -1:

            print("Found new chunk of messages")
            msg = len(all_content[all_msg]) - 1

            print(msg)

            while msg > -1:
                print("Sorted 1 message")
                sorted_content.append(all_content[all_msg][msg])
                msg -= 1

            all_msg -= 1

        # sorted_content = sorted(all_content, reverse=True)
        # all_content.reverse()

        # print(sorted_content)
        # print(f"type{type(sorted_content)}")

        for i in sorted_content:
            author = i['author']
            data['messages'] += f"<img src=\"https://cdn.discordapp.com/avatars/{author['id']}/{author['avatar']}?size=1024\" width=\"64\" height=\"64\"><br><span style=\"color: gray;\">{(i['timestamp'])}</span> | <a href=\"/user?id={author['id']}\">{author['username']} ({author['global_name']})</a><b>: {i['content']}</b><br><br>"

    else:
        data = {
            "title": f"{request.args['gn']} | {request.args['cn']}",
            "guild": guild,
            "messages": "<h3>Unable to view channel, maybe you are not authorized or it doesn't exist anymore.</h3>"
        }

    return render_template("channel.html", data=data)


@app.route("/example")
def example():
    # meant for testing...
    return requests.get(
        url=f"https://discord.com/api/v9/guilds/1151402600219037736/channels",
        headers={
            "Authorization": token
        }
    ).json()


app.run(use_reloader=True)