from functools import partial
import os
import urllib
import urlparse
import sys

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

from resources.lib import trakt


ACCESS_TOKEN = 'REDACTED'
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
addon = xbmcaddon.Addon()
if addon_handle > 0:
    xbmcplugin.setContent(addon_handle, 'videos')


def build_url(**kwargs):
    return base_url + '?' + urllib.urlencode(kwargs)


def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def main():
    args = dict(urlparse.parse_qsl(sys.argv[2][1:]))
    directory = 'special://userdata/addon_data/' + addon.getAddonInfo('id')
    directory = xbmc.translatePath(directory)
    mkdir(directory)
    mode = args.get('mode', None)
    if mode == None:
        _trakt = partial(trakt.get_request, auth_token=ACCESS_TOKEN)
        liked_lists = _trakt('users/likes/lists')
        for _list in liked_lists:
            name = _list['list']['ids']['slug']
            user_slug = _list['list']['user']['ids']['slug']
            list_id = _list['list']['ids']['trakt']
            path = 'users/{}/lists/{}/items'.format(user_slug, list_id)
            items = _trakt(path)
            list_dir = '{}/{}'.format(directory, name)
            mkdir(list_dir)
            for item in items:
                if 'movie' in item:
                    imdbid = item['movie']['ids']['imdb']
                    mov_dir = '{}/{}'.format(list_dir, imdbid)
                    mkdir(mov_dir)
                    nfo_file = '{}/{}.nfo'.format(mov_dir, imdbid)
                    strm_file = '{}/{}.strm'.format(mov_dir, imdbid)
                    with open(nfo_file, 'w') as nfo:
                        imdb_url = 'https://www.imdb.com/title/{}/'.format(
                            imdbid)
                        nfo.write(imdb_url)
                    with open(strm_file, 'w') as strm:
                        strm_url = ('plugin://plugin.video.openmeta/'
                                    'movies/play/imdb/{}').format(imdbid)
                        strm.write(strm_url)


if __name__ == '__main__':
    main()
