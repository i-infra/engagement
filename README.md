### Setup

 * Needs an instance of [ARGH](https://github.com/i-infra/argh) running locally because there's some amount of shenanigans blocking urllib requests from hitting the public endpoint...
 * No other dependencies except PIL aka PILLOW, the Python Image Library.
 * Not exactly documented at all.


``` bash
curl 'https://argh.tweeter.workers.dev/tw/timeline?username=infra_naut&since=2021-05-01&until=2021-07-01&limit=100000&indent=2' -o infra.may-june.json
python3 engagement.py infra_naut infra.may-june.json
curl --data-binary @infra_naut.png https://public.getpost.workers.dev
```

### Inspiration

 * https://chirpty.com/
 * https://orbit.livasch.com/

### Todo

 * Document things, actually.
 * Refactor until the codebase is plausibly intelligible.
 * Score timeline events like Orbit, rather than merely summing mentions, retweets, mentions, and replies evenly. 
 * Fix the weird demand on ARGH running locally. Not sure why this is so hard...
 * Add caching until the server load isn't too heavy.
 * Turn into a serverless project so other people can enjoy the nice dataviz.
