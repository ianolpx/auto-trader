# from handlers.api.line import LineHandler
from handlers.api.mailjet import MailJetHandler


class NotifyHandler():
    async def send_message(self, message):
        target = MailJetHandler()
        await target.send_message(message)


# python -m handlers.api.notifier
if __name__ == "__main__":
    import asyncio
    asyncio.run(NotifyHandler().send_message("Hello from NotifyHandler"))
