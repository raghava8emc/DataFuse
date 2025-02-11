import os
import json
from output.base_output import BaseOutput

class LocalOutput(BaseOutput):
    def __init__(self, config):
        super().__init__(storage_type="LOCAL", config=config)
        self.output_path = config.get("output_path", "data/")
        os.makedirs(self.output_path, exist_ok=True)

    def save(self, data, filename):
        file_path = os.path.join(self.output_path, filename)
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
        return file_path