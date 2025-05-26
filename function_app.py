import logging
import azure.functions as func
import asyncio
import time
from handlers.core import execute
from handlers.api import notifier
from settings import settings

app = func.FunctionApp()


# schedule="40 * * * * *",
@app.schedule(
    schedule="58 * * * *",
    arg_name="myTimer",
    run_on_startup=False,
    use_monitor=False)
async def timer_trigger(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')
    logging.info('Python timer trigger function executed.')
    # execute_handler = execute.ExecuteHandler()
    # await execute_handler.run()
    # await notifier.NotifyHandler().send_message("System is restarting...")
    try:
        await main_trigger()
    except Exception as e:
        await notifier.NotifyHandler().send_message(f"Error in timer trigger: {e}")


async def main_trigger():
    # utc time
    hour = time.localtime().tm_hour
    if settings.target_period == '4h':
        timetable = [3, 7, 11, 15, 19, 23]
    elif settings.target_period == '1d':
        timetable = [23]
    if hour in timetable:
        await notifier.NotifyHandler().send_message("System is restarting...")
        execute_handler = execute.ExecuteHandler()
        await execute_handler.run()
    else:
        logging.info('The timer is not in the list!')

# python -m function_app
if __name__ == '__main__':
    asyncio.run(main_trigger())
