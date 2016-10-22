# -*- coding: utf-8 -*-

"""Implements a simple listen/notify schema"""

from __future__ import unicode_literals, division

import weakref

class Notifier(object):
    """A notifier keeps a list of Listener instances that are to be informed of certain events.

       instance attributes:
        listeners       - a list of Listener instances
    """

    def __init__(self):
        self.listeners = weakref.WeakKeyDictionary()

    def add_listener(self, listener):
        """add a listener to the list (and self to listers' list)"""

        self.listeners[listener] = True
        listener.notifiers[self] = True

    def rem_listener(self, listener):
        """remove a listener from the list (and self from listers' list)"""

        del self.listeners[listener]
        del listener.notifiers[self]

    def send_notify(self, message):
        """send a message to all listeners"""
        for dest in self.listeners:
            dest.receive_notify(self, message)

class Listener(object):
    """A listener is notified by one or more Notifiers.

       instance attributes:
        notifiers           - a list of Notifier objects
    """

    def __init__(self):
        self.notifiers = weakref.WeakKeyDictionary();

    def add_notifier(self, notifier):
        """add a notifier to the list (and self to notifiers' list)"""
        self.notifiers[notifier] = True
        notifier.listeners[self] = True

    def rem_notifier(self, notifier):
        """remove a notifier from the list (and self from notifiers' list)"""
        del self.notifiers[notifier]
        del notifier.listeners[self]

    def receive_notify(self, source, message):
        """receive a message from a notifier. Implementing classes should override this."""
        print self,"receive_notify",source,message
