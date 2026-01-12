import threading
import PySimpleGUI as sg
import configparser
import os

from logic.config_watcher import cfg
from logic.logger import logger

sg.theme('DarkBlue3')


class ConfigEditor(threading.Thread):
    def __init__(self):
        super(ConfigEditor, self).__init__()
        self.daemon = True
        self.name = 'ConfigEditor'
        
        self.window = None
        self.running = True
        self.visible = True
        
        self.start()
    
    def run(self):
        self.create_window()
        while self.running:
            event, values = self.window.read(timeout=100)
            
            if event == sg.WIN_CLOSED or event == 'Exit':
                self.save_position()
                self.running = False
                break
            
            if event == '-TOGGLE_VISIBILITY-':
                self.visible = not self.visible
                self.window.hide() if not self.visible else self.window.un_hide()
                continue
            
            if event == '-RESET_DEFAULTS-':
                self.reset_to_defaults()
                continue
            
            if event == '-SAVE_CONFIG-':
                self.save_config_file()
                continue
            
            self.handle_value_change(event, values)
            
            if event and event.startswith('slider-') or event.startswith('checkbox-') or event.startswith('input-'):
                self.save_config_file()
        
        if self.window:
            self.window.close()
    
    def create_window(self):
        layout = [
            [sg.TabGroup([[
                sg.Tab('Detection Window', self.create_detection_window_tab()),
                sg.Tab('Capture Methods', self.create_capture_methods_tab()),
                sg.Tab('Aim Settings', self.create_aim_settings_tab()),
                sg.Tab('Hotkeys', self.create_hotkeys_tab()),
                sg.Tab('Mouse Settings', self.create_mouse_settings_tab()),
                sg.Tab('Shooting', self.create_shooting_tab()),
                sg.Tab('AI Settings', self.create_ai_settings_tab()),
                sg.Tab('Overlay & Debug', self.create_overlay_debug_tab()),
            ]], tab_background_color='#2a2a2a', title_color='white', selected_title_color='#4a90d9')],
            [sg.Button('Save Config', key='-SAVE_CONFIG-', button_color=('white', '#2e7d32')),
             sg.Button('Reset Defaults', key='-RESET_DEFAULTS-', button_color=('white', '#c62828')),
             sg.Button('Close', key='Exit', button_color=('white', '#616161'))]
        ]
        
        pos_x = getattr(cfg, 'config_gui_pos_x', 400)
        pos_y = getattr(cfg, 'config_gui_pos_y', 100)
        
        self.window = sg.Window(
            'Aimbot Config Editor',
            layout,
            resizable=True,
            size=(600, 500),
            location=(pos_x, pos_y),
            keep_on_top=True
        )
    
    def create_detection_window_tab(self):
        return [
            [sg.Text('Window Width:', size=(20, 1)), sg.Slider(range=(200, 640), default_value=cfg.detection_window_width, orientation='h', size=(20, 15), key='detection_window_width')],
            [sg.Text('Window Height:', size=(20, 1)), sg.Slider(range=(200, 640), default_value=cfg.detection_window_height, orientation='h', size=(20, 15), key='detection_window_height')],
            [sg.Checkbox('Circle Capture', default=cfg.circle_capture, key='circle_capture')]
        ]
    
    def create_capture_methods_tab(self):
        return [
            [sg.Checkbox('Bettercam Capture', default=cfg.Bettercam_capture, key='Bettercam_capture')],
            [sg.Checkbox('OBS Capture', default=cfg.Obs_capture, key='Obs_capture')],
            [sg.Checkbox('MSS Capture', default=cfg.mss_capture, key='mss_capture')],
            [sg.Text('Capture FPS:', size=(20, 1)), sg.Slider(range=(30, 120), default_value=cfg.capture_fps, orientation='h', size=(20, 15), key='capture_fps')]
        ]
    
    def create_aim_settings_tab(self):
        return [
            [sg.Text('Body Y Offset:', size=(20, 1)), sg.Slider(range=(0.0, 0.5), resolution=0.01, default_value=cfg.body_y_offset, orientation='h', size=(20, 15), key='body_y_offset')],
            [sg.Checkbox('Hideout Targets', default=cfg.hideout_targets, key='hideout_targets')],
            [sg.Checkbox('Disable Headshot', default=cfg.disable_headshot, key='disable_headshot')],
            [sg.Checkbox('Disable Prediction', default=cfg.disable_prediction, key='disable_prediction')],
            [sg.Text('Prediction Interval:', size=(20, 1)), sg.Slider(range=(0.5, 5.0), resolution=0.1, default_value=cfg.prediction_interval, orientation='h', size=(20, 15), key='prediction_interval')],
            [sg.Checkbox('Third Person', default=cfg.third_person, key='third_person')],
            [sg.Text('Own Player Filter Zone:', size=(20, 1)), sg.Slider(range=(0.0, 1.0), resolution=0.01, default_value=cfg.own_player_filter_zone, orientation='h', size=(20, 15), key='own_player_filter_zone')]
        ]
    
    def create_hotkeys_tab(self):
        return [
            [sg.Text('Targeting Key:', size=(20, 1)), sg.InputText(cfg.hotkey_targeting, key='hotkey_targeting', size=(15, 1))],
            [sg.Text('Exit Key:', size=(20, 1)), sg.InputText(cfg.hotkey_exit, key='hotkey_exit', size=(15, 1))],
            [sg.Text('Pause Key:', size=(20, 1)), sg.InputText(cfg.hotkey_pause, key='hotkey_pause', size=(15, 1))],
            [sg.Text('Reload Config Key:', size=(20, 1)), sg.InputText(cfg.hotkey_reload_config, key='hotkey_reload_config', size=(15, 1))],
            [sg.Text('Toggle Filter Key:', size=(20, 1)), sg.InputText(cfg.hotkey_toggle_own_player_filter, key='hotkey_toggle_own_player_filter', size=(15, 1))],
            [sg.Text('Switch Filter Side Key:', size=(20, 1)), sg.InputText(cfg.hotkey_switch_filter_side, key='hotkey_switch_filter_side', size=(15, 1))]
        ]
    
    def create_mouse_settings_tab(self):
        return [
            [sg.Text('DPI:', size=(20, 1)), sg.InputText(str(cfg.mouse_dpi), key='mouse_dpi', size=(15, 1))],
            [sg.Text('Sensitivity:', size=(20, 1)), sg.Slider(range=(0.5, 10.0), resolution=0.1, default_value=cfg.mouse_sensitivity, orientation='h', size=(20, 15), key='mouse_sensitivity')],
            [sg.Text('FOV Width:', size=(20, 1)), sg.Slider(range=(20, 200), default_value=cfg.mouse_fov_width, orientation='h', size=(20, 15), key='mouse_fov_width')],
            [sg.Text('FOV Height:', size=(20, 1)), sg.Slider(range=(20, 200), default_value=cfg.mouse_fov_height, orientation='h', size=(20, 15), key='mouse_fov_height')],
            [sg.Text('Min Speed Multiplier:', size=(20, 1)), sg.Slider(range=(0.5, 3.0), resolution=0.1, default_value=cfg.mouse_min_speed_multiplier, orientation='h', size=(20, 15), key='mouse_min_speed_multiplier')],
            [sg.Text('Max Speed Multiplier:', size=(20, 1)), sg.Slider(range=(0.5, 3.0), resolution=0.1, default_value=cfg.mouse_max_speed_multiplier, orientation='h', size=(20, 15), key='mouse_max_speed_multiplier')],
            [sg.Checkbox('Lock Target', default=cfg.mouse_lock_target, key='mouse_lock_target')],
            [sg.Checkbox('Auto Aim', default=cfg.mouse_auto_aim, key='mouse_auto_aim')],
            [sg.Checkbox('G-Hub Mouse', default=cfg.mouse_ghub, key='mouse_ghub')],
            [sg.Checkbox('Razer Mouse', default=cfg.mouse_rzr, key='mouse_rzr')]
        ]
    
    def create_shooting_tab(self):
        return [
            [sg.Checkbox('Auto Shoot', default=cfg.auto_shoot, key='auto_shoot')],
            [sg.Checkbox('Triggerbot', default=cfg.triggerbot, key='triggerbot')],
            [sg.Checkbox('Force Click', default=cfg.force_click, key='force_click')],
            [sg.Text('Scope Multiplier:', size=(20, 1)), sg.Slider(range=(0.5, 3.0), resolution=0.1, default_value=cfg.bScope_multiplier, orientation='h', size=(20, 15), key='bScope_multiplier')]
        ]
    
    def create_ai_settings_tab(self):
        return [
            [sg.Text('AI Confidence:', size=(20, 1)), sg.Slider(range=(0.1, 0.9), resolution=0.01, default_value=cfg.AI_conf, orientation='h', size=(20, 15), key='AI_conf')],
            [sg.Text('AI Device:', size=(20, 1)), sg.InputText(cfg.AI_device, key='AI_device', size=(15, 1))],
            [sg.Checkbox('Enable AMD', default=cfg.AI_enable_AMD, key='AI_enable_AMD')],
            [sg.Checkbox('Disable Tracker', default=cfg.disable_tracker, key='disable_tracker')]
        ]
    
    def create_overlay_debug_tab(self):
        return [
            [sg.Checkbox('Show Overlay', default=cfg.show_overlay, key='show_overlay')],
            [sg.Checkbox('Overlay Show Boxes', default=cfg.overlay_show_boxes, key='overlay_show_boxes')],
            [sg.Checkbox('Overlay Show Borders', default=cfg.overlay_show_borders, key='overlay_show_borders')],
            [sg.Checkbox('Show Window', default=cfg.show_window, key='show_window')],
            [sg.Checkbox('Show Boxes', default=cfg.show_boxes, key='show_boxes')],
            [sg.Checkbox('Show Labels', default=cfg.show_labels, key='show_labels')],
            [sg.Checkbox('Show Conf', default=cfg.show_conf, key='show_conf')],
            [sg.Text('Debug Window Scale %:', size=(20, 1)), sg.Slider(range=(50, 200), default_value=cfg.debug_window_scale_percent, orientation='h', size=(20, 15), key='debug_window_scale_percent')]
        ]
    
    def handle_value_change(self, event, values):
        try:
            if event.startswith('slider-'):
                key = event.replace('slider-', '')
                value = values[event]
                self.update_cfg_value(key, value)
            elif event.startswith('checkbox-'):
                key = event.replace('checkbox-', '')
                value = values[event]
                self.update_cfg_value(key, value)
            elif event.startswith('input-'):
                key = event.replace('input-', '')
                value = values[event]
                self.update_cfg_value(key, value)
            elif event in values:
                key = event
                value = values[event]
                self.update_cfg_value(key, value)
        except Exception as e:
            logger.error(f'[Config GUI] Error handling value change: {e}')
    
    def update_cfg_value(self, key, value):
        try:
            if hasattr(cfg, key):
                original_value = getattr(cfg, key)
                setattr(cfg, key, value)
                
                if key in ['mouse_dpi', 'mouse_sensitivity', 'mouse_fov_width', 'mouse_fov_height',
                           'mouse_min_speed_multiplier', 'mouse_max_speed_multiplier']:
                    try:
                        from logic.mouse import mouse
                        mouse.update_settings()
                    except:
                        pass
                
                if key in ['detection_window_width', 'detection_window_height', 'capture_fps']:
                    try:
                        from logic.capture import capture
                        capture.restart()
                    except:
                        pass
                        
                logger.info(f'[Config GUI] Updated {key}: {original_value} -> {value}')
        except Exception as e:
            logger.error(f'[Config GUI] Error updating config value: {e}')
    
    def save_config_file(self):
        try:
            config = configparser.ConfigParser()
            config.read('config.ini')
            
            detection_keys = ['detection_window_width', 'detection_window_height', 'circle_capture']
            capture_keys = ['capture_fps', 'Bettercam_capture', 'Obs_capture', 'mss_capture']
            aim_keys = ['body_y_offset', 'hideout_targets', 'disable_headshot', 'disable_prediction',
                        'prediction_interval', 'third_person', 'own_player_filter_zone']
            hotkey_keys = ['hotkey_targeting', 'hotkey_exit', 'hotkey_pause', 'hotkey_reload_config',
                          'hotkey_toggle_own_player_filter', 'hotkey_switch_filter_side']
            mouse_keys = ['mouse_dpi', 'mouse_sensitivity', 'mouse_fov_width', 'mouse_fov_height',
                         'mouse_min_speed_multiplier', 'mouse_max_speed_multiplier',
                         'mouse_lock_target', 'mouse_auto_aim', 'mouse_ghub', 'mouse_rzr']
            shooting_keys = ['auto_shoot', 'triggerbot', 'force_click', 'bScope_multiplier']
            ai_keys = ['AI_conf', 'AI_device', 'AI_enable_AMD', 'disable_tracker']
            overlay_keys = ['show_overlay', 'overlay_show_boxes', 'overlay_show_borders',
                           'show_window', 'show_boxes', 'show_labels', 'show_conf', 'debug_window_scale_percent']
            
            for key in detection_keys:
                if hasattr(cfg, key):
                    config.set('Detection window', key, str(getattr(cfg, key)))
            
            for key in capture_keys:
                if hasattr(cfg, key):
                    config.set('Capture Methods', key, str(getattr(cfg, key)))
            
            for key in aim_keys:
                if hasattr(cfg, key):
                    config.set('Aim', key, str(getattr(cfg, key)))
            
            for key in hotkey_keys:
                if hasattr(cfg, key):
                    config.set('Hotkeys', key, str(getattr(cfg, key)))
            
            for key in mouse_keys:
                if hasattr(cfg, key):
                    val = getattr(cfg, key)
                    if isinstance(val, bool):
                        config.set('Mouse', key, 'True' if val else 'False')
                    else:
                        config.set('Mouse', key, str(val))
            
            for key in shooting_keys:
                if hasattr(cfg, key):
                    val = getattr(cfg, key)
                    if isinstance(val, bool):
                        config.set('Shooting', key, 'True' if val else 'False')
                    else:
                        config.set('Shooting', key, str(val))
            
            for key in ai_keys:
                if hasattr(cfg, key):
                    val = getattr(cfg, key)
                    if isinstance(val, bool):
                        config.set('AI', key, 'True' if val else 'False')
                    else:
                        config.set('AI', key, str(val))
            
            for key in overlay_keys:
                if hasattr(cfg, key):
                    val = getattr(cfg, key)
                    if isinstance(val, bool):
                        config.set('overlay' if key.startswith('show_overlay') or key.startswith('overlay') else 'Debug window', 
                                  key, 'True' if val else 'False')
                    else:
                        config.set('Debug window', key, str(val))
            
            with open('config.ini', 'w', encoding='utf-8') as f:
                config.write(f)
            
            logger.info('[Config GUI] Config saved to file')
        except Exception as e:
            logger.error(f'[Config GUI] Error saving config: {e}')
    
    def save_position(self):
        try:
            if self.window:
                x, y = self.window.current_location()
                config = configparser.ConfigParser()
                config.read('config.ini')
                
                if not config.has_section('Config GUI'):
                    config.add_section('Config GUI')
                
                config.set('Config GUI', 'config_gui_pos_x', str(x))
                config.set('Config GUI', 'config_gui_pos_y', str(y))
                
                with open('config.ini', 'w', encoding='utf-8') as f:
                    config.write(f)
        except Exception as e:
            logger.error(f'[Config GUI] Error saving position: {e}')
    
    def reset_to_defaults(self):
        try:
            defaults = {
                'detection_window_width': 320,
                'detection_window_height': 320,
                'circle_capture': True,
                'capture_fps': 60,
                'Bettercam_capture': False,
                'Obs_capture': False,
                'mss_capture': True,
                'body_y_offset': 0.1,
                'hideout_targets': True,
                'disable_headshot': False,
                'disable_prediction': False,
                'prediction_interval': 2.0,
                'third_person': True,
                'own_player_filter_zone': 0.35,
                'hotkey_targeting': 'RightMouseButton',
                'hotkey_exit': 'F2',
                'hotkey_pause': 'F3',
                'hotkey_reload_config': 'F4',
                'hotkey_toggle_own_player_filter': 'Comma',
                'hotkey_switch_filter_side': 'Period',
                'mouse_dpi': 1100,
                'mouse_sensitivity': 3.0,
                'mouse_fov_width': 40,
                'mouse_fov_height': 40,
                'mouse_min_speed_multiplier': 1.0,
                'mouse_max_speed_multiplier': 1.5,
                'mouse_lock_target': False,
                'mouse_auto_aim': False,
                'mouse_ghub': False,
                'mouse_rzr': False,
                'auto_shoot': False,
                'triggerbot': False,
                'force_click': False,
                'bScope_multiplier': 1.0,
                'AI_conf': 0.2,
                'AI_device': '0',
                'AI_enable_AMD': False,
                'disable_tracker': False,
                'show_overlay': False,
                'overlay_show_boxes': False,
                'overlay_show_borders': True,
                'show_window': False,
                'show_boxes': True,
                'show_labels': False,
                'show_conf': True,
                'debug_window_scale_percent': 100
            }
            
            for key, value in defaults.items():
                if hasattr(cfg, key):
                    setattr(cfg, key, value)
            
            self.refresh_window()
            self.save_config_file()
            logger.info('[Config GUI] Reset to defaults')
        except Exception as e:
            logger.error(f'[Config GUI] Error resetting defaults: {e}')
    
    def refresh_window(self):
        self.window.close()
        self.create_window()
    
    def toggle_visibility(self):
        self.visible = not self.visible
        if self.visible:
            self.window.un_hide()
        else:
            self.window.hide()


config_gui = ConfigEditor()
