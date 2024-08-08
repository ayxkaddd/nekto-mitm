from typing import Callable, List

import websockets

from .messages.action import Action
from .messages.notice import Notice


class Client:
    ws_endpoint = "wss://im.nekto.me/socket.io/?EIO=3&transport=websocket"

    def __init__(self, token: str) -> None:
        self.token = token
        self.callbacks = {}
        self.id = None  # Initialize self.id to None
        self.dialog = None  # Initialize self.dialog to None

    def add_callback(self, notice: str, callback: Callable) -> None:
        self.callbacks[notice] = callback

    def open_dialog(self, dialog) -> None:
        self.dialog = dialog

    async def close_dialog(self) -> None:
        if hasattr(self, "dialog") and self.dialog is not None:
            action = Action("anon.leaveDialog", {"dialogId": self.dialog.id})
            self.dialog = None
            await self.ws.send(action.to_string())

    async def login(self):
        auth_action = Action("auth.sendToken", {"token": self.token})
        await self.ws.send(auth_action.to_string())
        print(f"[{self.token[:5]}] sent login action")

    async def search(self, my_sex: str, wish_sex: str, my_age: List[int], wish_age: List[List[int]]) -> None:
        action = Action(name="search.run", params={
            "mySex": my_sex,
            "myAge": my_age,
            "wishSex": wish_sex,
            "wishAge": wish_age,
        })
        await self.ws.send(action.to_string())

    async def connect(self) -> None:
        async with websockets.connect(self.ws_endpoint, ping_interval=None) as connection:
            self.ws = connection
            await self.login()
            async for message in connection:
                if message == "2":
                    await self.ws.send("2")
                    continue
                notice = Notice.parse(message)
                if notice:
                    if notice.name == "auth.successToken":
                        self.id = notice.params.get("id")
                        print(f"[{self.token[:5]}] authenticated with ID: {self.id}")
                    callback = self.callbacks.get(notice.name)
                    if callback:
                        await callback(self, notice)
