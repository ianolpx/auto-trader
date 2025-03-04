from unittest.mock import AsyncMock
from handlers.api.notifier import NotifyHandler
import pytest


@pytest.mark.asyncio
async def test_send_message():
    notifier = NotifyHandler()
    notifier.send_message = AsyncMock()
    message = "Hello from NotifyHandler"
    await notifier.send_message(message)
    notifier.send_message.assert_called_once_with(message)
