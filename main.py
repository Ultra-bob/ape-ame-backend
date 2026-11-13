import datetime
import os
from json import dumps, loads
from flask import Flask, request
import redis
import base64
import re
import requests

app = Flask(__name__)
DEV = False
DB_KEY = "scores" if not DEV else "scores_dev"
WEBHOOK_URL = "https://discord.com/api/webhooks/1233484325962518709/yUxyEYZzfxOvOhd3G892pSd4XHbwdj96UnLmL9oJXeimc7sqMfUPkGhs0VA-k34o-56J"

db = redis.Redis(
    host=os.getenv('REDIS_HOST', 'redis'),
    port=int(os.getenv('REDIS_PORT', '6379')),
    password=os.getenv('REDIS_PASSWORD') or None,
    socket_connect_timeout=5,
    socket_timeout=5,
    decode_responses=True
)

def seconds2mmss(total_seconds: float):
	seconds: float = total_seconds % 60
	minutes: int   =  int(total_seconds / 60.0) % 60
	return "%02d:%05.2f" % (minutes, seconds)

@app.get("/healthz")
def healthz():
    db.ping()
    return {"status": "ok"}

@app.get("/leaderboard")
def leaderboard():
    return {"scores": [x.split("|") for x in db.zrevrange(DB_KEY, 0, 50)]}

@app.route("/leaderboard", methods=["POST"])
def submit_score():
    data = request.args.get('score', '')
    print(data)
    if not data.startswith("EGH"):
        return "Decryption Failure!", 403
    
    score = base64.urlsafe_b64decode(data[3:].split("eHa")[0]).decode()
    uname = base64.urlsafe_b64decode(data.split("eHa")[1].split("lAx")[0]).decode()
    wave = base64.urlsafe_b64decode(data.split("eHa")[1].split("lAx")[1]).decode()

    if not re.match("^[A-Z]{3}$", uname):
        return "Invalid username", 405
    db.zadd(DB_KEY, {(uname + "|" + score + "|" + wave): int(wave) * 1e12 - float(score)})
    
    scores = [x.split("|") for x in db.zrevrange(DB_KEY, start=0, end=50)]

    position = db.zrevrank(DB_KEY, uname + "|" + score + "|" + wave) + 1
    print(position)
    if position == 1 and int(wave) > 5:
        print("WR ALERT!!!!")
        if DEV:
             return
        requests.post(WEBHOOK_URL, json={"content": f":warning: <@&1234952370387943517> WR ALERT :warning:\n`{uname.upper()}` set a new WR by reaching wave {wave} in `{seconds2mmss(float(score))}`"})

    if position > 50:
        position /= db.zcount(DB_KEY, "-inf", "inf")

    print(scores)

    return dumps({
        "scores": scores,
        "position": position
    })