import imgui


def draw_buttons(cfg):
    """Draw hotkey configuration section"""
    
    # Targeting hotkey
    imgui.text("Targeting Hotkey:")
    imgui.same_line()
    imgui.push_item_width(200)
    changed, value = imgui.combo(
        "##targeting",
        ["LeftMouseButton", "RightMouseButton", "MiddleMouseButton", "XButton1", "XButton2"],
        ["LeftMouseButton", "RightMouseButton", "MiddleMouseButton", "XButton1", "XButton2"].index(cfg.hotkey_targeting) if cfg.hotkey_targeting in ["LeftMouseButton", "RightMouseButton", "MiddleMouseButton", "XButton1", "XButton2"] else 0
    )
    imgui.pop_item_width()
    
    if changed:
        cfg.hotkey_targeting = ["LeftMouseButton", "RightMouseButton", "MiddleMouseButton", "XButton1", "XButton2"][value]
        cfg.hotkey_targeting_list = cfg.hotkey_targeting.split(",")
        cfg.save()
    
    # Exit hotkey
    imgui.text("Exit Hotkey:")
    imgui.same_line()
    imgui.push_item_width(200)
    changed, value = imgui.combo(
        "##exit",
        ["F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"],
        ["F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"].index(cfg.hotkey_exit) if cfg.hotkey_exit in ["F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"] else 0
    )
    imgui.pop_item_width()
    
    if changed:
        cfg.hotkey_exit = ["F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"][value]
        cfg.save()
    
    # Pause hotkey
    imgui.text("Pause Hotkey:")
    imgui.same_line()
    imgui.push_item_width(200)
    changed, value = imgui.combo(
        "##pause",
        ["F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"],
        ["F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"].index(cfg.hotkey_pause) if cfg.hotkey_pause in ["F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"] else 0
    )
    imgui.pop_item_width()
    
    if changed:
        cfg.hotkey_pause = ["F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"][value]
        cfg.save()
    
    # Reload config hotkey
    imgui.text("Reload Config Hotkey:")
    imgui.same_line()
    imgui.push_item_width(200)
    changed, value = imgui.combo(
        "##reload",
        ["F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"],
        ["F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"].index(cfg.hotkey_reload_config) if cfg.hotkey_reload_config in ["F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"] else 0
    )
    imgui.pop_item_width()
    
    if changed:
        cfg.hotkey_reload_config = ["F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"][value]
        cfg.save()
