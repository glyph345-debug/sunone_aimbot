import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import time
import configparser
import platform
import threading
import queue

class DebouncedButton:
    """Button wrapper with debouncing built-in"""
    DEBOUNCE_TIME = 0.15  # 150ms debounce
    
    def __init__(self, parent, text, command, **kwargs):
        self.button = ttk.Button(parent, command=self._debounced_handler, text=text, **kwargs)
        self._command = command
        self._last_click = 0
        
    def _debounced_handler(self):
        current_time = time.time()
        if current_time - self._last_click >= self.DEBOUNCE_TIME:
            self._last_click = current_time
            if self._command:
                self._command()
    
    def pack(self, **kwargs):
        self.button.pack(**kwargs)
    
    def grid(self, **kwargs):
        self.button.grid(**kwargs)
    
    def config(self, **kwargs):
        self.button.config(**kwargs)

class ConfigGUI:
    """Complete Config GUI with all settings and debouncing"""
    
    def __init__(self, config, hotkeys_watcher, mouse, capture, visual, root=None):
        self.cfg = config
        self.hotkeys_watcher = hotkeys_watcher
        self.mouse = mouse
        self.capture = capture
        self.visual = visual
        
        # Operation state flags
        self.operation_in_progress = False
        
        self.text_vars = {}
        
        # Create main window if not provided
        if root is None:
            self.root = tk.Tk()
        else:
            self.root = root
            
        self.setup_window()
        self.create_widgets()
        self.update_all_widgets()
    
    def setup_window(self):
        """Setup main window properties"""
        self.root.title("Configuration Editor")
        self.root.geometry("850x700")

        try:
            pos_x = int(getattr(self.cfg, 'config_gui_pos_x', 400))
            pos_y = int(getattr(self.cfg, 'config_gui_pos_y', 100))
            self.root.geometry(f"850x700+{pos_x}+{pos_y}")
        except Exception:
            pass

        self.root.resizable(True, True)
        
        try:
            if platform.system() == 'Windows':
                self.root.iconbitmap('media/logo.ico')
        except:
            pass
    
    def create_widgets(self):
        """Create all GUI widgets"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create all tabs
        self.create_detection_tab()
        self.create_capture_tab()
        self.create_aim_tab()
        self.create_hotkeys_tab()
        self.create_mouse_tab()
        self.create_arduino_tab()
        self.create_shooting_tab()
        self.create_ai_tab()
        self.create_overlay_tab()
        self.create_debug_tab()
        self.create_config_gui_tab()
        
        # Save/Reload buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        self.save_button = DebouncedButton(
            button_frame, 
            text="Save & Apply", 
            command=self.on_save_clicked
        )
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        self.reload_button = DebouncedButton(
            button_frame, 
            text="Reload from File", 
            command=self.on_reload_clicked
        )
        self.reload_button.pack(side=tk.LEFT, padx=5)
    
    def on_save_clicked(self):
        """Handle save button click with threading"""
        if self.operation_in_progress:
            return
        
        thread = threading.Thread(target=self._save_worker, daemon=True)
        thread.start()
    
    def on_reload_clicked(self):
        """Handle reload button click with threading"""
        if self.operation_in_progress:
            return
        
        thread = threading.Thread(target=self._reload_worker, daemon=True)
        thread.start()
    
    def _save_worker(self):
        """Worker thread for saving to prevent GUI freeze"""
        self.operation_in_progress = True
        try:
            self.root.config(cursor="watch")
            self.save_button.config(state='disabled')
            self.reload_button.config(state='disabled')
            
            print("[SAVE] Starting save operation...")
            self.save_all_changes()
            print("[SAVE] Save operation completed")
            
            self.root.after(0, lambda: messagebox.showinfo("Success", "Changes saved and applied!"))
        except Exception as e:
            print(f"[ERROR] Save failed: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Save failed: {e}"))
        finally:
            self.root.after(0, lambda: self.root.config(cursor=""))
            self.root.after(0, lambda: self.save_button.config(state='normal'))
            self.root.after(0, lambda: self.reload_button.config(state='normal'))
            self.operation_in_progress = False
    
    def _reload_worker(self):
        """Worker thread for reloading to prevent GUI freeze"""
        self.operation_in_progress = True
        try:
            self.root.config(cursor="watch")
            self.save_button.config(state='disabled')
            self.reload_button.config(state='disabled')
            
            print("[RELOAD] Starting reload operation...")
            self.reload_from_file()
            print("[RELOAD] Reload completed")
            
            self.root.after(0, lambda: messagebox.showinfo("Success", "Configuration reloaded from file!"))
        except Exception as e:
            print(f"[ERROR] Reload failed: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Reload failed: {e}"))
        finally:
            self.root.after(0, lambda: self.root.config(cursor=""))
            self.root.after(0, lambda: self.save_button.config(state='normal'))
            self.root.after(0, lambda: self.reload_button.config(state='normal'))
            self.operation_in_progress = False
    
    def save_all_changes(self):
        """Save all changes to config file and apply updates"""
        config_file = 'config.ini'
        if not os.path.exists(config_file):
            print("[WARNING] config.ini not found, will create it")
        
        # Read current config
        config = configparser.ConfigParser()
        config.read(config_file)
        
        # Ensure all sections exist
        sections = [
            'Detection window', 'Capture Methods', 'Aim', 'Hotkeys', 'Mouse',
            'Shooting', 'Arduino', 'AI', 'overlay', 'Debug window', 'Config GUI'
        ]
        for section in sections:
            if not config.has_section(section):
                config.add_section(section)
        
        # Save Detection window settings
        config.set('Detection window', 'detection_window_width', str(self.text_vars['detection_window_width'].get()))
        config.set('Detection window', 'detection_window_height', str(self.text_vars['detection_window_height'].get()))
        config.set('Detection window', 'circle_capture', str(self.text_vars['circle_capture'].get()))
        
        # Save Capture Methods settings
        config.set('Capture Methods', 'capture_fps', str(self.text_vars['capture_fps'].get()))
        config.set('Capture Methods', 'Bettercam_capture', str(self.text_vars['Bettercam_capture'].get()))
        config.set('Capture Methods', 'bettercam_monitor_id', str(self.text_vars['bettercam_monitor_id'].get()))
        config.set('Capture Methods', 'bettercam_gpu_id', str(self.text_vars['bettercam_gpu_id'].get()))
        config.set('Capture Methods', 'Obs_capture', str(self.text_vars['Obs_capture'].get()))
        config.set('Capture Methods', 'Obs_camera_id', str(self.text_vars['Obs_camera_id'].get()))
        config.set('Capture Methods', 'mss_capture', str(self.text_vars['mss_capture'].get()))
        
        # Save Aim settings
        config.set('Aim', 'body_y_offset', str(self.text_vars['body_y_offset'].get()))
        config.set('Aim', 'hideout_targets', str(self.text_vars['hideout_targets'].get()))
        config.set('Aim', 'disable_headshot', str(self.text_vars['disable_headshot'].get()))
        config.set('Aim', 'disable_prediction', str(self.text_vars['disable_prediction'].get()))
        config.set('Aim', 'prediction_interval', str(self.text_vars['prediction_interval'].get()))
        config.set('Aim', 'third_person', str(self.text_vars['third_person'].get()))
        
        # Save Hotkeys settings
        config.set('Hotkeys', 'hotkey_targeting', str(self.text_vars['hotkey_targeting'].get()))
        config.set('Hotkeys', 'hotkey_exit', str(self.text_vars['hotkey_exit'].get()))
        config.set('Hotkeys', 'hotkey_pause', str(self.text_vars['hotkey_pause'].get()))
        config.set('Hotkeys', 'hotkey_reload_config', str(self.text_vars['hotkey_reload_config'].get()))
        
        # Save Mouse settings
        config.set('Mouse', 'mouse_dpi', str(self.text_vars['mouse_dpi'].get()))
        config.set('Mouse', 'mouse_sensitivity', str(self.text_vars['mouse_sensitivity'].get()))
        config.set('Mouse', 'mouse_fov_width', str(self.text_vars['mouse_fov_width'].get()))
        config.set('Mouse', 'mouse_fov_height', str(self.text_vars['mouse_fov_height'].get()))
        config.set('Mouse', 'mouse_min_speed_multiplier', str(self.text_vars['mouse_min_speed_multiplier'].get()))
        config.set('Mouse', 'mouse_max_speed_multiplier', str(self.text_vars['mouse_max_speed_multiplier'].get()))
        config.set('Mouse', 'mouse_lock_target', str(self.text_vars['mouse_lock_target'].get()))
        config.set('Mouse', 'mouse_auto_aim', str(self.text_vars['mouse_auto_aim'].get()))
        config.set('Mouse', 'mouse_ghub', str(self.text_vars['mouse_ghub'].get()))
        config.set('Mouse', 'mouse_rzr', str(self.text_vars['mouse_rzr'].get()))
        
        # Save Shooting settings
        config.set('Shooting', 'auto_shoot', str(self.text_vars['auto_shoot'].get()))
        config.set('Shooting', 'triggerbot', str(self.text_vars['triggerbot'].get()))
        config.set('Shooting', 'force_click', str(self.text_vars['force_click'].get()))
        config.set('Shooting', 'bScope_multiplier', str(self.text_vars['bScope_multiplier'].get()))
        
        # Save Arduino settings
        config.set('Arduino', 'arduino_move', str(self.text_vars['arduino_move'].get()))
        config.set('Arduino', 'arduino_shoot', str(self.text_vars['arduino_shoot'].get()))
        config.set('Arduino', 'arduino_port', str(self.text_vars['arduino_port'].get()))
        config.set('Arduino', 'arduino_baudrate', str(self.text_vars['arduino_baudrate'].get()))
        config.set('Arduino', 'arduino_16_bit_mouse', str(self.text_vars['arduino_16_bit_mouse'].get()))
        
        # Save AI settings
        config.set('AI', 'AI_model_name', str(self.text_vars['AI_model_name'].get()))
        config.set('AI', 'AI_model_image_size', str(self.text_vars['AI_model_image_size'].get()))
        config.set('AI', 'AI_conf', str(self.text_vars['AI_conf'].get()))
        config.set('AI', 'AI_device', str(self.text_vars['AI_device'].get()))
        config.set('AI', 'AI_enable_AMD', str(self.text_vars['AI_enable_AMD'].get()))
        config.set('AI', 'disable_tracker', str(self.text_vars['disable_tracker'].get()))
        
        # Save Overlay settings
        config.set('overlay', 'show_overlay', str(self.text_vars['show_overlay'].get()))
        config.set('overlay', 'overlay_show_borders', str(self.text_vars['overlay_show_borders'].get()))
        config.set('overlay', 'overlay_show_boxes', str(self.text_vars['overlay_show_boxes'].get()))
        config.set('overlay', 'overlay_show_target_line', str(self.text_vars['overlay_show_target_line'].get()))
        config.set('overlay', 'overlay_show_target_prediction_line', str(self.text_vars['overlay_show_target_prediction_line'].get()))
        config.set('overlay', 'overlay_show_labels', str(self.text_vars['overlay_show_labels'].get()))
        config.set('overlay', 'overlay_show_conf', str(self.text_vars['overlay_show_conf'].get()))
        
        # Save Debug window settings
        config.set('Debug window', 'show_window', str(self.text_vars['show_window'].get()))
        config.set('Debug window', 'show_detection_speed', str(self.text_vars['show_detection_speed'].get()))
        config.set('Debug window', 'show_window_fps', str(self.text_vars['show_window_fps'].get()))
        config.set('Debug window', 'show_boxes', str(self.text_vars['show_boxes'].get()))
        config.set('Debug window', 'show_labels', str(self.text_vars['show_labels'].get()))
        config.set('Debug window', 'show_conf', str(self.text_vars['show_conf'].get()))
        config.set('Debug window', 'show_target_line', str(self.text_vars['show_target_line'].get()))
        config.set('Debug window', 'show_target_prediction_line', str(self.text_vars['show_target_prediction_line'].get()))
        config.set('Debug window', 'show_bScope_box', str(self.text_vars['show_bscope_box'].get()))
        config.set('Debug window', 'show_history_points', str(self.text_vars['show_history_points'].get()))
        config.set('Debug window', 'debug_window_always_on_top', str(self.text_vars['debug_window_always_on_top'].get()))
        config.set('Debug window', 'spawn_window_pos_x', str(self.text_vars['spawn_window_pos_x'].get()))
        config.set('Debug window', 'spawn_window_pos_y', str(self.text_vars['spawn_window_pos_y'].get()))
        config.set('Debug window', 'debug_window_scale_percent', str(self.text_vars['debug_window_scale_percent'].get()))
        config.set('Debug window', 'debug_window_screenshot_key', str(self.text_vars['debug_window_screenshot_key'].get()))
        
        # Save Config GUI settings
        config.set('Config GUI', 'config_gui_enabled', str(self.text_vars['config_gui_enabled'].get()))
        config.set('Config GUI', 'config_gui_pos_x', str(self.text_vars['config_gui_pos_x'].get()))
        config.set('Config GUI', 'config_gui_pos_y', str(self.text_vars['config_gui_pos_y'].get()))
        config.set('Config GUI', 'hotkey_toggle_config_editor', str(self.text_vars['hotkey_toggle_config_editor'].get()))
        
        # Write to file
        with open('config.ini', 'w') as f:
            config.write(f)
        print("[SAVE] Configuration written to config.ini")
        
        # Reload runtime config and apply
        self.reload_runtime_config()
    
    def reload_from_file(self):
        """Reload all values from config file and update GUI"""
        print("[RELOAD] Loading values from config.ini...")
        self.cfg.Read()
        self.update_all_widgets()
        self.reload_runtime_config()
    
    def reload_runtime_config(self):
        """Reload runtime components"""
        print("[RELOAD] Applying runtime configuration...")
        
        try:
            self.cfg.Read()
            print("[RELOAD] Config reloaded")
        except Exception as e:
            print(f"[ERROR] Failed to reload cfg: {e}")
        
        # Reload capture
        try:
            if self.capture and hasattr(self.capture, 'restart'):
                print("[RELOAD] Restarting capture...")
                self.capture.restart()
                print("[RELOAD] Capture restarted")
        except Exception as e:
            print(f"[ERROR] Failed to restart capture: {e}")
        
        # Update mouse
        try:
            if self.mouse and hasattr(self.mouse, 'update_settings'):
                print("[RELOAD] Updating mouse settings...")
                self.mouse.update_settings()
                print("[RELOAD] Mouse settings updated")
        except Exception as e:
            print(f"[ERROR] Failed to update mouse settings: {e}")
        
        # Update active classes
        try:
            if self.hotkeys_watcher and hasattr(self.hotkeys_watcher, 'clss'):
                print("[RELOAD] Updating active classes...")
                self.hotkeys_watcher.clss = self._get_active_classes(self.cfg)
                print(f"[RELOAD] Active classes: {self.hotkeys_watcher.clss}")
        except Exception as e:
            print(f"[ERROR] Failed to update active classes: {e}")
        
        # Update visuals
        try:
            if self.visual and hasattr(self.visual, 'start_if_not_running'):
                if self.cfg.show_overlay or self.cfg.show_window:
                    print("[RELOAD] Starting visuals...")
                    self.visual.start_if_not_running()
                    print("[RELOAD] Visuals thread started")
        except Exception as e:
            print(f"[ERROR] Failed to start visuals: {e}")
        
        print("[RELOAD] Runtime reload complete")
    
    def _get_active_classes(self, cfg):
        """Get active detection classes from config"""
        clss = [0.0, 1.0]
        
        if hasattr(cfg, 'hideout_targets') and cfg.hideout_targets:
            clss.extend([5.0, 6.0])
        
        if hasattr(cfg, 'disable_headshot') and not cfg.disable_headshot:
            clss.append(7.0)
            
        if hasattr(cfg, 'third_person') and cfg.third_person:
            clss.append(10.0)
        
        return clss
    
    def update_all_widgets(self):
        """Update all widget values from config"""
        print("[UPDATE] Updating all widgets...")
        current_tab = self.notebook.select()
        
        try:
            # Detection Window
            self.text_vars['detection_window_width'].set(self.cfg.detection_window_width)
            self.text_vars['detection_window_height'].set(self.cfg.detection_window_height)
            self.text_vars['circle_capture'].set(self.cfg.circle_capture)
            
            # Capture Methods
            self.text_vars['capture_fps'].set(self.cfg.capture_fps)
            self.text_vars['Bettercam_capture'].set(self.cfg.Bettercam_capture)
            self.text_vars['bettercam_monitor_id'].set(self.cfg.bettercam_monitor_id)
            self.text_vars['bettercam_gpu_id'].set(self.cfg.bettercam_gpu_id)
            self.text_vars['Obs_capture'].set(self.cfg.Obs_capture)
            self.text_vars['Obs_camera_id'].set(self.cfg.Obs_camera_id)
            self.text_vars['mss_capture'].set(self.cfg.mss_capture)
            
            # Aim
            self.text_vars['body_y_offset'].set(self.cfg.body_y_offset)
            self.text_vars['hideout_targets'].set(self.cfg.hideout_targets)
            self.text_vars['disable_headshot'].set(self.cfg.disable_headshot)
            self.text_vars['disable_prediction'].set(self.cfg.disable_prediction)
            self.text_vars['prediction_interval'].set(self.cfg.prediction_interval)
            self.text_vars['third_person'].set(self.cfg.third_person)
            
            # Hotkeys
            self.text_vars['hotkey_targeting'].set(self.cfg.hotkey_targeting)
            self.text_vars['hotkey_exit'].set(self.cfg.hotkey_exit)
            self.text_vars['hotkey_pause'].set(self.cfg.hotkey_pause)
            self.text_vars['hotkey_reload_config'].set(getattr(self.cfg, 'hotkey_reload_config', 'F4'))
            
            # Mouse
            self.text_vars['mouse_dpi'].set(self.cfg.mouse_dpi)
            self.text_vars['mouse_sensitivity'].set(self.cfg.mouse_sensitivity)
            self.text_vars['mouse_fov_width'].set(self.cfg.mouse_fov_width)
            self.text_vars['mouse_fov_height'].set(self.cfg.mouse_fov_height)
            self.text_vars['mouse_min_speed_multiplier'].set(self.cfg.mouse_min_speed_multiplier)
            self.text_vars['mouse_max_speed_multiplier'].set(self.cfg.mouse_max_speed_multiplier)
            self.text_vars['mouse_lock_target'].set(self.cfg.mouse_lock_target)
            self.text_vars['mouse_auto_aim'].set(self.cfg.mouse_auto_aim)
            self.text_vars['mouse_ghub'].set(self.cfg.mouse_ghub)
            self.text_vars['mouse_rzr'].set(self.cfg.mouse_rzr)
            
            # Shooting
            self.text_vars['auto_shoot'].set(self.cfg.auto_shoot)
            self.text_vars['triggerbot'].set(self.cfg.triggerbot)
            self.text_vars['force_click'].set(self.cfg.force_click)
            self.text_vars['bScope_multiplier'].set(self.cfg.bScope_multiplier)
            
            # Arduino
            self.text_vars['arduino_move'].set(self.cfg.arduino_move)
            self.text_vars['arduino_shoot'].set(self.cfg.arduino_shoot)
            self.text_vars['arduino_port'].set(self.cfg.arduino_port)
            self.text_vars['arduino_baudrate'].set(self.cfg.arduino_baudrate)
            self.text_vars['arduino_16_bit_mouse'].set(self.cfg.arduino_16_bit_mouse)
            
            # AI
            self.text_vars['AI_model_name'].set(self.cfg.AI_model_name)
            self.text_vars['AI_model_image_size'].set(self.cfg.ai_model_image_size)
            self.text_vars['AI_conf'].set(self.cfg.AI_conf)
            self.text_vars['AI_device'].set(self.cfg.AI_device)
            self.text_vars['AI_enable_AMD'].set(self.cfg.AI_enable_AMD)
            self.text_vars['disable_tracker'].set(self.cfg.disable_tracker)
            
            # Overlay
            self.text_vars['show_overlay'].set(self.cfg.show_overlay)
            self.text_vars['overlay_show_borders'].set(self.cfg.overlay_show_borders)
            self.text_vars['overlay_show_boxes'].set(self.cfg.overlay_show_boxes)
            self.text_vars['overlay_show_target_line'].set(self.cfg.overlay_show_target_line)
            self.text_vars['overlay_show_target_prediction_line'].set(self.cfg.overlay_show_target_prediction_line)
            self.text_vars['overlay_show_labels'].set(self.cfg.overlay_show_labels)
            self.text_vars['overlay_show_conf'].set(self.cfg.overlay_show_conf)
            
            # Debug Window
            self.text_vars['show_window'].set(self.cfg.show_window)
            self.text_vars['show_detection_speed'].set(self.cfg.show_detection_speed)
            self.text_vars['show_window_fps'].set(self.cfg.show_window_fps)
            self.text_vars['show_boxes'].set(self.cfg.show_boxes)
            self.text_vars['show_labels'].set(self.cfg.show_labels)
            self.text_vars['show_conf'].set(self.cfg.show_conf)
            self.text_vars['show_target_line'].set(self.cfg.show_target_line)
            self.text_vars['show_target_prediction_line'].set(self.cfg.show_target_prediction_line)
            self.text_vars['show_bscope_box'].set(getattr(self.cfg, 'show_bScope_box', False))
            self.text_vars['show_history_points'].set(self.cfg.show_history_points)
            self.text_vars['debug_window_always_on_top'].set(self.cfg.debug_window_always_on_top)
            self.text_vars['spawn_window_pos_x'].set(self.cfg.spawn_window_pos_x)
            self.text_vars['spawn_window_pos_y'].set(self.cfg.spawn_window_pos_y)
            self.text_vars['debug_window_scale_percent'].set(self.cfg.debug_window_scale_percent)
            self.text_vars['debug_window_screenshot_key'].set(self.cfg.debug_window_screenshot_key)
            
            # Config GUI
            self.text_vars['config_gui_enabled'].set(getattr(self.cfg, 'config_gui_enabled', True))
            self.text_vars['config_gui_pos_x'].set(getattr(self.cfg, 'config_gui_pos_x', 400))
            self.text_vars['config_gui_pos_y'].set(getattr(self.cfg, 'config_gui_pos_y', 100))
            self.text_vars['hotkey_toggle_config_editor'].set(getattr(self.cfg, 'hotkey_toggle_config_editor', 'F1'))
            
        except Exception as e:
            print(f"[WARNING] Error updating widgets: {e}")
        
        # Restore tab selection
        if current_tab in self.notebook.tabs():
            self.notebook.select(current_tab)
        
        print("[UPDATE] Widgets update complete")
    
    # Tab creation methods
    def create_detection_tab(self):
        """Create Detection Window tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Detection Window")
        
        outer_frame = ttk.Frame(frame)
        outer_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.add_slider(outer_frame, "Window Width", "detection_window_width", 200, 1920, 10)
        self.add_slider(outer_frame, "Window Height", "detection_window_height", 200, 1080, 10)
        self.add_checkbox(outer_frame, "Circle Capture", "circle_capture")
    
    def create_capture_tab(self):
        """Create Capture Methods tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Capture Methods")
        
        outer_frame = ttk.Frame(frame)
        outer_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.add_checkbox(outer_frame, "Enable Bettercam", "Bettercam_capture")
        self.add_text_entry(outer_frame, "Bettercam Monitor ID", "bettercam_monitor_id")
        self.add_text_entry(outer_frame, "Bettercam GPU ID", "bettercam_gpu_id")
        self.add_separator(outer_frame)
        self.add_checkbox(outer_frame, "Enable OBS Capture", "Obs_capture")
        self.add_text_entry(outer_frame, "OBS Camera ID", "Obs_camera_id")
        self.add_separator(outer_frame)
        self.add_checkbox(outer_frame, "Enable MSS Capture", "mss_capture")
        self.add_slider(outer_frame, "Capture FPS", "capture_fps", 30, 120, 1)
    
    def create_aim_tab(self):
        """Create Aim Settings tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Aim")
        
        outer_frame = ttk.Frame(frame)
        outer_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.add_slider(outer_frame, "Body Y Offset", "body_y_offset", 0.0, 0.5, 0.01)
        self.add_checkbox(outer_frame, "Hideout Targets", "hideout_targets")
        self.add_checkbox(outer_frame, "Disable Headshot", "disable_headshot")
        self.add_checkbox(outer_frame, "Disable Prediction", "disable_prediction")
        self.add_slider(outer_frame, "Prediction Interval", "prediction_interval", 0.5, 5.0, 0.1)
        self.add_checkbox(outer_frame, "Third Person", "third_person")
    
    def create_hotkeys_tab(self):
        """Create Hotkeys tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Hotkeys")
        
        outer_frame = ttk.Frame(frame)
        outer_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.add_text_entry(outer_frame, "Targeting", "hotkey_targeting")
        self.add_text_entry(outer_frame, "Exit", "hotkey_exit")
        self.add_text_entry(outer_frame, "Pause", "hotkey_pause")
        self.add_text_entry(outer_frame, "Reload Config", "hotkey_reload_config")
    
    def create_mouse_tab(self):
        """Create Mouse Settings tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Mouse")
        
        outer_frame = ttk.Frame(frame)
        outer_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.add_text_entry(outer_frame, "DPI", "mouse_dpi")
        self.add_slider(outer_frame, "Sensitivity", "mouse_sensitivity", 0.5, 10.0, 0.1)
        self.add_slider(outer_frame, "FOV Width", "mouse_fov_width", 20, 200, 5)
        self.add_slider(outer_frame, "FOV Height", "mouse_fov_height", 20, 200, 5)
        self.add_slider(outer_frame, "Min Speed Multiplier", "mouse_min_speed_multiplier", 0.5, 3.0, 0.1)
        self.add_slider(outer_frame, "Max Speed Multiplier", "mouse_max_speed_multiplier", 0.5, 3.0, 0.1)
        self.add_checkbox(outer_frame, "Lock Target", "mouse_lock_target")
        self.add_checkbox(outer_frame, "Auto Aim", "mouse_auto_aim")
        self.add_separator(outer_frame)
        self.add_checkbox(outer_frame, "GHub Mode", "mouse_ghub")
        self.add_checkbox(outer_frame, "Razer Mode", "mouse_rzr")
    
    def create_arduino_tab(self):
        """Create Arduino tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Arduino")
        
        outer_frame = ttk.Frame(frame)
        outer_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.add_checkbox(outer_frame, "Move", "arduino_move")
        self.add_checkbox(outer_frame, "Shoot", "arduino_shoot")
        self.add_text_entry(outer_frame, "Port", "arduino_port")
        self.add_text_entry(outer_frame, "Baudrate", "arduino_baudrate")
        self.add_checkbox(outer_frame, "16-bit Mouse", "arduino_16_bit_mouse")
    
    def create_shooting_tab(self):
        """Create Shooting tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Shooting")
        
        outer_frame = ttk.Frame(frame)
        outer_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.add_checkbox(outer_frame, "Auto Shoot", "auto_shoot")
        self.add_checkbox(outer_frame, "Triggerbot", "triggerbot")
        self.add_checkbox(outer_frame, "Force Click", "force_click")
        self.add_slider(outer_frame, "Scope Multiplier", "bScope_multiplier", 0.5, 3.0, 0.1)
    
    def create_ai_tab(self):
        """Create AI Settings tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="AI")
        
        outer_frame = ttk.Frame(frame)
        outer_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.add_text_entry(outer_frame, "Model Name", "AI_model_name")
        self.add_text_entry(outer_frame, "Model Image Size", "AI_model_image_size")
        self.add_slider(outer_frame, "Confidence Threshold", "AI_conf", 0.1, 0.9, 0.05)
        self.add_text_entry(outer_frame, "Device", "AI_device")
        self.add_checkbox(outer_frame, "Enable AMD", "AI_enable_AMD")
        self.add_checkbox(outer_frame, "Disable Tracker", "disable_tracker")
    
    def create_overlay_tab(self):
        """Create Overlay tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Overlay")
        
        outer_frame = ttk.Frame(frame)
        outer_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.add_checkbox(outer_frame, "Show Overlay", "show_overlay")
        self.add_separator(outer_frame)
        self.add_checkbox(outer_frame, "Show Borders", "overlay_show_borders")
        self.add_checkbox(outer_frame, "Show Boxes", "overlay_show_boxes")
        self.add_checkbox(outer_frame, "Show Target Line", "overlay_show_target_line")
        self.add_checkbox(outer_frame, "Show Prediction Line", "overlay_show_target_prediction_line")
        self.add_checkbox(outer_frame, "Show Labels", "overlay_show_labels")
        self.add_checkbox(outer_frame, "Show Confidence", "overlay_show_conf")
    
    def create_debug_tab(self):
        """Create Debug Window tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Debug")
        
        outer_frame = ttk.Frame(frame)
        outer_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.add_checkbox(outer_frame, "Show Window", "show_window")
        self.add_separator(outer_frame)
        self.add_checkbox(outer_frame, "Show Detection Speed", "show_detection_speed")
        self.add_checkbox(outer_frame, "Show Window FPS", "show_window_fps")
        self.add_checkbox(outer_frame, "Show Boxes", "show_boxes")
        self.add_checkbox(outer_frame, "Show Labels", "show_labels")
        self.add_checkbox(outer_frame, "Show Confidence", "show_conf")
        self.add_checkbox(outer_frame, "Show Target Line", "show_target_line")
        self.add_checkbox(outer_frame, "Show Prediction Line", "show_target_prediction_line")
        self.add_checkbox(outer_frame, "Show BScope Box", "show_bscope_box")
        self.add_checkbox(outer_frame, "Show History", "show_history_points")
        self.add_separator(outer_frame)
        self.add_checkbox(outer_frame, "Always On Top", "debug_window_always_on_top")
        self.add_text_entry(outer_frame, "Window X Position", "spawn_window_pos_x")
        self.add_text_entry(outer_frame, "Window Y Position", "spawn_window_pos_y")
        self.add_slider(outer_frame, "Window Scale (%)", "debug_window_scale_percent", 50, 200, 10)
        self.add_text_entry(outer_frame, "Screenshot Key", "debug_window_screenshot_key")

    def create_config_gui_tab(self):
        """Create Config GUI tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Config GUI")

        outer_frame = ttk.Frame(frame)
        outer_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.add_checkbox(outer_frame, "Enable Config GUI", "config_gui_enabled")
        self.add_text_entry(outer_frame, "GUI X Position", "config_gui_pos_x")
        self.add_text_entry(outer_frame, "GUI Y Position", "config_gui_pos_y")
        self.add_text_entry(outer_frame, "Toggle Hotkey", "hotkey_toggle_config_editor")
    
    # Widget helper methods
    def add_slider(self, parent, label_text, var_name, min_val, max_val, step):
        """Add a slider widget"""
        row = parent.grid_size()[1]
        
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=3)
        
        ttk.Label(frame, text=label_text, width=20).pack(side=tk.LEFT, padx=(0, 10))
        
        var = tk.DoubleVar() if isinstance(min_val, float) else tk.IntVar()
        self.text_vars[var_name] = var
        
        slider = ttk.Scale(frame, from_=min_val, to=max_val, variable=var, length=200)
        slider.pack(side=tk.LEFT)
        
        value_label = ttk.Label(frame, textvariable=var, width=8)
        value_label.pack(side=tk.LEFT, padx=(10, 0))
    
    def add_checkbox(self, parent, label_text, var_name):
        """Add a checkbox widget"""
        row = parent.grid_size()[1]
        
        var = tk.BooleanVar()
        self.text_vars[var_name] = var
        
        cb = ttk.Checkbutton(parent, text=label_text, variable=var)
        cb.grid(row=row, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)
    
    def add_text_entry(self, parent, label_text, var_name):
        """Add a text entry widget"""
        row = parent.grid_size()[1]
        
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=3)
        
        ttk.Label(frame, text=label_text, width=15).pack(side=tk.LEFT)
        
        var = tk.StringVar()
        self.text_vars[var_name] = var
        
        entry = ttk.Entry(frame, textvariable=var, width=25)
        entry.pack(side=tk.LEFT, padx=10)
    
    def add_separator(self, parent):
        """Add a separator"""
        sep = ttk.Separator(parent, orient=tk.HORIZONTAL)
        sep.grid(row=parent.grid_size()[1], column=0, columnspan=2, sticky=(tk.W, tk.E), pady=8)
    
    def show(self):
        """Show the GUI"""
        self.root.mainloop()
    
    def close(self):
        """Close the GUI"""
        if hasattr(self, 'root'):
            self.root.quit()

def create_config_gui(config, hotkeys_watcher=None, mouse=None, capture=None, visual=None):
    """Convenience function to create and run the config GUI"""
    gui = ConfigGUI(config, hotkeys_watcher, mouse, capture, visual)
    return gui


class ConfigGUIThread(threading.Thread):
    def __init__(self, config, hotkeys_watcher=None, mouse=None, capture=None, visual=None):
        super().__init__(daemon=True, name="ConfigGUIThread")
        self.cfg = config
        self.hotkeys_watcher = hotkeys_watcher
        self.mouse = mouse
        self.capture = capture
        self.visual = visual

        self.gui = None
        self._commands = queue.Queue()

    def run(self):
        self.gui = ConfigGUI(self.cfg, self.hotkeys_watcher, self.mouse, self.capture, self.visual)

        def on_close():
            self.hide()

        self.gui.root.protocol("WM_DELETE_WINDOW", on_close)
        self.gui.root.after(100, self._process_commands)
        self.gui.show()

    def _process_commands(self):
        if not self.gui or not hasattr(self.gui, 'root'):
            return

        try:
            while True:
                cmd = self._commands.get_nowait()
                if cmd == "toggle":
                    if self.gui.root.state() == "withdrawn":
                        self.gui.root.deiconify()
                    else:
                        self.gui.root.withdraw()
                elif cmd == "show":
                    self.gui.root.deiconify()
                elif cmd == "hide":
                    self.gui.root.withdraw()
        except queue.Empty:
            pass

        try:
            self.gui.root.after(100, self._process_commands)
        except Exception:
            pass

    def toggle_visibility(self):
        self._commands.put("toggle")

    def show_window(self):
        self._commands.put("show")

    def hide(self):
        self._commands.put("hide")


def launch_config_gui():
    """Launch the config editor GUI in a background thread."""
    from logic.config_watcher import cfg
    from logic.capture import capture
    from logic.mouse import mouse
    from logic.visual import visuals

    try:
        from logic.hotkeys_watcher import hotkeys_watcher
    except Exception:
        hotkeys_watcher = None

    gui_thread = ConfigGUIThread(cfg, hotkeys_watcher=hotkeys_watcher, mouse=mouse, capture=capture, visual=visuals)
    gui_thread.start()
    return gui_thread


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from helper import cfg
    
    gui = ConfigGUI(cfg, None, None, None, None)
    gui.show()