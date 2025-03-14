from ...aof.aof_text_consts import KYC

class AOFINDConstantsTexts:
    def __init__(self, json_data:dict, application_no:str,is_digilocker=True):
        """
        Note:
        Since, the AOFIND data is subset of AOF data i.e KYC data, we can use the KYC class to prepare the data.
        If that changes in future, we will have to modify this class to define all the constants texts for AOFIND.
        """
        self.data = KYC(kyc_data=json_data,application_no=application_no,is_digilocker=is_digilocker)