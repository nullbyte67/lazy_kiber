# Lazy Kiber

A utility for downloading media files from private Telegram groups using the Telegram API through Telethon.

## Features

- Download media from private Telegram groups.
- Download files from a specific forum topic (thread).
- Preserve original file extensions whenever possible.
- Skip files that have already been downloaded.
- Concurrent downloads for improved performance.
- Configurable output directory.
- Supports:
  - Voice messages (`.ogg`)
  - Audio files (`.mp3`, `.m4a`, `.ogg`)
  - Videos (`.mp4`)
  - Photos (`.jpg`)
  - Documents (preserves the original extension when available).

---

## Requirements

- Python 3.10 or newer
- A Telegram account
- A Telegram API ID and API Hash

Install the dependency:

```bash
pip install telethon
```

---

## Configuration

Create a `config.json` file in the project root.

```json
{
    "session_name": "session",
    "api_id": 12345678,
    "api_hash": "your_api_hash"
}
```

Get your API credentials from:

https://my.telegram.org

---

## Usage

Download media from a group:

```bash
python main.py --chat CHAT_ID
```

Download media from a specific topic:

```bash
python main.py --chat CHAT_ID --topic TOPIC_ID
```

### Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--chat` | Telegram group ID | Required |
| `--topic` | Topic ID (forum thread) | None |
| `--limit` | Maximum number of messages to scan | `500` |
| `--concurrent` | Maximum simultaneous downloads | `5` |
| `--config` | Configuration file | `config.json` |
| `--output` | Output directory | `downloads` |

---

## Output

Downloaded files are stored as follows:

```text
downloads/
└── Group Name/
    ├── 12345.mp4
    ├── 12346.ogg
    ├── 12347.jpg
    └── ...
```

When downloading from a topic:

```text
downloads/
└── Group Name_topic_123/
```

Files are named using their Telegram message ID to guarantee unique filenames.

---

## Notes

- Your Telegram account must be a member of the target group.
- Only messages containing media are downloaded.
- Existing files are skipped automatically.
- Downloads are performed using the official Telegram API through Telethon.

---

