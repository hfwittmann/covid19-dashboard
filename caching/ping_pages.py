# %%
from asyncio.tasks import sleep
import yaml
from pprint import pprint

with open('./sub/cache_pages.yaml', 'r') as f:
    cache_pages = yaml.safe_load(f)
# %%
pages_2_cache = [f"{cache_pages['basepage']}{p}" for p in cache_pages['pages']]

from requests_html import HTMLSession
session = HTMLSession()
for p in pages_2_cache:
    r = session.get(p)
    r.html.render(sleep=30)
    pprint(r.html.html)
# %%
