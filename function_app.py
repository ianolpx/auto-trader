import logging
import azure.functions as func
import asyncio
from handlers import main


app = func.FunctionApp()


@app.schedule(
    schedule="53 3,7,11,15,19,23 * * *",
    arg_name="myTimer",
    run_on_startup=True,
    use_monitor=False)
async def timer_trigger(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function executed.')
    MH = main.MainHandler()
    await MH.run()


async def test():
    MH = main.MainHandler()
    await MH.run()

if __name__ == '__main__':
    asyncio.run(test())
