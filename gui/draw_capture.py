import PySimpleGUI as sg

def draw_capture(cfg):
    """Returns PySimpleGUI layout for capture settings"""
    layout = [
        [sg.Text("Capture Settings", font=("Arial", 12, "bold"))],
        [sg.Text("Capture FPS:"), sg.Slider(range=(1, 240), default_value=cfg.capture_fps, orientation='h', key='-CAPTURE_FPS-', enable_events=True)],
        
        [sg.Checkbox("Bettercam Capture", default=cfg.Bettercam_capture, key='-BETTERCAM_CAPTURE-', enable_events=True)],
        [sg.Text("  Monitor ID:"), sg.Slider(range=(0, 10), default_value=cfg.bettercam_monitor_id, orientation='h', key='-BETTERCAM_MONITOR_ID-', enable_events=True)],
        [sg.Text("  GPU ID:"), sg.Slider(range=(0, 10), default_value=cfg.bettercam_gpu_id, orientation='h', key='-BETTERCAM_GPU_ID-', enable_events=True)],
        
        [sg.Checkbox("OBS Capture", default=cfg.Obs_capture, key='-OBS_CAPTURE-', enable_events=True)],
        [sg.Text("  OBS Camera ID:"), sg.Input(cfg.Obs_camera_id, key='-OBS_CAMERA_ID-', enable_events=True)],
        
        [sg.Checkbox("MSS Capture", default=cfg.mss_capture, key='-MSS_CAPTURE-', enable_events=True)],
        
        [sg.Separator()],
        [sg.Checkbox("Circle Capture", default=cfg.circle_capture, key='-CIRCLE_CAPTURE-', enable_events=True)],
        [sg.Text("Detection Width:"), sg.Slider(range=(320, 1920), default_value=cfg.detection_window_width, orientation='h', key='-DETECTION_WINDOW_WIDTH-', enable_events=True)],
        [sg.Text("Detection Height:"), sg.Slider(range=(320, 1080), default_value=cfg.detection_window_height, orientation='h', key='-DETECTION_WINDOW_HEIGHT-', enable_events=True)],
    ]
    return layout
