import imgui


def draw_stats(cfg, fps=0, detected_objects=0):
    """Draw performance statistics section"""
    
    # Detection FPS (if available from main thread)
    imgui.text(f"GUI FPS: {fps}")
    
    # Detected objects count placeholder (would be updated from main thread)
    imgui.text(f"Detected Objects: {detected_objects}")
    
    imgui.separator()
    imgui.text("Performance Info")
    imgui.text("This section shows real-time performance")
    imgui.text("statistics from the aimbot system.")
