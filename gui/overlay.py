import PySimpleGUI as sg
import threading
import time
import os
from logic.config_watcher import cfg
from . import draw_buttons, draw_capture, draw_ai, draw_mouse, draw_aim, draw_shooting, draw_arduino, draw_game_overlay, draw_debug, draw_stats, draw_depth

class Overlay:
    def __init__(self):
        self.thread = None
        self.running = False
        self.window = None
        self.last_time = time.time()
        self.frame_count = 0
        self.fps = 0

    def calculate_fps(self):
        self.frame_count += 1
        current_time = time.time()
        if current_time - self.last_time >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.last_time = current_time
        return self.fps

    def create_layout(self):
        sg.theme('DarkBlue3')
        
        tab_buttons = sg.Tab('Buttons', draw_buttons.draw_buttons(cfg), key='-TAB_BUTTONS-')
        tab_capture = sg.Tab('Capture', draw_capture.draw_capture(cfg), key='-TAB_CAPTURE-')
        tab_ai = sg.Tab('AI', draw_ai.draw_ai(cfg), key='-TAB_AI-')
        tab_mouse = sg.Tab('Mouse', draw_mouse.draw_mouse(cfg), key='-TAB_MOUSE-')
        tab_aim = sg.Tab('Aim', draw_aim.draw_aim(cfg), key='-TAB_AIM-')
        tab_shooting = sg.Tab('Shooting', draw_shooting.draw_shooting(cfg), key='-TAB_SHOOTING-')
        tab_arduino = sg.Tab('Arduino', draw_arduino.draw_arduino(cfg), key='-TAB_ARDUINO-')
        tab_depth = sg.Tab('Depth', draw_depth.draw_depth(cfg), key='-TAB_DEPTH-')
        tab_overlay = sg.Tab('Game Overlay', draw_game_overlay.draw_game_overlay(cfg), key='-TAB_OVERLAY-')
        tab_debug = sg.Tab('Debug', draw_debug.draw_debug(cfg), key='-TAB_DEBUG-')
        tab_stats = sg.Tab('Stats', draw_stats.draw_stats(cfg), key='-TAB_STATS-')

        layout = [
            [sg.TabGroup([[tab_buttons, tab_capture, tab_ai, tab_mouse, tab_aim, tab_shooting, tab_arduino, tab_depth, tab_overlay, tab_debug, tab_stats]], key='-TAB_GROUP-', expand_x=True, expand_y=True)],
            [sg.StatusBar('Ready', key='-STATUSBAR-')]
        ]
        return layout

    def run(self):
        self.window = sg.Window('Sunone Aimbot - Configuration', self.create_layout(), resizable=True, finalize=True)
        self.running = True
        
        last_cfg_time = os.path.getmtime("config.ini") if os.path.exists("config.ini") else 0
        
        while self.running:
            event, values = self.window.read(timeout=100)
            
            # Update stats if on stats tab
            if values and values['-TAB_GROUP-'] == '-TAB_STATS-':
                self.window['-GUI_FPS-'].update(value=str(self.calculate_fps()))
            
            # Check for external config reload
            try:
                current_cfg_time = os.path.getmtime("config.ini") if os.path.exists("config.ini") else 0
                if current_cfg_time > last_cfg_time:
                    # Wait a bit for the file to be fully written
                    time.sleep(0.1)
                    cfg.Read()
                    self.refresh_values()
                    last_cfg_time = current_cfg_time
            except:
                pass

            if event == sg.WIN_CLOSED:
                break
                
            if event and event != sg.TIMEOUT_KEY:
                self.handle_event(event, values)
                # Update last_cfg_time so we don't trigger a refresh after our own save
                try:
                    last_cfg_time = os.path.getmtime("config.ini") if os.path.exists("config.ini") else 0
                except:
                    pass

        self.window.close()
        self.running = False

    def refresh_values(self):
        if not self.window:
            return
        
        # This is a partial list of critical values to refresh on F4
        updates = {
            '-HOTKEY_TARGETING-': cfg.hotkey_targeting,
            '-HOTKEY_EXIT-': cfg.hotkey_exit,
            '-HOTKEY_PAUSE-': cfg.hotkey_pause,
            '-HOTKEY_RELOAD_CONFIG-': cfg.hotkey_reload_config,
            '-AI_MODEL_NAME-': cfg.AI_model_name,
            '-AI_CONF-': cfg.AI_conf,
            '-MOUSE_DPI-': cfg.mouse_dpi,
            '-MOUSE_SENSITIVITY-': cfg.mouse_sensitivity,
            '-SHOW_WINDOW-': cfg.show_window,
            '-SHOW_OVERLAY-': cfg.show_overlay
        }
        
        for key, value in updates.items():
            try:
                if key in self.window.AllKeysDict:
                    self.window[key].update(value=value)
            except:
                pass

    def handle_event(self, event, values):
        save_needed = False
        
        try:
            if event == '-HOTKEY_TARGETING-':
                cfg.hotkey_targeting = values[event]
                cfg.hotkey_targeting_list = cfg.hotkey_targeting.split(",")
                save_needed = True
            elif event == '-HOTKEY_EXIT-':
                cfg.hotkey_exit = values[event]
                save_needed = True
            elif event == '-HOTKEY_PAUSE-':
                cfg.hotkey_pause = values[event]
                save_needed = True
            elif event == '-HOTKEY_RELOAD_CONFIG-':
                cfg.hotkey_reload_config = values[event]
                save_needed = True
            
            # Capture settings
            elif event == '-CAPTURE_FPS-':
                cfg.capture_fps = int(values[event])
                save_needed = True
            elif event == '-BETTERCAM_CAPTURE-':
                cfg.Bettercam_capture = values[event]
                save_needed = True
            elif event == '-BETTERCAM_MONITOR_ID-':
                cfg.bettercam_monitor_id = int(values[event])
                save_needed = True
            elif event == '-BETTERCAM_GPU_ID-':
                cfg.bettercam_gpu_id = int(values[event])
                save_needed = True
            elif event == '-OBS_CAPTURE-':
                cfg.Obs_capture = values[event]
                save_needed = True
            elif event == '-OBS_CAMERA_ID-':
                cfg.Obs_camera_id = values[event]
                save_needed = True
            elif event == '-MSS_CAPTURE-':
                cfg.mss_capture = values[event]
                save_needed = True
            elif event == '-CIRCLE_CAPTURE-':
                cfg.circle_capture = values[event]
                save_needed = True
            elif event == '-DETECTION_WINDOW_WIDTH-':
                cfg.detection_window_width = int(values[event])
                save_needed = True
            elif event == '-DETECTION_WINDOW_HEIGHT-':
                cfg.detection_window_height = int(values[event])
                save_needed = True
                
            # AI settings
            elif event == '-AI_MODEL_NAME-':
                cfg.AI_model_name = values[event]
                save_needed = True
            elif event == '-AI_MODEL_IMAGE_SIZE-':
                cfg.ai_model_image_size = int(values[event])
                save_needed = True
            elif event == '-AI_CONF-':
                cfg.AI_conf = float(values[event])
                save_needed = True
            elif event == '-AI_DEVICE-':
                cfg.AI_device = values[event]
                save_needed = True
            elif event == '-AI_ENABLE_AMD-':
                cfg.AI_enable_AMD = values[event]
                save_needed = True
            elif event == '-DISABLE_TRACKER-':
                cfg.disable_tracker = values[event]
                save_needed = True
                
            # Mouse settings
            elif event == '-MOUSE_DPI-':
                cfg.mouse_dpi = int(values[event])
                save_needed = True
            elif event == '-MOUSE_SENSITIVITY-':
                cfg.mouse_sensitivity = float(values[event])
                save_needed = True
            elif event == '-MOUSE_FOV_WIDTH-':
                cfg.mouse_fov_width = int(values[event])
                save_needed = True
            elif event == '-MOUSE_FOV_HEIGHT-':
                cfg.mouse_fov_height = int(values[event])
                save_needed = True
            elif event == '-MOUSE_MIN_SPEED_MULTIPLIER-':
                cfg.mouse_min_speed_multiplier = float(values[event])
                save_needed = True
            elif event == '-MOUSE_MAX_SPEED_MULTIPLIER-':
                cfg.mouse_max_speed_multiplier = float(values[event])
                save_needed = True
            elif event == '-MOUSE_LOCK_TARGET-':
                cfg.mouse_lock_target = values[event]
                save_needed = True
            elif event == '-MOUSE_AUTO_AIM-':
                cfg.mouse_auto_aim = values[event]
                save_needed = True
            elif event == '-MOUSE_GHUB-':
                cfg.mouse_ghub = values[event]
                save_needed = True
            elif event == '-MOUSE_RZR-':
                cfg.mouse_rzr = values[event]
                save_needed = True
                
            # Aim settings
            elif event == '-BODY_Y_OFFSET-':
                cfg.body_y_offset = float(values[event])
                save_needed = True
            elif event == '-HIDEOUT_TARGETS-':
                cfg.hideout_targets = values[event]
                save_needed = True
            elif event == '-DISABLE_HEADSHOT-':
                cfg.disable_headshot = values[event]
                save_needed = True
            elif event == '-DISABLE_PREDICTION-':
                cfg.disable_prediction = values[event]
                save_needed = True
            elif event == '-PREDICTION_INTERVAL-':
                cfg.prediction_interval = float(values[event])
                save_needed = True
            elif event == '-THIRD_PERSON-':
                cfg.third_person = values[event]
                save_needed = True
                
            # Shooting settings
            elif event == '-AUTO_SHOOT-':
                cfg.auto_shoot = values[event]
                save_needed = True
            elif event == '-TRIGGERBOT-':
                cfg.triggerbot = values[event]
                save_needed = True
            elif event == '-FORCE_CLICK-':
                cfg.force_click = values[event]
                save_needed = True
            elif event == '-BSCOPE_MULTIPLIER-':
                cfg.bScope_multiplier = float(values[event])
                save_needed = True
                
            # Arduino settings
            elif event == '-ARDUINO_MOVE-':
                cfg.arduino_move = values[event]
                save_needed = True
            elif event == '-ARDUINO_SHOOT-':
                cfg.arduino_shoot = values[event]
                save_needed = True
            elif event == '-ARDUINO_PORT-':
                cfg.arduino_port = values[event]
                save_needed = True
            elif event == '-ARDUINO_BAUDRATE-':
                cfg.arduino_baudrate = int(values[event])
                save_needed = True
            elif event == '-ARDUINO_16_BIT_MOUSE-':
                cfg.arduino_16_bit_mouse = values[event]
                save_needed = True
                
            # Game Overlay settings
            elif event == '-SHOW_OVERLAY-':
                cfg.show_overlay = values[event]
                save_needed = True
            elif event == '-OVERLAY_SHOW_BORDERS-':
                cfg.overlay_show_borders = values[event]
                save_needed = True
            elif event == '-OVERLAY_SHOW_BOXES-':
                cfg.overlay_show_boxes = values[event]
                save_needed = True
            elif event == '-OVERLAY_SHOW_TARGET_LINE-':
                cfg.overlay_show_target_line = values[event]
                save_needed = True
            elif event == '-OVERLAY_SHOW_TARGET_PREDICTION_LINE-':
                cfg.overlay_show_target_prediction_line = values[event]
                save_needed = True
            elif event == '-OVERLAY_SHOW_LABELS-':
                cfg.overlay_show_labels = values[event]
                save_needed = True
            elif event == '-OVERLAY_SHOW_CONF-':
                cfg.overlay_show_conf = values[event]
                save_needed = True
                
            # Debug settings
            elif event == '-SHOW_WINDOW-':
                cfg.show_window = values[event]
                save_needed = True
            elif event == '-SHOW_DETECTION_SPEED-':
                cfg.show_detection_speed = values[event]
                save_needed = True
            elif event == '-SHOW_WINDOW_FPS-':
                cfg.show_window_fps = values[event]
                save_needed = True
            elif event == '-SHOW_BOXES-':
                cfg.show_boxes = values[event]
                save_needed = True
            elif event == '-SHOW_LABELS-':
                cfg.show_labels = values[event]
                save_needed = True
            elif event == '-SHOW_CONF-':
                cfg.show_conf = values[event]
                save_needed = True
            elif event == '-SHOW_TARGET_LINE-':
                cfg.show_target_line = values[event]
                save_needed = True
            elif event == '-SHOW_TARGET_PREDICTION_LINE-':
                cfg.show_target_prediction_line = values[event]
                save_needed = True
            elif event == '-SHOW_BSCOPE_BOX-':
                cfg.show_bScope_box = values[event]
                save_needed = True
            elif event == '-SHOW_HISTORY_POINTS-':
                cfg.show_history_points = values[event]
                save_needed = True
            elif event == '-DEBUG_WINDOW_ALWAYS_ON_TOP-':
                cfg.debug_window_always_on_top = values[event]
                save_needed = True
            elif event == '-SPAWN_WINDOW_POS_X-':
                cfg.spawn_window_pos_x = int(values[event])
                save_needed = True
            elif event == '-SPAWN_WINDOW_POS_Y-':
                cfg.spawn_window_pos_y = int(values[event])
                save_needed = True
            elif event == '-DEBUG_WINDOW_SCALE_PERCENT-':
                cfg.debug_window_scale_percent = int(values[event])
                save_needed = True
            elif event == '-DEBUG_WINDOW_SCREENSHOT_KEY-':
                cfg.debug_window_screenshot_key = values[event]
                save_needed = True

            if save_needed:
                cfg.save()
                if self.window:
                    self.window['-STATUSBAR-'].update(f'Config saved at {time.strftime("%H:%M:%S")}')
        except Exception as e:
            print(f"Error handling event {event}: {e}")

    def show(self):
        if self.thread is None or not self.thread.is_alive():
            self.thread = threading.Thread(target=self.run, daemon=True)
            self.thread.start()

config_window = Overlay()
