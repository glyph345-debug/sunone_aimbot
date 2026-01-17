import imgui


def draw_arduino(cfg):
    """Draw Arduino settings section"""
    
    # Arduino move
    changed, value = imgui.checkbox("Arduino Move", cfg.arduino_move)
    if changed:
        cfg.arduino_move = value
        cfg.save()
    
    # Arduino shoot
    changed, value = imgui.checkbox("Arduino Shoot", cfg.arduino_shoot)
    if changed:
        cfg.arduino_shoot = value
        cfg.save()
    
    # Arduino port
    imgui.text("Arduino Port:")
    imgui.same_line()
    imgui.push_item_width(200)
    changed, value = imgui.input_text("##arduino_port", cfg.arduino_port, 50)
    imgui.pop_item_width()
    if changed:
        cfg.arduino_port = value
        cfg.save()
    
    # Arduino baudrate
    changed, value = imgui.slider_int("Arduino Baudrate", cfg.arduino_baudrate, 1200, 115200)
    if changed:
        cfg.arduino_baudrate = value
        cfg.save()
    
    # Arduino 16-bit mouse
    changed, value = imgui.checkbox("Arduino 16-bit Mouse", cfg.arduino_16_bit_mouse)
    if changed:
        cfg.arduino_16_bit_mouse = value
        cfg.save()
