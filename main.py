import json
import discord
import requests

with open("./info.json", "r") as f:
    info = json.loads(f)

Discord_token = info['Discord']['token']

