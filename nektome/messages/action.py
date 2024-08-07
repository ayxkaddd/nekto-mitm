from typing import Dict
import json

class Action:
    def __init__(self, name: str, params: Dict) -> None:
        self.params = params
        self.params.update({"action": name})

    def to_string(self) -> str:
        return "42" + json.dumps(["action", self.params])
