import asyncio
import os
from telethon import TelegramClient, events
from config import accounts, configuration


def choose_bot():
    available_bots = list(configuration.keys())

    for index, bot_name in enumerate(available_bots):
        print(f"{index}. {bot_name}")

    while True:
        try:
            choice = int(input("Choose a bot: "))
            if 0 <= choice < len(available_bots):
                chosen_bot = available_bots[choice]
                print(f"\nYou have chosen: {chosen_bot}\n")
                return [chosen_bot, configuration[chosen_bot]]
            else:
                print(f"Invalid input. Please enter a number between 0 and {len(available_bots) - 1}.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")


async def start_search(client, client_name):
    await client.send_message(bot_username, '/search')
    print(f"Search started for session: {client_name}")


async def stop_and_restart_search(client, client_name):
    await client.send_message(bot_username, '/stop')
    await start_search(client, client_name)


async def relay_message(client1, client2, client1_name, client2_name):
    searching_client1 = False
    searching_client2 = False

    async def handle_end_conversation(client_stopping, client_searching, client_stopping_name, client_searching_name):
        nonlocal searching_client1, searching_client2

        print(f"Ending chat for {client_stopping_name}")
        await client_stopping.send_message(bot_username, '/stop')

        if client_searching_name == client1_name and not searching_client1:
            print(f"Searching new chat for {client_searching_name}")
            await start_search(client_searching, client_searching_name)
            searching_client1 = True
            searching_client2 = False
        elif client_searching_name == client2_name and not searching_client2:
            print(f"Searching new chat for {client_searching_name}")
            await start_search(client_searching, client_searching_name)
            searching_client2 = True
            searching_client1 = False

    @client1.on(events.NewMessage(chats=bot_username))
    async def handler1(event):
        nonlocal searching_client1
        if event.sender_id != bot_id:
            print(f"you: {event.raw_text} -> client 2")
            return

        if any(msg in event.raw_text for msg in config['ignore_messages']):
            return

        if config['end_conversation_msg'] in event.raw_text or config['you_end_conversation_msg'] in event.raw_text:
            print("client2 ended chat")
            await handle_end_conversation(client2, client1, client2_name, client1_name)
            searching_client1 = False
            return

        if event.message.media:
            file_path = await client1.download_media(event.message)
            await client2.send_file(bot_username, file_path)
            os.remove(file_path)
        else:
            print(f"client 1: {event.raw_text}")
            await client2.send_message(bot_username, event.raw_text)

    @client2.on(events.NewMessage(chats=bot_username))
    async def handler2(event):
        nonlocal searching_client2
        if event.sender_id != bot_id:
            print(f"you: {event.raw_text} -> client 1")
            return

        if any(msg in event.raw_text for msg in config['ignore_messages']):
            return

        if config['end_conversation_msg'] in event.raw_text or config['you_end_conversation_msg'] in event.raw_text:
            print("client1 ended chat")
            await handle_end_conversation(client1, client2, client1_name, client2_name)
            searching_client2 = False
            return

        if event.message.media:
            file_path = await client2.download_media(event.message)
            await client1.send_file(bot_username, file_path)
            os.remove(file_path)
        else:
            print(f"client 2: {event.raw_text}")
            await client1.send_message(bot_username, event.raw_text)

    await client1.run_until_disconnected()
    await client2.run_until_disconnected()


async def main():
    clients = []
    global bot_id

    for account in accounts:
        clients.append(TelegramClient(account['session_name'], account['api_id'], account['api_hash']))

    for client in clients:
        await client.start()
        me = await client.get_me()
        print(f"Logged in as {me.first_name}")

    bot_entity = await clients[0].get_entity(bot_username)
    bot_id = bot_entity.id

    await start_search(clients[0], clients[0].session.filename)
    await start_search(clients[1], clients[1].session.filename)

    await relay_message(clients[0], clients[1], clients[0].session.filename, clients[1].session.filename)


if __name__ == "__main__":
    result = choose_bot()
    bot_username = result[0]
    config = result[1]

    asyncio.run(main())
