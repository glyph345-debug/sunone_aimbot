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
from logic.logger import logger

class HotkeysWatcher(threading.Thread):
    def __init__(self):
        super(HotkeysWatcher, self).__init__()
        self.daemon = True
        self.name = 'HotkeysWatcher'
        
        self.app_pause = 0
        self.clss = self.active_classes()

        self.start()
    
    def run(self):
        cfg_reload_prev_state = 0
        
        while True:
            cfg_reload_prev_state = self.process_hotkeys(cfg_reload_prev_state)
                
            # terminate
            exit_vk = Buttons.KEY_CODES.get(cfg.hotkey_exit)
            if exit_vk and (win32api.GetAsyncKeyState(exit_vk) & 0xFF):
                capture.Quit()
                if cfg.show_window:
                    if hasattr(visuals, 'queue'):
                        visuals.queue.put(None)
                os._exit(0)
            
    def process_hotkeys(self, cfg_reload_prev_state):
        pause_vk = Buttons.KEY_CODES.get(cfg.hotkey_pause)
        reload_vk = Buttons.KEY_CODES.get(cfg.hotkey_reload_config)

        self.app_pause = 1 if (pause_vk and (win32api.GetAsyncKeyState(pause_vk) & 0x8000)) else 0
        app_reload_cfg = 1 if (reload_vk and (win32api.GetAsyncKeyState(reload_vk) & 0x8000)) else 0

        if app_reload_cfg and not cfg_reload_prev_state:
            logger.info('[Hotkeys] Reloading config')
            cfg.Read(verbose=True)
            capture.restart()
            mouse.update_settings()
            self.clss = self.active_classes()
            logger.info('[Hotkeys] Config reload applied (capture/mouse/classes)')
            if cfg.show_window == False:
                cv2.destroyAllWindows()

        cfg_reload_prev_state = app_reload_cfg
        return cfg_reload_prev_state

    def active_classes(self) -> List[int]:
        clss = [0.0, 1.0]

        if cfg.hideout_targets:
            clss.extend([5.0, 6.0])

        if not cfg.disable_headshot:
            clss.append(7.0)

        if cfg.third_person:
            clss.append(10.0)

        self.clss = clss
        return clss

hotkeys_watcher = HotkeysWatcher()