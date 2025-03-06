import apluggy as pluggy
import requests
from datetime import datetime
from lyikpluginmanager import (
    getProjectName,
    NSDLRootModel,
    NSDLDematSpec,
    GenericFormRecordModel,
)
from typing import Annotated
from typing_extensions import Doc

impl = pluggy.HookimplMarker(getProjectName())


class NSDLDemat(NSDLDematSpec):
    """"""

    @impl
    async def translate_to_nsdl_demat(
        self,
        context,
        from_record: Annotated[GenericFormRecordModel, Doc("Form Record")],
    ) -> Annotated[NSDLRootModel, Doc("The Desired output for NSDL Demat")]:
        """
        This function is to translate form record into NSDL demat request model
        """
        nsdl_model = NSDLRootModel()
        return nsdl_model

    def get_request_time(self):
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")

    # async def call_api(
    #     self,
    #     transaction_type: str,
    #     request_ref: str,
    #     requestor_id: str,
    #     requestor: str,
    #     digital_signature: str,
    #     request_data: NSDLRootModel,
    # ):
    #     try:
    #         url = f"https://eservices-test.nsdl.com/client-service/v5/instaDemat/{requestor_id}/order"
    #         headers = {
    #             "Content-Type": "application/json",
    #             "Transaction-Type": transaction_type,
    #             "Requestor": requestor,
    #             "Request-Reference": request_ref,
    #             "Request-Time": self.get_request_time(),
    #             "Success-Url": "http://nsdl.uat.com/exampleSuccess",
    #             "Fail-Url": "http://nsdl.uat.com/exampleFail",
    #             "Digital-Signature": digital_signature,
    #         }
    #         response = requests.post(
    #             url, json=request_data.model_dump(), headers=headers
    #         )
    #         return response.json()
    #     except Exception as e:
    #         print(e)


sample_request_data = {
    "instr": {
        "beneficiaryDetails": {
            "primaryBeneficiary": {
                "name": "Amit Kumar Mishra",
                "shortName": "amit",
                "pan": "BOYPP7655B",
                "panFlag": "Y",
                "grossAnnualIncome": "01",
                "dob": "19970804",
                "gender": "2",
                "aadhar": "",
                "mobile": "*************",
                "email": "abc@abc.com",
                "ddpiid": "123456",
                "eStatement": "E",
                "dematAccType": "04",
                "dematAccSubType": "01",
                "rbiRefNo": "12345",
                "rbiApprovalDate": "20201222",
                "modeOfOperation": "1",
                "communicationToBeSend": "2",
                "beneficiaryCoresAddress": {
                    "addressType": "1",
                    "addressLine1": "301, Matru chaya",
                    "addressLine2": "Meetha Ghar Road",
                    "addressLine3": "Nanepada Road Mulund East",
                    "addressLine4": "Near Kelakar college, Mumbai",
                    "zipcode": "400071",
                    "city": "Mumbai",
                    "statecode": "17",
                    "countrycode": "356",
                },
                "beneficiaryPermAddress": {
                    "addressType": "4",
                    "addressLine1": "Olympiad, Z-Wing",
                    "addressLine2": "99th floor, Gulbarg Marg",
                    "addressLine3": "Lower Parel, Mumbai 400013",
                    "addressLine4": "",
                    "zipcode": "400013",
                    "city": "Mumbai",
                    "statecode": "17",
                    "countrycode": "356",
                },
                "signature": "base64_encoded_signature_string",
            },
            "numOfJointHolders": "2",
            "listOfJointHolders": [
                {
                    "seq": "2",
                    "name": "Joint Holder 1",
                    "pan": "AXSDE1234K",
                    "panFlag": "Y",
                    "dob": "19970804",
                    "mobileNo": "9999999999",
                    "emailId": "abc@abc.com",
                    "smsfacility": "Y",
                },
                {
                    "seq": "3",
                    "name": "Joint Holder 2",
                    "pan": "AXSDE1234K",
                    "panFlag": "Y",
                    "dob": "19970804",
                    "mobileNo": "9999999999",
                    "emailId": "abc@abc.com",
                    "smsfacility": "Y",
                },
            ],
            "additionalBeneDetails": {
                "familyMobileFlag": "N",
                "familyEmailFlag": "N",
                "nominationOption": "Y",
                "occupation": "2",
                "fatherOrHusbandName": "Kariya",
                "dpId": "IN123456",
                "clientId": "80957190",
                "sharePercentEqually": "N",
                "numOfNominees": "2",
                "listOfNominees": [
                    {
                        "seqNo": "1",
                        "nomineeName": "Mahesh Patel",
                        "relationWithNominee": "01",
                        "nomineeAddress": {
                            "addressType": "3",
                            "addressLine1": "",
                            "addressLine2": "",
                            "addressLine3": "",
                            "addressLine4": "",
                            "zipcode": "",
                            "city": "",
                            "statecode": "",
                            "countrycode": "",
                        },
                        "nomineeMobileNum": "",
                        "nomineeEmailId": "test@test.com",
                        "nomineeShare": "30",
                        "nomineeIdentificationDtls": {
                            "pan": "QWERT1234Y",
                            "aadhar": "XXXXXXXXXXXXXX",
                            "savingBankAccNo": "XXXXXXXX",
                            "dematAccId": "INXXXXXXXXXXXXX",
                        },
                        "minor": "Y",
                        "dob": "20210101",
                        "guardianName": "Suresh Patel",
                        "guardianAddress": {
                            "addressType": "6",
                            "addressLine1": "test",
                            "addressLine2": "test",
                            "addressLine3": "",
                            "addressLine4": "",
                            "zipcode": "400071",
                            "city": "Mumbai",
                            "statecode": "17",
                            "countrycode": "91",
                        },
                        "guardianMobileNum": "00000000000",
                        "guardianEmailId": "test@test.com",
                        "guardianRelationship": "07",
                        "guardianIdentificationDtls": {
                            "pan": "XXXXXXXXXX",
                            "aadhar": "1111111111",
                            "savingBankAccNo": "",
                            "dematAccId": "",
                        },
                    }
                ],
            },
        },
        "bankDetails": {
            "accountNumber": "1234567890987654",
            "bankName": "XYZ Bank",
            "ifsc": "SBIN0000009",
            "micr": "400019060",
            "accountType": "10",
            "bankAddress": {
                "addressType": "2",
                "addressLine1": "301,Kamala Mills Compound",
                "addressLine2": "Gr Flr, Tulsi Pipe Rd, Lower Parel",
                "addressLine3": "Near NSDL",
                "addressLine4": "Mumbai, Maharashtra",
                "zipcode": "400071",
            },
        },
    }
}


# import asyncio


# async def main():
#     demat = NSDLDemat()

#     data = NSDLRootModel.model_validate(sample_request_data)

#     response = await demat.call_api(
#         transaction_type="IDD",
#         request_ref="TST00000142",
#         requestor_id="IN300001",
#         requestor="OBC",
#         digital_signature="",
#         request_data=data,
#     )
#     print(response)


# if __name__ == "__main__":
#     asyncio.run(main())
