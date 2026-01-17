import imgui


def draw_ai(cfg):
    """Draw AI model and detection settings section"""
    
    # AI model name
    imgui.text("AI Model Name:")
    imgui.same_line()
    imgui.push_item_width(300)
    changed, value = imgui.input_text("##model_name", cfg.AI_model_name, 100)
    imgui.pop_item_width()
    if changed:
        cfg.AI_model_name = value
        cfg.save()
    
    # Model image size
    changed, value = imgui.slider_int("Model Image Size", cfg.ai_model_image_size, 320, 1280)
    if changed:
        cfg.ai_model_image_size = value
        cfg.save()
    
    # Confidence threshold
    changed, value = imgui.slider_float("Confidence Threshold", cfg.AI_conf, 0.0, 1.0)
    if changed:
        cfg.AI_conf = value
        cfg.save()
    
    # Device selection
    imgui.text("AI Device:")
    imgui.same_line()
    imgui.push_item_width(200)
    changed, value = imgui.combo(
        "##device",
        ["cpu", "0", "1", "2", "3", "cuda", "mps"],
        0 if cfg.AI_device == "cpu" else int(cfg.AI_device) if cfg.AI_device.isdigit() else 5 if cfg.AI_device == "cuda" else 0
    )
    imgui.pop_item_width()
    if changed:
        cfg.AI_device = ["cpu", "0", "1", "2", "3", "cuda", "mps"][value]
        cfg.save()
    
    # AMD enable
    changed, value = imgui.checkbox("Enable AMD", cfg.AI_enable_AMD)
    if changed:
        cfg.AI_enable_AMD = value
        cfg.save()
    
    # Disable tracker
    changed, value = imgui.checkbox("Disable Tracker", cfg.disable_tracker)
    if changed:
        cfg.disable_tracker = value
        cfg.save()
