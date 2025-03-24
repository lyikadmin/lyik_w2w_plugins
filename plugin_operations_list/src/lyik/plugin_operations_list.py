import apluggy as pluggy
from lyikpluginmanager import (
    ContextModel,
    getProjectName,
    Operation,
    OperationsListResponseModel,
    OperationsListSpec,
    GenericFormRecordModel,
    PluginException,
)
from typing_extensions import Annotated, Doc
from typing import List
import jwt
from enum import Enum
import logging

logger = logging.getLogger(__name__)
impl = pluggy.HookimplMarker(getProjectName())

KRA_TEXT = """
KRA (KYC Registration Agency) Upload is a process to upload your KYC (Know Your Customer) documents to a KYC Registration Agency. This ensures that your KYC details are verified and stored securely.

Steps to use KRA Upload:
1. **Initiate KRA Upload**: Start the KRA upload process by selecting the document you want to upload.
2. **Document Selection**: Choose the type of document you want to upload (e.g., PAN Card, Passport, etc.).
3. **Upload Document**: Upload a clear and legible copy of the selected document.
4. **Verification**: The uploaded document will be verified by the KYC Registration Agency.

Ensure that the document you upload is valid and up-to-date to avoid any delays in the verification process.
"""

ESIGN = """
Aadhaar-based eSign is an online electronic signature service that allows an Aadhaar holder to digitally sign a document. The process is simple and secure, leveraging the Aadhaar authentication framework.

Steps to use Aadhaar-based eSign:
1. **Initiate eSign Request**: Start the eSign process by pressing Continue.
2. **Aadhaar Authentication**: Enter your Aadhaar number. You will receive an OTP (One-Time Password) on your registered mobile number or email.
3. **Enter OTP**: Input the OTP received to authenticate your identity.
4. **Digital Signature**: Upon successful authentication, the document is signed digitally using your Aadhaar credentials.

Ensure your Aadhaar details are up-to-date and your mobile number is registered with UIDAI to use this service.
"""

UCC_UPLOAD_TEXT = """
UCC(Unique Client Code) Upload is a process to send the client information to NSE/BSE.
"""

UCC_DOWNLOAD_TEXT = """
Download and verify the payload to be sent for UCC
"""

ALL_OPERATIONS = [
    Operation(
        op_id="PDF",
        op_name="PDF",
        display_text="Generates the PDF(s) and gives the link to download the file(s).",
    ),
    Operation(op_id="KRA", op_name="CVL KRA", display_text=KRA_TEXT),
    Operation(
        op_id="KRA_UPLOAD_DATA",
        op_name="Download CVL KRA Payload",
        display_text="Download and verify the payload to be sent for CVL KRA",
    ),
    Operation(op_id="ESIGN", op_name="eSign", display_text=ESIGN),
    Operation(
        op_id="UPLOAD_UCC",
        op_name="UCC Upload",
        display_text=UCC_UPLOAD_TEXT,
    ),
    Operation(
        op_id="UCC_PAYLOAD",
        op_name="Download UCC Payload",
        display_text=UCC_DOWNLOAD_TEXT,
    ),
    Operation(
        op_id="NSDL_DEMAT_ACCOUNT",
        op_name="Create NSDL Demat Account",
        display_text="To create a demat account in the NSDL depository",
    ),
    Operation(
        op_id="NSDL_DEMAT_ACCOUNT_DOWNLOAD",
        op_name="Download NSDL Demat Payload",
        display_text="To download and review the payload data to be sent to NSDL depository for Demat Account creation.",
    ),
    Operation(
        op_id="UPLOAD_CDSL",
        op_name="Create CDSL Demat Account",
        display_text="To create a demat account in the CDSL depository",
    ),
    Operation(
        op_id="CDSL_DEMAT_ACCOUNT_DOWNLOAD",
        op_name="Download CDSL Demat Payload",
        display_text="To download and review the payload data to be sent to CDSL depository for Demat Account creation.",
    ),
]


class DepositoryName(str, Enum):
    NSDL = "nsdl"
    CDSL = "cdsl"


class OperationsListPlugin(OperationsListSpec):
    """
    Plugin for fetching the list of operations available based on user roles and form data.
    """

    def get_user_roles(self, token: str) -> List[str]:
        """
        Extracts user roles from the provided JWT token.

        Args:
            token (str): The JWT token containing user metadata.

        Returns:
            List[str]: A list of roles assigned to the user.

        Raises:
            PluginException: If roles cannot be extracted or token is invalid.
        """
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            roles = (
                decoded.get("user_metadata", {}).get("user_info", {}).get("roles", [])
            )
            if not roles:
                raise PluginException("No roles found in token") from e
            return roles
        except Exception as e:
            raise PluginException("Error decoding token") from e

    def get_digilocker_status(self, form_record: GenericFormRecordModel) -> bool:
        """
        Checks if KYC Digilocker is selected in the form record.

        Args:
            form_record (GenericFormRecordModel): The form data.

        Returns:
            bool: True if Digilocker is selected, False otherwise.
        """
        try:
            form_dict = form_record.model_dump()
            return (
                form_dict.get("application_details", {})
                .get("kyc_digilocker", "")
                .upper()
                == "YES"
            )
        except Exception as e:
            return False

    def get_exchange_depository(
        self, form_record: GenericFormRecordModel
    ) -> DepositoryName | None:
        """
        Checks which depository is selected in the form record.

        Args:
            form_record (GenericFormRecordModel): The form data.

        Returns:
            Enum: Return depository type based on form record.
        """
        try:
            form_dict = form_record.model_dump()
            depository_name = (
                form_dict.get("dp_information", {})
                .get("dp_Account_information", {})
                .get("depository", "")
            )
            if not depository_name:
                return None
            if depository_name == "NSDL":
                return DepositoryName.NSDL
            return DepositoryName.CDSL
        except Exception as e:
            return None

    @impl
    async def get_operations_list(
        self,
        context: ContextModel,
        form_record: Annotated[
            GenericFormRecordModel,
            Doc("The form record for which the operations list is required"),
        ],
    ) -> Annotated[
        OperationsListResponseModel,
        Doc("The list of operations available for the current form as per user role"),
    ]:
        """
        Determines the list of operations available for a user based on their role and form data.

        - Maker & Client: Only PDF operation is returned.
        - Checker & Admin: All operations are returned, but E-Sign is excluded if Digilocker is not selected.

        Args:
            context (ContextModel): Contains metadata such as authentication token.
            form_record (GenericFormRecordModel): The form record containing application details.

        Returns:
            OperationsListResponseModel: The list of permitted operations.
        """
        try:
            token = context.token
            if not token:
                raise ValueError("Token is not provided")

            # Retrieve user roles
            roles = self.get_user_roles(token=token)
            # Retrieve digilocker status
            digilocker_selected = self.get_digilocker_status(form_record=form_record)
            # Retrieve depository type
            depository_type: DepositoryName | None = self.get_exchange_depository(
                form_record=form_record
            )

            # Rule 1: Maker & Client get only PDF operation
            if "maker" in roles or "client" in roles:
                return OperationsListResponseModel(
                    operations=[op for op in ALL_OPERATIONS if op.op_id == "PDF"]
                )

            ops_list: List[Operation] = ALL_OPERATIONS.copy()

            # Rule 2: Exclude operations based on depository type
            exclusion_map = {
                DepositoryName.NSDL: {"CDSL_DEMAT_ACCOUNT_DOWNLOAD", "UPLOAD_CDSL"},
                DepositoryName.CDSL: {
                    "NSDL_DEMAT_ACCOUNT_DOWNLOAD",
                    "NSDL_DEMAT_ACCOUNT",
                },
            }
            if depository_type in exclusion_map:
                ops_list = [
                    op
                    for op in ops_list
                    if op.op_id not in exclusion_map[depository_type]
                ]
            else:
                ops_list = [
                    op
                    for op in ops_list
                    if op.op_id
                    not in {
                        "NSDL_DEMAT_ACCOUNT_DOWNLOAD",
                        "NSDL_DEMAT_ACCOUNT",
                        "CDSL_DEMAT_ACCOUNT_DOWNLOAD",
                        "UPLOAD_CDSL",
                    }
                ]

            # Rule 3: Checker & Admin get all operations, but exclude E-Sign if Digilocker is not selected
            if not digilocker_selected:
                ops_list = [op for op in ops_list if op.op_id != "ESIGN"]

            return OperationsListResponseModel(operations=ops_list)
        except Exception as e:
            logger.debug(f"No operations available: {str(e)}")
            raise PluginException(
                f"No operations available for the current form record"
            ) from e
