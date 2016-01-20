#--*-- coding:utf-8 --*--

import requests
import urlparse
import os
import time
import random
import multiprocessing as mp

from gevent.monkey import patch_all
patch_all(thread=False)

#-------------------------------------------------------------------------
req_url_format = r'http://tile.openstreetmap.org/{z}/{x}/{y}.png'
root_path = '/home/pknam/maps/openstreetmap'
imgfile_extension = '.png'
request_referer = r'http://www.openstreetmap.org/'
#------------------------------------------------------------------------------
#req_url_format = r'http://khms1.google.co.kr/kh/v=190&x={x}&y={y}&z={z}'
#root_path = 'D:\\maps\\googlesatellite\\'
#imgfile_extension = '.jpg'
#request_referer = r'https://www.google.co.kr/'
#------------------------------------------------------------------------------
#req_url_format = r'http://mts1.google.com/vt/lyrs=m@186112443&hl=x-local&src=app&x={x}&y={y}&z={z}&s=Galile'
#root_path = '/home/pknam/maps/googlemap'
#imgfile_extension = '.png'
#request_referer = r'https://www.google.co.kr/'
#------------------------------------------------------------------------------
#req_url_format = r'http://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}'
#root_path = '/home/pknam/maps/google_hybrid/'
#imgfile_extension = '.jpg'
#request_referer = r'https://www.google.co.kr/'
#------------------------------------------------------------------------------

def get_random_header():
    return {
        'Referer' : request_referer,
        'Accept' : r'*/*',
        'User-Agent' : str.format("Mozilla/5.0 (Windows NT 6.1; WOW64; rv:{0}.0) Gecko/{2}{3:0>2}{4:0>2} Firefox/{0}.0.{1}",
            random.randint(3, 13),
            random.randint(1, 9),
            random.randint(2011, 2014),
            random.randint(1, 12),
            random.randint(1, 30))
    }

urls = [
    r'http://bigmap.osmz.ru/bigmap.php?xmin=53&xmax=56&ymin=23&ymax=25&zoom=6&scale=256&tiles=mapnik',
    r'http://bigmap.osmz.ru/bigmap.php?xmin=106&xmax=113&ymin=46&ymax=51&zoom=7&scale=256&tiles=mapnik',
    #r'http://bigmap.osmz.ru/bigmap.php?xmin=212&xmax=227&ymin=92&ymax=103&zoom=8&scale=256&tiles=mapnik',
    #r'http://bigmap.osmz.ru/bigmap.php?xmin=424&xmax=455&ymin=184&ymax=207&zoom=9&scale=256&tiles=mapnik',
    #r'http://bigmap.osmz.ru/bigmap.php?xmin=848&xmax=911&ymin=368&ymax=415&zoom=10&scale=256&tiles=mapnik',
    #r'http://bigmap.osmz.ru/bigmap.php?xmin=1696&xmax=1823&ymin=736&ymax=831&zoom=11&scale=256&tiles=mapnik',
    #r'http://bigmap.osmz.ru/bigmap.php?xmin=3392&xmax=3647&ymin=1472&ymax=1663&zoom=12&scale=256&tiles=mapnik',
    #r'http://bigmap.osmz.ru/bigmap.php?xmin=6784&xmax=7295&ymin=2944&ymax=3327&zoom=13&scale=256&tiles=mapnik',
    #r'http://bigmap.osmz.ru/bigmap.php?xmin=13568&xmax=14591&ymin=5888&ymax=6655&zoom=14&scale=256&tiles=mapnik',
    #r'http://bigmap.osmz.ru/bigmap.php?xmin=27136&xmax=29183&ymin=11776&ymax=13311&zoom=15&scale=256&tiles=mapnik',
]

def dummy_save(args):
    def save_img_url(url, save_path):
        data = None

        while True:
            try:
                res = requests.get(url, headers=get_random_header(), timeout=5)
                
                # if server does not have the tile image
                if res.status_code == 404:
                    return

                data = res.content
            except requests.exceptions.ConnectionError:
                pass
            except requests.exceptions.Timeout:
                pass

            if data is not None:
                break
            else:
                print "sleeping 5 sec"
                time.sleep(5)
                continue # retry

        with open(save_path, 'wb') as f:
            f.write(data)

    return save_img_url(*args)





if __name__ == '__main__':
    
    pool = mp.Pool(mp.cpu_count())

    for url in urls:
        parsed_query = urlparse.parse_qs(urlparse.urlparse(url).query)
    
        zoom = parsed_query['zoom'][0]
        xmin = parsed_query['xmin'][0]
        xmax = parsed_query['xmax'][0]
        ymin = parsed_query['ymin'][0]
        ymax = parsed_query['ymax'][0]

        zoom_dir = os.path.join(root_path, zoom)
        if not os.path.exists(zoom_dir):
            os.mkdir(zoom_dir)
    
        for x in range(int(xmin), int(xmax) + 1):
            x_dir = os.path.join(root_path, zoom, str(x))
            if not os.path.exists(x_dir):
                os.mkdir(x_dir)
        

            works = []

            for y in range(int(ymin), int(ymax) + 1):
                req_url = str.format(req_url_format, z=zoom, x=x, y=y)
                save_path = os.path.join(root_path, zoom, str(x), str(y) + imgfile_extension)

                if os.path.exists(save_path):
                    if os.stat(save_path).st_size > 0:
                        continue
                    else:
                        os.remove(save_path)
            
                # add to work pool
                works.append([req_url, save_path])

            
            # run process pool
            if len(works) > 0:
                pool.map(dummy_save, works)
                print "%d images downloaded. zoom : %s. x : %d" % (len(works), zoom, x)

                time.sleep(2)
            else:
                print "pass. zoom : %s. x : %d" % (zoom, x)
                
    pool.close()
