# Config Reload Test Scenarios

This document describes the expected behavior after the config reload fix.

## Test 1: Show Overlay Toggle

**Initial State:**
- `show_overlay = False` in config.ini
- GUI is open via F1
- No overlay visible

**Steps:**
1. Click the `show_overlay` checkbox in the "Overlay & Debug" tab
2. Verify checkbox is now checked (visual feedback)

**Expected Result:**
- Overlay window appears immediately over the game
- No need to close/reopen GUI
- Config.ini is updated with `show_overlay = True`
- Visual thread is started if not already running

## Test 2: Show Window Toggle

**Initial State:**
- `show_window = False` in config.ini
- GUI is open via F1
- No debug window visible

**Steps:**
1. Click the `show_window` checkbox in the "Overlay & Debug" tab
2. Verify checkbox is now checked

**Expected Result:**
- Debug window appears immediately
- No need to close/reopen GUI
- Config.ini is updated with `show_window = True`
- Visual thread is started if not already running

## Test 3: Mouse Sensitivity Slider

**Initial State:**
- `mouse_sensitivity = 1.0` in config.ini
- GUI is open in "Mouse Settings" tab

**Steps:**
1. Drag the "Sensitivity" slider to 5.0
2. Release mouse button

**Expected Result:**
- Value updates to 5.0 immediately
- Mouse movement sensitivity changes take effect immediately
- No need to close/reopen GUI
- Config.ini is updated with `mouse_sensitivity = 5.0`
- `mouse.update_settings()` is called automatically

## Test 4: Detection Window Size

**Initial State:**
- `detection_window_width = 640` in config.ini
- `detection_window_height = 640` in config.ini
- GUI is open in "Detection Window" tab

**Steps:**
1. Drag "Window Width" slider to 800
2. Release mouse button
3. Drag "Window Height" slider to 600
4. Release mouse button

**Expected Result:**
- Values update immediately
- Capture region resizes immediately
- Mouse FOV calculations update immediately
- No need to close/reopen GUI
- Config.ini is updated
- `capture.restart()` and `mouse.update_settings()` are called automatically

## Test 5: Aim Settings (Third Person)

**Initial State:**
- `third_person = False` in config.ini
- GUI is open in "Aim Settings" tab

**Steps:**
1. Click the `third_person` checkbox
2. Verify checkbox is now checked

**Expected Result:**
- Setting takes effect immediately
- Detection classes updated to include third person targets (class 10.0)
- No need to close/reopen GUI
- Config.ini is updated with `third_person = True`
- `hotkeys_watcher.clss` is updated automatically

## Test 6: Manual Input Field (Mouse DPI)

**Initial State:**
- `mouse_dpi = 800` in config.ini
- GUI is open in "Mouse Settings" tab

**Steps:**
1. Click in the "DPI" input field
2. Delete current value and type "1600"
3. Press Enter

**Expected Result:**
- Value updates to 1600 immediately
- Mouse movement calculations update immediately
- No need to close/reopen GUI
- Config.ini is updated with `mouse_dpi = 1600`
- `mouse.update_settings()` is called automatically

## Test 7: Capture FPS Slider

**Initial State:**
- `capture_fps = 60` in config.ini
- GUI is open in "Capture Methods" tab

**Steps:**
1. Drag "Capture FPS" slider to 90
2. Release mouse button

**Expected Result:**
- Value updates to 90 immediately
- Capture frame rate changes immediately
- No need to close/reopen GUI
- Config.ini is updated with `capture_fps = 90`
- `capture.restart()` is called automatically

## Test 8: Reload Button

**Initial State:**
- Config.ini has been manually edited outside the GUI
- GUI is open

**Steps:**
1. Click the "Reload" button

**Expected Result:**
- All values in GUI update to match config.ini
- All runtime components reload (capture, mouse, classes)
- Visual confirmation in logs
- No need to close/reopen GUI

## Implementation Details

When any setting is changed in the GUI:

1. **Checkboxes**: Immediately call `save_config()`
2. **Sliders**: Call `save_config()` on mouse up (after drag completes)
3. **Input fields**: Call `save_config()` when Enter is pressed or field loses focus

The `save_config()` method:
1. Writes all config values to config.ini (with file lock)
2. Calls `cfg.Read()` to reload from file
3. Calls `apply_runtime_updates()` which:
   - Restarts capture with `capture.restart()`
   - Updates mouse with `mouse.update_settings()`
   - Starts visuals with `visuals.start_if_not_running()` if overlay/window enabled
   - Updates detection classes with `hotkeys_watcher.clss = self.active_classes()`
4. Syncs GUI elements with cfg values

## Known Limitations

1. **Overlay dimensions**: The overlay window dimensions are set once at startup. Changing `detection_window_width` or `detection_window_height` will update the capture region but not resize the overlay. This would require restarting the overlay thread.

2. **Visual thread lifecycle**: If both `show_overlay` and `show_window` are disabled, the visual thread continues running but doesn't display anything. This is acceptable overhead.

3. **Hotkey changes**: Changes to hotkey bindings (like `hotkey_targeting`) take effect immediately in the config, but the GUI doesn't provide visual feedback for testing hotkeys.
