# PySimpleGUI Configuration GUI

This directory contains the new PySimpleGUI-based configuration GUI for the Sunone Aimbot project. It matches the visual design and organization of the C++ version.

## Architecture

The GUI is built using **PySimpleGUI**, a pure Python framework that requires no compilation. It uses a tabbed interface to organize different settings sections, similar to the C++ version's ImGui layout.

## Files

### Core Components

- **overlay.py** - Main configuration window with event loop and config binding
- **__init__.py** - Package initialization

### Drawing Modules (Modular Sections)

Each draw module returns a PySimpleGUI layout for its respective section:

- **draw_buttons.py** - Hotkey configuration (targeting, exit, pause, reload)
- **draw_capture.py** - Capture settings (FPS, monitor, methods, circle mask)
- **draw_aim.py** - Aim settings (offset, prediction, third person)
- **draw_ai.py** - AI model and detection settings (model, confidence, device)
- **draw_mouse.py** - Mouse movement settings (DPI, sensitivity, FOV, speed)
- **draw_depth.py** - Depth model settings
- **draw_shooting.py** - Shooting settings (auto shoot, triggerbot, bScope)
- **draw_arduino.py** - Arduino settings (port, baudrate, 16-bit mouse)
- **draw_game_overlay.py** - Game overlay/ESP settings (boxes, lines, labels)
- **draw_debug.py** - Debug window settings (position, scale, screenshot key)
- **draw_stats.py** - Performance statistics display

## Usage

The GUI is automatically started when the aimbot runs (`python run.py`):

```python
from gui import config_window

# Start the GUI window (runs in separate thread)
config_window.show()
```

## Features

- **Real-time config editing**: Every widget change immediately saves to `config.ini`
- **Config reload**: Automatically detects external config changes (e.g., F4) and refreshes GUI
- **Tabbed interface**: Organized sections matching the C++ version's look and feel
- **Professional theme**: Dark mode with blue accents (DarkBlue3)
- **Responsive**: Window is resizable and handles layout adjustments
- **Non-blocking**: Runs in a separate daemon thread, ensuring no impact on detection performance

## Integration with Existing Code

The GUI integrates with the existing config system:

- Uses `logic/config_watcher.py` Config class
- Auto-saves config via `cfg.save()` method
- Thread-safe config access via `cfg_file_lock`
- Compatible with existing F2/F3/F4 hotkey system

## Dependencies

Required dependencies (already in requirements.txt):

- `PySimpleGUI`
