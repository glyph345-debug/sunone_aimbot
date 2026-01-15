# Visuals Queue Fix - Implementation Summary

## Problem
When starting the application with `show_window=False` and `show_overlay=False`, the Visuals object didn't create its queue. When users later enabled the overlay via the config GUI, the code tried to use `visuals.queue.put()` but the queue didn't exist, causing an `AttributeError: 'Visuals' object has no attribute 'queue'`.

## Solution Implemented

### 1. Modified `logic/visual.py`
- **Queue Creation**: Always create the queue in `__init__()` regardless of `show_window`/`show_overlay` settings
- **Thread Initialization**: Only initialize and start the thread if `show_window` or `show_overlay` is True
- **New Method**: Added `start_if_not_running()` method to handle dynamic thread startup when overlay/window is enabled via GUI

### 2. Modified `logic/config_gui.py`
- **Integration**: Added call to `visuals.start_if_not_running()` in `apply_runtime_updates()` method
- **Condition**: Only call the method when `cfg.show_overlay or cfg.show_window` is True
- **Import**: Added import for `visuals` from `logic.visual`

### 3. Modified `run.py`
- **Safety Check**: Added `hasattr(visuals, 'queue')` check before using the queue
- **Robustness**: Ensures safe queue usage even if something unexpected happens

### 4. Modified `logic/hotkeys_watcher.py`
- **Safety Check**: Added `hasattr(visuals, 'queue')` check before using the queue for cleanup

## Files Changed
1. `logic/visual.py` - Core fix for queue creation and thread management
2. `logic/config_gui.py` - Integration to start thread when overlay is enabled
3. `run.py` - Safety check for queue usage
4. `logic/hotkeys_watcher.py` - Safety check for queue usage

## Expected Behavior After Fix
1. **Startup with disabled display**: Queue exists, thread is not running
2. **Enable overlay via GUI**: `start_if_not_running()` is called, thread starts
3. **No AttributeError**: Queue is always available for use
4. **Proper functionality**: Overlay works correctly when enabled dynamically

## Testing
The fix has been verified to:
- ✅ Always create the queue in Visuals.__init__()
- ✅ Handle thread initialization when overlay is enabled via GUI
- ✅ Include safety checks for queue usage
- ✅ Maintain backward compatibility
- ✅ Follow existing code patterns and conventions