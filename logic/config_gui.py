import threading
import cv2
import numpy as np
import configparser
import os
import time
import win32api

from logic.config_watcher import cfg, cfg_file_lock
from logic.buttons import Buttons
from logic.logger import logger


class ConfigEditor(threading.Thread):
    def __init__(self):
        super(ConfigEditor, self).__init__()
        self.daemon = True
        self.name = 'ConfigEditor'
        
        self.window_name = 'Modern Config Editor'
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
        
        # Modern canvas size
        self.canvas_width = 1000
        self.canvas_height = 700
        self.min_width = 900
        self.min_height = 600
        
        # Modern font settings
        self.font_scale = 0.6
        self.font_thickness = 1
        
        # Modern dark grey/purple color scheme (OpenCV BGR tuples)
        self.colors = {
            'bg_start': (26, 26, 26),        # #1a1a1a
            'bg_end': (26, 26, 26),
            'text': (224, 224, 224),         # #e0e0e0
            'text_shadow': (0, 0, 0),

            'button_normal': (74, 74, 74),   # #4a4a4a
            'button_hover': (90, 90, 90),
            'button_active': (255, 51, 153), # #9933ff in BGR
            'button_text': (255, 255, 255),

            'slider_track': (51, 51, 51),    # #333333
            'slider_handle': (255, 255, 0),  # #00ffff in BGR

            'tab_active': (255, 51, 153),    # #9933ff in BGR
            'tab_inactive': (74, 74, 74),

            'input_bg': (42, 42, 42),        # #2a2a2a
            'input_border': (74, 74, 74),

            'checkbox_active': (255, 51, 153),
            'checkbox_inactive': (74, 74, 74),

            'border': (68, 68, 68),
            'shadow': (0, 0, 0)
        }
        
        # Physical buttons data
        self.buttons = []
        self.button_states = {}  # Track button hover/pressed states
        
        self.ui_elements = []
        self.focused_input = None
        self.input_cursor_pos = 0
        self.input_cursor_visible = True
        self.input_cursor_timer = 0
        
        # Slider dragging state
        self.dragging_slider = None
        self.dragging_slider_element = None
        
        self.tab_elements = []
        self.tab_rects = []
        self.tab_bar_height = 45
        
        self.last_draw_time = 0
        self.needs_redraw = True
        self.mouse_moved = False
        self.key_pressed = False
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        self.mouse_callback_time = 0
        
        self.init_ui_elements()
        self.create_physical_buttons()
        self.start()
    
    def create_physical_buttons(self):
        """Create physical buttons for the GUI"""
        button_width = 120
        button_height = 35
        spacing = 10
        start_x = self.canvas_width - (button_width * 4 + spacing * 3) - 20
        start_y = 10
        
        self.buttons = [
            {'id': 'close_gui', 'text': 'Close GUI', 'x': start_x, 'y': start_y, 'w': button_width, 'h': button_height},
            {'id': 'exit_program', 'text': 'Exit', 'x': start_x + (button_width + spacing), 'y': start_y, 'w': button_width, 'h': button_height},
            {'id': 'reload_config', 'text': 'Reload', 'x': start_x + (button_width + spacing) * 2, 'y': start_y, 'w': button_width, 'h': button_height},
            {'id': 'save_config', 'text': 'Save', 'x': start_x + (button_width + spacing) * 3, 'y': start_y, 'w': button_width, 'h': button_height}
        ]
        
        # Initialize button states
        for button in self.buttons:
            self.button_states[button['id']] = {'hovered': False, 'pressed': False}
    
    def init_ui_elements(self):
        self.ui_elements = []
        self.tab_elements = []

        # Layout is relative to the content area under the tab bar.
        y_offset = 0
        row_height = 50
        label_x = 30
        slider_x = 240
        slider_width = 280
        input_width = 180

        self.tab_elements = [[] for _ in range(self.num_tabs)]

        self.tab_elements[0] = [
            {'type': 'slider', 'key': 'detection_window_width', 'x': slider_x, 'y': y_offset + row_height * 0, 'w': slider_width, 'h': 20,
             'min': 200, 'max': 1920, 'value': cfg.detection_window_width, 'label': 'Window Width:', 'label_x': label_x, 'is_int': True, 'increment': 10},
            {'type': 'slider', 'key': 'detection_window_height', 'x': slider_x, 'y': y_offset + row_height * 1, 'w': slider_width, 'h': 20,
             'min': 200, 'max': 1080, 'value': cfg.detection_window_height, 'label': 'Window Height:', 'label_x': label_x, 'is_int': True, 'increment': 10},
            {'type': 'checkbox', 'key': 'circle_capture', 'x': label_x, 'y': y_offset + row_height * 2, 'w': 20, 'h': 20,
             'value': cfg.circle_capture, 'label': 'Circle Capture'}
        ]

        self.tab_elements[1] = [
            {'type': 'checkbox', 'key': 'Bettercam_capture', 'x': label_x, 'y': y_offset + row_height * 0, 'w': 20, 'h': 20,
             'value': cfg.Bettercam_capture, 'label': 'Bettercam Capture'},
            {'type': 'checkbox', 'key': 'Obs_capture', 'x': label_x, 'y': y_offset + row_height * 1, 'w': 20, 'h': 20,
             'value': cfg.Obs_capture, 'label': 'OBS Capture'},
            {'type': 'checkbox', 'key': 'mss_capture', 'x': label_x, 'y': y_offset + row_height * 2, 'w': 20, 'h': 20,
             'value': cfg.mss_capture, 'label': 'MSS Capture'},
            {'type': 'slider', 'key': 'capture_fps', 'x': slider_x, 'y': y_offset + row_height * 3, 'w': slider_width, 'h': 20,
             'min': 30, 'max': 120, 'value': cfg.capture_fps, 'label': 'Capture FPS:', 'label_x': label_x, 'is_int': True, 'increment': 10}
        ]

        self.tab_elements[2] = [
            {'type': 'slider', 'key': 'body_y_offset', 'x': slider_x, 'y': y_offset + row_height * 0, 'w': slider_width, 'h': 20,
             'min': 0.0, 'max': 0.5, 'value': cfg.body_y_offset, 'label': 'Body Y Offset:', 'label_x': label_x, 'increment': 0.01},
            {'type': 'checkbox', 'key': 'hideout_targets', 'x': label_x, 'y': y_offset + row_height * 1, 'w': 20, 'h': 20,
             'value': cfg.hideout_targets, 'label': 'Hideout Targets'},
            {'type': 'checkbox', 'key': 'disable_headshot', 'x': label_x, 'y': y_offset + row_height * 2, 'w': 20, 'h': 20,
             'value': cfg.disable_headshot, 'label': 'Disable Headshot'},
            {'type': 'checkbox', 'key': 'disable_prediction', 'x': label_x, 'y': y_offset + row_height * 3, 'w': 20, 'h': 20,
             'value': cfg.disable_prediction, 'label': 'Disable Prediction'},
            {'type': 'slider', 'key': 'prediction_interval', 'x': slider_x, 'y': y_offset + row_height * 4, 'w': slider_width, 'h': 20,
             'min': 0.5, 'max': 5.0, 'value': cfg.prediction_interval, 'label': 'Prediction Interval:', 'label_x': label_x, 'increment': 0.1},
            {'type': 'checkbox', 'key': 'third_person', 'x': label_x, 'y': y_offset + row_height * 5, 'w': 20, 'h': 20,
             'value': cfg.third_person, 'label': 'Third Person'}
        ]

        self.tab_elements[3] = [
            {'type': 'input', 'key': 'hotkey_targeting', 'x': slider_x, 'y': y_offset + row_height * 0, 'w': input_width, 'h': 35,
             'value': str(cfg.hotkey_targeting), 'label': 'Targeting Key:', 'label_x': label_x, 'max_len': 20},
            {'type': 'input', 'key': 'hotkey_exit', 'x': slider_x, 'y': y_offset + row_height * 1, 'w': input_width, 'h': 35,
             'value': str(cfg.hotkey_exit), 'label': 'Exit Key:', 'label_x': label_x, 'max_len': 20},
            {'type': 'input', 'key': 'hotkey_pause', 'x': slider_x, 'y': y_offset + row_height * 2, 'w': input_width, 'h': 35,
             'value': str(cfg.hotkey_pause), 'label': 'Pause Key:', 'label_x': label_x, 'max_len': 20},
            {'type': 'input', 'key': 'hotkey_reload_config', 'x': slider_x, 'y': y_offset + row_height * 3, 'w': input_width, 'h': 35,
             'value': str(cfg.hotkey_reload_config), 'label': 'Reload Config Key:', 'label_x': label_x, 'max_len': 20}
        ]

        self.tab_elements[4] = [
            {'type': 'input', 'key': 'mouse_dpi', 'x': slider_x, 'y': y_offset + row_height * 0, 'w': input_width, 'h': 35,
             'value': str(cfg.mouse_dpi), 'label': 'DPI:', 'label_x': label_x, 'max_len': 10, 'is_int': True},
            {'type': 'slider', 'key': 'mouse_sensitivity', 'x': slider_x, 'y': y_offset + row_height * 1, 'w': slider_width, 'h': 20,
             'min': 0.5, 'max': 10.0, 'value': cfg.mouse_sensitivity, 'label': 'Sensitivity:', 'label_x': label_x, 'increment': 0.1},
            {'type': 'slider', 'key': 'mouse_fov_width', 'x': slider_x, 'y': y_offset + row_height * 2, 'w': slider_width, 'h': 20,
             'min': 20, 'max': 200, 'value': cfg.mouse_fov_width, 'label': 'FOV Width:', 'label_x': label_x, 'is_int': True, 'increment': 10},
            {'type': 'slider', 'key': 'mouse_fov_height', 'x': slider_x, 'y': y_offset + row_height * 3, 'w': slider_width, 'h': 20,
             'min': 20, 'max': 200, 'value': cfg.mouse_fov_height, 'label': 'FOV Height:', 'label_x': label_x, 'is_int': True, 'increment': 10},
            {'type': 'slider', 'key': 'mouse_min_speed_multiplier', 'x': slider_x, 'y': y_offset + row_height * 4, 'w': slider_width, 'h': 20,
             'min': 0.5, 'max': 3.0, 'value': cfg.mouse_min_speed_multiplier, 'label': 'Min Speed Multiplier:', 'label_x': label_x, 'increment': 0.1},
            {'type': 'slider', 'key': 'mouse_max_speed_multiplier', 'x': slider_x, 'y': y_offset + row_height * 5, 'w': slider_width, 'h': 20,
             'min': 0.5, 'max': 3.0, 'value': cfg.mouse_max_speed_multiplier, 'label': 'Max Speed Multiplier:', 'label_x': label_x, 'increment': 0.1},
            {'type': 'checkbox', 'key': 'mouse_lock_target', 'x': label_x, 'y': y_offset + row_height * 6, 'w': 20, 'h': 20,
             'value': cfg.mouse_lock_target, 'label': 'Lock Target'},
            {'type': 'checkbox', 'key': 'mouse_auto_aim', 'x': label_x + 180, 'y': y_offset + row_height * 6, 'w': 20, 'h': 20,
             'value': cfg.mouse_auto_aim, 'label': 'Auto Aim'},
            {'type': 'checkbox', 'key': 'mouse_ghub', 'x': label_x, 'y': y_offset + row_height * 7, 'w': 20, 'h': 20,
             'value': cfg.mouse_ghub, 'label': 'G-Hub Mouse'},
            {'type': 'checkbox', 'key': 'mouse_rzr', 'x': label_x + 180, 'y': y_offset + row_height * 7, 'w': 20, 'h': 20,
             'value': cfg.mouse_rzr, 'label': 'Razer Mouse'}
        ]

        self.tab_elements[5] = [
            {'type': 'checkbox', 'key': 'auto_shoot', 'x': label_x, 'y': y_offset + row_height * 0, 'w': 20, 'h': 20,
             'value': cfg.auto_shoot, 'label': 'Auto Shoot'},
            {'type': 'checkbox', 'key': 'triggerbot', 'x': label_x, 'y': y_offset + row_height * 1, 'w': 20, 'h': 20,
             'value': cfg.triggerbot, 'label': 'Triggerbot'},
            {'type': 'checkbox', 'key': 'force_click', 'x': label_x, 'y': y_offset + row_height * 2, 'w': 20, 'h': 20,
             'value': cfg.force_click, 'label': 'Force Click'},
            {'type': 'slider', 'key': 'bScope_multiplier', 'x': slider_x, 'y': y_offset + row_height * 3, 'w': slider_width, 'h': 20,
             'min': 0.5, 'max': 3.0, 'value': cfg.bScope_multiplier, 'label': 'Scope Multiplier:', 'label_x': label_x, 'increment': 0.1}
        ]

        self.tab_elements[6] = [
            {'type': 'slider', 'key': 'AI_conf', 'x': slider_x, 'y': y_offset + row_height * 0, 'w': slider_width, 'h': 20,
             'min': 0.1, 'max': 0.9, 'value': cfg.AI_conf, 'label': 'AI Confidence:', 'label_x': label_x, 'increment': 0.01},
            {'type': 'input', 'key': 'AI_device', 'x': slider_x, 'y': y_offset + row_height * 1, 'w': input_width, 'h': 35,
             'value': str(cfg.AI_device), 'label': 'AI Device:', 'label_x': label_x, 'max_len': 10},
            {'type': 'checkbox', 'key': 'AI_enable_AMD', 'x': label_x, 'y': y_offset + row_height * 2, 'w': 20, 'h': 20,
             'value': cfg.AI_enable_AMD, 'label': 'Enable AMD'},
            {'type': 'checkbox', 'key': 'disable_tracker', 'x': label_x, 'y': y_offset + row_height * 3, 'w': 20, 'h': 20,
             'value': cfg.disable_tracker, 'label': 'Disable Tracker'}
        ]

        self.tab_elements[7] = [
            {'type': 'checkbox', 'key': 'show_overlay', 'x': label_x, 'y': y_offset + row_height * 0, 'w': 20, 'h': 20,
             'value': cfg.show_overlay, 'label': 'Show Overlay'},
            {'type': 'checkbox', 'key': 'overlay_show_boxes', 'x': label_x, 'y': y_offset + row_height * 1, 'w': 20, 'h': 20,
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
             'min': 50, 'max': 200, 'value': cfg.debug_window_scale_percent, 'label': 'Debug Window Scale %:', 'label_x': label_x, 'is_int': True, 'increment': 10}
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
                
                raw_key = cv2.waitKey(1)
                key = raw_key & 0xFF
                
                # Only handle ESC key for closing - no more hotkey passthrough
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
        self.sync_elements_from_cfg()
        
        # Create gradient background
        canvas = self.create_gradient_background()
        
        # Draw UI components
        self.draw_tabs(canvas)
        self.draw_physical_buttons(canvas)
        self.draw_ui_elements(canvas)
        self.draw_status_bar(canvas)
        self.draw_fps(canvas)
        
        cv2.imshow(self.window_name, canvas)
        self.needs_redraw = False
    
    def create_gradient_background(self):
        """Create modern background (solid dark theme)."""
        canvas = np.zeros((self.canvas_height, self.canvas_width, 3), dtype=np.uint8)
        canvas[:, :] = self.colors['bg_start']
        return canvas
    
    def draw_physical_buttons(self, canvas):
        """Draw modern physical buttons with hover effects"""
        for button in self.buttons:
            x, y = button['x'], button['y']
            w, h = button['w'], button['h']
            text = button['text']
            button_id = button['id']
            
            state = self.button_states[button_id]
            is_hovered = state['hovered']
            is_pressed = state['pressed']
            
            # Draw shadow
            cv2.rectangle(canvas, (x + 2, y + 2), (x + w + 2, y + h + 2), self.colors['shadow'], -1)
            
            # Determine button color based on state
            if is_pressed:
                color = self.colors['button_active']
            elif is_hovered:
                color = self.colors['button_hover']
            else:
                color = self.colors['button_normal']
            
            # Draw button background with gradient effect
            cv2.rectangle(canvas, (x, y), (x + w, y + h), color, -1)
            cv2.rectangle(canvas, (x, y), (x + w, y + h), self.colors['border'], 2)
            
            # Draw text with shadow
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
            text_x = x + (w - text_size[0]) // 2
            text_y = y + (h + text_size[1]) // 2
            
            # Text shadow
            cv2.putText(canvas, text, (text_x + 1, text_y + 1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.colors['shadow'], 1)
            # Main text
            cv2.putText(canvas, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.colors['button_text'], 1)
    
    def draw_tabs(self, canvas):
        tab_height = 42
        padding_x = 15
        spacing = 8
        margin_x = 20
        start_y = 55  # Below the physical buttons

        self.tab_rects = []

        x = margin_x
        y = start_y
        row = 0

        for i, tab_name in enumerate(self.tab_names):
            text_size = cv2.getTextSize(tab_name, cv2.FONT_HERSHEY_SIMPLEX, self.font_scale, self.font_thickness)[0]
            tab_width = max(100, text_size[0] + padding_x * 2)

            if x + tab_width + margin_x > self.canvas_width and x > margin_x:
                row += 1
                x = margin_x
                y = start_y + row * tab_height

            x1, y1 = x, y
            x2, y2 = x + tab_width, y + tab_height

            self.tab_rects.append((i, x1, y1, x2, y2))

            # Modern tab design
            if i == self.current_tab:
                # Active tab - bright blue with shadow
                cv2.rectangle(canvas, (x1 + 1, y1 + 1), (x2 - 1, y2 + 10), self.colors['shadow'], -1)
                cv2.rectangle(canvas, (x1, y1), (x2, y2 + 10), self.colors['tab_active'], -1)
                cv2.rectangle(canvas, (x1, y1), (x2, y2 + 10), self.colors['border'], 1)
            else:
                # Inactive tab - darker with hover effect
                color = self.colors['tab_inactive']
                if self.is_point_in_rect(self.mouse_pos, (x1, y1, x2, y2 + 10)):
                    # Slightly brighter on hover
                    color = tuple(min(255, c + 20) for c in color)
                
                cv2.rectangle(canvas, (x1, y1), (x2, y2 + 5), color, -1)
                cv2.rectangle(canvas, (x1, y1), (x2, y2 + 5), self.colors['border'], 1)

            # Tab text with shadow
            text_x = x1 + (tab_width - text_size[0]) // 2
            text_y = y1 + int(tab_height * 0.65)
            
            # Text shadow
            cv2.putText(canvas, tab_name, (text_x + 1, text_y + 1), cv2.FONT_HERSHEY_SIMPLEX, self.font_scale, self.colors['shadow'], 1)
            # Main text
            cv2.putText(canvas, tab_name, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, self.font_scale, self.colors['text'], 1)

            x = x2 + spacing

        self.tab_bar_height = y + tab_height + 10
        cv2.line(canvas, (margin_x, self.tab_bar_height), (self.canvas_width - margin_x, self.tab_bar_height), self.colors['border'], 2)
    
    def draw_ui_elements(self, canvas):
        y_start = self.tab_bar_height + 25
        
        for element in self.ui_elements:
            if element['type'] == 'slider':
                self.draw_modern_slider(canvas, element, y_start)
            elif element['type'] == 'checkbox':
                self.draw_modern_checkbox(canvas, element, y_start)
            elif element['type'] == 'input':
                self.draw_modern_input(canvas, element, y_start)
    
    def draw_modern_slider(self, canvas, element, y_start):
        y = y_start + int(element.get('y', 0))

        x = element['x']
        w = element['w']
        min_val = element['min']
        max_val = element['max']
        value = element['value']
        label = element['label']
        label_x = element['label_x']

        # Label
        cv2.putText(canvas, label, (label_x + 1, y + 18), cv2.FONT_HERSHEY_SIMPLEX, self.font_scale, self.colors['shadow'], 1)
        cv2.putText(canvas, label, (label_x, y + 17), cv2.FONT_HERSHEY_SIMPLEX, self.font_scale, self.colors['text'], 1)

        # Slider track
        track_y = y + 25
        track_rect = (x, track_y, x + w, track_y + 6)
        element['_track_rect'] = track_rect

        cv2.rectangle(canvas, (track_rect[0], track_rect[1]), (track_rect[2], track_rect[3]), self.colors['slider_track'], -1)
        cv2.rectangle(canvas, (track_rect[0], track_rect[1]), (track_rect[2], track_rect[3]), self.colors['border'], 1)

        # Handle
        range_val = max_val - min_val
        handle_x = x
        if range_val > 0:
            ratio = (value - min_val) / range_val
            ratio = max(0.0, min(1.0, ratio))
            handle_x = int(x + ratio * w)

        handle_center = (handle_x, track_y + 3)
        element['_handle_center'] = handle_center

        handle_radius = 9
        cv2.circle(canvas, handle_center, handle_radius, self.colors['slider_handle'], -1)
        cv2.circle(canvas, handle_center, handle_radius, self.colors['text'], 1)

        # Value display
        if element.get('is_int', False):
            value_text = f'{int(round(float(value)))}'
        else:
            value_text = f'{float(value):.2f}'

        value_x = x + w + 10
        value_y = track_y + 5

        cv2.putText(canvas, value_text, (value_x + 1, value_y + 1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.colors['shadow'], 1)
        cv2.putText(canvas, value_text, (value_x, value_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.colors['text'], 1)

        # Manual numeric input box
        input_w = 70
        input_h = 25
        input_x = x + w + 60
        input_y = y + 10
        input_rect = (input_x, input_y, input_x + input_w, input_y + input_h)
        element['_input_rect'] = input_rect

        is_focused = (self.focused_input == element['key'])
        border_color = self.colors['button_active'] if is_focused else self.colors['input_border']

        # Hover effect
        if not is_focused and self.is_point_in_rect(self.mouse_pos, input_rect):
            border_color = tuple(min(255, c + 20) for c in border_color)

        cv2.rectangle(canvas, (input_rect[0] + 2, input_rect[1] + 2), (input_rect[2] + 2, input_rect[3] + 2), self.colors['shadow'], -1)
        cv2.rectangle(canvas, (input_rect[0], input_rect[1]), (input_rect[2], input_rect[3]), self.colors['input_bg'], -1)
        cv2.rectangle(canvas, (input_rect[0], input_rect[1]), (input_rect[2], input_rect[3]), border_color, 2)

        display_text = element.get('_input_text') if is_focused else value_text
        if display_text is None:
            display_text = value_text
        display_text = str(display_text)
        if is_focused and self.input_cursor_visible:
            display_text += '|'

        max_chars = int((input_w - 10) / 8)
        if len(display_text) > max_chars:
            display_text = display_text[-max_chars:]

        text_x = input_x + 6
        text_y = input_y + input_h - 8
        cv2.putText(canvas, display_text, (text_x + 1, text_y + 1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.colors['shadow'], 1)
        cv2.putText(canvas, display_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.colors['text'], 1)
    
    def draw_modern_checkbox(self, canvas, element, y_start):
        y = y_start + int(element.get('y', 0))
        x = element['x']
        value = element['value']
        label = element['label']

        # Checkbox
        box_size = 20
        box_x = x
        box_y = y + 5
        box_rect = (box_x, box_y, box_x + box_size, box_y + box_size)
        element['_box_rect'] = box_rect

        # Shadow
        cv2.rectangle(canvas, (box_x + 1, box_y + 1), (box_x + box_size + 1, box_y + box_size + 1), self.colors['shadow'], -1)

        # Background and border
        if value:
            bg_color = self.colors['checkbox_active']
            border_color = self.colors['checkbox_active']
        else:
            bg_color = self.colors['checkbox_inactive']
            border_color = self.colors['checkbox_inactive']

        # Hover effect
        if self.is_point_in_rect(self.mouse_pos, box_rect):
            bg_color = tuple(min(255, c + 20) for c in bg_color)
            border_color = tuple(min(255, c + 20) for c in border_color)

        cv2.rectangle(canvas, (box_x, box_y), (box_x + box_size, box_y + box_size), bg_color, -1)
        cv2.rectangle(canvas, (box_x, box_y), (box_x + box_size, box_y + box_size), border_color, 2)

        # Checkmark
        if value:
            check_points = np.array([
                [box_x + 4, box_y + 10],
                [box_x + 8, box_y + 14],
                [box_x + 16, box_y + 5]
            ])
            cv2.polylines(canvas, [check_points], False, (255, 255, 255), 2)

        # Label
        label_x = x + box_size + 10
        cv2.putText(canvas, label, (label_x + 1, y + 21), cv2.FONT_HERSHEY_SIMPLEX, self.font_scale, self.colors['shadow'], 1)
        cv2.putText(canvas, label, (label_x, y + 20), cv2.FONT_HERSHEY_SIMPLEX, self.font_scale, self.colors['text'], 1)
    
    def draw_modern_input(self, canvas, element, y_start):
        y = y_start + int(element.get('y', 0))

        x = element['x']
        w = element['w']
        h = element['h']
        value = str(element['value'])
        label = element['label']
        label_x = element['label_x']

        cv2.putText(canvas, label, (label_x + 1, y + 22), cv2.FONT_HERSHEY_SIMPLEX, self.font_scale, self.colors['shadow'], 1)
        cv2.putText(canvas, label, (label_x, y + 21), cv2.FONT_HERSHEY_SIMPLEX, self.font_scale, self.colors['text'], 1)

        input_x = x
        input_y = y + 5
        input_rect = (input_x, input_y, input_x + w, input_y + h)
        element['_input_rect'] = input_rect

        cv2.rectangle(canvas, (input_x + 2, input_y + 2), (input_x + w + 2, input_y + h + 2), self.colors['shadow'], -1)

        is_focused = (self.focused_input == element['key'])
        border_color = self.colors['button_active'] if is_focused else self.colors['input_border']

        if not is_focused and self.is_point_in_rect(self.mouse_pos, input_rect):
            border_color = tuple(min(255, c + 20) for c in border_color)

        cv2.rectangle(canvas, (input_x, input_y), (input_x + w, input_y + h), self.colors['input_bg'], -1)
        cv2.rectangle(canvas, (input_x, input_y), (input_x + w, input_y + h), border_color, 2)

        display_value = value
        if is_focused and self.input_cursor_visible:
            display_value += '|'

        max_chars = int((w - 10) / 8)
        if len(display_value) > max_chars:
            display_value = display_value[-max_chars:]

        text_x = input_x + 8
        text_y = input_y + h - 8

        cv2.putText(canvas, display_value, (text_x + 1, text_y + 1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.colors['shadow'], 1)
        cv2.putText(canvas, display_value, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.colors['text'], 1)
    
    def draw_status_bar(self, canvas):
        # Modern status bar
        status_y = self.canvas_height - 30
        cv2.rectangle(canvas, (0, status_y), (self.canvas_width, self.canvas_height), self.colors['border'], -1)
        cv2.line(canvas, (0, status_y), (self.canvas_width, status_y), self.colors['text'], 1)
        
        # Status text
        status_text = f'Tab: {self.tab_names[self.current_tab]} | F1: Toggle GUI | Use buttons for F2/F3/F4 actions'
        cv2.putText(canvas, status_text, (10, status_y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, self.colors['text'], 1)
    
    def draw_fps(self, canvas):
        fps_text = f'FPS: {self.current_fps}'
        text_size = cv2.getTextSize(fps_text, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
        cv2.putText(canvas, fps_text, (self.canvas_width - text_size[0] - 10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, self.colors['text'], 1)
    
    def is_point_in_rect(self, point, rect):
        """Check if point is inside rectangle"""
        x, y = point
        x1, y1, x2, y2 = rect
        return x1 <= x <= x2 and y1 <= y <= y2
    
    def mouse_callback(self, event, x, y, flags, param):
        self.mouse_pos = (x, y)
        self.mouse_moved = True
        
        if event == cv2.EVENT_LBUTTONDOWN:
            self.handle_mouse_down(x, y)
        elif event == cv2.EVENT_LBUTTONUP:
            self.handle_mouse_up(x, y)
        elif event == cv2.EVENT_MOUSEMOVE:
            self.handle_mouse_move(x, y)
    
    def handle_mouse_down(self, x, y):
        # Check physical buttons first
        for button in self.buttons:
            if self.is_point_in_rect((x, y), (button['x'], button['y'], button['x'] + button['w'], button['y'] + button['h'])):
                self.button_states[button['id']]['pressed'] = True
                self.needs_redraw = True
                return

        # Check tabs
        for i, (tab_id, x1, y1, x2, y2) in enumerate(self.tab_rects):
            if self.is_point_in_rect((x, y), (x1, y1, x2, y2)):
                self.current_tab = tab_id
                self.ui_elements = self.tab_elements[tab_id]
                self.focused_input = None  # Clear focus when switching tabs
                self.needs_redraw = True
                return

        # If an input is focused and we click outside it, commit the value
        if self.focused_input is not None:
            focused_element = None
            for el in self.ui_elements:
                if el['key'] == self.focused_input:
                    focused_element = el
                    break

            if focused_element is not None:
                focused_rect = focused_element.get('_input_rect')
                if focused_rect and not self.is_point_in_rect((x, y), focused_rect):
                    self.update_element_from_input(focused_element)
                    self.focused_input = None

        # Check UI elements
        for element in self.ui_elements:
            if element['type'] == 'slider':
                if self.handle_slider_mouse_down(element, x, y):
                    return
            elif element['type'] == 'checkbox':
                if self.handle_checkbox_click(element, x, y):
                    return
            elif element['type'] == 'input':
                if self.handle_input_click(element, x, y):
                    return

        # Click outside: clear focus
        if self.focused_input is not None:
            focused_element = None
            for el in self.ui_elements:
                if el['key'] == self.focused_input:
                    focused_element = el
                    break
            if focused_element is not None:
                self.update_element_from_input(focused_element)
            self.focused_input = None

        self.needs_redraw = True
    
    def handle_mouse_up(self, x, y):
        # Handle button clicks
        for button in self.buttons:
            button_id = button['id']
            was_pressed = self.button_states[button_id]['pressed']

            if self.is_point_in_rect((x, y), (button['x'], button['y'], button['x'] + button['w'], button['y'] + button['h'])):
                if was_pressed:
                    self.execute_button_action(button_id)

            self.button_states[button_id]['pressed'] = False

        # Finish slider drag
        if self.dragging_slider_element is not None:
            self.dragging_slider_element = None
            self.dragging_slider = None
            self.save_config()

        self.needs_redraw = True
    
    def handle_mouse_move(self, x, y):
        # Drag slider if active
        if self.dragging_slider_element is not None:
            self.update_slider_from_drag(self.dragging_slider_element, x)
            self.needs_redraw = True
            return

        # Update button hover states
        for button in self.buttons:
            button_id = button['id']
            was_hovered = self.button_states[button_id]['hovered']
            is_hovered = self.is_point_in_rect((x, y), (button['x'], button['y'], button['x'] + button['w'], button['y'] + button['h']))

            if was_hovered != is_hovered:
                self.button_states[button_id]['hovered'] = is_hovered
                self.needs_redraw = True
    
    def execute_button_action(self, button_id):
        """Execute actions for physical buttons"""
        try:
            if button_id == 'close_gui':
                self.toggle_visibility()
            elif button_id == 'exit_program':
                logger.info('[Config GUI] Exit button pressed - closing program')
                capture = None
                try:
                    from logic.capture import capture
                except:
                    pass
                if capture:
                    capture.Quit()
                os._exit(0)
            elif button_id == 'reload_config':
                logger.info('[Config GUI] Reload button pressed - reloading config')
                cfg.Read(verbose=True)
                try:
                    from logic.capture import capture
                    capture.restart()
                except:
                    pass
                try:
                    from logic.mouse import mouse
                    mouse.update_settings()
                except:
                    pass
                self.clss = self.active_classes()
                logger.info('[Config GUI] Config reload applied')
            elif button_id == 'save_config':
                logger.info('[Config GUI] Save button pressed - saving config')
                self.save_config()
        except Exception as e:
            logger.error(f'[Config GUI] Error executing button action {button_id}: {e}')
    
    def active_classes(self):
        """Get active classes for detection"""
        clss = [0.0, 1.0]
        
        if cfg.hideout_targets:
            clss.extend([5.0, 6.0])

        if not cfg.disable_headshot:
            clss.append(7.0)
            
        if cfg.third_person:
            clss.append(10.0)
        
        return clss
    
    def handle_slider_mouse_down(self, element, x, y):
        """Handle mouse down on slider (handle or input box)."""
        # Check input box first
        input_rect = element.get('_input_rect')
        if not input_rect:
            y_start = self.tab_bar_height + 25
            ey = y_start + int(element.get('y', 0))
            input_w = 70
            input_h = 25
            input_x = element['x'] + element['w'] + 60
            input_y = ey + 10
            input_rect = (input_x, input_y, input_x + input_w, input_y + input_h)

        if self.is_point_in_rect((x, y), input_rect):
            self.focused_input = element['key']
            # Start editing with current value
            if element.get('is_int', False):
                element['_input_text'] = str(int(round(float(element.get('value', 0)))))
            else:
                element['_input_text'] = f"{float(element.get('value', 0)):.4f}".rstrip('0').rstrip('.')
            self.needs_redraw = True
            return True

        # Check track/handle
        track_rect = element.get('_track_rect')
        if not track_rect:
            y_start = self.tab_bar_height + 25
            ey = y_start + int(element.get('y', 0))
            track_y = ey + 25
            track_rect = (element['x'], track_y, element['x'] + element['w'], track_y + 6)

        if self.is_point_in_rect((x, y), (track_rect[0], track_rect[1] - 10, track_rect[2], track_rect[3] + 10)):
            # Start dragging
            self.dragging_slider = element['key']
            self.dragging_slider_element = element
            self.update_slider_from_drag(element, x)
            self.needs_redraw = True
            return True

        return False

    def update_slider_from_drag(self, element, x):
        """Update slider value from drag position."""
        slider_x = element['x']
        slider_w = element['w']
        min_val = element['min']
        max_val = element['max']
        range_val = max_val - min_val

        if range_val <= 0:
            return

        # Calculate ratio from mouse position
        ratio = (x - slider_x) / slider_w
        ratio = max(0.0, min(1.0, ratio))
        new_value = min_val + ratio * range_val

        # Apply increment snapping
        increment = element.get('increment', 1)
        if increment:
            # Snap to increment
            new_value = round(new_value / increment) * increment

        # Clamp to range
        new_value = max(min_val, min(max_val, new_value))

        if element.get('is_int', False):
            new_value = int(round(new_value))

        element['value'] = new_value
        self.apply_element_value(element['key'], new_value)

    def handle_checkbox_click(self, element, x, y):
        """Handle checkbox click - toggle value and save immediately."""
        box_rect = element.get('_box_rect')
        if not box_rect:
            # Fallback if no rect stored yet
            checkbox_x = element['x']
            checkbox_y = element.get('y', 0) + self.tab_bar_height + 25 + 5
            checkbox_size = 20
            box_rect = (checkbox_x, checkbox_y, checkbox_x + checkbox_size, checkbox_y + checkbox_size)

        if self.is_point_in_rect((x, y), box_rect):
            # Toggle value
            element['value'] = not element['value']
            self.apply_element_value(element['key'], element['value'])
            # Immediately save to config.ini
            self.save_config()
            self.needs_redraw = True
            return True

        return False

    def handle_input_click(self, element, x, y):
        """Handle input box click."""
        input_rect = element.get('_input_rect')
        if not input_rect:
            # Fallback
            input_x = element['x']
            input_y = element.get('y', 0) + self.tab_bar_height + 25 + 5
            input_w = element['w']
            input_h = element['h']
            input_rect = (input_x, input_y, input_x + input_w, input_y + input_h)

        if self.is_point_in_rect((x, y), input_rect):
            self.focused_input = element['key']
            self.needs_redraw = True
            return True

        return False
    
    def handle_keyboard(self, key):
        if self.focused_input is None:
            return

        # Find the focused element
        focused_element = None
        for element in self.ui_elements:
            if element['key'] == self.focused_input:
                focused_element = element
                break

        if focused_element is None:
            return

        # For sliders, use _input_text; for regular inputs, use value
        if focused_element['type'] == 'slider':
            current_value = str(focused_element.get('_input_text', ''))
        else:
            current_value = str(focused_element['value'])

        if key == 8:  # Backspace
            if current_value:
                current_value = current_value[:-1]
        elif key == 13:  # Enter
            self.focused_input = None
            self.update_element_from_input(focused_element)
            return
        elif 32 <= key <= 126:  # Printable ASCII
            # For numeric inputs, allow numbers, decimal points, and minus sign
            char = chr(key)
            if focused_element['type'] == 'slider' or focused_element.get('is_int', False):
                if char.isdigit() or char in '.-':
                    current_value += char
            else:
                if len(current_value) < focused_element.get('max_len', 20):
                    current_value += char
        elif key == 27:  # Escape
            self.focused_input = None
            if focused_element['type'] == 'slider':
                focused_element['_input_text'] = ''
            return

        # Update the appropriate field
        if focused_element['type'] == 'slider':
            focused_element['_input_text'] = current_value
        else:
            focused_element['value'] = current_value

        self.needs_redraw = True
    
    def update_element_from_input(self, element):
        """Update element value from input text."""
        try:
            key = element['key']

            # For sliders, use _input_text if available
            if element['type'] == 'slider':
                value_str = str(element.get('_input_text', element['value']))
            else:
                value_str = str(element['value'])

            # Parse the value
            if element.get('is_int', False) or element['type'] == 'slider':
                try:
                    new_value = float(value_str)
                    if element.get('is_int', False):
                        new_value = int(round(new_value))
                except (ValueError, TypeError):
                    # Invalid input, keep old value
                    logger.warning(f'[Config GUI] Invalid numeric input for {key}: {value_str}')
                    if element['type'] == 'slider':
                        element['_input_text'] = ''
                    return
            else:
                new_value = value_str

            # For sliders, clamp to range and apply increment
            if element['type'] == 'slider':
                min_val = element['min']
                max_val = element['max']
                new_value = max(min_val, min(max_val, new_value))
                
                increment = element.get('increment', 1)
                if increment:
                    new_value = round(new_value / increment) * increment

                if element.get('is_int', False):
                    new_value = int(round(new_value))

                element['_input_text'] = ''  # Clear input text

            element['value'] = new_value
            self.apply_element_value(key, new_value)
            self.save_config()  # Save after manual input
        except Exception as e:
            logger.error(f'[Config GUI] Error updating element {element["key"]}: {e}')
    
    def apply_element_value(self, key, value):
        """Apply value change to config"""
        try:
            if hasattr(cfg, key):
                setattr(cfg, key, value)
                self.needs_redraw = True
        except Exception as e:
            logger.error(f'[Config GUI] Error applying value to {key}: {e}')
    
    def sync_elements_from_cfg(self):
        """Sync UI elements from config."""
        for element in self.ui_elements:
            key = element['key']

            # Don't overwrite text while the user is typing.
            if self.focused_input == key and element.get('type') == 'input':
                continue

            if hasattr(cfg, key):
                element['value'] = getattr(cfg, key)
    
    def save_config(self):
        """Save all current config values to config.ini"""
        try:
            with cfg_file_lock:
                config = configparser.ConfigParser()
                config.read('config.ini')
                
                # Define key mappings for different config sections
                detection_keys = ['detection_window_width', 'detection_window_height', 'circle_capture']
                capture_keys = ['capture_fps', 'Bettercam_capture', 'bettercam_monitor_id', 'bettercam_gpu_id', 'Obs_capture', 'Obs_camera_id', 'mss_capture']
                aim_keys = ['body_y_offset', 'hideout_targets', 'disable_headshot', 'disable_prediction', 'prediction_interval', 'third_person']
                hotkey_keys = ['hotkey_targeting', 'hotkey_exit', 'hotkey_pause', 'hotkey_reload_config']
                mouse_keys = ['mouse_dpi', 'mouse_sensitivity', 'mouse_fov_width', 'mouse_fov_height', 'mouse_min_speed_multiplier', 'mouse_max_speed_multiplier', 'mouse_lock_target', 'mouse_auto_aim', 'mouse_ghub', 'mouse_rzr']
                shooting_keys = ['auto_shoot', 'triggerbot', 'force_click', 'bScope_multiplier']
                arduino_keys = ['arduino_move', 'arduino_shoot', 'arduino_port', 'arduino_baudrate', 'arduino_16_bit_mouse']
                ai_keys = ['AI_model_name', 'AI_model_image_size', 'AI_conf', 'AI_device', 'AI_enable_AMD', 'disable_tracker']
                overlay_keys = ['show_overlay', 'overlay_show_borders', 'overlay_show_boxes', 'overlay_show_target_line', 'overlay_show_target_prediction_line', 'overlay_show_labels', 'overlay_show_conf']
                debug_keys = ['show_window', 'show_detection_speed', 'show_window_fps', 'show_boxes', 'show_labels', 'show_conf', 'show_target_line', 'show_target_prediction_line', 'show_bScope_box', 'show_history_points', 'debug_window_always_on_top', 'spawn_window_pos_x', 'spawn_window_pos_y', 'debug_window_scale_percent', 'debug_window_screenshot_key']
                
                # Save each section
                for key in detection_keys:
                    if hasattr(cfg, key):
                        val = getattr(cfg, key)
                        if isinstance(val, bool):
                            config.set('Detection window', key, 'True' if val else 'False')
                        else:
                            config.set('Detection window', key, str(val))
                
                for key in capture_keys:
                    if hasattr(cfg, key):
                        val = getattr(cfg, key)
                        if isinstance(val, bool):
                            config.set('Capture Methods', key, 'True' if val else 'False')
                        else:
                            config.set('Capture Methods', key, str(val))
                
                for key in aim_keys:
                    if hasattr(cfg, key):
                        val = getattr(cfg, key)
                        if isinstance(val, bool):
                            config.set('Aim', key, 'True' if val else 'False')
                        else:
                            config.set('Aim', key, str(val))
                
                for key in hotkey_keys:
                    if hasattr(cfg, key):
                        val = getattr(cfg, key)
                        config.set('Hotkeys', key, str(val))
                
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
                
                for key in arduino_keys:
                    if hasattr(cfg, key):
                        val = getattr(cfg, key)
                        if isinstance(val, bool):
                            config.set('Arduino', key, 'True' if val else 'False')
                        else:
                            config.set('Arduino', key, str(val))
                
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
                
                for key in debug_keys:
                    if hasattr(cfg, key):
                        val = getattr(cfg, key)
                        if isinstance(val, bool):
                            config.set('Debug window', key, 'True' if val else 'False')
                        else:
                            config.set('Debug window', key, str(val))

                with open('config.ini', 'w', encoding='utf-8') as f:
                    config.write(f)

            cfg.Read(verbose=False)
            self.apply_runtime_updates()
            self.sync_elements_from_cfg()

            logger.info('[Config GUI] Config saved & applied')
        except Exception as e:
            logger.error(f'[Config GUI] Error saving config: {e}')
    
    def apply_runtime_updates(self):
        """Apply runtime updates after config save"""
        try:
            # Import required modules
            from logic.capture import capture
            from logic.mouse import mouse
            from logic.visual import visuals
            
            # Restart capture
            capture.restart()
            
            # Update mouse settings
            mouse.update_settings()
            
            # Start visuals thread if overlay or window is enabled and it's not running
            if cfg.show_overlay or cfg.show_window:
                visuals.start_if_not_running()
            
            # Update active classes
            self.clss = self.active_classes()
            
        except Exception as e:
            logger.error(f'[Config GUI] Error applying runtime updates: {e}')
    
    def save_position(self):
        try:
            x, y = self.window_pos
            with cfg_file_lock:
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