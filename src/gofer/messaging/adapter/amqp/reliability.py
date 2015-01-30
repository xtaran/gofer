# Copyright (c) 2013 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public
# License as published by the Free Software Foundation; either version
# 2 of the License (GPLv2) or (at your option) any later version.
# There is NO WARRANTY for this software, express or implied,
# including the implied warranties of MERCHANTABILITY,
# NON-INFRINGEMENT, or FITNESS FOR A PARTICULAR PURPOSE. You should
# have received a copy of GPLv2 along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
# Jeff Ortel (jortel@redhat.com)

from time import sleep

from gofer.messaging.adapter.amqp.connection import Connection, CONNECTION_EXCEPTIONS


def reliable(fn):
    def _fn(thing, *args, **kwargs):
        while True:
            try:
                return fn(thing, *args, **kwargs)
            except CONNECTION_EXCEPTIONS:
                sleep(3)
                thing.close()
                thing.connection.close()
                thing.open()
    return _fn


def endpoint(fn):
    def _fn(url):
        _endpoint = Endpoint(url)
        _endpoint.open()
        try:
            return fn(_endpoint)
        finally:
            _endpoint.close()
    return _fn


class Endpoint(object):

    def __init__(self, url):
        self.url = url
        self.connection = Connection(url)
        self.channel = None

    def open(self):
        self.connection.open()
        self.channel = self.connection.channel()

    def close(self):
        try:
            self.channel.close()
        except Exception:
            pass