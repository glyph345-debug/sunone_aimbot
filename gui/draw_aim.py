import imgui


def draw_aim(cfg):
    """Draw aim settings section"""
    
    # Body Y offset
    changed, value = imgui.slider_float("Body Y Offset", cfg.body_y_offset, 0.0, 1.0)
    if changed:
        cfg.body_y_offset = value
        cfg.save()
    
    # Hideout targets
    changed, value = imgui.checkbox("Hideout Targets", cfg.hideout_targets)
    if changed:
        cfg.hideout_targets = value
        cfg.save()
    
    # Disable headshot
    changed, value = imgui.checkbox("Disable Headshot", cfg.disable_headshot)
    if changed:
        cfg.disable_headshot = value
        cfg.save()
    
    # Disable prediction
    changed, value = imgui.checkbox("Disable Prediction", cfg.disable_prediction)
    if changed:
        cfg.disable_prediction = value
        cfg.save()
    
    # Prediction interval
    changed, value = imgui.slider_float("Prediction Interval", cfg.prediction_interval, 0.0, 10.0)
    if changed:
        cfg.prediction_interval = value
        cfg.save()
    
    # Third person
    changed, value = imgui.checkbox("Third Person", cfg.third_person)
    if changed:
        cfg.third_person = value
        cfg.save()
