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
import ctypes
import wx
import globalVars

addonHandler.initTranslation()

SEND_KEY_INTERVAL = 60  # Interval in seconds

# Key codes for Windows key and D key
VK_LWIN = 0x5B
VK_D = 0x44

SendInput = ctypes.windll.user32.SendInput

# Define necessary structures
PUL = ctypes.POINTER(ctypes.c_ulong)

class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

# Functions to press and release a key
def press_key(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(hexKeyCode, 0, 0, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def release_key(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_.ki = KeyBdInput(hexKeyCode, 0, 2, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

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
        press_key(VK_LWIN)
        press_key(VK_D)
        time.sleep(0.1)
        release_key(VK_D)
        release_key(VK_LWIN)
        wx.CallAfter(ui.message, "Windows + D keys sent.")

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
