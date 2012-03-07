#!/usr/bin/env python
# Copyright 2011 Jonathan Beluch. 
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from Handlers import XBMCVideoPluginHandler
from utils import urlread
from BeautifulSoup import BeautifulSoup as BS, SoupStrainer as SS
import re
import urlparse
from resources.lib.youtube import get_flv, get_plugin_url

#MODE_MIT_DEPARTMENTS = '10'
MODE_MIT_COURSES = '11'
MODE_MIT_LECTURES = '12'
MODE_MIT_VIDEO = '13'
DEFAULT_MODE = MODE_MIT_COURSES

class _BasePluginHandler(XBMCVideoPluginHandler):
    base_url = 'http://ocw.mit.edu'
    courses_url = 'http://ocw.mit.edu/courses/audio-video-courses/'

    def urljoin(self, path):
        return urlparse.urljoin(self.base_url, path)

class Courses(_BasePluginHandler):
    def getAllCourse(self, includeSelected=False):
        src = urlread(self.courses_url)
        div_tags = BS(src, parseOnlyThese=SS('tr', {'class': re.compile('row|alt-row')}))

        #filter out classes that don't have full video lectures available
        if includeSelected:
            lectureFilter = re.compile('Video lectures|Selected video lectures')
        else:
            lectureFilter = 'Video lectures'
            
        video_divs = filter(lambda d: d.find('a', {'title': lectureFilter}), div_tags)

        items = [{'name': div.u.string,
                 'url': self.urljoin(div.a['href']),
                 'mode': MODE_MIT_LECTURES} for div in video_divs]
        
        return items
    
    def run(self):
        items = self.getAllCourse()
        self.app.add_dirs(items, sort=True)

class Lectures(_BasePluginHandler):
    def parse_normal_course(self, div_tags):
        return [{'name': div.a['alt'].encode('utf-8'),
                  'url': self.urljoin(div.a['href']),
                  'tn': self.urljoin(div.img['src']),
                  'mode': MODE_MIT_VIDEO,
                  'info': {'title': div.a['alt'].encode('utf-8')},
                  } for div in div_tags]

    def parse_rm_course(self, src):
        #not implemented yet
        #example url: http://ocw.mit.edu/courses/urban-studies-and-planning/11-969-workshop-on-deliberative-democracy-and-dispute-resolution-summer-2005/lecture-notes/
        return [{'name': 'NO LECTURES FOUND'}]
        pass

    def getLecuresFor(self, url):
        src = urlread(url)
        div_tags = BS(src, parseOnlyThese=SS('div', {'class': 'medialisting'}))

        #attempt to parse normal page
        if len(div_tags) > 0:
            items = self.parse_normal_course(div_tags)
        else:
            items = self.parse_rm_course(src)
        
        return items
            
    def run(self):
        items = self.getLecuresFor(url=self.args['url'])
        self.app.add_resolvable_dirs(items)

class PlayVideo(_BasePluginHandler):
    def extractYouTubeFile(self, src):
        p = r"http://www.youtube.com/v/(?P<videoid>.+?)'"
        m = re.search(p, src)
        if not m:
            print 'NO VIDEO FOUND'
            return None
        video_id = m.group('videoid')
        
#        youtube_url = get_flv(video_id=video_id)
        youtube_url = get_plugin_url(video_id=video_id)
        return youtube_url
    
    def extractInternetArchiveFiles(self, src):
        p = r'"(http://www.archive.org/download/.*)"'
        m = re.search(p, src)
        if not m:
            print 'NO VIDEO FOUND'
            return None
        return m.group(1)
    
    def extractMediaFile(self, url, preferArchive=False):
        ocw_page_url = url
        src = urlread(ocw_page_url)
        
        if preferArchive:
            archive = self.extractInternetArchiveFiles(src=src)
            if archive:
                return archive
        
        youtube_url = self.extractYouTubeFile(src=src)        
        
        return youtube_url
    
    def run(self):
        url = self.args['url']
        mediaURL = self.extractMediaFile(url=url)
        
        if mediaURL:
#            self.app.play_video(mediaURL)
            self.app.set_resolved_url(mediaURL)


site_listing = {'name': 'MIT',
                'mode': DEFAULT_MODE, 
                'info': {'plot': 'Free lecture notes, exams, and videos from MIT.',
                        'title': 'MIT'},
} 

handler_map = [(MODE_MIT_COURSES, Courses),
               (MODE_MIT_LECTURES, Lectures),
               (MODE_MIT_VIDEO, PlayVideo),
              ]

if __name__ == '__main__':
    pass