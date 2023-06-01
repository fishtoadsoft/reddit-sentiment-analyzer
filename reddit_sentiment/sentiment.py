#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import re
import datetime

from reddit_sentiment.api.scraper import Scraper
from reddit_sentiment.api.reddit import Reddit
from nltk.sentiment.vader import SentimentIntensityAnalyzer


happy_sentiment = "😁"
sad_sentiment = "😕"
neutral_sentiment = "😐"


class Sentiment():
    """Performs the sentiment analysis on a given set of Reddit Objects.
    
    :param enable_auth (optional): enable authentication to reddit api
    :param generate_report (optional): output a file with relevant data
    """

    def __init__(self, enable_auth=False, generate_report=False):
        self.api = Scraper()
        self.score = 0
        self.sentiment = neutral_sentiment
        self.headers = {'User-agent': "Reddit Sentiment Analyzer"}
        self.generate_report = generate_report

        if enable_auth:
            self.api = Reddit()

    def get_user_sentiment(self, username):
        """Obtains the sentiment for a user's comments.

        :param username: name of user to search
        """
        comments = self.api.parse_user(username, headers=self.headers)
        self.score = self._analyze(comments)
        self.sentiment = self._get_sentiment(self.score)

        user_id = "/user/{username}".format(username=username)

        if self.generate_report:
            now = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
            report_file = "{user_id}-{now}.txt"
            self._generate_output_file(report_file, comments, user_id)
        else:
             self._print_comments(comments, user_id)

    def get_listing_sentiment(self, subreddit, article):
        """Obtains the sentiment for a listing's comments.

        :param subreddit: a subreddit
        :param article: an article associated with the subreddit
        """
        comments = self.api.parse_listing(subreddit,
                                          article,
                                          headers=self.headers)
        self.score = self._analyze(comments)
        self.sentiment = self._get_sentiment(self.score)

        article_id = "/r/{subreddit}/comments/{article}".format(subreddit=subreddit,
                                                                article=article)

        if self.generate_report:
            now = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
            report_file = "{article_id}-{now}.txt"
            self._generate_output_file(report_file, comments, article_id)
        else:
             self._print_comments(comments, article_id)

    def _analyze(self, comments):
        """Obtains the sentiment for a user's comments.

        :param comments: comments to perform analysis on.
        :return: combined sentiment score of all sentences.
        """
        sentiment_analyzer = SentimentIntensityAnalyzer()
        final_score = 0

        cleanup_regex = re.compile('<.*?>')

        for comment in comments:
            comment = re.sub(cleanup_regex, '', str(comment))

            # provides compound, negative, neutral, and positive scores
            all_scores = sentiment_analyzer.polarity_scores(comment)
            score = all_scores['compound']
            final_score = final_score + score

        try:
            rounded_final = round(final_score/len(comments), 4)
            return rounded_final
        except ZeroDivisionError:
            logging.error("No comments found")

    def _get_sentiment(self, score):
        """Obtains the sentiment using a sentiment score.

        :param score: the sentiment score.
        :return: sentiment from score.
        """
        if score == 0:
            return neutral_sentiment
        elif score > 0:
            return happy_sentiment
        else:
            return sad_sentiment

    def _generate_output_file(self, filename, comments, url):
        """Outputs a file containing a detailed sentiment analysis per
        sentence.

        :param: filename: the name of the file to create and edit
        :param: comments: the parsed contents to analyze.
        :param: url: the url being parsed.
        """
        target = open(filename, 'w+')

        target.write("Sentiment analysis for '{url}'\n".format(url=url))
        target.write("Score: {score} \n".format(score=self.score))
        target.write("Sentiment: {sentiment}\n\n".format(
            sentiment=self.sentiment))

        comment_count = 1
        for comment in comments:
            score = self._analyze([comment])
            sentiment = self._get_sentiment(score)
            target.write("{comment_count}: {comment}\nScore: {score}, Sentiment: "
                         "{sentiment}\n".format(comment_count=str(comment_count),
                                                comment=comment,
                                                score=score,
                                                sentiment=sentiment))
            comment_count = comment_count + 1


    def _print_comments(self, comments, url):
        """Prints out sentences of user comments.

        :param: comments: the parsed contents to analyze.
        :param: url: the url being parsed.
        """
        
        print("Sentiment analysis for '{url}'".format(url=url))
        print("Score: {score}".format(score=self.score))
        print("Sentiment: {sentiment}\n".format(sentiment=self.sentiment))

        comment_count = 1
        for comment in comments:
            print("%s: %s" % (comment_count, comment.encode('ascii', 'ignore').decode("utf-8")))
            comment_count = comment_count + 1