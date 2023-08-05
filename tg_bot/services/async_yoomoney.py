import aiohttp
from datetime import datetime
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Union

from yoomoney.operation.operation import Operation

from yoomoney.exceptions import (
    IllegalParamType,
    IllegalParamStartRecord,
    IllegalParamRecords,
    IllegalParamLabel,
    IllegalParamFromDate,
    IllegalParamTillDate,
    TechnicalError
    )

class Quickpay:
    def __init__(self,
                 receiver: str,
                 quickpay_form : str,
                 targets: str,
                 paymentType: str,
                 sum: float,
                 formcomment: str = None,
                 short_dest: str = None,
                 label: str = None,
                 comment: str = None,
                 successURL: str = None,
                 message: str = None,
                 need_fio: bool = None,
                 need_email: bool = None,
                 need_phone: bool = None,
                 need_address: bool = None,
                 ):
        self.receiver = receiver
        self.quickpay_form = quickpay_form
        self.targets = targets
        self.paymentType = paymentType
        self.sum = sum
        self.formcomment = formcomment
        self.short_dest = short_dest
        self.label = label
        self.comment = comment
        self.successURL = successURL
        self.message = message
        self.need_fio = need_fio
        self.need_email = need_email
        self.need_phone = need_phone
        self.need_address = need_address

    async def get_redirect_url(self):

        self.base_url = "https://yoomoney.ru/quickpay/confirm.xml?"

        payload = {}

        payload["receiver"] = self.receiver
        payload["quickpay_form"] = self.quickpay_form
        payload["targets"] = self.targets
        payload["paymentType"] = self.paymentType
        payload["sum"] = self.sum

        if self.formcomment != None:
            payload["formcomment"] = self.formcomment
        if self.short_dest != None:
            payload["short_dest"] = self.short_dest
        if self.label != None:
            payload["label"] = self.label
        if self.comment != None:
            payload["comment"] = self.comment
        if self.successURL != None:
            payload["successURL"] = self.successURL
        if self.message != None:
            payload["message"] = self.message
        if self.need_fio != None:
            payload["need_fio"] = self.need_fio
        if self.need_email != None:
            payload["need_email"] = self.need_email
        if self.need_phone != None:
            payload["need_phone"] = self.need_phone
        if self.need_address != None:
            payload["need_address"] = self.need_address

        for value in payload:
            self.base_url+=str(value).replace("_","-") + "=" + str(payload[value])
            self.base_url+="&"

        self.base_url = self.base_url[:-1].replace(" ", "%20")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url) as response:  
                    self.redirected_url = str(response.url)
        except Exception:
            self.redirected_url = None

        return self.redirected_url

class Client:
    def __init__(self,
                 token: str = None,
                 base_url: str = None,
                 ):

        if base_url is None:
            self.base_url = "https://yoomoney.ru/api/"

        if token is not None:
            self.token = token

    async def operation_history(self,
                          type: str = None,
                          label: str = None,
                          from_date: datetime = None,
                          till_date: datetime = None,
                          start_record: str = None,
                          records: int = None,
                          details: bool = None,
                          ):
        method = "operation-history"
        history = History(base_url=self.base_url,
                       token=self.token,
                       method=method,
                       type=type,
                       label=label,
                       from_date=from_date,
                       till_date=till_date,
                       start_record=start_record,
                       records=records,
                       details=details,
                       )

        return await history.get_operations()

class History:
    def __init__(self,
                 base_url: str = None,
                 token: str = None,
                 method: str = None,
                 type: str = None,
                 label: str = None,
                 from_date: Optional[datetime] = None,
                 till_date: Optional[datetime] = None,
                 start_record: str = None,
                 records: int = None,
                 details: bool = None,
                 ):

        self.__private_method = method

        self.__private_base_url = base_url
        self.__private_token = token

        self.type = type
        self.label = label
        try:
            if from_date is not None:
                from_date = "{Y}-{m}-{d}T{H}:{M}:{S}".format(
                    Y=str(from_date.year),
                    m=str(from_date.month),
                    d=str(from_date.day),
                    H=str(from_date.hour),
                    M=str(from_date.minute),
                    S=str(from_date.second)
                )
        except:
            raise IllegalParamFromDate()

        try:
            if till_date is not None:
                till_date = "{Y}-{m}-{d}T{H}:{M}:{S}".format(
                    Y=str(till_date.year),
                    m=str(till_date.month),
                    d=str(till_date.day),
                    H=str(till_date.hour),
                    M=str(till_date.minute),
                    S=str(till_date.second)
                )
        except:
            IllegalParamTillDate()

        self.from_date = from_date
        self.till_date = till_date
        self.start_record = start_record
        self.records = records
        self.details = details


    async def get_operations(self):

        access_token = str(self.__private_token)
        url = self.__private_base_url + self.__private_method

        headers = {
            'Authorization': 'Bearer ' + str(access_token),
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        payload = {}
        if self.type is not None:
            payload["type"] = self.type
        if self.label is not None:
            payload["label"] = self.label
        if self.from_date is not None:
            payload["from"] = self.from_date
        if self.till_date is not None:
            payload["till"] = self.till_date
        if self.start_record is not None:
            payload["start_record"] = self.start_record
        if self.records is not None:
            payload["records"] = self.records
        if self.details is not None:
            payload["details"] = self.details

        async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=payload) as response:  
                    data = await response.json()

        if "error" in data:
            if data["error"] == "illegal_param_type":
                raise IllegalParamType()
            elif data["error"] == "illegal_param_start_record":
                raise IllegalParamStartRecord()
            elif data["error"] == "illegal_param_records":
                raise IllegalParamRecords()
            elif data["error"] == "illegal_param_label":
                raise IllegalParamLabel()
            elif data["error"] == "illegal_param_from":
                raise IllegalParamFromDate()
            elif data["error"] == "illegal_param_till":
                raise IllegalParamTillDate()
            else:
                raise TechnicalError()


        self.next_record = None
        if "next_record" in data:
            self.next_record = data["next_record"]

        self.operations = list()
        for operation_data in data["operations"]:
            param = {}
            if "operation_id" in operation_data:
                param["operation_id"] = operation_data["operation_id"]
            else:
                param["operation_id"] = None
            if "status" in operation_data:
                param["status"] = operation_data["status"]
            else:
                param["status"] = None
            if "datetime" in operation_data:
                param["datetime"] = datetime.strptime(str(operation_data["datetime"]).replace("T", " ").replace("Z", ""), '%Y-%m-%d %H:%M:%S')
            else:
                param["datetime"] = None
            if "title" in operation_data:
                param["title"] = operation_data["title"]
            else:
                param["title"] = None
            if "pattern_id" in operation_data:
                param["pattern_id"] = operation_data["pattern_id"]
            else:
                param["pattern_id"] = None
            if "direction" in operation_data:
                param["direction"] = operation_data["direction"]
            else:
                param["direction"] = None
            if "amount" in operation_data:
                param["amount"] = operation_data["amount"]
            else:
                param["amount"] = None
            if "label" in operation_data:
                param["label"] = operation_data["label"]
            else:
                param["label"] = None
            if "type" in operation_data:
                param["type"] = operation_data["type"]
            else:
                param["type"] = None


            operation = Operation(
                operation_id= param["operation_id"],
                status=param["status"],
                datetime=datetime.strptime(str(param["datetime"]).replace("T", " ").replace("Z", ""), '%Y-%m-%d %H:%M:%S'),
                title=param["title"],
                pattern_id=param["pattern_id"],
                direction=param["direction"],
                amount=param["amount"],
                label=param["label"],
                type=param["type"],
            )
            self.operations.append(operation)

        return self.operations
        