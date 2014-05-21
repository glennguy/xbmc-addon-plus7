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

import sys
import traceback
import re
import htmlentitydefs
import cgi
import unicodedata
import urllib
import textwrap
import config
import xbmc

pattern = re.compile("&(\w+?);")

def descape_entity(m, defs=htmlentitydefs.entitydefs):
    # callback: translate one entity to its ISO Latin value
    try:
        return defs[m.group(1)]
    except KeyError:
        return m.group(0) # use as is


def descape(string):
    # Fix the hack back from parsing with BeautifulSoup
    string = string.replace('&#38;', '&amp;')

    return pattern.sub(descape_entity, string)


def get_url(s):
    dict = {}
    pairs = s.lstrip("?").split("&")
    for pair in pairs:
        if len(pair) < 3: continue
        kv = pair.split("=",1)
        k = kv[0]
        v = urllib.unquote_plus(kv[1])
        dict[k] = v
    return dict


def make_url(d):
    pairs = []
    for k,v in d.iteritems():
        k = urllib.quote_plus(k)
        # Values can possibly be - UTF-8 as an ASCII str, ASCII as an ASCII str, or unicode. Want clean ASCII for URL.
        if not isinstance(v, unicode):
            v = str(v)
            v = v.decode("utf-8")
        v = unicodedata.normalize('NFC', v).encode('ascii','ignore')
        v = urllib.quote_plus(v)
        pairs.append("%s=%s" % (k,v))
    return "&".join(pairs)


def log(s):
    print "[%s v%s] %s" % (config.NAME, config.VERSION, s)


def log_error(message=None):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    if message:
        exc_value = message
    print "[%s v%s] ERROR: %s (%d) - %s" % (config.NAME, config.VERSION, exc_traceback.tb_frame.f_code.co_name, exc_traceback.tb_lineno, exc_value)
    print traceback.print_exc()


def dialog_error(msg):
    # Generate a list of lines for use in XBMC dialog
    content = []
    exc_type, exc_value, exc_traceback = sys.exc_info()
    content.append("%s v%s Error" % (config.NAME, config.VERSION))
    content.append("%s (%d) - %s" % (exc_traceback.tb_frame.f_code.co_name, exc_traceback.tb_lineno, msg))
    content.append(str(exc_value))
    return content


def dialog_message(msg, title=None):
    if not title:
        title = "%s v%s" % (config.NAME, config.VERSION)
    # Add title to the first pos of the textwrap list
    content = textwrap.wrap(msg, 60)
    content.insert(0, title)
    return content


def get_platform():
    if xbmc.getCondVisibility('system.platform.osx'):
        return "OSX"
    elif xbmc.getCondVisibility('system.platform.atv2'):
        return "ATV2"
    elif xbmc.getCondVisibility('system.platform.ios'):
        return "iOS"
    elif xbmc.getCondVisibility('system.platform.windows'):
        return "Windows"
    elif xbmc.getCondVisibility('system.platform.linux'):
        return "Linux"
    elif xbmc.getCondVisibility('system.platform.android'):
        return "Android"
    return "Unknown"


def get_xbmc_version():
    # 12.3 Git:Unknown
    version = xbmc.getInfoLabel('system.buildversion')
    version_number = version.split(' ')[0]
    return version_number


def does_not_support_https_hls():
    """ HTTPS HLS support is only found in XBMC v13, but not if the platform
        is iOS or Android. Return True if we are on one of these platforms
    """
    version = get_xbmc_version()
    platform = get_platform()

    log("Found XBMC version/platform: %s/%s" % (platform, version))

    major_ver = version.split('.')[0]
    if int(major_ver) < 13:
        return True

    if platform in ['ATV2', 'iOS', 'Android']:
        return True

    return False
