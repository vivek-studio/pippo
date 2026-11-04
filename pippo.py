from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# ==========================================
# PIPPO CONFIGURATION
# ==========================================

BOT_TOKEN = ""
APP_TOKEN = ""

SOURCE_CHANNEL_ID = "C0CENFBMMH9"
TARGET_CHANNEL_ID = "C0CELEHEX45"


# ==========================================
# SLACK CONNECTION
# ==========================================

client = WebClient(token=BOT_TOKEN)


# ==========================================
# READ LATEST MESSAGE
# ==========================================

def read_latest_message(channel_id):

    response = client.conversations_history(
        channel=channel_id,
        limit=1
    )

    messages = response["messages"]

    if not messages:
        return None

    return messages[0]


# ==========================================
# PROCESS MESSAGE
# ==========================================

def process_message(message):

    text = message.get("text", "")

    print("Latest message:", text)

    # Temporary test: return the message
    return text


# ==========================================
# SEND RESPONSE
# ==========================================

def send_reply(message):

    client.chat_postMessage(
        channel=TARGET_CHANNEL_ID,
        text=message,
        mrkdwn=True
    )


# ==========================================
# MAIN TEST
# ==========================================

def main():

    try:
        print("🐱 Pippo is checking the source channel...")

        latest = read_latest_message(SOURCE_CHANNEL_ID)

        if not latest:
            print("No messages found.")
            return

        result = process_message(latest)

        if result:
            send_reply(
                f"🐾 I found the latest update!\n\n{result}"
            )

        print("Pippo completed the test!")

    except SlackApiError as e:
        print("Slack API error:", e.response["error"])

    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    main()