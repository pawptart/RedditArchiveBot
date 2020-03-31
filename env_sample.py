#!/usr/bin/env python

import os


class SetupHelper():
    def setup_environment_variables(self):
        # Reddit instance details
        os.environ['REDDIT_CLIENT_ID']     = 'REDDIT_CLIENT_ID'
        os.environ['REDDIT_CLIENT_SECRET'] = 'REDDIT_CLIENT_SECRET'
        os.environ['REDDIT_USER_AGENT']    = 'REDDIT_USER_AGENT'
        os.environ['REDDIT_USERNAME']      = 'REDDIT_USERNAME'
        os.environ['REDDIT_PASSWORD']      = 'REDDIT_PASSWORD'

        # Bot instance details
        os.environ['REDDIT_SUBREDDIT']     = 'REDDIT_SUBREDDIT'
        os.environ['REDDIT_ARCHIVE']       = 'REDDIT_ARCHIVE'
