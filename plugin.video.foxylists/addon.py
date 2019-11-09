from functools import partial
import os
import time

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

from resources.lib import trakt
from resources.lib.router import router



def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)
        return True
    return False


@router.route('/auth_trakt')
def authenticate_trakt():
    init = trakt.authenticate()
    dialog = xbmcgui.DialogProgress()
    dialog.create('Enter code at: {}'.format(init['verification_url']),
                  init['user_code'])
    expires = time.time() + init['expires_in']
    while True:
        time.sleep(init['interval'])
        try:
            token = trakt.authenticate(init['device_code'])
        except Exception:
            pct_timeout = (time.time() - expires) / init['expires_in'] * 100
            pct_timeout = 100 - int(abs(pct_timeout))
            if pct_timeout >= 100 or dialog.iscanceled():
                dialog.close()
                xbmcgui.Dialog().notification('FoxyLists', 'Trakt Auth failed')
                return
            dialog.update(int(pct_timeout))
        else:
            dialog.close()
            save_trakt_auth(token)
            return


def save_trakt_auth(response):
    router.addon.setSettingString('trakt.access_token',
                                  response['access_token'])
    router.addon.setSettingString('trakt.refresh_token',
                                  response['refresh_token'])
    expires = response['created_at'] + response['expires_in']
    router.addon.setSettingInt('trakt.expires', expires)


def traktapi():
    access_token = router.addon.getSettingString('trakt.access_token')
    refresh_token = router.addon.getSettingString('trakt.refresh_token')
    expires = router.addon.getSettingInt('trakt.expires')
    new_auth = trakt.authenticate(refresh_token, expires)
    if new_auth:
        access_token = new_auth['access_token']
        save_trakt_auth(new_auth)
    return partial(trakt.get_request, auth_token=access_token)


@router.route('/refresh_liked_lists')
def refresh_liked():
    directory = 'special://userdata/addon_data/' + router.id_
    directory = xbmc.translatePath(directory)
    mkdir(directory)
    _trakt = traktapi()
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
                if not mkdir(mov_dir):
                    continue
                nfo_file = '{}/{}.nfo'.format(mov_dir, imdbid)
                strm_file = '{}/{}.strm'.format(mov_dir, imdbid)
                with open(nfo_file, 'w') as nfo:
                    imdb_url = 'https://www.imdb.com/title/{}/'.format(imdbid)
                    nfo.write(imdb_url)
                with open(strm_file, 'w') as strm:
                    strm_url = ('plugin://plugin.video.openmeta/'
                                'movies/play/imdb/{}').format(imdbid)
                    strm.write(strm_url)
    xbmcgui.Dialog().notification('FoxyLists', 'Updated liked trakt lists')


@router.route('/open_lists')
def open_list_dir():
    directory = 'special://userdata/addon_data/' + router.id_
    xbmc.executebuiltin('ActivateWindow(10025,'+directory+', return)')


@router.route('/')
def root():
    xbmcplugin.addDirectoryItem(router.handle,
                                router.build_url(authenticate_trakt),
                                xbmcgui.ListItem('Authenticate Trakt'))
    xbmcplugin.addDirectoryItem(router.handle,
                                router.build_url(refresh_liked),
                                xbmcgui.ListItem('Refresh Liked'))
    xbmcplugin.addDirectoryItem(router.handle,
                                router.build_url(open_list_dir),
                                xbmcgui.ListItem('Open Lists'))
    xbmcplugin.endOfDirectory(router.handle)


if __name__ == '__main__':
    router.run()
