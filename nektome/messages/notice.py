import json
from typing import Dict, Optional


class Notice:
    @staticmethod
    def parse(received_message: str) -> Optional['Notice']:
        try:
            if received_message.startswith("42"):
                params = json.loads(received_message[2:])[1]
                name, data = params.get("notice"), params.get("data")
                if name:
                    return Notice(name, data)
        except (IndexError, ValueError):
            pass
        return None

    def __init__(self, name: str, params: Dict) -> None:
        self.params = params
        self.name = name
