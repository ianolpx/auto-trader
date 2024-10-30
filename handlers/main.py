from handlers.algo import AlgoHandler
from handlers.cosmosdb import CosmosDBHandler
from handlers.bybit import BybitHandler
import asyncio
import logging


class MainHandler():
    db = CosmosDBHandler()
    algo = AlgoHandler()
    bybit = BybitHandler()
    profile = None

    async def run(self):
        logging.info('Running main handler...')
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
        logging.info(profile)
        logging.info(signal)
        if signal['status'] == 'buy':
            res = self.bybit.buy_eth()
            await self.db.update_profile({
                'status': 'bought',
                'id': '1',
                'T1': 'bybit'
            }, container)
            logging.info(res)
        elif signal['status'] == 'sell':
            res = self.bybit.sell_eth()
            await self.db.update_profile({
                'status': 'ready',
                'id': '1',
                'T1': 'bybit'
            }, container)
            logging.info(res)
        else:
            logging.info('Holding...')
        await self.db.close()


async def main():
    main = MainHandler()
    await main.run()

# python -m handlers.main
if __name__ == "__main__":
    asyncio.run(main())
