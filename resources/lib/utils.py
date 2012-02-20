'''
Created on Feb 19, 2012

@author: alex
'''
import urllib2

def urlread(url, data=None):
    """Helper function to reduce code needed for a simple urlopen()"""
    f = urllib2.urlopen(url, data)
    page_contents = f.read()
    f.close()
    return page_contents