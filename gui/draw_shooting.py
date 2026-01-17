import imgui


def draw_shooting(cfg):
    """Draw shooting settings section"""
    
    # Auto shoot
    changed, value = imgui.checkbox("Auto Shoot", cfg.auto_shoot)
    if changed:
        cfg.auto_shoot = value
        cfg.save()
    
    # Triggerbot
    changed, value = imgui.checkbox("Triggerbot", cfg.triggerbot)
    if changed:
        cfg.triggerbot = value
        cfg.save()
    
    # Force click
    changed, value = imgui.checkbox("Force Click", cfg.force_click)
    if changed:
        cfg.force_click = value
        cfg.save()
    
    # bScope multiplier
    changed, value = imgui.slider_float("bScope Multiplier", cfg.bScope_multiplier, 0.1, 5.0)
    if changed:
        cfg.bScope_multiplier = value
        cfg.save()
