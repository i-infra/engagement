import io
import itertools
import math
import sys
import json

from PIL import Image, ImageChops, ImageDraw, ImageEnhance


def rerle(xs):
    return [
        (sum([i[0] for i in x[1]]), x[0]) for x in itertools.groupby(xs, lambda x: x[1])
    ]


def rle(xs):
    return [(len(list(gp)), x) for x, gp in itertools.groupby(xs)]


def rld(xs):
    return itertools.chain.from_iterable((itertools.repeat(x, n) for n, x in xs))


def _flatten(l):
    return list(itertools.chain(*[[x] if type(x) not in [list] else x for x in l]))


# username as first arg

input_username = sender = sys.argv[-2]

# json file path as last argument

chunk = [el for el in json.loads(open(sys.argv[-1]).read()) if el]

sent = [t for t in chunk if t.get("username") == sender]
resp = [t for t in chunk if t.get("username") != sender]

total_likes = sum([t.get("likes_count") for t in sent])
top_liked = [
    (t.get("link"), t.get("tweet"), t.get("retweets_count"), t.get("likes_count"))
    for t in sorted(sent, key=lambda t: t.get("likes_count"), reverse=True)[0:5]
]
words = _flatten(
    [t.get("tweet").split(" ") for t in sent if t.get("tweet").count("@") < 10]
)
words += _flatten(
    [t.get("tweet").split(" ") for t in resp if t.get("tweet").count("@") < 10]
)

accounts = sorted(
    rle(
        sorted(
            [
                w
                for w in words
                if w and w[0] == "@" and (sender not in w) and ("eigenrobot" not in w)
            ]
        )
    )
)
max_inters = max([ct for (ct, name) in accounts])

top40 = [(ct, name) for (ct, name) in accounts if ct > max_inters // 40]

import urllib.request

total = sum([ct for (ct, name) in top40])
balanced = [{"datum": ct / total, "id": name} for (ct, name) in top40]
balanced = sorted(balanced, key=lambda x: x.get("datum"))

# some day this will be the normal public ARGH
host = "localhost:8080"
import circlify

rings = circlify.circlify(balanced, show_enclosure=True)
metadata = json.loads(
    urllib.request.urlopen(
        f"http://{host}/tw/users?usernames="
        + ",".join([u.lstrip("@") for (ct, u) in top40])
    ).read()
)
print(accounts)
print(top_liked)
user_pics = {m.get("screen_name"): m.get("profile_image_url_https") for m in metadata}
user_pics[sender] = json.loads(
    urllib.request.urlopen(f"http://{host}/tw/users?usernames=" + sender).read()
)[0].get("profile_image_url_https")


base = Image.new("RGBA", (800, 800))


def crop_to_circle(im):
    bigsize = (im.size[0] * 3, im.size[1] * 3)
    mask = Image.new("L", bigsize, 0)
    ImageDraw.Draw(mask).ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(im.size, Image.ANTIALIAS)
    mask = ImageChops.darker(mask, im.split()[-1])
    im.putalpha(mask)
    return im


user_imgs = {
    n: crop_to_circle(
        Image.open(io.BytesIO(urllib.request.urlopen(u).read())).convert("RGBA")
    )
    for (n, u) in user_pics.items()
}
enhancer = ImageEnhance.Contrast(user_imgs[sender])
user_imgs[sender] = enhancer.enhance(0.2)
enhancer = ImageEnhance.Brightness(user_imgs[sender])
user_imgs[sender] = enhancer.enhance(1.8)

for circle in rings:
    if not circle.ex:
        circle.ex = {"id": sender}
    username = circle.ex.get("id").strip("@")
    d = math.floor(circle.r * 800)
    if username in user_imgs:
        img = user_imgs[username].resize((d, d))
        base.paste(
            img,
            (
                400 + int((circle.x - circle.r) * 400),
                400 + int((circle.y - circle.r) * 400),
            ),
            img,
        )

base.save(f"{input_username}.png")
