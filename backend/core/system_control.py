import os
import logging
import subprocess
from typing import Dict, Any, List, Optional, Tuple

# Import necessary libraries for system control
try:
    import pyautogui
    import psutil
except ImportError:
    logging.error("Required libraries for system control not installed.")
    logging.error("Please run: pip install pyautogui psutil")

class SystemController:
    """Handles system control operations including application management,
    system settings, and file operations."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the system controller with configuration settings.
        
        Args:
            config: Dictionary containing configuration parameters
                - app_paths: Dictionary mapping app names to their executable paths
                - default_file_dir: Default directory for file operations
        """
        self.config = config
        self.app_paths = config.get("app_paths", {})
        self.default_file_dir = config.get("default_file_dir", os.path.expanduser("~"))
        
        # Set PyAutoGUI failsafe
        pyautogui.FAILSAFE = True
    
    def launch_application(self, app_name: str) -> bool:
        """Launch an application by name.
        
        Args:
            app_name: Name of the application to launch
            
        Returns:
            bool: True if successful, False otherwise
        """
        app_path = self.app_paths.get(app_name.lower())
        
        if not app_path:
            logging.warning(f"No path configured for application: {app_name}")
            return False
        
        try:
            subprocess.Popen(app_path)
            logging.info(f"Launched application: {app_name}")
            return True
        except Exception as e:
            logging.error(f"Failed to launch application {app_name}: {e}")
            return False
    
    def close_application(self, app_name: str) -> bool:
        """Close an application by name.
        
        Args:
            app_name: Name of the application to close
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                # Case-insensitive partial match for process name
                if app_name.lower() in proc.info['name'].lower():
                    pid = proc.info['pid']
                    process = psutil.Process(pid)
                    process.terminate()
                    logging.info(f"Closed application: {app_name}")
                    return True
            
            logging.warning(f"Application not found: {app_name}")
            return False
        except Exception as e:
            logging.error(f"Failed to close application {app_name}: {e}")
            return False
    
    def get_running_applications(self) -> List[str]:
        """Get a list of currently running applications.
        
        Returns:
            List[str]: Names of running applications
        """
        try:
            running_apps = []
            for proc in psutil.process_iter(['pid', 'name']):
                running_apps.append(proc.info['name'])
            return running_apps
        except Exception as e:
            logging.error(f"Failed to get running applications: {e}")
            return []
    
    def adjust_volume(self, level: int) -> bool:
        """Adjust system volume level.
        
        Args:
            level: Volume level (0-100)
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Ensure level is within valid range
        level = max(0, min(100, level))
        
        try:
            # Platform-specific volume control
            if os.name == 'nt':  # Windows
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(
                    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                
                # Convert from 0-100 scale to 0.0-1.0 scale
                volume.SetMasterVolumeLevelScalar(level / 100.0, None)
                logging.info(f"Set volume to {level}%")
                return True
            elif os.name == 'posix':  # Linux/Mac
                if 'darwin' in os.sys.platform:  # Mac
                    os.system(f"osascript -e 'set volume output volume {level}'")
                else:  # Linux
                    os.system(f"amixer -D pulse sset Master {level}%")
                logging.info(f"Set volume to {level}%")
                return True
            else:
                logging.error("Unsupported operating system for volume control")
                return False
        except Exception as e:
            logging.error(f"Failed to adjust volume: {e}")
            return False
    
    def adjust_brightness(self, level: int) -> bool:
        """Adjust screen brightness level.
        
        Args:
            level: Brightness level (0-100)
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Ensure level is within valid range
        level = max(0, min(100, level))
        
        try:
            # Platform-specific brightness control
            if os.name == 'nt':  # Windows
                # Windows requires a third-party library or WMI
                logging.warning("Brightness control on Windows requires additional setup")
                return False
            elif os.name == 'posix':  # Linux/Mac
                if 'darwin' in os.sys.platform:  # Mac
                    os.system(f"brightness {level/100.0}")
                else:  # Linux
                    # Find the first backlight device
                    backlight_dirs = os.listdir('/sys/class/backlight/')
                    if backlight_dirs:
                        device = backlight_dirs[0]
                        max_brightness_file = f"/sys/class/backlight/{device}/max_brightness"
                        brightness_file = f"/sys/class/backlight/{device}/brightness"
                        
                        with open(max_brightness_file, 'r') as f:
                            max_brightness = int(f.read().strip())
                        
                        # Convert percentage to device-specific value
                        brightness_value = int((level / 100.0) * max_brightness)
                        
                        # Set brightness (requires root privileges)
                        os.system(f"echo {brightness_value} | sudo tee {brightness_file}")
                
                logging.info(f"Set brightness to {level}%")
                return True
            else:
                logging.error("Unsupported operating system for brightness control")
                return False
        except Exception as e:
            logging.error(f"Failed to adjust brightness: {e}")
            return False
    
    def file_operation(self, operation: str, source: str, destination: Optional[str] = None) -> bool:
        """Perform file operations like copy, move, delete.
        
        Args:
            operation: Operation to perform ('copy', 'move', 'delete')
            source: Source file path
            destination: Destination path (not needed for 'delete')
            
        Returns:
            bool: True if successful, False otherwise
        """
        import shutil
        
        try:
            # Resolve paths
            source_path = os.path.expanduser(source)
            if not os.path.isabs(source_path):
                source_path = os.path.join(self.default_file_dir, source_path)
            
            if destination:
                dest_path = os.path.expanduser(destination)
                if not os.path.isabs(dest_path):
                    dest_path = os.path.join(self.default_file_dir, dest_path)
            
            # Perform the requested operation
            if operation.lower() == 'copy':
                if os.path.isdir(source_path):
                    shutil.copytree(source_path, dest_path)
                else:
                    shutil.copy2(source_path, dest_path)
                logging.info(f"Copied {source_path} to {dest_path}")
            elif operation.lower() == 'move':
                shutil.move(source_path, dest_path)
                logging.info(f"Moved {source_path} to {dest_path}")
            elif operation.lower() == 'delete':
                if os.path.isdir(source_path):
                    shutil.rmtree(source_path)
                else:
                    os.remove(source_path)
                logging.info(f"Deleted {source_path}")
            else:
                logging.error(f"Unknown file operation: {operation}")
                return False
            
            return True
        except Exception as e:
            logging.error(f"File operation error: {e}")
            return False
    
    def take_screenshot(self, save_path: Optional[str] = None) -> Optional[str]:
        """Take a screenshot of the current screen.
        
        Args:
            save_path: Path to save the screenshot (optional)
            
        Returns:
            str: Path to the saved screenshot or None if failed
        """
        try:
            if not save_path:
                # Generate a default filename with timestamp
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = os.path.join(self.default_file_dir, f"screenshot_{timestamp}.png")
            
            # Take the screenshot
            screenshot = pyautogui.screenshot()
            screenshot.save(save_path)
            logging.info(f"Screenshot saved to {save_path}")
            return save_path
        except Exception as e:
            logging.error(f"Failed to take screenshot: {e}")
            return None
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information including CPU, memory, disk usage.
        
        Returns:
            Dict: System information
        """
        try:
            # CPU information
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count(logical=True)
            
            # Memory information
            memory = psutil.virtual_memory()
            memory_total = memory.total / (1024 ** 3)  # GB
            memory_used = memory.used / (1024 ** 3)    # GB
            memory_percent = memory.percent
            
            # Disk information
            disk = psutil.disk_usage('/')
            disk_total = disk.total / (1024 ** 3)      # GB
            disk_used = disk.used / (1024 ** 3)        # GB
            disk_percent = disk.percent
            
            # Battery information (if available)
            battery = None
            if hasattr(psutil, 'sensors_battery'):
                battery_stats = psutil.sensors_battery()
                if battery_stats:
                    battery = {
                        "percent": battery_stats.percent,
                        "power_plugged": battery_stats.power_plugged,
                        "seconds_left": battery_stats.secsleft
                    }
            
            return {
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count
                },
                "memory": {
                    "total_gb": round(memory_total, 2),
                    "used_gb": round(memory_used, 2),
                    "percent": memory_percent
                },
                "disk": {
                    "total_gb": round(disk_total, 2),
                    "used_gb": round(disk_used, 2),
                    "percent": disk_percent
                },
                "battery": battery
            }
        except Exception as e:
            logging.error(f"Failed to get system info: {e}")
            return {"error": str(e)}