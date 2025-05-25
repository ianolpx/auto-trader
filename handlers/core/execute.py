from handlers.core.algo import AlgoHandler
from handlers.db.cosmosdb import CosmosDBHandler
from handlers.api.bybit import BybitHandler
from handlers.api.notifier import NotifyHandler
from handlers.api.writer import WriterHandler
from handlers.utils.common import get_current_time
import asyncio
import logging
import time


class ExecuteHandler():
    db = CosmosDBHandler()
    algo = AlgoHandler()
    bybit = BybitHandler()
    writer = WriterHandler().get_cursor()
    profile = None

    async def execute_action(self, action, item, container, insight):
        t = get_current_time()
        if action == 'buy':
            try:
                res = self.bybit.buy_eth(symbol=item)
                await self.db.update_profile({
                    'status': 'bought3L' if '3L' in item else 'bought3S',
                    'id': '1',
                    'T1': 'bybit'
                }, container)
                await NotifyHandler().send_message(
                    f"{item} bought")
                self.writer.append_row(
                    [t, f"{item} bought", insight['status']])

            except Exception as e:
                await NotifyHandler().send_message(
                    f"Error buying {item}, {e}")
        elif action == 'sell':
            try:
                res = self.bybit.sell_eth(
                    symbol=item,
                    qty_symbol=item.split('USDT')[0]
                )
                await self.db.update_profile({
                    'status': 'ready',
                    'id': '1',
                    'T1': 'bybit'
                }, container)
                budget = self.bybit.get_available_budget_usdt()
                await NotifyHandler().send_message(
                    f"{item} sold, budget: {budget}")
                self.writer.append_row(
                    [t, f"{item} sold", insight['status']])
            except Exception as e:
                await NotifyHandler().send_message(
                    f"Error selling {item}, {e}")
        else:
            # await LineHandler().send_message("Holding")
            pass

    async def run(self):
        # await LineHandler().send_message("Running main handler")
        try:
            container = await self.db.get_or_create_container()
        except Exception as e:
            logging.error(e)

        try:
            profile = await self.db.get_profile(container)
        except Exception as e:
            logging.error(e)
            profile = {
                'status': 'exception(profile)',
                'id': '1',
                'T1': 'bybit'
            }

        try:
            signal, insight = await self.algo.get_signal(profile)
        except Exception as e:
            logging.error(e)
            signal = {
                'status': 'hold-exception(signal)',
                'case': 'case5'
            }

        for action, item in zip(signal['actions'], signal['items']):
            await self.execute_action(action, item, container, insight)
            time.sleep(3)
        await self.db.close()


async def main():
    execute_handler = ExecuteHandler()
    await execute_handler.run()

# python -m handlers.core.execute
if __name__ == "__main__":
    asyncio.run(main())
