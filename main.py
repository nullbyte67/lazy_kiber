from telethon import TelegramClient
import asyncio
import os
import json
import argparse
import sys


def load_config(path="config.json"):
    if not os.path.exists(path):
        print(f"Error: {path} not found")
        sys.exit(1)

    with open(path, "r") as f:
        return json.load(f)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chat", required=True)
    parser.add_argument("--topic", type=int)
    parser.add_argument("--limit", type=int, default=500)
    parser.add_argument("--concurrent", type=int, default=5)
    parser.add_argument("--config", default="config.json")
    parser.add_argument("--output", default="downloads")
    return parser.parse_args()


def get_original_extension(message):
    if message.voice:
        return ".ogg"

    if message.audio:
        if message.audio.mime_type:
            extension_map = {
                "audio/mpeg": ".mp3",
                "audio/mp4": ".m4a",
                "audio/ogg": ".ogg",
            }
            return extension_map.get(message.audio.mime_type, ".mp3")
        return ".mp3"

    if message.video:
        return ".mp4"

    if message.document:
        for attribute in message.document.attributes:
            if hasattr(attribute, "file_name") and attribute.file_name:
                _, extension = os.path.splitext(attribute.file_name)
                return extension if extension else ".bin"
        return ".bin"

    if message.photo:
        return ".jpg"

    return ".bin"


async def download_file(message, directory, semaphore):
    async with semaphore:
        extension = get_original_extension(message)
        filename = f"{message.id}{extension}"
        path = os.path.join(directory, filename)

        if os.path.exists(path):
            print(f"[SKIP] {filename}")
            return message.id

        try:
            await message.download_media(file=path)
            print(f"[OK] {filename}")
            return message.id
        except Exception as error:
            print(f"[ERROR] {message.id}: {error}")
            return None


async def main():
    args = parse_args()
    config = load_config(args.config)

    client = TelegramClient(
        config["session_name"],
        config["api_id"],
        config["api_hash"],
    )

    await client.start()

    group = await client.get_entity(int(args.chat))
    print(f"Group: {group.title}")

    base_name = group.title
    if args.topic:
        base_name = f"{base_name}_topic_{args.topic}"

    output_directory = os.path.join(
        args.output,
        base_name.replace("/", "_"),
    )
    os.makedirs(output_directory, exist_ok=True)

    print(f"Searching messages from topic {args.topic}...")
    messages = []

    async for message in client.iter_messages(
        group,
        limit=args.limit,
        reply_to=args.topic,
    ):
        if message.media:
            messages.append(message)

            media_type = (
                "voice"
                if message.voice
                else "audio"
                if message.audio
                else "other"
            )

            print(f"Found: message {message.id} | type: {media_type}")

    print(f"Found {len(messages)} files")

    if not messages:
        await client.disconnect()
        return

    semaphore = asyncio.Semaphore(args.concurrent)

    tasks = [
        download_file(message, output_directory, semaphore)
        for message in messages
    ]

    results = await asyncio.gather(*tasks)

    successful = [result for result in results if result]
    print(f"Downloaded: {len(successful)} / {len(messages)}")

    await client.disconnect()


if __name__ == "__main__":
    print("""
 ██▓    ▄▄▄      ▒███████▒▓██   ██▓    ██ ▄█▀ ██▓ ▄▄▄▄   ▓█████  ██▀███
▓██▒   ▒████▄    ▒ ▒ ▒ ▄▀░ ▒██  ██▒    ██▄█▒ ▓██▒▓█████▄ ▓█   ▀ ▓██ ▒ ██▒
▒██░   ▒██  ▀█▄  ░ ▒ ▄▀▒░   ▒██ ██░   ▓███▄░ ▒██▒▒██▒ ▄██▒███   ▓██ ░▄█ ▒
▒██░   ░██▄▄▄▄██   ▄▀▒   ░  ░ ▐██▓░   ▓██ █▄ ░██░▒██░█▀  ▒▓█  ▄ ▒██▀▀█▄
░██████▒▓█   ▓██▒▒███████▒  ░ ██▒▓░   ▒██▒ █▄░██░░▓█  ▀█▓░▒████▒░██▓ ▒██▒
░ ▒░▓  ░▒▒   ▓▒█░░▒▒ ▓░▒░▒   ██▒▒▒    ▒ ▒▒ ▓▒░▓  ░▒▓███▀▒░░ ▒░ ░░ ▒▓ ░▒▓░
░ ░ ▒  ░ ▒   ▒▒ ░░░▒ ▒ ░ ▒ ▓██ ░▒░    ░ ░▒ ▒░ ▒ ░▒░▒   ░  ░ ░  ░  ░▒ ░ ▒░
  ░ ░    ░   ▒   ░ ░ ░ ░ ░ ▒ ▒ ░░     ░ ░░ ░  ▒ ░ ░    ░    ░     ░░   ░
    ░  ░     ░  ░  ░ ░     ░ ░        ░  ░    ░   ░         ░  ░   ░
                 ░         ░ ░                         ░
    """)

    asyncio.run(main())
