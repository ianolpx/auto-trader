from settings import settings
import requests
import asyncio


class LineHandler:
    url = "https://notify-api.line.me/api/notify"
    token = settings.line_token

    async def send_message(self, message):
        with requests.post(
            self.url,
            headers={
                "Authorization": f"Bearer {self.token}"
            },
            data={
                "message": message
            }
        ) as response:
            return response.text


async def test():
    await LineHandler().send_message("Hello from LineHandler")

# python -m handlers.line
if __name__ == "__main__":
    asyncio.run(test())
