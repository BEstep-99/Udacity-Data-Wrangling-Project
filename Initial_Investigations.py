#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pprint
import xml.etree.cElementTree as ET
import re
from collections import defaultdict

charlotte_map = "charlotte_map.osm"
tags = defaultdict(int)
def count_tags(filename):
    tags_count = []
    for event, elem in ET.iterparse(filename, events=("start",)):
        if event == 'start':
            tags_count.append(elem.tag)
    for tag in tags_count:
        if tag not in tags:
            tags[tag]=tags_count.count(tag)
    return tags
tags = count_tags(charlotte_map)

pprint.pprint(tags)


# In[2]:


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


def key_type(element, keys):
    if element.tag == "tag":
        value = element.attrib["k"]
        if lower.search(value):
            keys["lower"]+=1
        elif lower_colon.search(value):
            keys["lower_colon"]+=1
        elif problemchars.search(value):
            keys["problemchars"]+=1
        else:
            keys["other"]+=1
        pass
        
    return keys



def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys

keys = process_map('charlotte_map.osm')
pprint.pprint(keys)


# In[3]:


def process_users(filename):
    users = {}
    for _, element in ET.iterparse(filename):
        if element.tag in ["node", "way", "relation"]:
            user_id = element.attrib["uid"]
            user = element.attrib["user"]
            users[user_id] = user
        pass

    return users

users = process_users('charlotte_map.osm')
pprint.pprint(users)


# In[ ]:




