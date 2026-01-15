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

config_gui_thread = None
config_gui_enabled = False
_config_gui_instance = None

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
        toggle_config_editor_prev_state = 0
        
        while True:
            cfg_reload_prev_state, toggle_config_editor_prev_state = self.process_hotkeys(
                cfg_reload_prev_state,
                toggle_config_editor_prev_state
            )
                
            # terminate
            exit_vk = Buttons.KEY_CODES.get(cfg.hotkey_exit)
            if exit_vk and (win32api.GetAsyncKeyState(exit_vk) & 0xFF):
                capture.Quit()
                if cfg.show_window:
                    if hasattr(visuals, 'queue'):
                        visuals.queue.put(None)
                os._exit(0)
            
    def process_hotkeys(self, cfg_reload_prev_state, toggle_config_editor_prev_state):
        pause_vk = Buttons.KEY_CODES.get(cfg.hotkey_pause)
        reload_vk = Buttons.KEY_CODES.get(cfg.hotkey_reload_config)
        toggle_vk = Buttons.KEY_CODES.get(cfg.hotkey_toggle_config_editor, Buttons.KEY_CODES.get('F1', 112))

        self.app_pause = 1 if (pause_vk and (win32api.GetAsyncKeyState(pause_vk) & 0x8000)) else 0
        app_reload_cfg = 1 if (reload_vk and (win32api.GetAsyncKeyState(reload_vk) & 0x8000)) else 0
        app_toggle_config_editor = 1 if (toggle_vk and (win32api.GetAsyncKeyState(toggle_vk) & 0x8000)) else 0

        if app_reload_cfg and not cfg_reload_prev_state:
            logger.info('[Hotkeys] Reloading config')
            cfg.Read(verbose=True)
            capture.restart()
            mouse.update_settings()
            self.clss = self.active_classes()
            logger.info('[Hotkeys] Config reload applied (capture/mouse/classes)')
            if cfg.show_window == False:
                cv2.destroyAllWindows()

        if app_toggle_config_editor and not toggle_config_editor_prev_state:
            try:
                global config_gui_thread, config_gui_enabled, _config_gui_instance

                if not config_gui_enabled:
                    # First F1 press - launch the GUI in a new thread
                    from logic.config_gui import launch_config_gui
                    _config_gui_instance = launch_config_gui()
                    config_gui_thread = _config_gui_instance
                    config_gui_enabled = True
                    logger.info('[Hotkeys] Launched Config GUI')
                else:
                    # Subsequent F1 presses - toggle visibility
                    if _config_gui_instance is not None and hasattr(_config_gui_instance, 'toggle_visibility'):
                        _config_gui_instance.toggle_visibility()
            except (ImportError, AttributeError) as e:
                logger.error(f'[Hotkeys] Error toggling config GUI: {e}')

        cfg_reload_prev_state = app_reload_cfg
        toggle_config_editor_prev_state = app_toggle_config_editor
        return cfg_reload_prev_state, toggle_config_editor_prev_state

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