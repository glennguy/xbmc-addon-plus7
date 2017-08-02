#
#   Plus7 XBMC Plugin
#   Copyright (C) 2014 Andy Botting
#
#
#   This plugin is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This plugin is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this plugin. If not, see <http://www.gnu.org/licenses/>.
#

import comm
import sys
import xbmcgui
import xbmcplugin

from aussieaddonscommon import utils


def make_series_list(url):
    utils.log('Showing series list')
    try:
        params = utils.get_url(url)
        series_list = comm.get_index()
        series_list.sort()

        ok = True
        for s in series_list:
            if params['category'] == 'All TV Shows':
                pass
            else:
                if params['category'] not in s.genre:
                    continue
            url = "%s?series_id=%s" % (sys.argv[0], s.id)
            thumbnail = s.get_thumbnail()

            # Thumbnail that doesn't exist breaks XBMC 12
            listitem = xbmcgui.ListItem(s.get_title())
            if thumbnail:
                listitem = xbmcgui.ListItem(s.get_title(),
                                            iconImage=thumbnail,
                                            thumbnailImage=thumbnail)

            listitem.setInfo('video', {'plot': s.get_description()})

            # add the item to the media list
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                             url=url,
                                             listitem=listitem,
                                             isFolder=True)

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')
    except Exception:
        utils.handle_error("Unable to fetch series listing")
