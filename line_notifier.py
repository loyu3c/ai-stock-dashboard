from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError
from config import Config

class LineNotifier:
    def __init__(self):
        if not Config.LINE_CHANNEL_ACCESS_TOKEN or not Config.LINE_USER_ID:
            print("⚠️ Warning: LINE Messaging API credentials not set in .env")
            self.line_bot_api = None
            self.user_id = None
            return

        try:
            self.line_bot_api = LineBotApi(Config.LINE_CHANNEL_ACCESS_TOKEN)
            self.user_id = Config.LINE_USER_ID
            print("✅ Initialized LINE Messaging API")
        except Exception as e:
            print(f"❌ Failed to initialize LINE API: {e}")
            self.line_bot_api = None

    def send_message(self, message: str):
        """
        Sends a push message to the configured User ID.
        """
        if not self.line_bot_api or not self.user_id:
            print("❌ Cannot send message: LINE API not configured.")
            return

        try:
            self.line_bot_api.push_message(
                self.user_id, 
                TextSendMessage(text=message)
            )
            print("✅ LINE Message sent successfully!")
        except LineBotApiError as e:
            print(f"❌ Failed to send LINE message: {e.status_code} - {e.error.message}")
        except Exception as e:
            print(f"❌ Error sending LINE message: {e}")

if __name__ == "__main__":
    # Test Run
    notifier = LineNotifier()
    notifier.send_message("🔔 AI選股小幫手: 這是一則測試訊息！\n如果您收到這個，代表 Messaging API 設定成功囉！🚀")
