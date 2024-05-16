from xml.etree import ElementTree
import os
import re
import math
from datetime import datetime

def parse_library(root):
    output = []
    for medium in root.findall("Video"):
        output.append(medium.attrib)

    if len(output) == 0:
        for medium in root.findall("Directory"):
            output.append(medium.attrib)

    if len(output) == 0:
        for medium in root.findall("Photo"):
            output.append(medium.attrib)

    return output

def parse_data(data, max, base_url, token, identifier, section_key, images_base_url):
    data = sorted(data, key=lambda i: i['addedAt'], reverse=True)[:max]

    output = []
    for item in data:
        date = datetime.strptime(item.get("originallyAvailableAt", "1900-01-01"), "%Y-%m-%d").strftime('%Y-%m-%dT%H:%M:%SZ')
        thumb = item.get("thumb", item.get("parentThumb", item.get("grandparentThumb", None)))
        art = item.get("art", item.get("grandparentArt", None))
        deep_link_position = -1
        if section_key == "artist":
            deep_link_position = -2
        deep_link = f'{base_url}/web/index.html#!/server/{identifier}/details?key=%2Flibrary%2Fmetadata%2F{item.get("key", "").split("/")[deep_link_position]}'

        output.append(
            {
                "airdate": date,
                "title": item.get("grandparentTitle", item.get("parentTitle", item.get("title", ""))),
                "release": datetime.utcfromtimestamp(int(item.get("addedAt", 0))).strftime('%Y-%m-%dT%H:%M:%SZ'),
                "episode": item.get("title", ""),
                "number": f'S{"{:0>2}".format(item.get("parentIndex", "1"))}E{"{:0>2}".format(item.get("index", "1"))}' if item.get("parentIndex", None) and item.get("index", None) else "",
                "season_num": item.get("parentIndex", ""),
                "season_num": item.get("parentIndex", "1"),
                "episode_num": item.get("index", "1"),
                "genres": ", ".join([genre['tag'] for genre in item.get('Genre', [])][:3]),
                "rating": ('\N{BLACK STAR} ' + str(item.get("rating"))) if int(float(item.get("rating", 0))) > 0 else '',
                "studio": item.get("grandparentTitle", ""),
                "aired": date,
                "runtime": math.floor(int(item.get("duration", 0)) / 60000),
                "poster": (f'{images_base_url}?path={thumb}') if thumb else "",
                "fanart": (f'{images_base_url}?path={art}') if art else "",
                "flag": "viewCount" not in item,
                "deep_link": deep_link if identifier else None
            }
        )

    return output


