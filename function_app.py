import logging
import azure.functions as func
from settings import settings

app = func.FunctionApp()


@app.schedule(schedule="30 * * * * *", arg_name="myTimer", run_on_startup=True,
              use_monitor=False) 
async def timer_trigger(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function executed.')
    logging.info(f'App version: {settings.app_version}')
    logging.info(f'CosmosDB endpoint: {settings.cosmos_endpoint}')
    logging.info(f'CosmosDB database_id: {settings.cosmos_database_id}')
