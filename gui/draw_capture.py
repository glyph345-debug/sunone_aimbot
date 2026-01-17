import imgui


def draw_capture(cfg):
    """Draw capture settings section"""
    
    # Capture FPS
    changed, value = imgui.slider_int("Capture FPS", cfg.capture_fps, 1, 240)
    if changed:
        cfg.capture_fps = value
        cfg.save()
    
    # Bettercam capture
    changed, value = imgui.checkbox("Bettercam Capture", cfg.Bettercam_capture)
    if changed:
        cfg.Bettercam_capture = value
        cfg.save()
    
    if cfg.Bettercam_capture:
        changed, value = imgui.slider_int("Monitor ID", cfg.bettercam_monitor_id, 0, 10)
        if changed:
            cfg.bettercam_monitor_id = value
            cfg.save()
        
        changed, value = imgui.slider_int("GPU ID", cfg.bettercam_gpu_id, 0, 10)
        if changed:
            cfg.bettercam_gpu_id = value
            cfg.save()
    
    # OBS capture
    changed, value = imgui.checkbox("OBS Capture", cfg.Obs_capture)
    if changed:
        cfg.Obs_capture = value
        cfg.save()
    
    if cfg.Obs_capture:
        imgui.text("OBS Camera ID:")
        imgui.same_line()
        imgui.push_item_width(200)
        changed, value = imgui.input_text("##obs_camera_id", cfg.Obs_camera_id, 10)
        imgui.pop_item_width()
        if changed:
            cfg.Obs_camera_id = value
            cfg.save()
    
    # MSS capture
    changed, value = imgui.checkbox("MSS Capture", cfg.mss_capture)
    if changed:
        cfg.mss_capture = value
        cfg.save()
    
    # Circle capture
    imgui.separator()
    changed, value = imgui.checkbox("Circle Capture", cfg.circle_capture)
    if changed:
        cfg.circle_capture = value
        cfg.save()
    
    # Detection window size
    changed, value = imgui.slider_int("Detection Width", cfg.detection_window_width, 320, 1920)
    if changed:
        cfg.detection_window_width = value
        cfg.save()
    
    changed, value = imgui.slider_int("Detection Height", cfg.detection_window_height, 320, 1080)
    if changed:
        cfg.detection_window_height = value
        cfg.save()
