"""
keyboard.py : what to do when someone wants to communicate via keys
"""
import AppKit
import Quartz
from pynput._util.darwin import ListenerMixin
from pynput.keyboard import _base

class MediaKeyListener(ListenerMixin, _base.Listener):
    """
    MediaKeyListener: object for registering event handlers for Mac OSX media keys
    """
    keys_of_interest = {
        16: 'play_pause',
        19: 'next_track',
        20: 'prev_track',
        7: 'mute',
        1: 'volume_down',
        0: 'volume_up',
    }

    # When you call either CGEventTapCreate or CGEventTapCreateForPSN to
    # register an event tap, you supply a bit mask that identifies the set
    # of events to be observed. You specify each event using one of the event
    # type constants listed in CGEventType. To form the bit mask, use the
    # CGEventMaskBit macro to convert each constant into an event mask and
    # then OR the individual masks together.
    _EVENTS = (Quartz.CGEventMaskBit(AppKit.NSEventTypeSystemDefined))

    def __init__(self, *args, **kwargs):
        super(MediaKeyListener, self).__init__(*args, **kwargs)
        self._intercept = self._options.get(
            'intercept',
            None)
        self._handlers = {}

    def _handle(self, dummy_proxy, event_type, event, dummy_refcon):
        """
        _handle: handle Quartz events

        decode the event given to us by looking at the data1 field of the event
        run the registered handler (if any) based on the value of the key that was pressed
        """
        ns_event = AppKit.NSEvent.eventWithCGEvent_(event)
        if ns_event.subtype() != 8:
            return event
        data = ns_event.data1()
        code = (data & 0xFFFF0000) >> 16
        state = (data & 0xFF00) >> 8
        try:
            if state == AppKit.NSKeyDown and code in self.keys_of_interest:
                if self.keys_of_interest[code] in self._handlers:
                    self._handlers[self.keys_of_interest[code]]()
        except Exception as err:
            print(err)
        return

    def on(self, event_name, func):
        """
        on: register an event handler for a given button
        """
        self._handlers[event_name] = func
