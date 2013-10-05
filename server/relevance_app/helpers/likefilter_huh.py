
from random import choice

# takes a list of (like, category) tuples
# returns a dictionary of {Category: [like1, like2,...]}
def createLikeDict(likes):
  dict = {};

  for like in likes:
    if like[1] in dict:
      dict[like[1]].append(like[0]);
    else:
      dict[like[1]] = [like[0]];
  return dict;

# takes a list of (like,category) tuples
# returns a list of just 5 "likes"
def chooseLike(dict):
  # choose random element from random category
  return choice(dict[choice(dict.keys())]);

def likefilter(dict):
  return len(dict);
  # Case 1: Fewer than 5 likes

def main():
  likes = [("Starbucks", "restaurant"), ("Qdoba", "restaurant"), ("Borders", "store")];
  dict = createLikeDict(likes);
  #print "Dictionary: ";
  #print dict;

  #print chooseLike(dict);
  print likefilter(dict);
main();
