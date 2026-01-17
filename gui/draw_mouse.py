import imgui


def draw_mouse(cfg):
    """Draw mouse movement settings section"""
    
    # Mouse DPI
    changed, value = imgui.slider_int("Mouse DPI", cfg.mouse_dpi, 100, 20000)
    if changed:
        cfg.mouse_dpi = value
        cfg.save()
    
    # Mouse sensitivity
    changed, value = imgui.slider_float("Mouse Sensitivity", cfg.mouse_sensitivity, 0.1, 10.0)
    if changed:
        cfg.mouse_sensitivity = value
        cfg.save()
    
    # FOV width
    changed, value = imgui.slider_int("FOV Width", cfg.mouse_fov_width, 10, 500)
    if changed:
        cfg.mouse_fov_width = value
        cfg.save()
    
    # FOV height
    changed, value = imgui.slider_int("FOV Height", cfg.mouse_fov_height, 10, 500)
    if changed:
        cfg.mouse_fov_height = value
        cfg.save()
    
    # Speed multipliers
    changed, value = imgui.slider_float("Min Speed Multiplier", cfg.mouse_min_speed_multiplier, 0.1, 5.0)
    if changed:
        cfg.mouse_min_speed_multiplier = value
        cfg.save()
    
    changed, value = imgui.slider_float("Max Speed Multiplier", cfg.mouse_max_speed_multiplier, 0.1, 5.0)
    if changed:
        cfg.mouse_max_speed_multiplier = value
        cfg.save()
    
    # Lock target
    changed, value = imgui.checkbox("Lock Target", cfg.mouse_lock_target)
    if changed:
        cfg.mouse_lock_target = value
        cfg.save()
    
    # Auto aim
    changed, value = imgui.checkbox("Auto Aim", cfg.mouse_auto_aim)
    if changed:
        cfg.mouse_auto_aim = value
        cfg.save()
    
    # G HUB
    changed, value = imgui.checkbox("G HUB Support", cfg.mouse_ghub)
    if changed:
        cfg.mouse_ghub = value
        cfg.save()
    
    # Razer
    changed, value = imgui.checkbox("Razer Support", cfg.mouse_rzr)
    if changed:
        cfg.mouse_rzr = value
        cfg.save()
