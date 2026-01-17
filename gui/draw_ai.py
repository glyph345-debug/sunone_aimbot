import PySimpleGUI as sg

def draw_ai(cfg):
    """Returns PySimpleGUI layout for AI settings"""
    devices = ["cpu", "0", "1", "2", "3", "cuda", "mps"]
    
    layout = [
        [sg.Text("AI Settings", font=("Arial", 12, "bold"))],
        [sg.Text("AI Model Name:"), sg.Input(cfg.AI_model_name, key='-AI_MODEL_NAME-', enable_events=True)],
        [sg.Text("Model Image Size:"), sg.Slider(range=(320, 1280), default_value=cfg.ai_model_image_size, orientation='h', key='-AI_MODEL_IMAGE_SIZE-', enable_events=True)],
        [sg.Text("Confidence Threshold:"), sg.Slider(range=(0.0, 1.0), resolution=0.01, default_value=cfg.AI_conf, orientation='h', key='-AI_CONF-', enable_events=True)],
        [sg.Text("AI Device:"), sg.Combo(devices, default_value=cfg.AI_device, key='-AI_DEVICE-', enable_events=True, readonly=True)],
        [sg.Checkbox("Enable AMD", default=cfg.AI_enable_AMD, key='-AI_ENABLE_AMD-', enable_events=True)],
        [sg.Checkbox("Disable Tracker", default=cfg.disable_tracker, key='-DISABLE_TRACKER-', enable_events=True)],
    ]
    return layout
