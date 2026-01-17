import PySimpleGUI as sg

def draw_depth(cfg):
    """Returns PySimpleGUI layout for depth settings"""
    layout = [
        [sg.Text("Depth Settings (Future)", font=("Arial", 12, "bold"))],
        [sg.Text("Depth Model Path:"), sg.Input("", key='-DEPTH_MODEL_PATH-', enable_events=True, disabled=True)],
        [sg.Checkbox("Enable Depth", default=False, key='-DEPTH_ENABLE-', enable_events=True, disabled=True)],
        [sg.Text("These settings are currently not implemented in the logic.")],
    ]
    return layout
