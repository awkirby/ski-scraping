# Practise with making requests to the stack overflow API

#%%
import requests
from pprint import pprint as pp

#%%
# Last 100 posts
ENDPOINT = "https://api.stackexchange.com"
POSTS = "/2.2/posts?page=1&pagesize=100&order=desc&sort=activity&site=stackoverflow"
r = requests.get(ENDPOINT+POSTS)
# %%
pp(r.json())
# %%
# Find who answered the most questions in the last hour

