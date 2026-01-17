import imgui
import glfw
import OpenGL.GL as gl
import threading
import time
from queue import Queue

from logic.config_watcher import cfg
from logic.logger import logger


class ConfigWindow:
    def __init__(self):
        self.queue = Queue()
        self.thread = None
        self.running = False
        self.window = None
        self.io = None
        self.impl_glfw = None
        self.impl_gl = None
        
        # Performance stats
        self.fps = 0
        self.frame_count = 0
        self.last_time = time.time()
        
        # Import drawing modules
        from . import draw_buttons
        from . import draw_capture
        from . import draw_aim
        from . import draw_ai
        from . import draw_mouse
        from . import draw_shooting
        from . import draw_arduino
        from . import draw_game_overlay
        from . import draw_debug
        from . import draw_stats
        
        self.draw_buttons = draw_buttons
        self.draw_capture = draw_capture
        self.draw_aim = draw_aim
        self.draw_ai = draw_ai
        self.draw_mouse = draw_mouse
        self.draw_shooting = draw_shooting
        self.draw_arduino = draw_arduino
        self.draw_game_overlay = draw_game_overlay
        self.draw_debug = draw_debug
        self.draw_stats = draw_stats

    def init_imgui(self):
        """Initialize ImGui with GLFW backend"""
        if not glfw.init():
            logger.error("[GUI] Failed to initialize GLFW")
            return False
        
        # Create window
        self.window = glfw.create_window(720, 500, "Sunone Aimbot - Configuration", None, None)
        if not self.window:
            glfw.terminate()
            logger.error("[GUI] Failed to create GLFW window")
            return False
        
        glfw.make_context_current(self.window)
        glfw.swap_interval(1)  # Enable vsync
        
        # Setup ImGui
        imgui.create_context()
        self.io = imgui.get_io()
        self.io.ini_filename = None  # Disable imgui.ini
        self.io.log_filename = None  # Disable imgui.log
        
        # Setup GLFW/OpenGL bindings
        self.impl_glfw = imgui.backends.glfw_impl_glfw.GlfwImplGlfw(self.window)
        self.impl_gl = imgui.backends.glfw_impl_opengl3.GlfwImplOpenGL3()
        
        return True

    def render(self):
        """Main render loop"""
        while not glfw.window_should_close(self.window) and self.running:
            glfw.poll_events()
            
            # Calculate FPS
            current_time = time.time()
            self.frame_count += 1
            if current_time - self.last_time >= 1.0:
                self.fps = self.frame_count
                self.frame_count = 0
                self.last_time = current_time
            
            # Start new ImGui frame
            self.impl_glfw.new_frame()
            imgui.new_frame()
            
            # Create main window
            imgui.set_next_window_size(720, 500, imgui.FIRST_USE_EVER)
            imgui.set_next_window_size_constraints(420, 300)
            imgui.begin("Sunone Aimbot Configuration", True)
            
            # Create sections using ImGui's built-in collapsing header
            if imgui.collapsing_header("Hotkeys", imgui.TREE_NODE_DEFAULT_OPEN):
                self.draw_buttons.draw_buttons(cfg)
            
            if imgui.collapsing_header("Capture Settings"):
                self.draw_capture.draw_capture(cfg)
            
            if imgui.collapsing_header("Aim Settings"):
                self.draw_aim.draw_aim(cfg)
            
            if imgui.collapsing_header("AI Settings", imgui.TREE_NODE_DEFAULT_OPEN):
                self.draw_ai.draw_ai(cfg)
            
            if imgui.collapsing_header("Mouse Settings", imgui.TREE_NODE_DEFAULT_OPEN):
                self.draw_mouse.draw_mouse(cfg)
            
            if imgui.collapsing_header("Shooting Settings"):
                self.draw_shooting.draw_shooting(cfg)
            
            if imgui.collapsing_header("Arduino Settings"):
                self.draw_arduino.draw_arduino(cfg)
            
            if imgui.collapsing_header("Game Overlay"):
                self.draw_game_overlay.draw_game_overlay(cfg)
            
            if imgui.collapsing_header("Debug Window"):
                self.draw_debug.draw_debug(cfg)
            
            # Show FPS at bottom
            imgui.separator()
            imgui.text(f"FPS: {self.fps}")
            
            imgui.end()
            
            # Render
            gl.glClearColor(0.1, 0.1, 0.1, 1.0)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
            imgui.render()
            self.impl_gl.render(imgui.get_draw_data())
            
            glfw.swap_buffers(self.window)
        
        # Cleanup
        glfw.destroy_window(self.window)
        glfw.terminate()

    def run(self):
        """Run the configuration window in a thread"""
        if not self.init_imgui():
            return
        
        self.running = True
        try:
            self.render()
        except Exception as e:
            logger.error(f"[GUI] Error in render loop: {e}")
        finally:
            self.running = False

    def show(self):
        """Start the configuration window thread"""
        if self.thread is None or not self.thread.is_alive():
            self.running = True
            self.thread = threading.Thread(target=self.run, daemon=True, name="GUI_ConfigWindow")
            self.thread.start()
            logger.info("[GUI] Configuration window started")

    def hide(self):
        """Stop the configuration window"""
        self.running = False
        if self.window:
            glfw.set_window_should_close(self.window, True)
        if self.thread:
            self.thread.join(timeout=2.0)


config_window = ConfigWindow()
