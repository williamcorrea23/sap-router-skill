#!/usr/bin/env python3
import os
import asyncio
import logging
import sys
from typing import Sequence

from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

from sap_gui_server.sap_controller import SapController

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_log_level(env_var, default_level):
    """Get logging level from environment variable"""
    level = os.getenv(env_var, default_level)
    return getattr(logging, level.upper(), getattr(logging, default_level))

# Configure logging
logging.basicConfig(
    level=get_log_level('LOG_LEVEL', 'ERROR'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)

# Configure module loggers
logger = logging.getLogger(__name__)
logger.setLevel(get_log_level('SERVER_LOG_LEVEL', 'DEBUG'))

# Set third-party loggers
logging.getLogger('mcp').setLevel(get_log_level('MCP_LOG_LEVEL', 'WARNING'))
logging.getLogger('asyncio').setLevel(get_log_level('ASYNCIO_LOG_LEVEL', 'WARNING'))
logging.getLogger('sap_gui_server.sap_controller').setLevel(get_log_level('SAP_CONTROLLER_LOG_LEVEL', 'DEBUG'))

class SapGuiServer:
    def __init__(self):
        logger.info("Initializing SAP GUI Server...")
        self.sap = None  # Initialize lazily
        self.server = Server("mcp-sap-gui", "0.1.0")
        logger.info("Setting up request handlers...")
        self._setup_handlers()
        logger.info("SAP GUI Server initialized")
        self.last_screenshot = None
        
    def _setup_handlers(self):
        """Set up request handlers for MCP tools"""
        
        def handle_image_response(result, return_screenshot="none", arguments=None):
            """Handle image response based on return_screenshot mode"""
            # Validate return_screenshot parameter
            valid_modes = ["none", "as_file", "as_base64", "as_imagecontent", "as_imageurl"]
            if return_screenshot not in valid_modes:
                logger.error(f"Invalid return_screenshot mode: {return_screenshot}")
                return [types.TextContent(type="text", text=f"Error: Invalid return_screenshot mode. Must be one of: {', '.join(valid_modes)}")]
            
            if not result.get("image"):
                return []
                
            self.last_screenshot = result["image"]
            
            if return_screenshot == "none":
                return []
            elif return_screenshot == "as_file":
                from datetime import datetime
                from PIL import Image
                import base64
                from io import BytesIO
                
                # Get target folder path
                target_folder = arguments.get("as_file_target_folder")
                if not target_folder:
                    logger.error("Target folder path is required when using 'as_file' return format")
                    return [types.TextContent(type="text", text="Error: Target folder path is required when using 'as_file' return format")]
                
                # Create target folder if it doesn't exist
                try:
                    os.makedirs(target_folder, exist_ok=True)
                except Exception as e:
                    error_msg = f"Failed to create target folder: {str(e)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=f"Error: {error_msg}")]
                
                # Check if folder is writable
                if not os.access(target_folder, os.W_OK):
                    error_msg = f"Target folder is not writable: {target_folder}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=f"Error: {error_msg}")]
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"sap_screenshot_{timestamp}.png"
                full_path = os.path.join(target_folder, filename)
                
                image_data = base64.b64decode(result["image"])
                image = Image.open(BytesIO(image_data))
                image.save(full_path)
                
                return [types.TextContent(type="text", text=f"Screenshot saved as {full_path}")]
            elif return_screenshot == "as_base64":
                return [types.TextContent(type="text", text=result["image"])]
            elif return_screenshot == "as_imagecontent":
                return [types.ImageContent(type="image", data=result["image"], mimeType="image/png")]
            elif return_screenshot == "as_imageurl":
                return [
                    types.EmbeddedResource(
                        type="resource",
                        resource=types.TextResourceContents(
                            uri="application:image",
                            mimeType="image/png",
                            text=f"data:image/png;base64,{result['image']}"
                        )
                    )
                ]
            return []

        # Define handlers
        async def handle_list_tools() -> list[types.Tool]:
            screenshot_schema = {
                "type": "string",
                "description": "Screenshot return format",
                "enum": ["none", "as_file", "as_base64", "as_imagecontent", "as_imageurl"],
                "default": "none"
            }
            
            # Common properties for all tools that can return screenshots
            screenshot_properties = {
                "return_screenshot": screenshot_schema,
                "as_file_target_folder": {
                    "type": "string",
                    "description": "Target folder path for saving screenshots when using 'as_file' return format. Will be created if it doesn't exist."
                }
            }
            
            return [
                types.Tool(
                    name="launch_transaction",
                    description="Launch SAP transaction code and return a screenshot of the resulting screen",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "transaction": {
                                "type": "string",
                                "description": "SAP transaction code to launch (e.g. VA01, ME21N, MM03)"
                            },
                            **screenshot_properties
                        },
                        "required": ["transaction"]
                    }
                ),
                types.Tool(
                    name="sap_click",
                    description="Click at specific coordinates and return a screenshot of the resulting screen",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "x": {
                                "type": "integer",
                                "description": "Horizontal pixel coordinate (0-1920) where the click should occur"
                            },
                            "y": {
                                "type": "integer",
                                "description": "Vertical pixel coordinate (0-1080) where the click should occur"
                            },
                            **screenshot_properties
                        },
                        "required": ["x", "y"]
                    }
                ),
                types.Tool(
                    name="sap_move_mouse",
                    description="Move mouse cursor to specific coordinates and return a screenshot of the screen",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "x": {
                                "type": "integer",
                                "description": "Horizontal pixel coordinate (0-1920) to move the cursor to"
                            },
                            "y": {
                                "type": "integer",
                                "description": "Vertical pixel coordinate (0-1080) to move the cursor to"
                            },
                            **screenshot_properties
                        },
                        "required": ["x", "y"]
                    }
                ),
                types.Tool(
                    name="sap_type",
                    description="Type text at current cursor position and return a screenshot of the resulting screen",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "Text to enter at the current cursor position in the SAP GUI window"
                            },
                            **screenshot_properties
                        },
                        "required": ["text"]
                    }
                ),
                types.Tool(
                    name="sap_scroll",
                    description="Scroll the SAP GUI screen and return a screenshot of the resulting view",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "direction": {
                                "type": "string",
                                "enum": ["up", "down"],
                                "description": "Direction to scroll the screen ('up' moves content down, 'down' moves content up)"
                            },
                            **screenshot_properties
                        },
                        "required": ["direction"]
                    }
                ),
                types.Tool(
                    name="end_transaction",
                    description="End the current SAP transaction and close the window",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="save_last_screenshot",
                    description="Save the last captured screenshot to a file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Path where the screenshot will be saved (e.g. 'screenshot.png', supports PNG, JPG, BMP formats)"
                            }
                        },
                        "required": ["filename"]
                    }
                ),
            ]

        async def handle_call_tool(
            name: str,
            arguments: dict
            ) -> Sequence[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            try:
                logger.info(f"Executing tool: {name} with arguments: {arguments}")
                sap = self.get_sap_controller()

                content = []  # Initialize content list
                return_screenshot = arguments.get("return_screenshot", "none")
                
                # Validate return_screenshot parameter
                valid_modes = ["none", "as_file", "as_base64", "as_imagecontent", "as_imageurl"]
                if return_screenshot not in valid_modes:
                    error_msg = f"Invalid return_screenshot mode. Must be one of: {', '.join(valid_modes)}"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=f"Error: {error_msg}")]

                if name == "launch_transaction":
                    logger.info(f"Launching transaction: {arguments['transaction']}")
                    result = sap.launch_transaction(arguments["transaction"])
                    
                    # Get window text first
                    window_text = sap._get_window_text()
                    
                    # Add error messages if any
                    if window_text["error_messages"]:
                        error_text = "Errors: " + ", ".join(window_text["error_messages"])
                        logger.info(f"Error messages detected: {error_text}")
                        content.append(types.TextContent(type="text", text=error_text))
                    
                    # Add status messages if any
                    if window_text["status_messages"]:
                        status_text = "Status: " + ", ".join(window_text["status_messages"])
                        logger.info(f"Status messages detected: {status_text}")
                        content.append(types.TextContent(type="text", text=status_text))
                    
                    # Add field values if any
                    if window_text["field_values"]:
                        fields_text = "Fields:\n" + "\n".join(f"{k}: {v}" for k, v in window_text["field_values"].items())
                        logger.info(f"Field values detected: {fields_text}")
                        content.append(types.TextContent(type="text", text=fields_text))

                    # Add screenshot based on return mode
                    if "image" in result:
                        logger.info("Screenshot captured in response")
                        content.extend(handle_image_response(result, return_screenshot, arguments))

                elif name == "sap_click":
                    # Extract and validate coordinates
                    try:
                        x = int(arguments.get('x', 0))
                        y = int(arguments.get('y', 0))
                    except (ValueError, TypeError):
                        raise ValueError("Coordinates must be valid integers")

                    logger.info(f"Clicking at position: ({x}, {y})")
                    result = sap.click_position(x, y)
                    if "status" in result:
                        status_text = f"Status: {result['status']}"
                        if "message" in result:
                            status_text += f"\\n{result['message']}"
                        logger.info(f"Tool execution result - {status_text}")
                        content.append(types.TextContent(type="text", text=status_text))
                    if "image" in result:
                        logger.info("Screenshot captured in response")
                        content.extend(handle_image_response(result, return_screenshot, arguments))

                elif name == "sap_move_mouse":
                    logger.info(f"Moving mouse to: ({arguments['x']}, {arguments['y']})")
                    result = sap.move_mouse(arguments["x"], arguments["y"])
                    if "status" in result:
                        status_text = f"Status: {result['status']}"
                        if "message" in result:
                            status_text += f"\\n{result['message']}"
                        logger.info(f"Tool execution result - {status_text}")
                        content.append(types.TextContent(type="text", text=status_text))
                    if "image" in result:
                        logger.info("Screenshot captured in response")
                        content.extend(handle_image_response(result, return_screenshot, arguments))

                elif name == "sap_type":
                    logger.info(f"Typing text: {arguments['text']}")
                    result = sap.type_text(arguments["text"])
                    if "status" in result:
                        status_text = f"Status: {result['status']}"
                        if "message" in result:
                            status_text += f"\\n{result['message']}"
                        logger.info(f"Tool execution result - {status_text}")
                        content.append(types.TextContent(type="text", text=status_text))
                    if "image" in result:
                        logger.info("Screenshot captured in response")
                        content.extend(handle_image_response(result, return_screenshot, arguments))

                elif name == "sap_scroll":
                    logger.info(f"Scrolling screen: {arguments['direction']}")
                    result = sap.scroll_screen(arguments["direction"])
                    if "status" in result:
                        status_text = f"Status: {result['status']}"
                        if "message" in result:
                            status_text += f"\\n{result['message']}"
                        logger.info(f"Tool execution result - {status_text}")
                        content.append(types.TextContent(type="text", text=status_text))
                    if "image" in result:
                        logger.info("Screenshot captured in response")
                        content.extend(handle_image_response(result, return_screenshot, arguments))
                        
                elif name == "end_transaction":
                    logger.info("Ending transaction")
                    sap.end_session()
                    content.append(types.TextContent(type="text", text="Status: success"))

                elif name == "save_last_screenshot":
                    if self.last_screenshot is None:
                        content.append(types.TextContent(type="text", text="Error: No screenshot available"))
                    else:
                        filename = arguments.get("filename")
                        if not filename:
                            content.append(types.TextContent(type="text", text="Error: Filename is required"))
                        else:
                            try:
                                # Decode base64 and save
                                from PIL import Image
                                import base64
                                from io import BytesIO

                                # Get current working directory
                                cwd = os.getcwd()
                                full_path = os.path.join(cwd, filename)
                                
                                image_data = base64.b64decode(self.last_screenshot)
                                image = Image.open(BytesIO(image_data))
                                image.save(full_path)
                                logger.info(f"Screenshot saved as {full_path}")
                                content.append(types.TextContent(type="text", text=f"Screenshot saved as {full_path}"))
                            except Exception as e:
                                logger.error(f"Error saving screenshot: {str(e)}")
                                content.append(types.TextContent(type="text", text=f"Error saving screenshot: {str(e)}"))
                else:
                    error_msg = f"Unknown tool: {name}"
                    logger.error(error_msg)
                    content.append(types.TextContent(type="text", text=error_msg))

                logger.info(f"Tool {name} executed successfully")
                return content

            except Exception as e:
                logger.error(f"Error executing {name}: {str(e)}", exc_info=True)
                error_msg = f"Error executing {name}: {str(e)}"
                return [types.TextContent(type="text", text=f"Error: {error_msg}")]

        # Register handlers with server and store as instance methods
        self.handle_list_tools = self.server.list_tools()(handle_list_tools)
        self.handle_call_tool = self.server.call_tool()(handle_call_tool)

    def get_sap_controller(self) -> SapController:
        """Get or create SAP controller instance"""
        if self.sap is None:
            logger.info("Initializing new SAP controller instance...")
            try:
                self.sap = SapController()
                logger.info("SAP controller initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing SAP controller: {str(e)}", exc_info=True)
                raise
        else:
            logger.debug("Using existing SAP controller instance")
        return self.sap

    async def start(self):
        """Start the MCP server"""
        logger.info("SAP GUI MCP server starting...")
        try:
            logger.info("Initializing stdio server transport...")
            async with stdio_server() as (read_stream, write_stream):
                logger.info("Server transport initialized, starting MCP server...")
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )
                logger.info("MCP server started successfully")
        except Exception as e:
            logger.error(f"Error starting server: {str(e)}", exc_info=True)
            raise
        finally:
            logger.info("Server shutting down...")
            if self.sap:
                try:
                    self.sap.end_session()
                    logger.info("SAP session ended successfully")
                except Exception as e:
                    logger.error(f"Error ending SAP session: {str(e)}", exc_info=True)

def main():
    server = SapGuiServer()
    asyncio.run(server.start())

if __name__ == "__main__":
    main()
