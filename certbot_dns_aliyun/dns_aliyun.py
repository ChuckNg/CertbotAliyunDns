#-*- coding:utf-8 -*-
""" DNS Authenticator for Aliyun """
import json
import logging

import zope.interface
from certbot import interfaces
from certbot.plugins import dns_common

LOGGER = logging.getLogger(__name__)


@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.provider(interfaces.IPluginFactory)
class Authenticator(dns_common.DNSAuthenticator):
    """
    Implement the Certbot with Aliyun DNS SDK.
    """

    description = ('Obtain certificates using a DNS TXT record (if you are using Aliyun DNS '
                   'for DNS).')

    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)
        self.credentials = None

    @classmethod
    def add_parser_arguments(cls, add):
        super(Authenticator, cls).add_parser_arguments(add, default_propagation_seconds=60)
        add("credentials",
            help=("Path to local stored Aliyun Access Key &Secret for update DNS record in Aliyun"),
            default=None)

    def more_info(self):
        return "This plugins setup DNS TXT record for dns-01 challenge by using Aliyun API."

    def _setup_credentials(self):
        self._configure_file("credentials",
                             "path to Aliyun DNS access secret JSON file")
        dns_common.validate_file_permissions(self.conf("credentials"))

    def _perform(self, domain_name, record_name, record_value):
        self._get_aliyundns_client().add_txt_record(domain_name, record_name, record_value)

    def _cleanup(self, domain_name, record_name, record_value):
        self._get_aliyundns_client().delete_txt_record(domain_name, record_name, record_value)

    def _get_aliyundns_client(self):
        return _AliyunDnsClient(self.conf("credentials"))

TTL = 600
PAGE_SIZE = 100
DEFAULT_REGION = "cn-beijing"


class _AliyunDnsClient():
    """
    Encapsulates base DNS operation with Aliyun DNS SDK: aliyunsdkalidns.
    """

    def __init__(self, secret_key_path=None):
        from aliyunsdkcore import client
        try:
            with open(secret_key_path, 'r') as file:
                json_content = file.read()
                self._access_key, self._access_secret = json.loads(json_content)["access_key"], \
                                                        json.loads(json_content)["access_secret"]
                self._client = client.AcsClient(self._access_key, \
                                               self._access_secret, \
                                               DEFAULT_REGION)
        except IOError:
            LOGGER.error("Aliyun access secret file: %s not found.", secret_key_path)
        except Exception as error:
            LOGGER.error("Aliyun SDK client init failed: %s.", error)

    def add_txt_record(self, domain_name, record_name, record_value):
        from aliyunsdkalidns.request.v20150109 import AddDomainRecordRequest
 
        request = AddDomainRecordRequest.AddDomainRecordRequest()
        request.set_accept_format("json")
        #
        request.set_DomainName(domain_name)
        request.set_Type("TXT")
        record_name = record_name.replace(("." + domain_name), "")
        request.set_RR(record_name)
        request.set_Value(record_value)
        request.set_TTL(TTL)
        LOGGER.info("domain_name: %s, record_name: %s, record_value: %s.",\
                domain_name, record_name, record_value)
        result = json.loads(self._client.do_action_with_exception(request))
        LOGGER.info("add result: %s.", result)
    
    def delete_txt_record(self, domain_name, record_name, record_value):
        from aliyunsdkalidns.request.v20150109 \
        import DescribeDomainRecordsRequest, DeleteDomainRecordRequest

        # describe request for dns record id
        record_id = None
        des_request = DescribeDomainRecordsRequest.DescribeDomainRecordsRequest()
        des_request.set_accept_format("json")
        des_request.set_PageNumber(1)
        des_request.set_PageSize(PAGE_SIZE)

        # delete request for delete corresponsing dns record
        del_request = DeleteDomainRecordRequest.DeleteDomainRecordRequest()
        del_request.set_accept_format("json")

        record_name = record_name.replace(("." + domain_name), "")
        des_request.set_DomainName(domain_name)
        record_first_page_result = json.loads(self._client.do_action_with_exception(des_request))
        
        total_record_count = record_first_page_result["TotalCount"]
        if total_record_count < PAGE_SIZE:
            result = record_first_page_result["DomainRecords"]["Record"]
            for record in result:
                if record["Type"] == "TXT" and \
                   record["RR"] == record_name and \
                   record["Value"] == record_value and \
                   record["DomainName"] == domain_name:
                    record_id = record["RecordId"]
                    LOGGER.info("Delete record %s %s-%s, record Id: %s.",\
                        record_name, domain_name, record["Value"], record_id)
        else:
            page_num = (total_record_count / PAGE_SIZE) if total_record_count % PAGE_SIZE == 0 \
                       else (int(total_record_count/PAGE_SIZE) + 1)
            for page in range(2, page_num + 1):
                des_request.set_PageNumber(page)
                result = json.loads(self._client.do_action_with_exception(des_request))
                for record in result:
                    if record["Type"] == "TXT" and \
                       record["RR"] == record_name and \
                       record["DomainName"] == domain_name:
                        record_id = record["RecordId"]
                        LOGGER.info("Delete record %s %s-%s, record Id: %s.",\
                            record_name, domain_name, record["Value"], record_id)
                        break
        LOGGER.info("record id: {}.".format(record_id))
        # no record Id no delete operation.
        if record_id:
            del_request.set_RecordId(record_id)
            del_result = json.loads(self._client.do_action_with_exception(del_request))
            LOGGER.info("delete result: %s.", del_result)
        else:
            raise Exception("%s %s-%s record cannot be found.",\
                record_name, domain_name, record["Value"])
