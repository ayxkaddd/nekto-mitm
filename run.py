import sys
import asyncio
from nektome.client import Client
from nektome.dialog import Dialog
from nektome.messages.notice import Notice
from config import TOKENS

if len(TOKENS) != 2:
    print("not enought auth tokens")
    sys.exit()

male_client = Client(TOKENS[0])
female_client = Client(TOKENS[1])

async def on_found(client: Client, notice: Notice) -> None:
    print(f"[{client.token[:5]}] connected to dialog {notice.params['id']}")
    dialog = Dialog(notice.params["id"], client)
    client.open_dialog(dialog)


async def on_message(client: Client, notice: Notice) -> None:
    if notice.params["senderId"] == client.id:
        return

    if hasattr(client, "dialog") and client.dialog is not None:
        await client.dialog.read_message(notice.params["id"])
        message = notice.params["message"]
        target_client = female_client if client == male_client else male_client
        if hasattr(target_client, "dialog") and target_client.dialog is not None:
            await target_client.dialog.send_message(message)
            print(f"{client.token[:5]}: {message} -> {target_client.token[:5]}")
    else:
        print(f"[{client.token[:5]}] received a message but has no active dialog")


async def on_start(client: Client, sex: str, target_sex: str) -> None:
    print(f"[{client.token[:5]}] searching for {target_sex}")
    await client.search(my_sex=sex, wish_sex=target_sex, wish_age=[[18, 21]], my_age=[18, 21])


async def on_close(client: Client, notice: Notice) -> None:
    print(f"[{client.token[:5]}] closed dialog {notice.params['id']}")
    target_client = female_client if client == male_client else male_client
    if hasattr(target_client, "dialog") and target_client.dialog is not None:
        await target_client.close_dialog()

    await asyncio.gather(
        on_start(male_client, "M", "F"),
        on_start(female_client, "F", "M")
    )


async def main():
    callbacks = {
        "dialog.opened": on_found,
        "auth.successToken": lambda c, n: asyncio.create_task(on_start(c, "M" if c == male_client else "F", "F" if c == male_client else "M")),
        "messages.new": on_message,
        "dialog.closed": on_close
    }

    for event, callback in callbacks.items():
        male_client.add_callback(event, callback)
        female_client.add_callback(event, callback)

    await asyncio.gather(
        male_client.connect(),
        female_client.connect()
    )


if __name__ == "__main__":
    asyncio.run(main())
