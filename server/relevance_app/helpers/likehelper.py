from globals import *

from random import choice
from random import shuffle
from math import ceil

import logging

from relevance_app.helpers.newsfetcher import *

logging.basicConfig(level=logging.INFO)
class LikeHelper():
    
    def createLikeDict(self, likes):
        
        dict = {}
        
        # get a like tuple (like, category)
        for likeItem in likes:
            like = likeItem[0]
            category = likeItem[1]
            
            if category in dict:
                dict[category].append(like)
            else:
                dict[category] = [like]
        
        return dict
    
    def findArticle(self, newsfetcher, articles, dict, category):
        
        like = choice(dict[category])
        
        # extract a relevant article for the given like
        article = newsfetcher.getTopArticleForTopic('"' + like + '"')
        dict[category].remove(like) # Don't repeat a like
        
        # print article
        # if a valid article, update list of articles
        if article:
            article.like = like
            articles.append(article)
            return 1
        return 0
    
    
    def likefilter(self, dict, totalArticles = 5):
        
        count = 0                       # how many articles found so far
        newsfetcher = NewsFetcher()     # NewFetcher finds the news
        articles = []                   # list of articles that will be returned
        
        presetCategories = ['Professional sports team', 'Musician/band', 'University', 'Politician', 'Tv show']
        articlesPerCat = ceil(totalArticles/(1.0 * len(presetCategories)))
        shuffle(presetCategories)
        
        for category in presetCategories:
            
            stepCount = count
            
            # Found enough articles, quit
            if count >= totalArticles:
                break
            
            # If the dictionary does not contain the category
            if not dict.has_key(category):
                continue
            
            # If the corresponding list contains a nonempty list
            # If we haven't selected more than the limit number of articles for a given category
            while dict[category] and count - stepCount < articlesPerCat:
                count += LikeHelper().findArticle(newsfetcher, articles, dict, category)
            
            if not dict[category]:
                del dict[category]

        while count < totalArticles and dict:
            
            category = choice(dict.keys())
            count += LikeHelper().findArticle(newsfetcher, articles, dict, category)
            
            if not dict[category]:
                del dict[category]
        
        return articles