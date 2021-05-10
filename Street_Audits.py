#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pprint
import xml.etree.cElementTree as ET
import re
from collections import defaultdict

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Circle", "Crossing", "Cove", "North", "South", "East", 
            "West", "Northeast", "Northwest", "Southeast", "Southwest", "Extension", "Loop", "Highway",
            "Way", ]

mapping = {"St": "Street",
           "St.": "Street",
           "Rd.": "Road",
           "Ave": "Avenue",
           "Ave.": "Avenue",
           "Blvd": "Boulevard",
           "Cir": "Circle",
           "Courts": "Court",
           "Ct": "Court",
           "Dr": "Drive",
           "Dr.": "Drive",
           "Ext": "Extension",
           "Hwy": "Highway",
           "Rd": "Road",
           "N": "North",
           "S": "South",
           "E": "East",
           "W":"West"
            }

#Takes the street name as input and outputs the 
#street type in street_name.
def audit_street_type(street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            return street_type

#Checks if the 'k' attribute of the element is 
#a street, and returns True or False.        
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

#Takes the street name and associated type as input
#and returns the new, correct street name.
def update_name(name, st_type):
    if st_type in mapping:    
        name = name.replace(st_type, mapping[st_type])
    return name


# In[ ]:




