
"""
    Shubhro's temporary like-filtering solution
"""

from random import choice

def filter_likes(likes):

    output = []
    for i in range(1,6):
        output.append(choice(likes)[0])

    return output