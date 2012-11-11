# This file is a part of search-pinboard.
#
# search-pinboard is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# search-pinboard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with search-pinboard.  If not, see
# <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2012 Red Hat, Inc.
# Author: Ralph Bean <rbean@redhat.com>

# Acknowledgement - This project was based on a fork from fedmsg-notify
# Copyright (C) 2012 Red Hat, Inc.
# Author: Luke Macken <lmacken@redhat.com>


import dbus
import dbus.glib
import dbus.service
import os
import urllib
import webbrowser

from gi.repository import Gio
import gobject

import pinboardutils


config_tool = "gnome-shell-search-pinboard-config"

# Convenience shorthand for declaring dbus interface methods.
# s.b.n. -> search_bus_name
search_bus_name = 'org.gnome.Shell.SearchProvider'
sbn = dict(dbus_interface=search_bus_name)


class SearchPinboardService(dbus.service.Object):
    """ The Pinboard Search Daemon.

    This service is started through DBus activation by calling the
    :meth:`Enable` method, and stopped with :meth:`Disable`.

    """
    bus_name = 'org.gnome.pinboard.search'
    enabled = False

    http_prefix = "https://pinboard.in"

    _icon_cache_dir = os.path.expanduser("~/.cache/search-pinboard/")
    remote_icon = "http://pinboard.in/bluepin.gif"
    local_icon = _icon_cache_dir + "/bluepin.gif"

    _search_cache = {}

    _object_path = '/%s' % bus_name.replace('.', '/')
    __name__ = "SearchPinboardService"

    def __init__(self):
        self.settings = Gio.Settings.new(self.bus_name)
        if not self.settings.get_boolean('enabled'):
            return


        self._initialize_icon_cache()

        self.session_bus = dbus.SessionBus()
        bus_name = dbus.service.BusName(self.bus_name, bus=self.session_bus)
        dbus.service.Object.__init__(self, bus_name, self._object_path)
        self.enabled = True

    @dbus.service.method(in_signature='s', **sbn)
    def ActivateResult(self, search_id):
        webbrowser.open(search_id.split(':__:')[1])

    @dbus.service.method(in_signature='as', out_signature='as', **sbn)
    def GetInitialResultSet(self, terms):
        return self._basic_search(terms)

    @dbus.service.method(in_signature='as', out_signature='aa{sv}', **sbn)
    def GetResultMetas(self, ids):
        return [dict(
            id=id,
            name=id.split(":__:")[0].split('/')[-1],
            gicon=self.local_icon,
        ) for id in ids]

    @dbus.service.method(in_signature='asas', out_signature='as', **sbn)
    def GetSubsearchResultSet(self, previous_results, new_terms):
        return self._basic_search(new_terms)

    def _initialize_icon_cache(self):
        if not os.path.isdir(self._icon_cache_dir):
            os.mkdir(self._icon_cache_dir)

        urllib.urlretrieve(self.remote_icon, self.local_icon)

    def _basic_search(self, terms):
        term = ''.join(terms)

        def __build_rows(username, auth):
            matches = pinboardutils.get_all(username, auth, term)
            rows = [r['description'] + ":__:" + r['link'] for r in matches]
            return rows

        if not term in self._search_cache:
            username, password = auth = pinboardutils.load_auth()

            if not username:
                os.system(config_tool)
                return []

            rows = __build_rows(username, auth)

            self._search_cache[term] = rows

        return self._search_cache[term]


def main():
    service = SearchPinboardService()
    loop = gobject.MainLoop()
    loop.run()

if __name__ == '__main__':
    main()
