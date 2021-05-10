#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pprint
import xml.etree.cElementTree as ET
import re
from collections import defaultdict

# Changes user to default_value if user is 'OSMF Redaction Account',
# else returns original value
def correct_user(user, default_value):
    if user == 'OSMF Redaction Account':
        return default_value
    else:
        return user


# In[ ]:




