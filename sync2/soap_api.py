from datetime import datetime


class SoapTestApis:
    def __init__(self, repositories, jasper_soap_api, config, ServiceBusClient, QueueClient, Message):
        self.audit_repo = repositories['audit']
        self.carrier_repo = repositories['carrier']
        self.device_repo = repositories['device']
        self.sync_repo = repositories['sync']
        self.usage_repo = repositories['usage']
        self.jasper_soap_api = jasper_soap_api
        self.Message = Message
        self.ServiceBusClient = ServiceBusClient
        self.QueueClient = QueueClient
        self.config = config


    def set_carrier_jasper_soap_api_credentials(self, carrier):
        self.jasper_soap_api.set_credentials(
            username=carrier['jasper']['credentials']['username'],
            password=carrier['jasper']['credentials']['password'],
            api_path=carrier['jasper']['credentials']['apiPath'],
            license_key=carrier['jasper']['credentials']['licenseKey'],
            carrier_id=carrier['id'],
            carrier_name=carrier['name'])


    def get_device_details(self, iccid, carrier_id):
        carrier = self.carrier_repo.get_carrier(carrier_id)
        self.set_carrier_jasper_soap_api_credentials(carrier)
        details = self.jasper_soap_api.get_terminal_details([iccid], '')
        return details

    def get_modified_terminals(self, carrier_id):
        carrier = self.carrier_repo.get_carrier(carrier_id)
        self.set_carrier_jasper_soap_api_credentials(carrier)
        config_updated =   datetime(2020, 5, 10)
        details = self.jasper_soap_api.get_modified_terminals(config_updated, '', 121)
        print(details)
        
