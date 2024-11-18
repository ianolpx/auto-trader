import logging
import azure.functions as func
import asyncio
from handlers.core import execute

app = func.FunctionApp()


@app.schedule(
    schedule="49 23 * * *",
    arg_name="myTimer",
    run_on_startup=True,
    use_monitor=False)
async def timer_trigger(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function executed.')
    execute_handler = execute.ExecuteHandler()
    await execute_handler.run()


async def test():
    execute_handler = execute.ExecuteHandler()
    await execute_handler.run()

# python -m function_app
if __name__ == '__main__':
    asyncio.run(test())
