import asyncio

from telethon import TelegramClient, events

from config import (
    accounts,
    configuration
)

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


async def start_search(client):
    await client.send_message(bot_username, '/search')
    print(f"Search started for session: {client.session.filename}")


async def stop_and_restart_search(client):
    await client.send_message(bot_username, '/stop')
    await start_search(client)


async def relay_message(client1, client2):
    @client1.on(events.NewMessage(chats=bot_username))
    async def handler1(event):
        if config['end_conversation_msg'] in event.raw_text or config['you_end_conversation_msg'] in event.raw_text:
            print("client2 ended chat")
            await stop_and_restart_search(client1)
            await stop_and_restart_search(client2)
        elif any(msg in event.raw_text for msg in config['ignore_messages']):
            print(f"ignoring message from client 1: {event.raw_text}")
        else:
            print(f"client 1: {event.raw_text}")
            await client2.send_message(bot_username, event.raw_text)

    @client2.on(events.NewMessage(chats=bot_username))
    async def handler2(event):
        if config['end_conversation_msg'] in event.raw_text or config['you_end_conversation_msg'] in event.raw_text:
            print("client1 ended chat")
            await stop_and_restart_search(client1)
            await stop_and_restart_search(client2)
        elif any(msg in event.raw_text for msg in config['ignore_messages']):
            print(f"ignoring message from client 2: {event.raw_text}")
        else:
            print(f"client 2: {event.raw_text}")
            await client1.send_message(bot_username, event.raw_text)

    await client1.run_until_disconnected()
    await client2.run_until_disconnected()


async def main():
    clients = []

    for account in accounts:
        clients.append(TelegramClient(account['session_name'], account['api_id'], account['api_hash']))

    for client in clients:
        await client.start()
        me = await client.get_me()
        print(f"Logged in as {me.first_name}")

        await start_search(client)

    await relay_message(*clients)


if __name__ == "__main__":
    result = choose_bot()
    bot_username = result[0]
    config = result[1]

    asyncio.run(main())
