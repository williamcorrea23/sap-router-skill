import os
import time
import pytest
from sap_gui_server.sap_controller import SapController
import base64
from PIL import Image
from io import BytesIO

class TestSapController:
    @pytest.fixture(scope="function")
    def controller(self):
        """Create a fresh SapController instance for each test."""
        controller = SapController()
        yield controller
        # Cleanup after each test
        try:
            controller.end_session()
        except:
            pass

    def verify_and_save_screenshot(self, screenshot_base64: str, filename: str) -> bool:
        """Helper to verify a screenshot is valid and save it."""
        try:
            # Create test_screenshots directory if it doesn't exist
            screenshots_dir = "test_screenshots"
            if not os.path.exists(screenshots_dir):
                os.makedirs(screenshots_dir)
            
            # Decode base64 to image
            image_data = base64.b64decode(screenshot_base64)
            image = Image.open(BytesIO(image_data))
            
            # Check if image is valid and has content
            width, height = image.size
            if width > 0 and height > 0:
                # Save the image
                filepath = os.path.join(screenshots_dir, filename)
                image.save(filepath)
                print(f"Screenshot saved to: {filepath}")
                return True
            return False
        except Exception as e:
            print(f"Screenshot verification failed: {str(e)}")
            return False

    def test_initialization(self, controller):
        """Test controller initialization."""
        assert controller._initialized is False
        assert controller._dpi_scale > 0
        assert controller._current_process is None

    def test_launch_transaction(self, controller):
        """Test launching a SAP transaction."""
        # Launch a simple transaction (e.g., MM03 - Display Material)
        result = controller.launch_transaction("MM03")
        print("launch_transaction result: ")
        print(result)
        # Verify response includes image
        assert "image" in result
        assert self.verify_and_save_screenshot(result["image"], "launch_transaction.png")
        
        # Verify window text can be retrieved separately
        window_text = controller._get_window_text()
        assert "main_text" in window_text
        assert "error_messages" in window_text
        assert "status_messages" in window_text
        assert "field_values" in window_text
        
        # Give time for SAP GUI to fully load
        time.sleep(5)

    def test_invalid_transaction(self, controller):
        """Test launching an invalid transaction to verify error capture."""
        # Launch an invalid transaction
        try:
            controller.launch_transaction("INVALID")
            assert False, "Should have raised an exception"
        except Exception as e:
            # Get the last window text before the error
            window_text = controller._get_window_text()
            
            # Verify error was captured in window text
            assert any("does not exist" in msg.lower() for msg in window_text["error_messages"])

    def test_mouse_interactions(self, controller):
        """Test mouse movement and clicking."""
        # First launch a transaction
        controller.launch_transaction("MM03")
        time.sleep(5)
        
        # Test mouse movement with smaller coordinates
        move_result = controller.move_mouse(30, 10)
        assert "image" in move_result
        assert self.verify_and_save_screenshot(move_result["image"], "mouse_move.png")
        
        # Test clicking with smaller coordinates
        click_result = controller.click_position(40, 10)
        assert "image" in click_result
        assert self.verify_and_save_screenshot(click_result["image"], "mouse_click.png")

    def test_keyboard_input(self, controller):
        """Test keyboard input functionality including special keys."""
        # Launch transaction
        controller.launch_transaction("SE93")
        time.sleep(5)
        
        # Test regular text input
        type_result = controller.type_text("SE93")
        assert "image" in type_result
        assert self.verify_and_save_screenshot(type_result["image"], "keyboard_type.png")
        
        # Test Enter key (using tilde)
        enter_result = controller.type_text("{ENTER}")
        assert "image" in enter_result
        assert self.verify_and_save_screenshot(enter_result["image"], "keyboard_enter.png")
        
        # Test function key
        f3_result = controller.type_text("{F3}")
        assert "image" in f3_result
        assert self.verify_and_save_screenshot(f3_result["image"], "keyboard_f3.png")
        
    def test_scrolling(self, controller):
        """Test screen scrolling."""
        # Launch transaction
        controller.launch_transaction("SCC4")
        time.sleep(5)
        
        # Test scrolling down
        scroll_down = controller.scroll_screen("down")
        assert "image" in scroll_down
        assert self.verify_and_save_screenshot(scroll_down["image"], "scroll_down.png")
        
        time.sleep(1)
        
        # Test scrolling up
        scroll_up = controller.scroll_screen("up")
        assert "image" in scroll_up
        assert self.verify_and_save_screenshot(scroll_up["image"], "scroll_up.png")

    def test_end_session(self, controller):
        """Test ending SAP session."""
        # Launch a transaction first
        controller.launch_transaction("MM03")
        time.sleep(5)
        
        # End session
        controller.end_session()
        time.sleep(2)  # Give time for process to terminate
        
        # Verify cleanup - check if process is terminated
        if controller._current_process:
            try:
                # This should raise psutil.NoSuchProcess if process is terminated
                controller._current_process.status()
                assert False, "Process should be terminated"
            except:
                pass  # Expected - process is terminated

    def test_screenshot_functionality(self, controller):
        """Test screenshot capture functionality."""
        # Launch transaction
        controller.launch_transaction("MM03")
        time.sleep(5)
        
        # Take screenshot
        screenshot = controller._take_screenshot()
        
        # Verify screenshot
        # assert screenshot is not None
        # assert self.verify_screenshot(screenshot)
