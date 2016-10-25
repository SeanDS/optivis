# -*- coding: utf-8 -*-

"""Implements a simple listen/notify schema"""

from __future__ import unicode_literals, division

import abc
import weakref

class Notifier(object):
    """Keeps a list of :class:`~.Listener` instances that are to be informed of
    certain events"""

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        """Instantiate a Notifier"""

        # create listeners dict, using weak references to prevent references
        # to deleted objects being kept
        self.listeners = weakref.WeakKeyDictionary()

    def add_listener(self, listener):
        """Adds a listener to the list (and self to lister's list)"""

        # add listener to dict
        self.register_listener(listener)

        # add this notifier to the listener
        listener.register_notifier(self)

    def rem_listener(self, listener):
        """Removes a listener from the list (and self from lister's list)"""

        # delete listener reference from dict
        self.unregister_listener(listener)

        # delete this notifier from the listener
        listener.unregister_notifier(self)

    def register_listener(self, listener):
        """Registers the specified :class:`~.Listener` with this notifier

        :param listener: :class:`~.Listener` to register
        """

        # add to dict
        self.listeners[listener] = True

    def unregister_listener(self, listener):
        """Unregisters the specified :class:`~.Listener` with this notifier

        :param listener: :class:`~.Listener` to unregister
        """

        # remove from dict
        del(self.listeners[listener])

    def send_notify(self, message):
        """Sends the specified message to all listeners

        :param message: message to send"""

        # call notifier method on all listeners
        map(lambda x: x.receive_notify(self, message), self.listeners)

class Listener(object):
    """Listens for notifications from :class:`~.Notifier` objects"""

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        """Instantiate a Notifier"""

        # create notifiers dict, using weak references to prevent references
        # to deleted objects being kept
        self.notifiers = weakref.WeakKeyDictionary()

    def add_notifier(self, notifier):
        """Adds a notifier to the list (and self to notifier's list)"""

        # add notifier to dict
        self.register_notifier(notifier)

        # add this listener to the notifier
        notifier.register_listener(self)

    def rem_notifier(self, notifier):
        """Removes a notifier from the list (and self from notifier's list)"""

        # delete notifier reference from dict
        self.unregister_notifier(notifier)

        # delete this listener from the notifier
        notifier.unregister_listener(self)

    def register_notifier(self, notifier):
        """Registers the specified :class:`~.Notifier` with this listener

        :param notifier: :class:`~.Notifier` to register
        """

        # add to dict
        self.notifiers[notifier] = True

    def unregister_notifier(self, notifier):
        """Unregisters the specified :class:`~.Notifier` with this listener

        :param notifier: :class:`~.Notifier` to unregister
        """

        # remove from dict
        del(self.notifiers[notifier])

    @abc.abstractmethod
    def receive_notify(self, source, message):
        """Receives a message from a :class:`~.Notifier:

        Implementing classes should override this method."""

        logging.getLogger("notify").debug("Listener received notification \
from %s: %s", source, message)
