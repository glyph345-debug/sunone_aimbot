import imgui


def draw_debug(cfg):
    """Draw debug window settings section"""
    
    # Show debug window
    changed, value = imgui.checkbox("Show Debug Window", cfg.show_window)
    if changed:
        cfg.show_window = value
        cfg.save()
    
    # Show detection speed
    changed, value = imgui.checkbox("Show Detection Speed", cfg.show_detection_speed)
    if changed:
        cfg.show_detection_speed = value
        cfg.save()
    
    # Show window FPS
    changed, value = imgui.checkbox("Show Window FPS", cfg.show_window_fps)
    if changed:
        cfg.show_window_fps = value
        cfg.save()
    
    # Show boxes
    changed, value = imgui.checkbox("Show Boxes", cfg.show_boxes)
    if changed:
        cfg.show_boxes = value
        cfg.save()
    
    # Show labels
    changed, value = imgui.checkbox("Show Labels", cfg.show_labels)
    if changed:
        cfg.show_labels = value
        cfg.save()
    
    # Show confidence
    changed, value = imgui.checkbox("Show Confidence", cfg.show_conf)
    if changed:
        cfg.show_conf = value
        cfg.save()
    
    # Show target line
    changed, value = imgui.checkbox("Show Target Line", cfg.show_target_line)
    if changed:
        cfg.show_target_line = value
        cfg.save()
    
    # Show target prediction line
    changed, value = imgui.checkbox("Show Target Prediction Line", cfg.show_target_prediction_line)
    if changed:
        cfg.show_target_prediction_line = value
        cfg.save()
    
    # Show bScope box
    changed, value = imgui.checkbox("Show bScope Box", cfg.show_bScope_box)
    if changed:
        cfg.show_bScope_box = value
        cfg.save()
    
    # Show history points
    changed, value = imgui.checkbox("Show History Points", cfg.show_history_points)
    if changed:
        cfg.show_history_points = value
        cfg.save()
    
    # Debug window always on top
    changed, value = imgui.checkbox("Always On Top", cfg.debug_window_always_on_top)
    if changed:
        cfg.debug_window_always_on_top = value
        cfg.save()
    
    # Window position
    changed, value = imgui.slider_int("Window Position X", cfg.spawn_window_pos_x, 0, 3840)
    if changed:
        cfg.spawn_window_pos_x = value
        cfg.save()
    
    changed, value = imgui.slider_int("Window Position Y", cfg.spawn_window_pos_y, 0, 2160)
    if changed:
        cfg.spawn_window_pos_y = value
        cfg.save()
    
    # Window scale
    changed, value = imgui.slider_int("Window Scale Percent", cfg.debug_window_scale_percent, 50, 200)
    if changed:
        cfg.debug_window_scale_percent = value
        cfg.save()
    
    # Screenshot key
    imgui.text("Screenshot Key:")
    imgui.same_line()
    imgui.push_item_width(200)
    changed, value = imgui.input_text("##screenshot_key", cfg.debug_window_screenshot_key, 20)
    imgui.pop_item_width()
    if changed:
        cfg.debug_window_screenshot_key = value
        cfg.save()
