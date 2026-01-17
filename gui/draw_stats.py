import PySimpleGUI as sg

def draw_stats(cfg):
    """Returns PySimpleGUI layout for performance statistics"""
    layout = [
        [sg.Text("Performance Statistics", font=("Arial", 12, "bold"))],
        [sg.Text("GUI FPS:"), sg.Text("0", key='-GUI_FPS-')],
        [sg.Text("Detected Objects:"), sg.Text("0", key='-DETECTED_OBJECTS-')],
        [sg.Separator()],
        [sg.Text("Performance Info")],
        [sg.Text("This section shows real-time performance")],
        [sg.Text("statistics from the aimbot system.")],
    ]
    return layout
