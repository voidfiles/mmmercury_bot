# MMMercury Bot

MMMercruy bot is the code that runs the bot part of http://alpha.app.net/mmmercury.

The documentation is incredibly light at this point. If you want help understand any of it just talk to me https://alpha.app.net/voidfiles.

# Install

Right now the bot requires that you have redis installed.

```sh
cd mmmercury_bot
virtualenv --no-site-packages venv
source venv/bin/activate
pip install -r requirements.txt
```

# Examples

### test_stream.py

Test stream is an example implmentation of the stream store class. You will need an [app token](http://developers.app.net/docs/authentication/flows/app-access-token/). This script starts a stream consumer. The stream consumer stores posts into redis. It also indexes certain actions like reposts, and stars so that posts can be ranked by another script.

```sh
./test_stream.py --app-token="APP_TOKEN" --stream-name mmmercury
```

### test_rank.py

Test rank ranks the currently stored posts. It also establishes a post queue. Every time you run the test_rank.py command it trys to establish the top 100 posts that are currently stored in redis.

As new items enter the top 100 it checks the publish queue to see if that post is already waiting to be published, or has been published. If the post is in neither it gets added to the waiting to be published queue. Then one item is popped of that queue and append to the published queue. That item to be published is returned.

At this point you need to determine how you want to publish that item.

