import xmltodict
from datetime import datetime
import logging
logger = logging.getLogger(__name__)

class JasperSoapApiError(Exception):
    def __init__(self, message, content, fault):
        super().__init__(message)
        self.message = message
        self.content = content
        self.fault = fault

class JasperSoapApi:

    def __init__(self, requests):
        self.requests = requests

    def set_credentials(self, username, password, license_key, api_path, carrier_id, carrier_name):
        self.username = username
        self.password = password
        self.license_key = license_key
        self.api_path = api_path
        self.carrier_id = carrier_id
        self.carrier_name = carrier_name

    def parse_with_default(self, node, name, default=''):
        if name in node:
            return node[name]
        else:
            return default

    def parse_date(self, node, name):
        if name in node:
            return datetime.strptime(node[name],'%Y-%m-%dT%H:%M:%S.%f%z')
        else:
            return None

    def parse_float(self, node, name):
        if name in node:
            return float(node[name])
        else:
            return 0.0

    def parse_int(self, node, name):
        if name in node:
            return int(node[name])
        else:
            return 0

    def is_node_null(self, node, name):
        return True if name in node and '@xsi:nil' in node[name] and node[name]['@xsi:nil'] == "true" else False

    def parse_nullable_with_default(self, node, name, default):
        if self.is_node_null(node, name):
            return default
        else:
            return node[name]

    def parse_terminal(self, terminal):

        return {
            'accountId': terminal['ns2:accountId'],
            'ctdSessionCount': int(self.parse_nullable_with_default(terminal, 'ns2:ctdSessionCount', 0)),
            'custom1': terminal['ns2:custom1'],
            'custom2': terminal['ns2:custom2'],
            'custom3': terminal['ns2:custom3'],
            'custom4': terminal['ns2:custom4'],
            'custom5': terminal['ns2:custom5'],
            'custom6': terminal['ns2:custom6'],
            'custom7': terminal['ns2:custom7'],
            'custom8': terminal['ns2:custom8'],
            'custom9': terminal['ns2:custom9'],
            'custom10': terminal['ns2:custom10'],
            'customer': self.parse_with_default(terminal, 'ns2:customer'),
            'dateActivated': self.parse_date(terminal, 'ns2:dateActivated'),
            'dateAdded': self.parse_date(terminal, 'ns2:dateAdded'),
            'dateModified': self.parse_date(terminal, 'ns2:dateModified'),
            'dateShipped': self.parse_date(terminal, 'ns2:dateShipped'),
            'fixedIpAddress': self.parse_nullable_with_default(terminal, 'ns2:fixedIpAddress', None),
            'iccid': terminal['ns2:iccid'],
            'imei': terminal['ns2:imei'],
            'imsi': terminal['ns2:imsi'],
            'modem': self.parse_with_default(terminal, 'ns2:modem'),
            'monthToDateUsage': self.parse_float(terminal, 'ns2:monthToDateUsage'),
            'monthToDateDataUsage': self.parse_float(terminal, 'ns2:monthToDateDataUsage'),
            'monthToDateSMSUsage': self.parse_int(terminal,'ns2:monthToDateSMSUsage'),
            'monthToDateVoiceUsage': self.parse_int(terminal,'ns2:monthToDateVoiceUsage'),
            'msisdn': self.parse_with_default(terminal, '@msisdn', None),
            'ratePlan': terminal['ns2:ratePlan'],
            'status': terminal['ns2:status'],
            'terminalId': self.parse_with_default(terminal, 'ns2:terminalId')
        }

    def parse_for_soap_fault(self, content):
        if content:
            try:
                xml = xmltodict.parse(content)
                fault = xml['SOAP-ENV:Envelope']['SOAP-ENV:Body']['SOAP-ENV:Fault']
                return fault
            except:
                pass
        return None

    def build_soap_envelope(self, token, message):
        return \
            f'<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">' \
            '<SOAP-ENV:Header>' \
            f'{token}' \
            '</SOAP-ENV:Header>' \
            '<SOAP-ENV:Body>' \
            f'{message}' \
            '</SOAP-ENV:Body>' \
            '</SOAP-ENV:Envelope>'

    def build_username_token(self, username, password):
        return \
           '<wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" SOAP-ENV:mustUnderstand="1">' \
           '<wsse:UsernameToken xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" wsu:Id="XWSSGID-1533767078840-1882724546">' \
           f'<wsse:Username>{username}</wsse:Username>' \
           f'<wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">{password}</wsse:Password>' \
           '</wsse:UsernameToken>' \
           '</wsse:Security>'

    def build_soap_action(self, service, message):
        return f'http://api.jasperwireless.com/ws/service/{service}/{message}'

    def build_url(self, service):
        return f'{self.api_path}/ws/service/{service}'

    def get_modified_terminals(self, since, message_id, page_number=None):

        logger.debug(f'get_modified_terminals called - since:{since} message_id:{message_id} page_number:{page_number}')

        sinceIso = since.isoformat()
        page_number_element = f'<jws:pageNumber>{page_number}</jws:pageNumber>' if page_number else ''

        message = \
            f'<jws:GetModifiedTerminalsRequest xmlns:jws="http://api.jasperwireless.com/ws/schema">' \
            f'<jws:messageId>{message_id}</jws:messageId><jws:version>1.0</jws:version>' \
            f'<jws:licenseKey>{self.license_key}</jws:licenseKey>' \
            f'<jws:since>{sinceIso}</jws:since>' \
            f'{page_number_element}' \
            '</jws:GetModifiedTerminalsRequest>'

        action = self.build_soap_action(service='terminal', message='GetModifiedTerminals')
        headers = {'content-type': 'text/xml', 'SOAPAction': action}
        url = self.build_url('terminal')
        token = self.build_username_token(username=self.username, password=self.password)
        env = self.build_soap_envelope(token=token, message=message)

        logger.debug(f'get_modified_terminals request: {url} {headers} {env}')

        results = { 'pages':0, 'iccids':[]}

        response = self.requests.post(url, headers=headers, data=env)
        content = response.content.decode('utf-8')
        logger.debug(
            f"get_modified_terminals response: {response.status_code} {response.content.decode('utf-8')}")

        if response.status_code == 200:
            xml = xmltodict.parse(content)
            response = xml['SOAP-ENV:Envelope']['SOAP-ENV:Body']['ns2:GetModifiedTerminalsResponse']

            results['pages'] = int(response['ns2:totalPages'])
            container = response['ns2:iccids']
            if container:
                iccids = container['ns2:iccid']
                if isinstance(iccids, list):
                    results['iccids'].extend(iccids)
                elif isinstance(iccids, str):
                    results['iccids'].append(iccids)

            logger.debug(f"get_modified_terminals return: {results}")

            return results
        else:
            fault = self.parse_for_soap_fault(content)
            print(fault)
            logger.debug(f"get_modified_terminals error {fault} {content}")
            raise JasperSoapApiError('get_modified_terminals error', fault, content)


    def get_terminal_details(self, iccids, message_id):

        logger.debug(f'get_terminal_details called - iccids:{iccids} message_id:{message_id}')

        iccid_elements = ''.join([f'<jws:iccid>{iccid}</jws:iccid>' for iccid in iccids])

        message = \
            '<jws:GetTerminalDetailsRequest xmlns:jws="http://api.jasperwireless.com/ws/schema">' \
            f'<jws:messageId>{message_id}</jws:messageId>' \
            '<jws:version>1.0</jws:version>' \
            f'<jws:licenseKey>{self.license_key}</jws:licenseKey>' \
            f'<jws:iccids>{iccid_elements}</jws:iccids>' \
            '</jws:GetTerminalDetailsRequest>'

        action = self.build_soap_action(service='terminal', message='GetTerminalDetails')
        headers = {'content-type': 'text/xml', 'SOAPAction': action}
        url = self.build_url('terminal')
        token = self.build_username_token(username=self.username, password=self.password)
        env = self.build_soap_envelope(token=token, message=message)

        logger.debug(f'get_terminal_details request: {url} {headers} {env}')

        details = []

        response = self.requests.post(url, headers=headers, data=env)
        content = response.content.decode('utf-8')
        logger.debug(
            f"get_modified_terminals response: {response.status_code} {content}")

        if response.status_code == 200:
            xml = xmltodict.parse(content)
            response = xml['SOAP-ENV:Envelope']['SOAP-ENV:Body']['ns2:GetTerminalDetailsResponse']
            terminals = response['ns2:terminals']['ns2:terminal']

            if isinstance(terminals, list):
                for i in range(len(terminals)):
                    terminal = terminals[i]
                    detail = self.parse_terminal(terminal)
                    details.append(detail)
            elif isinstance(terminals, dict):
                detail = self.parse_terminal(terminals)
                details.append(detail)
            return details

        else:
            fault = self.parse_for_soap_fault(content)
            logger.debug(f"get_terminal_details error {fault} {content}")
            raise JasperSoapApiError('get_terminal_details error', fault, content)

