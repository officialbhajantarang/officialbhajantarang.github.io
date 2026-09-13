#!/usr/bin/env python3
import json, os, urllib.parse, urllib.request
from pathlib import Path
from datetime import datetime, timezone

API_KEY=os.environ["YOUTUBE_API_KEY"]
HANDLE="@officialbhajantarang"
BASE="https://www.googleapis.com/youtube/v3/"

def get(endpoint, params):
    q=urllib.parse.urlencode({**params, "key": API_KEY})
    with urllib.request.urlopen(BASE+endpoint+"?"+q, timeout=30) as r:
        return json.load(r)

channel=get("channels", {"part":"contentDetails", "forHandle":HANDLE})
items=channel.get("items", [])
if not items:
    raise SystemExit("Could not find YouTube channel for "+HANDLE)

uploads=items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
feed=get("playlistItems", {"part":"snippet,contentDetails,status", "playlistId":uploads, "maxResults":9})

videos=[]
for item in feed.get("items", []):
    if item.get("status",{}).get("privacyStatus") != "public":
        continue
    sn=item.get("snippet",{})
    vid=item.get("contentDetails",{}).get("videoId")
    if not vid: continue
    thumbs=sn.get("thumbnails",{})
    thumb=(thumbs.get("maxres") or thumbs.get("high") or thumbs.get("medium") or thumbs.get("default") or {}).get("url")
    videos.append({"videoId":vid,"title":sn.get("title",""),"publishedAt":sn.get("publishedAt",""),
                   "thumbnail":thumb or f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg",
                   "url":f"https://www.youtube.com/watch?v={vid}"})

Path("youtube-videos.json").write_text(json.dumps({
    "updatedAt":datetime.now(timezone.utc).isoformat(),"videos":videos
},ensure_ascii=False,indent=2),encoding="utf-8")
print(f"Updated {len(videos)} videos.")
