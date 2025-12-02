import re
from collections import defaultdict

def parse_data(path):
    data = []
    current_category = None
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            if line.startswith("#"):
                current_category = line[1:].strip()
                continue

            if line.startswith("- name:"):
                entry = {"category": current_category}
                entry["name"] = line.split(":", 1)[1].strip()
                entry["url"] = ""
                entry["description"] = ""
                entry["tags"] = []

                # read following lines until blank or next '- name:'
                while True:
                    pos = f.tell()
                    next_line = f.readline()
                    if not next_line or next_line.strip().startswith("- name:") or next_line.strip().startswith("#"):
                        f.seek(pos)
                        break
                    next_line = next_line.strip()
                    if next_line.startswith("url:"):
                        entry["url"] = next_line.split(":", 1)[1].strip()
                    elif next_line.startswith("description:"):
                        entry["description"] = next_line.split(":", 1)[1].strip()
                    elif next_line.startswith("tags:"):
                        tags_str = re.search(r"\[(.*?)\]", next_line)
                        if tags_str:
                            tags = [t.strip() for t in tags_str.group(1).split(",")]
                            entry["tags"] = tags
                data.append(entry)
    return data


def generate_html(entries, output_path="index.html"):
    # group by tag
    tag_map = defaultdict(list)
    for e in entries:
        for tag in e["tags"]:
            tag_map[tag].append(e)

    html_head = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>websitesno1talksabout</title>
<style>
body {font-family: monospace; background:#fafafa; color:#222; max-width:700px; margin:40px auto;}
h1{text-align:center;}
details{border:1px solid #ccc;border-radius:4px;margin:10px 0;padding:5px 10px;background:#fff;}
summary{cursor:pointer;font-weight:bold;}
a{color:#0044cc;text-decoration:none;}
a:hover{text-decoration:underline;}
footer{text-align:center;margin-top:40px;color:#777;}
.tag-list{text-align:center;margin-bottom:20px;}
.tag-list a{margin:0 5px; text-decoration:none; color:#0044cc;}
</style>
</head>
<body>
<h1>websitesno1talksabout</h1>
<p style="text-align:center">a living archive of curious websites</p>
<div class="tag-list">
"""
    # tag index links
    for tag in sorted(tag_map.keys(), key=str.lower):
        html_head += f'<a href="#{tag}">{tag}</a>'

    html_head += "</div>"

    html_footer = """<footer><small>Last updated automatically</small></footer></body></html>"""

    body = ""
    for tag, sites in sorted(tag_map.items()):
        body += f'<details id="{tag}"><summary>{tag}</summary><ul>'
        for e in sites:
            body += f'<li><a href="{e["url"]}" target="_blank">{e["name"]}</a>'
            if e["description"]:
                body += f' — {e["description"]}'
            body += "</li>"
        body += "</ul></details>\n"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_head + body + html_footer)


if __name__ == "__main__":
    entries = parse_data("data/websites.txt")
    generate_html(entries)
    print("index.html generated with tag navigation.")