# PyImGui Configuration GUI

This directory contains the new PyImGui-based configuration GUI for the Sunone Aimbot project.

## Architecture

The GUI is built using **PyImGui** (Python bindings for Dear ImGui) with **GLFW** for window management and **PyOpenGL** for rendering. This provides the same immediate-mode GUI architecture as the C++ version.

## Files

### Core Components

- **config_window.py** - Main configuration window with render loop
- **__init__.py** - Package initialization

### Drawing Modules (Modular Sections)

Each draw module is independent and handles its own section of the GUI:

- **draw_buttons.py** - Hotkey configuration (targeting, exit, pause, reload)
- **draw_capture.py** - Capture settings (FPS, monitor, methods, circle mask)
- **draw_aim.py** - Aim settings (offset, prediction, third person)
- **draw_ai.py** - AI model and detection settings (model, confidence, device)
- **draw_mouse.py** - Mouse movement settings (DPI, sensitivity, FOV, speed)
- **draw_shooting.py** - Shooting settings (auto shoot, triggerbot, bScope)
- **draw_arduino.py** - Arduino settings (port, baudrate, 16-bit mouse)
- **draw_game_overlay.py** - Game overlay/ESP settings (boxes, lines, labels)
- **draw_debug.py** - Debug window settings (position, scale, screenshot key)
- **draw_stats.py** - Performance statistics display

## Usage

The GUI is automatically started when the aimbot runs (`python run.py`):

```python
from gui.config_window import config_window

# Start the GUI window (runs in separate thread)
config_window.show()

# Stop the GUI window
config_window.hide()
```

## Features

- **Real-time config editing**: Every widget change immediately saves to `config.ini`
- **Config reload**: Press F4 to reload config from file (F2/F3/F4 hotkeys still work)
- **Thread-safe**: Config access uses RLock for thread safety
- **Modular**: Each draw module is independent and can be modified separately
- **Collapsible sections**: Use ImGui collapsing headers to organize settings
- **Responsive**: Window is resizable (min 420x300, default 720x500)
- **FPS display**: Shows GUI FPS at bottom of window
- **Non-blocking**: Runs in daemon thread, doesn't affect detection performance

## Integration with Existing Code

The GUI integrates with the existing config system:

- Uses `logic/config_watcher.py` Config class
- Auto-saves config via `cfg.save()` method
- Thread-safe config access via `cfg_file_lock`
- Compatible with existing F2/F3/F4 hotkey system

## Dependencies

Required dependencies (added to requirements.txt):

- `imgui[glfw]` - PyImGui with GLFW backend
- `PyOpenGL` - OpenGL rendering
- `glfw` - Window management

## Future Enhancements

- Add depth model settings (draw_depth.py)
- Add real-time performance stats integration
- Add wind mouse settings
- Add snap/near radius configuration
- Add transparency/overlay mode
