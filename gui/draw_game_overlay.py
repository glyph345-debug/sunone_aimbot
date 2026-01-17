import imgui


def draw_game_overlay(cfg):
    """Draw game overlay/ESP settings section"""
    
    # Show overlay
    changed, value = imgui.checkbox("Show Overlay", cfg.show_overlay)
    if changed:
        cfg.show_overlay = value
        cfg.save()
    
    # Show borders
    changed, value = imgui.checkbox("Show Borders", cfg.overlay_show_borders)
    if changed:
        cfg.overlay_show_borders = value
        cfg.save()
    
    # Show boxes
    changed, value = imgui.checkbox("Show Boxes", cfg.overlay_show_boxes)
    if changed:
        cfg.overlay_show_boxes = value
        cfg.save()
    
    # Show target line
    changed, value = imgui.checkbox("Show Target Line", cfg.overlay_show_target_line)
    if changed:
        cfg.overlay_show_target_line = value
        cfg.save()
    
    # Show target prediction line
    changed, value = imgui.checkbox("Show Target Prediction Line", cfg.overlay_show_target_prediction_line)
    if changed:
        cfg.overlay_show_target_prediction_line = value
        cfg.save()
    
    # Show labels
    changed, value = imgui.checkbox("Show Labels", cfg.overlay_show_labels)
    if changed:
        cfg.overlay_show_labels = value
        cfg.save()
    
    # Show confidence
    changed, value = imgui.checkbox("Show Confidence", cfg.overlay_show_conf)
    if changed:
        cfg.overlay_show_conf = value
        cfg.save()
