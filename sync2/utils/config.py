import os

from dotenv import load_dotenv
load_dotenv()

log_level = os.getenv('LOG_LEVEL')
mongo_uri = os.getenv('MONGO_URI')
mongo_db = os.getenv('MONGO_DB')
appinsights_instrumentationkey = os.getenv('APPINSIGHTS_INSTRUMENTATIONKEY')
service_bus_connection_string = os.getenv('SERVICE_BUS_CONNECTION_STRING')
search_service_name = os.getenv('SEARCH_SERVICE_NAME')
search_api_key = os.getenv('SEARCH_API_KEY')