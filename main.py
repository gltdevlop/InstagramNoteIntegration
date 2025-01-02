import windows.windows_manager as wm_node
from managers.config_manager import ConfigManager

config_manager = ConfigManager()

wm_node.start_app()

api_url = config_manager.get("note_integration", "False")
print(api_url)