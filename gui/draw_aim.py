import PySimpleGUI as sg

def draw_aim(cfg):
    """Returns PySimpleGUI layout for aim settings"""
    layout = [
        [sg.Text("Aim Settings", font=("Arial", 12, "bold"))],
        [sg.Text("Body Y Offset:"), sg.Slider(range=(0.0, 1.0), resolution=0.01, default_value=cfg.body_y_offset, orientation='h', key='-BODY_Y_OFFSET-', enable_events=True)],
        [sg.Checkbox("Hideout Targets", default=cfg.hideout_targets, key='-HIDEOUT_TARGETS-', enable_events=True)],
        [sg.Checkbox("Disable Headshot", default=cfg.disable_headshot, key='-DISABLE_HEADSHOT-', enable_events=True)],
        [sg.Checkbox("Disable Prediction", default=cfg.disable_prediction, key='-DISABLE_PREDICTION-', enable_events=True)],
        [sg.Text("Prediction Interval:"), sg.Slider(range=(0.0, 10.0), resolution=0.1, default_value=cfg.prediction_interval, orientation='h', key='-PREDICTION_INTERVAL-', enable_events=True)],
        [sg.Checkbox("Third Person", default=cfg.third_person, key='-THIRD_PERSON-', enable_events=True)],
    ]
    return layout
