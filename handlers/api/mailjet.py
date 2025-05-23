from mailjet_rest import Client
from settings import settings
import asyncio
import time


class MailJetHandler():
    def __init__(self):
        self.mailjet = Client(auth=(
            settings.mailjet_api_key,
            settings.mailjet_api_secret
        ), version='v3.1')

    async def send_message(self, message):
        utc_time = time.strftime(
            '%Y-%m-%d %H:%M:%S', time.gmtime())
        message = f"{message} at {utc_time} (UTC)"
        data = {
            'Messages': [
                {
                    "From": {
                        "Email": f"{settings.mailjet_sender_id}@gmail.com",
                        "Name": "Auto Trader"
                    },
                    "To": [
                        {
                            "Email": "{}@gmail.com".format(
                                settings.mailjet_receiver_id),
                            "Name": settings.mailjet_receiver_id
                        }
                    ],
                    "Subject": "Auto Trader Notification",
                    "TextPart": message,
                }
            ]
        }
        result = self.mailjet.send.create(data=data)
        return result.json()


async def test():
    await MailJetHandler().send_message("Hello from MailJetHandler")


# python -m handlers.api.mailjet
if __name__ == "__main__":
    asyncio.run(test())
