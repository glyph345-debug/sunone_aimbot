import PySimpleGUI as sg

def draw_arduino(cfg):
    """Returns PySimpleGUI layout for Arduino settings"""
    layout = [
        [sg.Text("Arduino Settings", font=("Arial", 12, "bold"))],
        [sg.Checkbox("Arduino Move", default=cfg.arduino_move, key='-ARDUINO_MOVE-', enable_events=True)],
        [sg.Checkbox("Arduino Shoot", default=cfg.arduino_shoot, key='-ARDUINO_SHOOT-', enable_events=True)],
        [sg.Text("Arduino Port:"), sg.Input(cfg.arduino_port, key='-ARDUINO_PORT-', enable_events=True)],
        [sg.Text("Arduino Baudrate:"), sg.Slider(range=(1200, 115200), default_value=cfg.arduino_baudrate, orientation='h', key='-ARDUINO_BAUDRATE-', enable_events=True)],
        [sg.Checkbox("Arduino 16-bit Mouse", default=cfg.arduino_16_bit_mouse, key='-ARDUINO_16_BIT_MOUSE-', enable_events=True)],
    ]
    return layout
