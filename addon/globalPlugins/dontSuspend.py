# -*- coding: utf-8 -*-
# Addon for NVDA that sends Windows + D every 60 seconds
# Copyright (C) 2024 Jesús Pavón Abián <galorasd@gmail.com>
# This file is covered by the GNU General Public License.

import globalPluginHandler
import scriptHandler
from threading import Thread, Event
import ui
import addonHandler
import time
import wx
import globalVars
import inputCore
import keyboardHandler

addonHandler.initTranslation()

SEND_KEY_INTERVAL = 60  # Interval in seconds

class SendKeysThread(Thread):
    def __init__(self):
        super(SendKeysThread, self).__init__()
        self.stop_event = Event()
        self.daemon = True

    def run(self):
        while not self.stop_event.is_set():
            self.send_keys()
            time.sleep(SEND_KEY_INTERVAL)

    def send_keys(self):
        inputCore.manager.emulateGesture(keyboardHandler.KeyboardInputGesture.fromName("windows+d"))

    def stop(self):
        self.stop_event.set()

# Decorator to disable in secure mode
def disableInSecureMode(decoratedCls):
    if globalVars.appArgs.secure:
        return globalPluginHandler.GlobalPlugin
    return decoratedCls

@disableInSecureMode
class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    def __init__(self):
        super(GlobalPlugin, self).__init__()
        self.send_keys_thread = None

    def terminate(self):
        if self.send_keys_thread and self.send_keys_thread.is_alive():
            self.send_keys_thread.stop()
            self.send_keys_thread.join()

    @scriptHandler.script(description=_("Toggles sending Windows + D keys every 60 seconds"), gesture=None, category=_("Don't suspend"))
    def script_toggleSendKeys(self, gesture):
        if self.send_keys_thread and self.send_keys_thread.is_alive():
            self.send_keys_thread.stop()
            self.send_keys_thread.join()
            self.send_keys_thread = None
            ui.message("Function deactivated.")
        else:
            self.send_keys_thread = SendKeysThread()
            self.send_keys_thread.start()
            ui.message("Function activated.")
