# /u/SubredditArchiveBot
SubredditArchiveBot is a tool for backing up a subreddit using Reddit itself. SAR streams submissions and comments from your subreddit, and copies those into an archive subreddit for later use.

## Usage

Create a new subreddit to house your archive (recommended format is your subreddit name + archive, but you can obviously use whatever you like). You'll need a new Reddit account for your bot and a registered script with Reddit. The bot account you created also needs to be a moderator of your archive subreddit.

If you've never set up a Reddit bot before, [these instructions](https://www.reddit.com/r/RequestABot/comments/cyll80/a_comprehensive_guide_to_running_your_reddit_bot/) are very helpful.

Next, you'll need to clone or download this repository, then copy `env_sample.py` to `env.py`. 

If you're on Mac or Linux, you can do this with:

```
cp env_sample.py env.py
```

Then, you'll need to edit the file with your script details.

## Setting master/slave subreddit

Before you run SAR, you'll need to set your master subreddit (the source subreddit) and your slave subreddit (the destination subreddit) in `env.py`. These variables are `REDDIT_SUBREDDIT` and `REDDIT_ARCHIVE` respectively:

```
os.environ['REDDIT_SUBREDDIT'] = 'MASTER_SUBREDDIT'
os.environ['REDDIT_ARCHIVE']   = 'SLAVE_SUBREDDIT'
```

## Running the bot

Simply:

```
python main.py
```

## Known limitations

- No handling for edits. SAR only archives the original comment, and doesn't account for any post editing later
- Any existing `/u/` mentions in the post will trigger a notification to the user being mentioned

## TODO
 - [ ] Escape username mentions to avoid notification triggers
 - [ ] Add `originally posted by...` message to any archive posts
