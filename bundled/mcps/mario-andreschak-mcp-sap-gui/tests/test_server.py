import pytest
import pytest_asyncio
import asyncio
import json
from sap_gui_server.server import SapGuiServer
import mcp.types as types
import base64
from PIL import Image
from io import BytesIO
import os
import time

class TestSapGuiServer:
    @pytest_asyncio.fixture(scope="function")
    async def server(self):
        """Create a fresh SapGuiServer instance for each test."""
        server = SapGuiServer()
        try:
            yield server
        finally:
            # Cleanup
            if hasattr(server, 'sap') and server.sap:
                try:
                    server.sap.end_session()
                except:
                    pass

    def verify_screenshot(self, screenshot_base64: str) -> bool:
        """Helper to verify a screenshot is valid."""
        try:
            image_data = base64.b64decode(screenshot_base64)
            print(f"Screenshot VERIFICATION: {screenshot_base64}")

            image = Image.open(BytesIO(image_data))
            width, height = image.size
            return width > 0 and height > 0
        except Exception as e:
            print(f"Screenshot verification failed: {str(e)}")
            return False

    @pytest.mark.asyncio
    async def test_list_tools(self, server: SapGuiServer):
        """Test tool listing functionality."""
        # Get the decorated function
        tools = await server.handle_list_tools()
        
        # Verify all expected tools are present
        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "launch_transaction",
            "sap_click",
            "sap_move_mouse",
            "sap_type",
            "sap_scroll",
            "end_transaction",
            "save_last_screenshot"
        ]
        
        for tool in expected_tools:
            assert tool in tool_names

    @pytest.mark.asyncio
    async def test_launch_transaction_tool(self, server: SapGuiServer):
        """Test launch_transaction tool."""
        result = await server.handle_call_tool("launch_transaction", {"transaction": "MM03"})
        print(f"Result from launch_transaction: {result}")
        # Verify response
        assert len(result) > 0
        for content in result:
            if isinstance(content, types.ImageContent):
                assert self.verify_screenshot(content.data)
        
        time.sleep(5)

    @pytest.mark.asyncio
    async def test_launch_transaction_no_screenshot(self, server: SapGuiServer):
        """Test launch_transaction tool without screenshot."""
        result = await server.handle_call_tool("launch_transaction", {"transaction": "MM03", "include_screenshot": False})
        # Verify no ImageContent is returned
        assert not any(isinstance(content, types.ImageContent) for content in result)

    @pytest.mark.asyncio
    async def test_mouse_interaction_tools(self,  server: SapGuiServer):
        """Test mouse movement and clicking tools."""
        # First launch a transaction
        await server.handle_call_tool("launch_transaction", {"transaction": "MM03", "include_screenshot": True})
        time.sleep(5)
        
        # Test mouse movement
        move_result = await server.handle_call_tool("sap_move_mouse", {"x": 100, "y": 100, "include_screenshot": True})
        assert any(isinstance(content, types.ImageContent) for content in move_result)
        
        # Test clicking
        click_result = await server.handle_call_tool("sap_click", {"x": 100, "y": 100, "include_screenshot": True})
        assert any(isinstance(content, types.ImageContent) for content in click_result)

    @pytest.mark.asyncio
    async def test_mouse_interaction_tools_no_screenshot(self, server: SapGuiServer):
        """Test mouse movement and clicking tools without screenshot."""
        # First launch a transaction
        await server.handle_call_tool("launch_transaction", {"transaction": "MM03", "include_screenshot": False})
        time.sleep(5)

        # Test mouse movement
        move_result = await server.handle_call_tool("sap_move_mouse", {"x": 100, "y": 100, "include_screenshot": False})
        assert not any(isinstance(content, types.ImageContent) for content in move_result)

        # Test clicking
        click_result = await server.handle_call_tool("sap_click", {"x": 100, "y": 100, "include_screenshot": False})
        assert not any(isinstance(content, types.ImageContent) for content in click_result)

    @pytest.mark.asyncio
    async def test_keyboard_input_tool(self, server: SapGuiServer):
        """Test keyboard input tool."""
        # Launch transaction
        await server.handle_call_tool("launch_transaction", {"transaction": "MM03", "include_screenshot": True})
        time.sleep(5)
        
        # Type text
        type_result = await server.handle_call_tool("sap_type", {"text": "100-100", "include_screenshot": True})
        assert any(isinstance(content, types.ImageContent) for content in type_result)

    @pytest.mark.asyncio
    async def test_keyboard_input_tool_no_screenshot(self, server: SapGuiServer):
        """Test keyboard input tool without screenshot."""
        # Launch transaction
        await server.handle_call_tool("launch_transaction", {"transaction": "MM03", "include_screenshot": False})
        time.sleep(5)

        # Type text
        type_result = await server.handle_call_tool("sap_type", {"text": "100-100", "include_screenshot": False})
        assert not any(isinstance(content, types.ImageContent) for content in type_result)

    @pytest.mark.asyncio
    async def test_scroll_tool(self, server: SapGuiServer):
        """Test scrolling tool."""
        # Launch transaction
        await server.handle_call_tool("launch_transaction", {"transaction": "MM03", "include_screenshot": True})
        time.sleep(5)
        
        # Test scroll down
        scroll_down = await server.handle_call_tool("sap_scroll", {"direction": "down", "include_screenshot": True})
        assert any(isinstance(content, types.ImageContent) for content in scroll_down)
        
        time.sleep(1)
        
        # Test scroll up
        scroll_up = await server.handle_call_tool("sap_scroll", {"direction": "up", "include_screenshot": True})
        assert any(isinstance(content, types.ImageContent) for content in scroll_up)

    @pytest.mark.asyncio
    async def test_scroll_tool_no_screenshot(self, server: SapGuiServer):
        """Test scrolling tool without screenshot."""
        # Launch transaction
        await server.handle_call_tool("launch_transaction", {"transaction": "MM03", "include_screenshot": False})
        time.sleep(5)

        # Test scroll down
        scroll_down = await server.handle_call_tool("sap_scroll", {"direction": "down", "include_screenshot": False})
        assert not any(isinstance(content, types.ImageContent) for content in scroll_down)

        time.sleep(1)

        # Test scroll up
        scroll_up = await server.handle_call_tool("sap_scroll", {"direction": "up", "include_screenshot": False})
        assert not any(isinstance(content, types.ImageContent) for content in scroll_up)

    @pytest.mark.asyncio
    async def test_end_transaction_tool(self, server: SapGuiServer):
        """Test end_transaction tool."""
        # First launch a transaction
        await server.handle_call_tool("launch_transaction", {"transaction": "MM03"})
        time.sleep(5)
        
        # End transaction
        end_result = await server.handle_call_tool("end_transaction", {})
        assert any(isinstance(content, types.TextContent) for content in end_result)

    @pytest.mark.asyncio
    async def test_save_screenshot_tool(self, server: SapGuiServer):
        """Test save_screenshot tool and verify absolute path."""
        # Launch transaction to get a screenshot
        await server.handle_call_tool("launch_transaction", {"transaction": "MM03", "include_screenshot": True})
        time.sleep(5)
        
        # Save screenshot
        filename = "test_screenshot.png"
        save_result = await server.handle_call_tool("save_last_screenshot", {"filename": filename})
        
        # Verify file was created and path is absolute
        assert len(save_result) == 1
        assert isinstance(save_result[0], types.TextContent)
        saved_path = save_result[0].text.replace("Screenshot saved to ", "")
        assert os.path.isabs(saved_path)
        assert os.path.exists(saved_path)

        try:
            # Clean up
            os.remove(saved_path)
        except:
            pass

    @pytest.mark.asyncio
    async def test_error_handling(self, server: SapGuiServer):
        """Test error handling with invalid inputs."""
        # Test invalid transaction code
        with pytest.raises(Exception):
            await server.handle_call_tool("launch_transaction", {"transaction": "INVALID"})
        
        # Test invalid coordinates
        with pytest.raises(Exception):
            await server.handle_call_tool("sap_click", {"x": -1, "y": -1})
