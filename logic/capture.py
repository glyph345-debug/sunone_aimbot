import cv2
import bettercam
import mss
from screeninfo import get_monitors
import threading
import queue
import numpy as np

from logic.config_watcher import cfg
from logic.logger import logger

class Capture(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.name = "Capture"
        
        self.print_startup_messages()
        
        self._custom_region = []
        self._offset_x = None
        self._offset_y = None
        self._lock = threading.RLock()

        self.screen_x_center = int(cfg.detection_window_width / 2)
        self.screen_y_center = int(cfg.detection_window_height / 2)

        self.prev_detection_window_width = cfg.detection_window_width
        self.prev_detection_window_height = cfg.detection_window_height
        self.prev_capture_fps = cfg.capture_fps
        self.prev_bettercam_monitor_id = cfg.bettercam_monitor_id
        self.prev_bettercam_gpu_id = cfg.bettercam_gpu_id
        self.prev_obs_camera_id = cfg.Obs_camera_id
        
        self.frame_queue = queue.Queue(maxsize=1)
        
        self.sct = None
        
        self.running = True
    
        self.current_method = None
        if cfg.Bettercam_capture:
            self.setup_bettercam()
            self.current_method = 'bettercam'
        elif cfg.Obs_capture:
            self.setup_obs()
            self.current_method = 'obs'
        elif cfg.mss_capture:
            self.setup_mss()
            self.current_method = 'mss'

    def setup_bettercam(self):
        self.bc = bettercam.create(
            device_idx=cfg.bettercam_monitor_id,
            output_idx=cfg.bettercam_gpu_id,
            output_color="BGR",
            max_buffer_len=16,
            region=self.calculate_screen_offset()
        )
        if not self.bc.is_capturing:
            self.bc.start(
                region=self.calculate_screen_offset(
                    custom_region=[] if len(self._custom_region) == 0 else self._custom_region,
                    x_offset=self._offset_x if self._offset_x is not None else 0,
                    y_offset=self._offset_y if self._offset_y is not None else 0
                ),
                target_fps=cfg.capture_fps
            )

    def setup_obs(self):
        camera_id = self.find_obs_virtual_camera() if cfg.Obs_camera_id == 'auto' else int(cfg.Obs_camera_id) if cfg.Obs_camera_id.isdigit() else None
        if camera_id is None:
            logger.info('[Capture] OBS Virtual Camera not found')
            exit(0)
        
        self.obs_camera = cv2.VideoCapture(camera_id)
        self.obs_camera.set(cv2.CAP_PROP_FRAME_WIDTH, cfg.detection_window_width)
        self.obs_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg.detection_window_height)
        self.obs_camera.set(cv2.CAP_PROP_FPS, cfg.capture_fps)

    def setup_mss(self):
        left, top, width, height = self.calculate_mss_offset()
        self.monitor = {"left": left, "top": top, "width": width, "height": height}

    def run(self):
        try:
            while self.running:
                if cfg.mss_capture and self.sct is None:
                    with self._lock:
                        if cfg.mss_capture and self.sct is None:
                            self.sct = mss.mss()
                            if not hasattr(self, 'monitor'):
                                self.setup_mss()

                frame = self.capture_frame()
                if frame is not None:
                    if self.frame_queue.full():
                        self.frame_queue.get()
                    self.frame_queue.put(frame, block=False)
        finally:
            if self.sct is not None:
                self.sct.close()
            
    def capture_frame(self):
        with self._lock:
            if cfg.Bettercam_capture:
                if not hasattr(self, 'bc'):
                    self.setup_bettercam()
                    self.current_method = 'bettercam'
                return self.bc.get_latest_frame()
            
            if cfg.Obs_capture:
                if not hasattr(self, 'obs_camera'):
                    self.setup_obs()
                    self.current_method = 'obs'
                ret_val, img = self.obs_camera.read()
                return img if ret_val else None

            if cfg.mss_capture:
                if self.sct is None:
                    self.sct = mss.mss()
                if not hasattr(self, 'monitor'):
                    self.setup_mss()
                screenshot = self.sct.grab(self.monitor)
                img = np.frombuffer(screenshot.bgra, np.uint8).reshape((screenshot.height, screenshot.width, 4))
                return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    def get_new_frame(self):
        try:
            return self.frame_queue.get(timeout=1)
        except queue.Empty:
            return None
    
    def _get_selected_method(self):
        if cfg.Bettercam_capture:
            return 'bettercam'
        if cfg.Obs_capture:
            return 'obs'
        if cfg.mss_capture:
            return 'mss'
        return self.current_method or 'bettercam'

    def _shutdown_bettercam(self):
        if hasattr(self, 'bc'):
            try:
                self.bc.stop()
            except Exception:
                pass
            try:
                del self.bc
            except Exception:
                pass

    def _shutdown_obs(self):
        if hasattr(self, 'obs_camera'):
            try:
                self.obs_camera.release()
            except Exception:
                pass
            try:
                del self.obs_camera
            except Exception:
                pass

    def _shutdown_mss(self):
        if self.sct is not None:
            try:
                self.sct.close()
            except Exception:
                pass
            self.sct = None

    def _shutdown_all(self):
        self._shutdown_bettercam()
        self._shutdown_obs()
        self._shutdown_mss()

    def restart(self):
        with self._lock:
            desired_method = self._get_selected_method()

            method_changed = desired_method != self.current_method and desired_method is not None
            size_changed = (
                self.prev_detection_window_width != cfg.detection_window_width or
                self.prev_detection_window_height != cfg.detection_window_height
            )
            fps_changed = self.prev_capture_fps != cfg.capture_fps

            bettercam_device_changed = (
                self.prev_bettercam_monitor_id != cfg.bettercam_monitor_id or
                self.prev_bettercam_gpu_id != cfg.bettercam_gpu_id
            )
            obs_device_changed = self.prev_obs_camera_id != cfg.Obs_camera_id

            if method_changed:
                self._shutdown_all()
                if desired_method == 'bettercam':
                    self.setup_bettercam()
                elif desired_method == 'obs':
                    self.setup_obs()
                elif desired_method == 'mss':
                    self.setup_mss()
                    if self.sct is None:
                        self.sct = mss.mss()

                self.current_method = desired_method
                logger.info(f'[Capture] Capture method switched to {desired_method}')

            if self.current_method == 'bettercam' and (size_changed or fps_changed or bettercam_device_changed):
                self._shutdown_bettercam()
                self.setup_bettercam()
                logger.info('[Capture] Bettercam capture reloaded')
            elif self.current_method == 'obs' and (size_changed or fps_changed or obs_device_changed):
                self._shutdown_obs()
                self.setup_obs()
                logger.info('[Capture] OBS capture reloaded')
            elif self.current_method == 'mss' and size_changed:
                self.setup_mss()
                logger.info('[Capture] MSS capture region reloaded')

            self.screen_x_center = int(cfg.detection_window_width / 2)
            self.screen_y_center = int(cfg.detection_window_height / 2)

            self.prev_detection_window_width = cfg.detection_window_width
            self.prev_detection_window_height = cfg.detection_window_height
            self.prev_capture_fps = cfg.capture_fps
            self.prev_bettercam_monitor_id = cfg.bettercam_monitor_id
            self.prev_bettercam_gpu_id = cfg.bettercam_gpu_id
            self.prev_obs_camera_id = cfg.Obs_camera_id

    def calculate_screen_offset(self, custom_region=[], x_offset=None, y_offset=None):
        if x_offset is None:
            x_offset = 0
        if y_offset is None:
            y_offset = 0
        
        if not custom_region:
            left, top = self.get_primary_display_resolution()
        else:
            left, top = custom_region
        
        left = left / 2 - cfg.detection_window_width / 2 + x_offset
        top = top / 2 - cfg.detection_window_height / 2 - y_offset
        width = cfg.detection_window_width
        height = cfg.detection_window_height
        
        return (int(left), int(top), int(width), int(height))

    def calculate_mss_offset(self):
        x, y = self.get_primary_display_resolution()
        left = x / 2 - cfg.detection_window_width / 2
        top = y / 2 - cfg.detection_window_height / 2
        return int(left), int(top), int(cfg.detection_window_width), int(cfg.detection_window_height)

    def get_primary_display_resolution(self):
        for m in get_monitors():
            if m.is_primary:
                return m.width, m.height
            
    def find_obs_virtual_camera(self):
        max_tested = 20
        obs_camera_name = 'DSHOW'
        
        for i in range(max_tested):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if not cap.isOpened():
                continue
            if cap.getBackendName() == obs_camera_name:
                logger.info(f'[Capture] OBS Virtual Camera found at index {i}')
                cap.release()
                return i
            cap.release()
        return -1
    
    def print_startup_messages(self):
        version = 0
        try:
            with open('./version', 'r') as f:
                version = f.readline().split('=')[1].strip()
        except FileNotFoundError:
            logger.info('(version file is not found)')
        except Exception as e:
            logger.info(f'Error with read version file: {str(e)}')

        logger.info(f"""
Sunone Aimbot is started! (Version {version})
Hotkeys:
[{cfg.hotkey_targeting}] - Aiming at the target
[{cfg.hotkey_exit}] - EXIT
[{cfg.hotkey_pause}] - PAUSE AIM
[{cfg.hotkey_reload_config}] - Reload config
""")
    
    def convert_to_circle(self, image):
        height, width = image.shape[:2]
        mask = np.zeros((height, width), dtype=np.uint8)
        cv2.ellipse(mask, (width // 2, height // 2), (width // 2, height // 2), 0, 0, 360, 255, -1)
        return cv2.bitwise_and(image, cv2.merge([mask, mask, mask]))

    def Quit(self):
        self.running = False

        if hasattr(self, 'bc'):
            try:
                if getattr(self.bc, 'is_capturing', False):
                    self.bc.stop()
            except Exception:
                pass

        if hasattr(self, 'obs_camera'):
            try:
                self.obs_camera.release()
            except Exception:
                pass

        if self.sct is not None:
            try:
                self.sct.close()
            except Exception:
                pass
            self.sct = None

        self.join()

capture = Capture()
capture.start()