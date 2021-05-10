#!/usr/bin/env python
# coding: utf-8

# In[26]:


get_ipython().run_line_magic('run', 'Street_Audits.py')


# In[27]:


get_ipython().run_line_magic('run', 'User_Correction.py')


# In[28]:


get_ipython().run_line_magic('run', 'Audit_Cities.py')


# In[29]:


import pprint
import xml.etree.cElementTree as ET
import re
from collections import defaultdict

import codecs
import csv
import cerberus
import schema

schema = {
    'node': {
        'type': 'dict',
        'schema': {
            'id': {'required': True, 'type': 'integer', 'coerce': int},
            'lat': {'required': True, 'type': 'float', 'coerce': float},
            'lon': {'required': True, 'type': 'float', 'coerce': float},
            'user': {'required': True, 'type': 'string'},
            'uid': {'required': True, 'type': 'integer', 'coerce': int},
            'version': {'required': True, 'type': 'string'},
            'changeset': {'required': True, 'type': 'integer', 'coerce': int},
            'timestamp': {'required': True, 'type': 'string'}
        }
    },
    'node_tags': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'id': {'required': True, 'type': 'integer', 'coerce': int},
                'key': {'required': True, 'type': 'string'},
                'value': {'required': True, 'type': 'string'},
                'type': {'required': True, 'type': 'string'}
            }
        }
    },
    'way': {
        'type': 'dict',
        'schema': {
            'id': {'required': True, 'type': 'integer', 'coerce': int},
            'user': {'required': True, 'type': 'string'},
            'uid': {'required': True, 'type': 'integer', 'coerce': int},
            'version': {'required': True, 'type': 'string'},
            'changeset': {'required': True, 'type': 'integer', 'coerce': int},
            'timestamp': {'required': True, 'type': 'string'}
        }
    },
    'way_nodes': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'id': {'required': True, 'type': 'integer', 'coerce': int},
                'node_id': {'required': True, 'type': 'integer', 'coerce': int},
                'position': {'required': True, 'type': 'integer', 'coerce': int}
            }
        }
    },
    'way_tags': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'id': {'required': True, 'type': 'integer', 'coerce': int},
                'key': {'required': True, 'type': 'string'},
                'value': {'required': True, 'type': 'string'},
                'type': {'required': True, 'type': 'string'}
            }
        }
    }
}

OSM_PATH = "charlotte_map.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

# Shape element into correct dictionaries for conversion into CSV format.
def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    
    if element.tag == 'node':
        for field in node_attr_fields:
            if field == 'user':
                username = correct_user(field, 'No User')
                node_attribs[field] = username
            else:
                node_attribs[field] = element.attrib[field]
        for tag in element.iter('tag'):
            colon = (tag.attrib['k']).find(':')
            if colon > -1:
                if is_street_name(tag):
                    st_type = audit_street_type(tag.attrib['v'])
                    name = update_name(tag.attrib['v'], st_type)
                    tags.append({'id': node_attribs["id"],
                                     'key': tag.attrib['k'][colon+1:],
                                     'value': name,
                                     'type': tag.attrib['k'][0:colon]})
                else:
                    tags.append({'id': node_attribs["id"],
                                         'key': tag.attrib['k'][colon+1:],
                                         'value': tag.attrib['v'],
                                         'type': tag.attrib['k'][0:colon]})
            else:
                if is_street_name(tag):
                    st_type = audit_street_type(tag.attrib['v'])
                    name = update_name(tag.attrib['v'], st_type)
                    tags.append({'id': node_attribs['id'],
                                     'key': tag.attrib['k'],
                                     'value': name,
                                     'type': default_tag_type})
                else:
                    tags.append({'id': node_attribs['id'],
                                         'key': tag.attrib['k'],
                                         'value': tag.attrib['v'],
                                         'type': default_tag_type})
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        for field in way_attr_fields:
            way_attribs[field] = element.attrib[field]
        nd_position = 0
        for tag in element.iter('tag'):
            colon = (tag.attrib['k']).find(':')
            if colon > -1:
                if is_street_name(tag):
                    st_type = audit_street_type(tag.attrib['v'])
                    name = update_name(tag.attrib['v'], st_type)
                    tags.append({'id': way_attribs["id"],
                                     'key': tag.attrib['k'][colon+1:],
                                     'value': name,
                                     'type': tag.attrib['k'][0:colon]})
                else:
                    tags.append({'id': way_attribs["id"],
                                         'key': tag.attrib['k'][colon+1:],
                                         'value': tag.attrib['v'],
                                         'type': tag.attrib['k'][0:colon]})
            else:
                if is_street_name(tag):
                    st_type = audit_street_type(tag.attrib['v'])
                    name = update_name(tag.attrib['v'], st_type)
                    tags.append({'id': way_attribs['id'],
                                     'key': tag.attrib['k'],
                                     'value': name,
                                     'type': default_tag_type})
                else:
                    tags.append({'id': way_attribs['id'],
                                         'key': tag.attrib['k'],
                                         'value': tag.attrib['v'],
                                         'type': default_tag_type})
        for tag in element.iter('nd'):
            way_nodes.append({'id': way_attribs['id'],
                              'node_id': tag.attrib['ref'],
                              'position': nd_position})
            nd_position+=1
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}

# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: v for k, v in row.items()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w', 'utf-8') as nodes_file,          codecs.open(NODE_TAGS_PATH, 'w', 'utf-8') as nodes_tags_file,          codecs.open(WAYS_PATH, 'w', 'utf-8') as ways_file,          codecs.open(WAY_NODES_PATH, 'w', 'utf-8') as way_nodes_file,          codecs.open(WAY_TAGS_PATH, 'w', 'utf-8') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


# In[30]:


process_map(OSM_PATH, validate=True)


# In[ ]:




