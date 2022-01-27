import datetime, os
import logging
from .real_time_prod_data import RealTimeData
import azure.functions as func


def main(mytimer: func.TimerRequest) -> None:
    FINGRID_API_KEY = os.getenv("FINGRID_API_KEY")
    fingrid_api = RealTimeData()
    fingrid_api.fetch_data_fi(FINGRID_API_KEY)
    logging.info(f"API call succeeded at UTC: {datetime.datetime.utcnow()}")