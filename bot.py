#!/usr/bin/env python

import datetime
from env import SetupHelper
import os
import praw
from praw.models import Submission, Comment
from prawcore.exceptions import NotFound
import re
import time
import traceback

SetupHelper().setup_environment_variables()

SUBMISSION_INDEX_MSG = ('This comment is auto-generated to link your archive to your master subreddit.\n\n'
                        'Deleting this comment is VERY DANGEROUS and will break your archive.')
ARCHIVE_INDEX_MSG = ('This sticky is auto-generated to link your archive to your master subreddit.\n\n'
                     'Deleting this submission is VERY DANGEROUS and will break your archive.')

reddit = praw.Reddit(client_id=os.environ['REDDIT_CLIENT_ID'],
                     client_secret=os.environ['REDDIT_CLIENT_SECRET'],
                     user_agent=os.environ['REDDIT_USER_AGENT'],
                     username=os.environ['REDDIT_USERNAME'],
                     password=os.environ['REDDIT_PASSWORD'])


def run():
    if archive_needs_setup():
        set_up_archive()

    subreddit = reddit.subreddit(os.environ['REDDIT_SUBREDDIT'])
    stream = praw.models.util.stream_generator(
        lambda **kwargs: submissions_and_comments(subreddit, **kwargs))
    submission_type = praw.models.reddit.submission.Submission
    for post in stream:
        if isinstance(post, submission_type):
            archive_submission(post)
        else:
            archive_reply_to(post)


def submissions_and_comments(subreddit, **kwargs):
    results = []
    results.extend(subreddit.new(**kwargs))
    results.extend(subreddit.comments(**kwargs))
    results.sort(key=lambda post: post.created_utc, reverse=True)
    return results


def archive_reply_to(post):
    submission_type = praw.models.reddit.submission.Submission

    if isinstance(post.parent(), submission_type):
        archive_submission = find_archive_submission(post.parent())
        archive_post = archive_submission.reply(post.body)
        update_submission_index(
            post.id, archive_post.id, archive_submission.id)

        return archive_post
    else:
        archive_post = find_archive_comment(post)

        if archive_post == None:
            parent = archive_reply_to(post.parent())
            archive_post = parent.reply(post.body)

        update_submission_index(post.id, archive_post.id,
                                archive_post.submission.id)
        return archive_post


def archive_submission(submission):
    if submission.is_self:
        archived_submission = reddit.subreddit(os.environ['REDDIT_ARCHIVE']).submit(
            submission.title, selftext=submission.selftext)
    else:
        archived_submission = reddit.subreddit(os.environ['REDDIT_ARCHIVE']).submit(
            submission.title, url=submission.url)

    update_subreddit_index(submission.id, archived_submission.id)


def update_submission_index(comment_id, archive_comment_id, submission_id):
    submission = reddit.submission(id=submission_id)
    index = index_comment(submission)

    if index:
        old_index = index.body
        existing_codes_matches = re.search(index_matcher(), old_index)

        if existing_codes_matches == None:
            existing_codes = ''
        else:
            existing_codes = existing_codes_matches[0]

        new_index = build_index_comment(
            comment_id, archive_comment_id, existing_codes)
        index.edit(new_index)
    else:
        create_submission_index(comment_id, archive_comment_id, submission_id)


def index_comment(submission):
    try:
        return [comment for comment in reddit.submission(submission.id).comments if comment.distinguished][0]
    except IndexError:
        return None


def create_submission_index(comment_id, archive_comment_id, submission_id):
    index_comment_body = build_index_comment(comment_id, archive_comment_id)
    index_comment = reddit.submission(
        id=submission_id).reply(index_comment_body)
    index_comment.mod.distinguish(sticky=True)

    print('Pausing for a few seconds to distinguish the index comment.')
    # Pause for a few seconds, for some reason distinguishing a comment takes quite a long time.
    time.sleep(10)


def update_subreddit_index(submission_id, archive_submission_id):
    index = reddit.subreddit(os.environ['REDDIT_ARCHIVE']).sticky()
    old_index = index.selftext
    existing_codes_matches = re.search(index_matcher(), old_index)

    if existing_codes_matches == None:
        existing_codes = ''
    else:
        existing_codes = existing_codes_matches[0]

    new_index = build_master_index_comment(
        submission_id, archive_submission_id, existing_codes)
    index.edit(new_index)


def build_index_comment(post_id, archive_id, existing_codes=''):
    base_message = SUBMISSION_INDEX_MSG + "\n\n$index: " + existing_codes

    return base_message + '{}:{};\n\n'.format(post_id, archive_id) + timestamp()


def build_master_index_comment(post_id, archive_id, existing_codes=''):
    base_message = ARCHIVE_INDEX_MSG + "\n\n$index: " + existing_codes

    return base_message + '{}:{};\n\n'.format(post_id, archive_id) + timestamp()


def find_archive_submission(submission):
    index = reddit.subreddit(os.environ['REDDIT_ARCHIVE']).sticky()
    old_index = index.selftext
    existing_codes = re.search(index_matcher(), old_index)[0]
    submission_matcher = re.compile(
        r'(?<={}\:).*?(?=\;)'.format(submission.id))
    submission_id = re.search(submission_matcher, existing_codes)[0]

    return reddit.submission(submission_id)


def find_archive_comment(comment):
    try:
        archive_submission = find_archive_submission(comment.submission)

        index = index_comment(archive_submission).body
        existing_codes = re.search(index_matcher(), index)[0]
        comment_matcher = re.compile(r'(?<={}\:).*?(?=\;)'.format(comment.id))
        parent_id = re.search(comment_matcher, existing_codes)[0]

        return reddit.comment(parent_id)
    except Exception:
        return None


def find_parent_comment(comment, submission):
    try:
        if isinstance(comment.parent(), Submission):
            return submission
        else:
            index = index_comment(submission).body
            existing_codes = re.search(index_matcher(), index)[0]
            comment_matcher = re.compile(
                r'(?<={}\:).*?(?=\;)'.format(comment.parent().id))
            parent_id = re.search(comment_matcher, existing_codes)[0]

            return reddit.comment(parent_id)
    except (TypeError, AttributeError):
        print('Could not find parent comment for comment with ID {}'.format(comment.id),
              'Posting to submission {} instead.'.format(submission.id))
        return submission


def archive_cleaner():
    for submission in reddit.subreddit(os.environ['REDDIT_ARCHIVE']).top('all'):
        submission.delete()


def set_up_archive():
    submission = reddit.subreddit(os.environ['REDDIT_ARCHIVE']).submit(
        'Archive Index for /r/{}'.format(os.environ['REDDIT_SUBREDDIT']), ARCHIVE_INDEX_MSG + timestamp())
    submission.mod.sticky()


def archive_needs_setup():
    try:
        reddit.subreddit(os.environ['REDDIT_ARCHIVE']).sticky()
        return False
    except NotFound:
        return True


def timestamp():
    return '\n\nLast updated: {}'.format(datetime.datetime.utcnow())


def index_matcher():
    return re.compile(r'(?<=\$index\:\s).*(?=\n)')


if __name__ == '__main__':
    while True:
        try:
            run()
        except KeyboardInterrupt:
            print('Exiting...')
            break
        except Exception:
            traceback.print_exc()
            break
