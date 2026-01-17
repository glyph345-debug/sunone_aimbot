import PySimpleGUI as sg

def draw_debug(cfg):
    """Returns PySimpleGUI layout for debug settings"""
    layout = [
        [sg.Text("Debug Settings", font=("Arial", 12, "bold"))],
        [sg.Checkbox("Show Debug Window", default=cfg.show_window, key='-SHOW_WINDOW-', enable_events=True)],
        [sg.Checkbox("Show Detection Speed", default=cfg.show_detection_speed, key='-SHOW_DETECTION_SPEED-', enable_events=True)],
        [sg.Checkbox("Show Window FPS", default=cfg.show_window_fps, key='-SHOW_WINDOW_FPS-', enable_events=True)],
        [sg.Checkbox("Show Boxes", default=cfg.show_boxes, key='-SHOW_BOXES-', enable_events=True)],
        [sg.Checkbox("Show Labels", default=cfg.show_labels, key='-SHOW_LABELS-', enable_events=True)],
        [sg.Checkbox("Show Confidence", default=cfg.show_conf, key='-SHOW_CONF-', enable_events=True)],
        [sg.Checkbox("Show Target Line", default=cfg.show_target_line, key='-SHOW_TARGET_LINE-', enable_events=True)],
        [sg.Checkbox("Show Target Prediction Line", default=cfg.show_target_prediction_line, key='-SHOW_TARGET_PREDICTION_LINE-', enable_events=True)],
        [sg.Checkbox("Show bScope Box", default=cfg.show_bScope_box, key='-SHOW_BSCOPE_BOX-', enable_events=True)],
        [sg.Checkbox("Show History Points", default=cfg.show_history_points, key='-SHOW_HISTORY_POINTS-', enable_events=True)],
        [sg.Checkbox("Always On Top", default=cfg.debug_window_always_on_top, key='-DEBUG_WINDOW_ALWAYS_ON_TOP-', enable_events=True)],
        [sg.Text("Window Position X:"), sg.Slider(range=(0, 3840), default_value=cfg.spawn_window_pos_x, orientation='h', key='-SPAWN_WINDOW_POS_X-', enable_events=True)],
        [sg.Text("Window Position Y:"), sg.Slider(range=(0, 2160), default_value=cfg.spawn_window_pos_y, orientation='h', key='-SPAWN_WINDOW_POS_Y-', enable_events=True)],
        [sg.Text("Window Scale Percent:"), sg.Slider(range=(50, 200), default_value=cfg.debug_window_scale_percent, orientation='h', key='-DEBUG_WINDOW_SCALE_PERCENT-', enable_events=True)],
        [sg.Text("Screenshot Key:"), sg.Input(cfg.debug_window_screenshot_key, key='-DEBUG_WINDOW_SCREENSHOT_KEY-', enable_events=True)],
    ]
    return layout
