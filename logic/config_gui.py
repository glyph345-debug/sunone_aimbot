import threading
import cv2
import numpy as np
import configparser
import os
import time

from logic.config_watcher import cfg
from logic.logger import logger


class ConfigEditor(threading.Thread):
    def __init__(self):
        super(ConfigEditor, self).__init__()
        self.daemon = True
        self.name = 'ConfigEditor'
        
        self.window_name = 'Config Editor'
        self.window = None
        self.running = True
        self.visible = True
        self.minimized = False
        
        self.current_tab = 0
        self.num_tabs = 8
        
        self.tab_names = [
            'Detection Window',
            'Capture Methods',
            'Aim Settings',
            'Hotkeys',
            'Mouse Settings',
            'Shooting',
            'AI Settings',
            'Overlay & Debug'
        ]
        
        self.mouse_pos = (0, 0)
        self.dragging = False
        self.drag_start = None
        self.window_pos = (400, 100)
        self.resizing = False
        self.resize_start = None
        self.resize_corner = None
        
        self.canvas_width = 800
        self.canvas_height = 600
        self.min_width = 600
        self.min_height = 400
        
        self.font_scale = 0.6
        self.font_thickness = 1
        
        self.colors = {
            'bg': (50, 50, 50),
            'text': (255, 255, 255),
            'active': (0, 255, 255),
            'inactive': (100, 100, 100),
            'slider_track': (80, 80, 80),
            'slider_handle': (0, 255, 255),
            'checkbox': (0, 255, 255),
            'input': (70, 70, 70),
            'input_focus': (90, 90, 90),
            'tab_active': (40, 40, 40),
            'tab_inactive': (60, 60, 60),
            'border': (100, 100, 100)
        }
        
        self.ui_elements = []
        self.focused_input = None
        self.input_cursor_pos = 0
        self.input_cursor_visible = True
        self.input_cursor_timer = 0
        
        self.tab_elements = []
        
        self.last_draw_time = 0
        self.needs_redraw = True
        self.mouse_moved = False
        self.key_pressed = False
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        self.mouse_callback_time = 0
        
        self.init_ui_elements()
        self.start()
    
    def init_ui_elements(self):
        self.ui_elements = []
        self.tab_elements = []
        
        y_offset = 60
        row_height = 40
        label_x = 20
        slider_x = 180
        slider_width = 200
        
        self.tab_elements = [[] for _ in range(self.num_tabs)]
        
        self.tab_elements[0] = [
            {'type': 'slider', 'key': 'detection_window_width', 'x': slider_x, 'y': y_offset, 'w': slider_width, 'h': 20,
             'min': 200, 'max': 640, 'value': cfg.detection_window_width, 'label': 'Window Width:', 'label_x': label_x},
            {'type': 'slider', 'key': 'detection_window_height', 'x': slider_x, 'y': y_offset + row_height, 'w': slider_width, 'h': 20,
             'min': 200, 'max': 640, 'value': cfg.detection_window_height, 'label': 'Window Height:', 'label_x': label_x},
            {'type': 'checkbox', 'key': 'circle_capture', 'x': label_x, 'y': y_offset + row_height * 2, 'w': 20, 'h': 20,
             'value': cfg.circle_capture, 'label': 'Circle Capture'}
        ]
        
        y_offset = 60
        self.tab_elements[1] = [
            {'type': 'checkbox', 'key': 'Bettercam_capture', 'x': label_x, 'y': y_offset, 'w': 20, 'h': 20,
             'value': cfg.Bettercam_capture, 'label': 'Bettercam Capture'},
            {'type': 'checkbox', 'key': 'Obs_capture', 'x': label_x, 'y': y_offset + row_height, 'w': 20, 'h': 20,
             'value': cfg.Obs_capture, 'label': 'OBS Capture'},
            {'type': 'checkbox', 'key': 'mss_capture', 'x': label_x, 'y': y_offset + row_height * 2, 'w': 20, 'h': 20,
             'value': cfg.mss_capture, 'label': 'MSS Capture'},
            {'type': 'slider', 'key': 'capture_fps', 'x': slider_x, 'y': y_offset + row_height * 3, 'w': slider_width, 'h': 20,
             'min': 30, 'max': 120, 'value': cfg.capture_fps, 'label': 'Capture FPS:', 'label_x': label_x, 'is_int': True}
        ]
        
        y_offset = 60
        self.tab_elements[2] = [
            {'type': 'slider', 'key': 'body_y_offset', 'x': slider_x, 'y': y_offset, 'w': slider_width, 'h': 20,
             'min': 0.0, 'max': 0.5, 'value': cfg.body_y_offset, 'label': 'Body Y Offset:', 'label_x': label_x},
            {'type': 'checkbox', 'key': 'hideout_targets', 'x': label_x, 'y': y_offset + row_height, 'w': 20, 'h': 20,
             'value': cfg.hideout_targets, 'label': 'Hideout Targets'},
            {'type': 'checkbox', 'key': 'disable_headshot', 'x': label_x, 'y': y_offset + row_height * 2, 'w': 20, 'h': 20,
             'value': cfg.disable_headshot, 'label': 'Disable Headshot'},
            {'type': 'checkbox', 'key': 'disable_prediction', 'x': label_x, 'y': y_offset + row_height * 3, 'w': 20, 'h': 20,
             'value': cfg.disable_prediction, 'label': 'Disable Prediction'},
            {'type': 'slider', 'key': 'prediction_interval', 'x': slider_x, 'y': y_offset + row_height * 4, 'w': slider_width, 'h': 20,
             'min': 0.5, 'max': 5.0, 'value': cfg.prediction_interval, 'label': 'Prediction Interval:', 'label_x': label_x},
            {'type': 'checkbox', 'key': 'third_person', 'x': label_x, 'y': y_offset + row_height * 5, 'w': 20, 'h': 20,
             'value': cfg.third_person, 'label': 'Third Person'}
        ]
        
        y_offset = 60
        input_width = 150
        self.tab_elements[3] = [
            {'type': 'input', 'key': 'hotkey_targeting', 'x': slider_x, 'y': y_offset, 'w': input_width, 'h': 30,
             'value': str(cfg.hotkey_targeting), 'label': 'Targeting Key:', 'label_x': label_x, 'max_len': 20},
            {'type': 'input', 'key': 'hotkey_exit', 'x': slider_x, 'y': y_offset + row_height, 'w': input_width, 'h': 30,
             'value': str(cfg.hotkey_exit), 'label': 'Exit Key:', 'label_x': label_x, 'max_len': 20},
            {'type': 'input', 'key': 'hotkey_pause', 'x': slider_x, 'y': y_offset + row_height * 2, 'w': input_width, 'h': 30,
             'value': str(cfg.hotkey_pause), 'label': 'Pause Key:', 'label_x': label_x, 'max_len': 20},
            {'type': 'input', 'key': 'hotkey_reload_config', 'x': slider_x, 'y': y_offset + row_height * 3, 'w': input_width, 'h': 30,
             'value': str(cfg.hotkey_reload_config), 'label': 'Reload Config Key:', 'label_x': label_x, 'max_len': 20}
        ]
        
        y_offset = 60
        self.tab_elements[4] = [
            {'type': 'input', 'key': 'mouse_dpi', 'x': slider_x, 'y': y_offset, 'w': input_width, 'h': 30,
             'value': str(cfg.mouse_dpi), 'label': 'DPI:', 'label_x': label_x, 'max_len': 10, 'is_int': True},
            {'type': 'slider', 'key': 'mouse_sensitivity', 'x': slider_x, 'y': y_offset + row_height, 'w': slider_width, 'h': 20,
             'min': 0.5, 'max': 10.0, 'value': cfg.mouse_sensitivity, 'label': 'Sensitivity:', 'label_x': label_x},
            {'type': 'slider', 'key': 'mouse_fov_width', 'x': slider_x, 'y': y_offset + row_height * 2, 'w': slider_width, 'h': 20,
             'min': 20, 'max': 200, 'value': cfg.mouse_fov_width, 'label': 'FOV Width:', 'label_x': label_x, 'is_int': True},
            {'type': 'slider', 'key': 'mouse_fov_height', 'x': slider_x, 'y': y_offset + row_height * 3, 'w': slider_width, 'h': 20,
             'min': 20, 'max': 200, 'value': cfg.mouse_fov_height, 'label': 'FOV Height:', 'label_x': label_x, 'is_int': True},
            {'type': 'slider', 'key': 'mouse_min_speed_multiplier', 'x': slider_x, 'y': y_offset + row_height * 4, 'w': slider_width, 'h': 20,
             'min': 0.5, 'max': 3.0, 'value': cfg.mouse_min_speed_multiplier, 'label': 'Min Speed Multiplier:', 'label_x': label_x},
            {'type': 'slider', 'key': 'mouse_max_speed_multiplier', 'x': slider_x, 'y': y_offset + row_height * 5, 'w': slider_width, 'h': 20,
             'min': 0.5, 'max': 3.0, 'value': cfg.mouse_max_speed_multiplier, 'label': 'Max Speed Multiplier:', 'label_x': label_x},
            {'type': 'checkbox', 'key': 'mouse_lock_target', 'x': label_x, 'y': y_offset + row_height * 6, 'w': 20, 'h': 20,
             'value': cfg.mouse_lock_target, 'label': 'Lock Target'},
            {'type': 'checkbox', 'key': 'mouse_auto_aim', 'x': label_x + 150, 'y': y_offset + row_height * 6, 'w': 20, 'h': 20,
             'value': cfg.mouse_auto_aim, 'label': 'Auto Aim'},
            {'type': 'checkbox', 'key': 'mouse_ghub', 'x': label_x, 'y': y_offset + row_height * 7, 'w': 20, 'h': 20,
             'value': cfg.mouse_ghub, 'label': 'G-Hub Mouse'},
            {'type': 'checkbox', 'key': 'mouse_rzr', 'x': label_x + 150, 'y': y_offset + row_height * 7, 'w': 20, 'h': 20,
             'value': cfg.mouse_rzr, 'label': 'Razer Mouse'}
        ]
        
        y_offset = 60
        self.tab_elements[5] = [
            {'type': 'checkbox', 'key': 'auto_shoot', 'x': label_x, 'y': y_offset, 'w': 20, 'h': 20,
             'value': cfg.auto_shoot, 'label': 'Auto Shoot'},
            {'type': 'checkbox', 'key': 'triggerbot', 'x': label_x, 'y': y_offset + row_height, 'w': 20, 'h': 20,
             'value': cfg.triggerbot, 'label': 'Triggerbot'},
            {'type': 'checkbox', 'key': 'force_click', 'x': label_x, 'y': y_offset + row_height * 2, 'w': 20, 'h': 20,
             'value': cfg.force_click, 'label': 'Force Click'},
            {'type': 'slider', 'key': 'bScope_multiplier', 'x': slider_x, 'y': y_offset + row_height * 3, 'w': slider_width, 'h': 20,
             'min': 0.5, 'max': 3.0, 'value': cfg.bScope_multiplier, 'label': 'Scope Multiplier:', 'label_x': label_x}
        ]
        
        y_offset = 60
        self.tab_elements[6] = [
            {'type': 'slider', 'key': 'AI_conf', 'x': slider_x, 'y': y_offset, 'w': slider_width, 'h': 20,
             'min': 0.1, 'max': 0.9, 'value': cfg.AI_conf, 'label': 'AI Confidence:', 'label_x': label_x},
            {'type': 'input', 'key': 'AI_device', 'x': slider_x, 'y': y_offset + row_height, 'w': input_width, 'h': 30,
             'value': str(cfg.AI_device), 'label': 'AI Device:', 'label_x': label_x, 'max_len': 10},
            {'type': 'checkbox', 'key': 'AI_enable_AMD', 'x': label_x, 'y': y_offset + row_height * 2, 'w': 20, 'h': 20,
             'value': cfg.AI_enable_AMD, 'label': 'Enable AMD'},
            {'type': 'checkbox', 'key': 'disable_tracker', 'x': label_x, 'y': y_offset + row_height * 3, 'w': 20, 'h': 20,
             'value': cfg.disable_tracker, 'label': 'Disable Tracker'}
        ]
        
        y_offset = 60
        self.tab_elements[7] = [
            {'type': 'checkbox', 'key': 'show_overlay', 'x': label_x, 'y': y_offset, 'w': 20, 'h': 20,
             'value': cfg.show_overlay, 'label': 'Show Overlay'},
            {'type': 'checkbox', 'key': 'overlay_show_boxes', 'x': label_x, 'y': y_offset + row_height, 'w': 20, 'h': 20,
             'value': cfg.overlay_show_boxes, 'label': 'Overlay Show Boxes'},
            {'type': 'checkbox', 'key': 'overlay_show_borders', 'x': label_x, 'y': y_offset + row_height * 2, 'w': 20, 'h': 20,
             'value': cfg.overlay_show_borders, 'label': 'Overlay Show Borders'},
            {'type': 'checkbox', 'key': 'show_window', 'x': label_x, 'y': y_offset + row_height * 3, 'w': 20, 'h': 20,
             'value': cfg.show_window, 'label': 'Show Window'},
            {'type': 'checkbox', 'key': 'show_boxes', 'x': label_x, 'y': y_offset + row_height * 4, 'w': 20, 'h': 20,
             'value': cfg.show_boxes, 'label': 'Show Boxes'},
            {'type': 'checkbox', 'key': 'show_labels', 'x': label_x, 'y': y_offset + row_height * 5, 'w': 20, 'h': 20,
             'value': cfg.show_labels, 'label': 'Show Labels'},
            {'type': 'checkbox', 'key': 'show_conf', 'x': label_x, 'y': y_offset + row_height * 6, 'w': 20, 'h': 20,
             'value': cfg.show_conf, 'label': 'Show Conf'},
            {'type': 'slider', 'key': 'debug_window_scale_percent', 'x': slider_x, 'y': y_offset + row_height * 7, 'w': slider_width, 'h': 20,
             'min': 50, 'max': 200, 'value': cfg.debug_window_scale_percent, 'label': 'Debug Window Scale %:', 'label_x': label_x, 'is_int': True}
        ]
        
        self.ui_elements = self.tab_elements[self.current_tab]
    
    def run(self):
        try:
            self.create_window()
            self.main_loop()
        except Exception as e:
            logger.error(f'[Config GUI] Error in main loop: {e}')
        finally:
            self.cleanup()
    
    def create_window(self):
        pos_x = getattr(cfg, 'config_gui_pos_x', 400)
        pos_y = getattr(cfg, 'config_gui_pos_y', 100)
        
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, self.canvas_width, self.canvas_height)
        cv2.moveWindow(self.window_name, pos_x, pos_y)
        
        cv2.setMouseCallback(self.window_name, self.mouse_callback)
    
    def main_loop(self):
        target_fps = 30
        frame_time = 1.0 / target_fps
        last_time = time.time()
        last_input_time = time.time()
        
        while self.running:
            current_time = time.time()
            elapsed = current_time - last_time
            
            if elapsed >= frame_time or self.needs_redraw:
                if self.visible and not self.minimized:
                    self.draw()
                
                self.fps_counter += 1
                if current_time - self.fps_start_time >= 1.0:
                    self.current_fps = self.fps_counter
                    self.fps_counter = 0
                    self.fps_start_time = current_time
                
                last_time = current_time
            
            input_elapsed = current_time - last_input_time
            if input_elapsed >= frame_time:
                self.input_cursor_timer += input_elapsed
                if self.input_cursor_timer >= 0.5:
                    self.input_cursor_visible = not self.input_cursor_visible
                    self.input_cursor_timer = 0
                    self.needs_redraw = True
                
                key = cv2.waitKey(1) & 0xFF
                if key == 27:
                    self.toggle_visibility()
                elif self.focused_input is not None and key != 255:
                    self.handle_keyboard(key)
                    self.needs_redraw = True
                
                if self.mouse_moved:
                    self.needs_redraw = True
                    self.mouse_moved = False
                
                last_input_time = current_time
            
            time.sleep(0.001)
    
    def draw(self):
        canvas = np.full((self.canvas_height, self.canvas_width, 3), self.colors['bg'], dtype=np.uint8)
        
        self.draw_tabs(canvas)
        self.draw_ui_elements(canvas)
        self.draw_status_bar(canvas)
        self.draw_fps(canvas)
        
        cv2.imshow(self.window_name, canvas)
        self.needs_redraw = False
    
    def draw_tabs(self, canvas):
        tab_width = self.canvas_width // self.num_tabs
        tab_height = 40
        
        for i, tab_name in enumerate(self.tab_names):
            x1 = i * tab_width
            y1 = 0
            x2 = (i + 1) * tab_width
            y2 = tab_height
            
            if i == self.current_tab:
                color = self.colors['tab_active']
            else:
                color = self.colors['tab_inactive']
            
            cv2.rectangle(canvas, (x1, y1), (x2, y2), color, -1)
            cv2.rectangle(canvas, (x1, y1), (x2, y2), self.colors['border'], 1)
            
            text_x = x1 + 10
            text_y = y1 + 25
            
            text_size = cv2.getTextSize(tab_name, cv2.FONT_HERSHEY_SIMPLEX, self.font_scale, self.font_thickness)[0]
            center_x = x1 + (tab_width - text_size[0]) // 2
            
            cv2.putText(canvas, tab_name, (center_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, self.font_scale, self.colors['text'], self.font_thickness)
        
        cv2.line(canvas, (0, tab_height), (self.canvas_width, tab_height), self.colors['border'], 2)
    
    def draw_ui_elements(self, canvas):
        y_start = 60
        row_height = 45
        
        for i, element in enumerate(self.ui_elements):
            if element['type'] == 'slider':
                self.draw_slider(canvas, element, y_start + i * row_height)
            elif element['type'] == 'checkbox':
                self.draw_checkbox(canvas, element, y_start + i * row_height)
            elif element['type'] == 'input':
                self.draw_input(canvas, element, y_start + i * row_height)
    
    def draw_slider(self, canvas, element, y):
        x = element['x']
        w = element['w']
        h = element['h']
        min_val = element['min']
        max_val = element['max']
        value = element['value']
        label = element['label']
        label_x = element['label_x']
        
        cv2.putText(canvas, label, (label_x, y + 15), cv2.FONT_HERSHEY_SIMPLEX, self.font_scale, self.colors['text'], self.font_thickness)
        
        track_y = y + 20
        
        cv2.rectangle(canvas, (x, track_y), (x + w, track_y + 8), self.colors['slider_track'], -1)
        cv2.rectangle(canvas, (x, track_y), (x + w, track_y + 8), self.colors['border'], 1)
        
        range_val = max_val - min_val
        if range_val > 0:
            ratio = (value - min_val) / range_val
            handle_x = int(x + ratio * w)
            cv2.circle(canvas, (handle_x, track_y + 4), 8, self.colors['slider_handle'], -1)
            cv2.circle(canvas, (handle_x, track_y + 4), 8, self.colors['text'], 1)
        
        if element.get('is_int', False):
            value_text = f'{int(value)}'
        else:
            value_text = f'{value:.2f}'
        
        value_size = cv2.getTextSize(value_text, cv2.FONT_HERSHEY_SIMPLEX, self.font_scale, self.font_thickness)[0]
        cv2.putText(canvas, value_text, (x + w + 10, track_y + 8), cv2.FONT_HERSHEY_SIMPLEX, self.font_scale, self.colors['active'], self.font_thickness)
    
    def draw_checkbox(self, canvas, element, y):
        x = element['x']
        w = element['w']
        h = element['h']
        checked = element['value']
        label = element['label']
        
        if checked:
            cv2.rectangle(canvas, (x, y), (x + w, y + h), self.colors['checkbox'], -1)
            cv2.rectangle(canvas, (x, y), (x + w, y + h), self.colors['text'], 1)
            
            margin = 4
            cv2.line(canvas, (x + margin, y + margin), (x + w - margin, y + h - margin), (255, 255, 255), 2)
            cv2.line(canvas, (x + w - margin, y + margin), (x + margin, y + h - margin), (255, 255, 255), 2)
        else:
            cv2.rectangle(canvas, (x, y), (x + w, y + h), self.colors['inactive'], -1)
            cv2.rectangle(canvas, (x, y), (x + w, y + h), self.colors['text'], 1)
        
        text_x = x + w + 10
        text_y = y + 15
        cv2.putText(canvas, label, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, self.font_scale, self.colors['text'], self.font_thickness)
    
    def draw_input(self, canvas, element, y):
        x = element['x']
        w = element['w']
        h = element['h']
        value = element['value']
        label = element['label']
        label_x = element['label_x']
        is_focused = self.focused_input == element['key']
        
        cv2.putText(canvas, label, (label_x, y + 18), cv2.FONT_HERSHEY_SIMPLEX, self.font_scale, self.colors['text'], self.font_thickness)
        
        input_bg_color = self.colors['input_focus'] if is_focused else self.colors['input']
        cv2.rectangle(canvas, (x, y), (x + w, y + h), input_bg_color, -1)
        cv2.rectangle(canvas, (x, y), (x + w, y + h), self.colors['active'] if is_focused else self.colors['border'], 1)
        
        display_text = value
        if is_focused and self.input_cursor_visible and len(value) > 0:
            display_text = value[:self.input_cursor_pos] + '|' + value[self.input_cursor_pos:]
        
        text_size = cv2.getTextSize(display_text, cv2.FONT_HERSHEY_SIMPLEX, self.font_scale, self.font_thickness)[0]
        
        if text_size[0] > w - 10:
            ratio = (w - 10) / text_size[0]
            char_width = text_size[0] / len(display_text) if display_text else 8
            visible_chars = int((w - 10) / char_width)
            start_pos = max(0, self.input_cursor_pos - visible_chars + 1)
            display_text = value[start_pos:start_pos + visible_chars]
            if is_focused and self.input_cursor_visible:
                cursor_rel_pos = self.input_cursor_pos - start_pos
                if cursor_rel_pos < len(display_text):
                    display_text = display_text[:cursor_rel_pos] + '|' + display_text[cursor_rel_pos:]
                else:
                    display_text = display_text + '|'
        
        if display_text:
            cv2.putText(canvas, display_text, (x + 5, y + 20), cv2.FONT_HERSHEY_SIMPLEX, self.font_scale, self.colors['text'], self.font_thickness)
    
    def draw_status_bar(self, canvas):
        status_y = self.canvas_height - 30
        
        cv2.rectangle(canvas, (0, status_y), (self.canvas_width, self.canvas_height), (30, 30, 30), -1)
        cv2.line(canvas, (0, status_y), (self.canvas_width, status_y), self.colors['border'], 1)
        
        status_text = 'F5: Toggle | ESC: Close | Click tabs to switch | Click and drag sliders to adjust | Click checkboxes/inputs to toggle/edit'
        text_size = cv2.getTextSize(status_text, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
        text_x = (self.canvas_width - text_size[0]) // 2
        text_y = status_y + 20
        cv2.putText(canvas, status_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)
    
    def draw_fps(self, canvas):
        fps_text = f'FPS: {self.current_fps}'
        fps_size = cv2.getTextSize(fps_text, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
        text_x = self.canvas_width - fps_size[0] - 10
        text_y = 30
        
        if self.current_fps < 25:
            color = (0, 0, 255)
        elif self.current_fps < 30:
            color = (0, 255, 255)
        else:
            color = (0, 255, 0)
        
        cv2.putText(canvas, fps_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
    
    def mouse_callback(self, event, x, y, flags, param):
        if not self.running:
            return
        
        self.mouse_pos = (x, y)
        
        if event == cv2.EVENT_LBUTTONDOWN:
            self.mouse_callback_time = time.time()
            self.handle_click(x, y)
            self.needs_redraw = True
        elif event == cv2.EVENT_MOUSEMOVE:
            if time.time() - self.mouse_callback_time > 0.01:
                self.handle_mouse_move(x, y)
                self.mouse_moved = True
                self.mouse_callback_time = time.time()
        elif event == cv2.EVENT_LBUTTONUP:
            self.dragging = False
            self.resizing = False
            self.needs_redraw = True
    
    def handle_click(self, x, y):
        tab_height = 40
        
        if y < tab_height:
            tab_index = x // (self.canvas_width // self.num_tabs)
            if 0 <= tab_index < self.num_tabs:
                self.current_tab = tab_index
                self.ui_elements = self.tab_elements[self.current_tab]
                self.focused_input = None
                return
        
        y_start = 60
        row_height = 45
        
        for element in self.ui_elements:
            if element['type'] == 'slider':
                elem_y = y_start + self.ui_elements.index(element) * row_height
                if (element['x'] <= x <= element['x'] + element['w'] and
                    elem_y <= y <= elem_y + 30):
                    self.update_slider(element, x)
                    return
            elif element['type'] == 'checkbox':
                elem_y = y_start + self.ui_elements.index(element) * row_height
                if (element['x'] <= x <= element['x'] + element['w'] + 150 and
                    elem_y <= y <= elem_y + element['h']):
                    element['value'] = not element['value']
                    self.update_cfg_value(element['key'], element['value'])
                    self.save_config_file()
                    return
            elif element['type'] == 'input':
                elem_y = y_start + self.ui_elements.index(element) * row_height
                if (element['x'] <= x <= element['x'] + element['w'] and
                    elem_y <= y <= elem_y + element['h']):
                    self.focused_input = element['key']
                    self.input_cursor_pos = len(element['value'])
                    
                    char_width = 8
                    self.input_cursor_pos = min(self.input_cursor_pos, (x - element['x'] - 5) // char_width)
                    self.input_cursor_pos = min(self.input_cursor_pos, len(element['value']))
                    return
                else:
                    if self.focused_input == element['key']:
                        self.save_input_value(element)
    
    def handle_mouse_move(self, x, y):
        if self.dragging:
            dx = x - self.drag_start[0]
            dy = y - self.drag_start[1]
            self.window_pos = (self.window_pos[0] + dx, self.window_pos[1] + dy)
            self.drag_start = (x, y)
            cv2.moveWindow(self.window_name, self.window_pos[0], self.window_pos[1])
        elif self.resizing:
            dx = x - self.resize_start[0]
            dy = y - self.resize_start[1]
            new_width = max(self.min_width, self.canvas_width + dx)
            new_height = max(self.min_height, self.canvas_height + dy)
            self.canvas_width = new_width
            self.canvas_height = new_height
            self.resize_start = (x, y)
            cv2.resizeWindow(self.window_name, self.canvas_width, self.canvas_height)
        else:
            tab_height = 40
            
            if y < tab_height:
                tab_index = x // (self.canvas_width // self.num_tabs)
                if 0 <= tab_index < self.num_tabs:
                    if tab_index != self.current_tab:
                        self.current_tab = tab_index
                        self.ui_elements = self.tab_elements[self.current_tab]
    
    def update_slider(self, element, x):
        min_val = element['min']
        max_val = element['max']
        
        ratio = max(0, min(1, (x - element['x']) / element['w']))
        new_value = min_val + ratio * (max_val - min_val)
        
        if element.get('is_int', False):
            new_value = int(round(new_value))
        else:
            new_value = round(new_value, 2)
        
        element['value'] = new_value
        self.update_cfg_value(element['key'], new_value)
        self.save_config_file()
    
    def handle_keyboard(self, key):
        if self.focused_input is None:
            return
        
        updated = False
        for element in self.ui_elements:
            if element['key'] == self.focused_input:
                current_value = element['value']
                max_len = element.get('max_len', 20)
                
                if key == 8:
                    if self.input_cursor_pos > 0:
                        current_value = current_value[:self.input_cursor_pos - 1] + current_value[self.input_cursor_pos:]
                        self.input_cursor_pos -= 1
                        updated = True
                elif key == 127:
                    if self.input_cursor_pos < len(current_value):
                        current_value = current_value[:self.input_cursor_pos] + current_value[self.input_cursor_pos + 1:]
                        updated = True
                elif key == 13:
                    self.save_input_value(element)
                    self.focused_input = None
                    updated = True
                elif key == 27:
                    self.focused_input = None
                    updated = True
                elif 32 <= key <= 126:
                    if len(current_value) < max_len:
                        char = chr(key)
                        current_value = current_value[:self.input_cursor_pos] + char + current_value[self.input_cursor_pos:]
                        self.input_cursor_pos += 1
                        updated = True
                
                element['value'] = current_value
                break
        
        if updated:
            self.needs_redraw = True
    
    def save_input_value(self, element):
        try:
            key = element['key']
            value = element['value']
            
            if element.get('is_int', False):
                value = int(value)
            
            self.update_cfg_value(key, value)
            self.save_config_file()
        except (ValueError, TypeError):
            pass
    
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
                        'prediction_interval', 'third_person']
            hotkey_keys = ['hotkey_targeting', 'hotkey_exit', 'hotkey_pause', 'hotkey_reload_config']
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
                        if key.startswith('show_overlay') or key.startswith('overlay'):
                            config.set('overlay', key, 'True' if val else 'False')
                        else:
                            config.set('Debug window', key, 'True' if val else 'False')
                    else:
                        config.set('Debug window', key, str(val))
            
            with open('config.ini', 'w', encoding='utf-8') as f:
                config.write(f)
            
            logger.info('[Config GUI] Config saved to file')
        except Exception as e:
            logger.error(f'[Config GUI] Error saving config: {e}')
    
    def save_position(self):
        try:
            x, y = self.window_pos
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
    
    def cleanup(self):
        try:
            self.save_position()
            if self.window is not None:
                cv2.destroyWindow(self.window_name)
        except Exception as e:
            logger.error(f'[Config GUI] Error during cleanup: {e}')
    
    def toggle_visibility(self):
        self.visible = not self.visible
        if self.visible:
            cv2.imshow(self.window_name, np.zeros((100, 100, 3), dtype=np.uint8))
            cv2.setMouseCallback(self.window_name, self.mouse_callback)
        else:
            try:
                cv2.destroyWindow(self.window_name)
            except:
                pass


def launch_config_gui():
    """Launch the config GUI in a new thread (callable from hotkeys_watcher)."""
    return ConfigEditor()
