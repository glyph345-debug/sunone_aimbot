import PySimpleGUI as sg

def draw_mouse(cfg):
    """Returns PySimpleGUI layout for mouse settings"""
    layout = [
        [sg.Text("Mouse Settings", font=("Arial", 12, "bold"))],
        [sg.Text("Mouse DPI:"), sg.Slider(range=(100, 20000), default_value=cfg.mouse_dpi, orientation='h', key='-MOUSE_DPI-', enable_events=True)],
        [sg.Text("Mouse Sensitivity:"), sg.Slider(range=(0.1, 10.0), resolution=0.1, default_value=cfg.mouse_sensitivity, orientation='h', key='-MOUSE_SENSITIVITY-', enable_events=True)],
        [sg.Text("FOV Width:"), sg.Slider(range=(10, 500), default_value=cfg.mouse_fov_width, orientation='h', key='-MOUSE_FOV_WIDTH-', enable_events=True)],
        [sg.Text("FOV Height:"), sg.Slider(range=(10, 500), default_value=cfg.mouse_fov_height, orientation='h', key='-MOUSE_FOV_HEIGHT-', enable_events=True)],
        [sg.Text("Min Speed Multiplier:"), sg.Slider(range=(0.1, 5.0), resolution=0.1, default_value=cfg.mouse_min_speed_multiplier, orientation='h', key='-MOUSE_MIN_SPEED_MULTIPLIER-', enable_events=True)],
        [sg.Text("Max Speed Multiplier:"), sg.Slider(range=(0.1, 5.0), resolution=0.1, default_value=cfg.mouse_max_speed_multiplier, orientation='h', key='-MOUSE_MAX_SPEED_MULTIPLIER-', enable_events=True)],
        [sg.Checkbox("Lock Target", default=cfg.mouse_lock_target, key='-MOUSE_LOCK_TARGET-', enable_events=True)],
        [sg.Checkbox("Auto Aim", default=cfg.mouse_auto_aim, key='-MOUSE_AUTO_AIM-', enable_events=True)],
        [sg.Checkbox("G HUB Support", default=cfg.mouse_ghub, key='-MOUSE_GHUB-', enable_events=True)],
        [sg.Checkbox("Razer Support", default=cfg.mouse_rzr, key='-MOUSE_RZR-', enable_events=True)],
    ]
    return layout
