import threading
from typing import List
import cv2
import win32api
import os

from logic.config_watcher import cfg
from logic.buttons import Buttons
from logic.capture import capture
from logic.mouse import mouse
from logic.visual import visuals
from logic.shooting import shooting

class HotkeysWatcher(threading.Thread):
    def __init__(self):
        super(HotkeysWatcher, self).__init__()
        self.daemon = True
        self.name = 'HotkeysWatcher'
        
        self.app_pause = 0
        self.clss = self.active_classes()
        self.filter_own_player_enabled = False
        self.filter_own_player_side = "left"

        self.start()
    
    def run(self):
        cfg_reload_prev_state = 0
        filter_own_player_prev_state = 0
        switch_filter_side_prev_state = 0
        while True:
            cfg_reload_prev_state, filter_own_player_prev_state, switch_filter_side_prev_state = self.process_hotkeys(cfg_reload_prev_state, filter_own_player_prev_state, switch_filter_side_prev_state)
                
            # terminate
            if win32api.GetAsyncKeyState(Buttons.KEY_CODES.get(cfg.hotkey_exit)) & 0xFF:
                capture.Quit()
                if cfg.show_window:
                    visuals.queue.put(None)
                os._exit(0)
            
    def process_hotkeys(self, cfg_reload_prev_state, filter_own_player_prev_state, switch_filter_side_prev_state):
        self.app_pause = win32api.GetKeyState(Buttons.KEY_CODES[cfg.hotkey_pause])
        app_reload_cfg = win32api.GetKeyState(Buttons.KEY_CODES[cfg.hotkey_reload_config])
        app_filter_own_player = win32api.GetKeyState(Buttons.KEY_CODES[cfg.hotkey_toggle_own_player_filter])
        app_switch_filter_side = win32api.GetKeyState(Buttons.KEY_CODES[cfg.hotkey_switch_filter_side])

        if app_filter_own_player != filter_own_player_prev_state:
            if app_filter_own_player in (1, 0):
                if not self.filter_own_player_enabled:
                    self.filter_own_player_enabled = True
                    self.filter_own_player_side = "left"
                else:
                    self.filter_own_player_enabled = False
        
        if app_switch_filter_side != switch_filter_side_prev_state:
            if app_switch_filter_side in (1, 0):
                self.filter_own_player_side = "right" if self.filter_own_player_side == "left" else "left"
        
        if app_reload_cfg != cfg_reload_prev_state:
            if app_reload_cfg in (1, 0):
                cfg.Read(verbose=True)
                capture.restart()
                mouse.update_settings()
                self.clss = self.active_classes()
                self.filter_own_player_enabled = False
                self.filter_own_player_side = "left"
                if cfg.show_window == False:
                    cv2.destroyAllWindows()
                    
        cfg_reload_prev_state = app_reload_cfg
        filter_own_player_prev_state = app_filter_own_player
        switch_filter_side_prev_state = app_switch_filter_side
        return cfg_reload_prev_state, filter_own_player_prev_state, switch_filter_side_prev_state

    def active_classes(self) -> List[int]:
        clss = [0.0, 1.0]
        
        if cfg.hideout_targets:
            clss.extend([5.0, 6.0])

        if not cfg.disable_headshot:
            clss.append(7.0)
            
        if cfg.third_person:
            clss.append(10.0)
        
        self.clss = clss
    
hotkeys_watcher = HotkeysWatcher()