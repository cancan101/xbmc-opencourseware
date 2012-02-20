#!/usr/bin/env python
import re
import urllib
#from urlparse import parse_qs
#from xbmccommon import parse_qs
#from BeautifulSoup import BeautifulSoup as BS, SoupStrainer as SS
import urllib2
import httplib
import socket
try:
    from urlparse import parse_qs
except ImportError:
    from cgi import parse_qs

_VALID_URL = r'^((?:https?://)?(?:youtu\.be/|(?:\w+\.)?youtube(?:-nocookie)?\.com/)(?!view_play_list|my_playlists|artist|playlist)(?:(?:(?:v|embed|e)/)|(?:(?:watch(?:_popup)?(?:\.php)?)?(?:\?|#!?)(?:.+&)?v=))?)?([0-9A-Za-z_-]+)(?(1).+)?$'
_available_formats = ['38', '37', '22', '45', '35', '44', '34', '18', '43', '6', '5', '17', '13']

def get_flv(url=None, video_id=None):
    if video_id is None:
        if url is None:
            print "No URL"
            return None
        # Extract video id from URL
        mobj = re.match(_VALID_URL, url)
        if mobj is None:
            print (u'ERROR: invalid URL: %s' % url)
            return None
        video_id = mobj.group(2)

    # Get video info
    for el_type in ['&el=embedded', '&el=detailpage', '&el=vevo', '']:
        video_info_url = ('http://www.youtube.com/get_video_info?&video_id=%s%s&ps=default&eurl=&gl=US&hl=en'
                % (video_id, el_type))
        request = urllib2.Request(video_info_url)
        try:
            video_info_webpage = urllib2.urlopen(request).read()
            video_info = parse_qs(video_info_webpage)
            if 'token' in video_info:
                break
        except (urllib2.URLError, httplib.HTTPException, socket.error), err:
            print (u'ERROR: unable to download video info webpage: %s' % str(err))
            return
    if 'token' not in video_info:
        if 'reason' in video_info:
            print (u'ERROR: YouTube said: %s' % video_info['reason'][0].decode('utf-8'))
        else:
            print  (u'ERROR: "token" parameter not in video info for unknown reason')
        return None


    if 'conn' in video_info and video_info['conn'][0].startswith('rtmp'):
        return video_info['conn'][0]
    elif 'url_encoded_fmt_stream_map' in video_info and len(video_info['url_encoded_fmt_stream_map']) >= 1:
        url_data_strs = video_info['url_encoded_fmt_stream_map'][0].split(',')
        url_data = [parse_qs(uds) for uds in url_data_strs]
        url_data = filter(lambda ud: 'itag' in ud and 'url' in ud, url_data)
        url_map = dict((ud['itag'][0], ud['url'][0]) for ud in url_data)

        available_formats = _available_formats
        format_list = available_formats
        existing_formats = [x for x in format_list if x in url_map]
        if len(existing_formats) == 0:
            print (u'ERROR: no known formats available for video')
            return None
        
        return url_map[existing_formats[0]] # Best quality   

def get_flvs(videoid=None, url=None):
#    REMOTE_DBG = True 
#
#    # append pydev remote debugger
#    if REMOTE_DBG:
#        # Make pydev debugger works for auto reload.
#        # Note pydevd module need to be copied in XBMC\system\python\Lib\pysrc
#        #import sys
#        #print sys.path
#        try:
#            import pysrc.pydevd as pydevd
#        # stdoutToServer and stderrToServer redirect stdout and stderr to eclipse console
#        except ImportError, ex:
#            import sys
#            sys.stderr.write("Error: " +
#                "You must add org.python.pydev.debug.pysrc to your PYTHONPATH. %s" %  ex)
#            sys.exit(1)
#
#    pydevd.settrace('192.168.1.100', stdoutToServer=True, stderrToServer=True)
    
    #if videoid, construct url
    if videoid:
        url = 'http://www.youtube.com/watch?v=%s' % videoid
    src = urllib.urlopen(url).read()

    p = r'<param name=\\"flashvars\\" value=\\"(.+?)\\"'
    m = re.search(p, src)
    if not m:
        print 'error with match'
        return
    
    flashvars = m.group(1)
    params = parse_qs(flashvars)
    #when using urlparse.parse_qs, a list si returned for vals, so get 0th element
    #urls = params['fmt_url_map'][0].split(',')
    #fmts = params['fmt_list'][0].split(',')
    urls = params['fmt_url_map'].split(',')
    fmts = params['fmt_list'].split(',')


    urldict = dict((pair.split('|', 1) for pair in urls))
    fmtdict = dict((pair.split('/')[:2] for pair in fmts))
    flvs = dict(((fmtdict[key], urldict[key]) for key in urldict.keys()))
    return flvs

def get_high_quality(youtube_urls):
    hres = [(key, int(key.split('x')[0])) for key in youtube_urls.keys()]
    #highest quality is last in list
    hres = sorted(hres, key=lambda h: h[1])
    return youtube_urls[hres[-1][0]]
