import PySimpleGUI as sg

def draw_shooting(cfg):
    """Returns PySimpleGUI layout for shooting settings"""
    layout = [
        [sg.Text("Shooting Settings", font=("Arial", 12, "bold"))],
        [sg.Checkbox("Auto Shoot", default=cfg.auto_shoot, key='-AUTO_SHOOT-', enable_events=True)],
        [sg.Checkbox("Triggerbot", default=cfg.triggerbot, key='-TRIGGERBOT-', enable_events=True)],
        [sg.Checkbox("Force Click", default=cfg.force_click, key='-FORCE_CLICK-', enable_events=True)],
        [sg.Text("bScope Multiplier:"), sg.Slider(range=(0.1, 5.0), resolution=0.1, default_value=cfg.bScope_multiplier, orientation='h', key='-BSCOPE_MULTIPLIER-', enable_events=True)],
    ]
    return layout
