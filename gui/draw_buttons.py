import PySimpleGUI as sg

def draw_buttons(cfg):
    """Returns PySimpleGUI layout for hotkey configuration"""
    keys = ["F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"]
    mouse_keys = ["LeftMouseButton", "RightMouseButton", "MiddleMouseButton", "XButton1", "XButton2"]
    
    layout = [
        [sg.Text("Hotkey Configuration", font=("Arial", 12, "bold"))],
        [sg.Text("Targeting Hotkey:"), sg.Combo(mouse_keys, default_value=cfg.hotkey_targeting, key='-HOTKEY_TARGETING-', enable_events=True, readonly=True)],
        [sg.Text("Exit Hotkey:"), sg.Combo(keys, default_value=cfg.hotkey_exit, key='-HOTKEY_EXIT-', enable_events=True, readonly=True)],
        [sg.Text("Pause Hotkey:"), sg.Combo(keys, default_value=cfg.hotkey_pause, key='-HOTKEY_PAUSE-', enable_events=True, readonly=True)],
        [sg.Text("Reload Config Hotkey:"), sg.Combo(keys, default_value=cfg.hotkey_reload_config, key='-HOTKEY_RELOAD_CONFIG-', enable_events=True, readonly=True)],
    ]
    return layout
