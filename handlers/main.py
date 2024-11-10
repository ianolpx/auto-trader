from handlers.algo import AlgoHandler
from handlers.cosmosdb import CosmosDBHandler
from handlers.bybit import BybitHandler
from handlers.line import LineHandler
import asyncio
import logging
import time


class MainHandler():
    db = CosmosDBHandler()
    algo = AlgoHandler()
    bybit = BybitHandler()
    profile = None

    async def execute_action(self, action, item, container):
        if action == 'buy':
            try:
                res = self.bybit.buy_eth(symbol=item)
                await self.db.update_profile({
                    'status': 'bought3L' if '3L' in item else 'bought3S',
                    'id': '1',
                    'T1': 'bybit'
                }, container)
                await LineHandler().send_message(
                    f"{item} bought")
            except Exception as e:
                await LineHandler().send_message(
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
                logging.info(res)
                await LineHandler().send_message(
                    f"{item} sold")
            except Exception as e:
                await LineHandler().send_message(
                    f"Error selling {item}, {e}")
        else:
            await LineHandler().send_message(
                "Holding")

    async def run(self):
        await LineHandler().send_message("Running main handler")
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
            signal = await self.algo.get_signal(profile)
        except Exception as e:
            logging.error(e)
            signal = {
                'status': 'hold-exception(signal)',
                'case': 'case5'
            }

        for action, item in zip(signal['actions'], signal['items']):
            await self.execute_action(action, item, container)
            time.sleep(3)
        await self.db.close()


async def main():
    main = MainHandler()
    await main.run()

# python -m handlers.main
if __name__ == "__main__":
    asyncio.run(main())
