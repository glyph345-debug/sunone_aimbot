import PySimpleGUI as sg

def draw_game_overlay(cfg):
    """Returns PySimpleGUI layout for game overlay settings"""
    layout = [
        [sg.Text("Game Overlay Settings", font=("Arial", 12, "bold"))],
        [sg.Checkbox("Show Overlay", default=cfg.show_overlay, key='-SHOW_OVERLAY-', enable_events=True)],
        [sg.Checkbox("Show Borders", default=cfg.overlay_show_borders, key='-OVERLAY_SHOW_BORDERS-', enable_events=True)],
        [sg.Checkbox("Show Boxes", default=cfg.overlay_show_boxes, key='-OVERLAY_SHOW_BOXES-', enable_events=True)],
        [sg.Checkbox("Show Target Line", default=cfg.overlay_show_target_line, key='-OVERLAY_SHOW_TARGET_LINE-', enable_events=True)],
        [sg.Checkbox("Show Target Prediction Line", default=cfg.overlay_show_target_prediction_line, key='-OVERLAY_SHOW_TARGET_PREDICTION_LINE-', enable_events=True)],
        [sg.Checkbox("Show Labels", default=cfg.overlay_show_labels, key='-OVERLAY_SHOW_LABELS-', enable_events=True)],
        [sg.Checkbox("Show Confidence", default=cfg.overlay_show_conf, key='-OVERLAY_SHOW_CONF-', enable_events=True)],
    ]
    return layout
