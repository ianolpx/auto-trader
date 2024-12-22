import logging
import azure.functions as func
import asyncio
import time
from handlers.core import execute

app = func.FunctionApp()


@app.schedule(
    schedule="57 * * * *",
    arg_name="myTimer",
    run_on_startup=True,
    use_monitor=False)
async def timer_trigger(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function executed.')
    # execute_handler = execute.ExecuteHandler()
    # await execute_handler.run()
    await main_trigger()


async def main_trigger():
    # utc time
    hour = time.localtime().tm_hour
    if hour in [3, 7, 11, 15, 19, 23]:
        execute_handler = execute.ExecuteHandler()
        await execute_handler.run()
    else:
        logging.info('The timer is not in the list!')

# python -m function_app
if __name__ == '__main__':
    asyncio.run(main_trigger())
