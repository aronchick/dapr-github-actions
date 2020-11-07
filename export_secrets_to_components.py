import os
from pathlib import Path

component_dir = Path("components")
print(f"Component dir: {str(component_dir.absolute())}")
if not (component_dir.exists()):
    component_dir.mkdir()

for key in os.environ.keys():
    component_value = os.environ.get(key)
    if component_value is not None and key.startswith("COMPONENT_"):
        file_path = component_dir / f"{key}.yaml"
        print(f"Writing to {str(file_path.absolute())}")
        file_path.write_text(component_value)