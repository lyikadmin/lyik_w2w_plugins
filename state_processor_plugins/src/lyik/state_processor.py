import logging
import os
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, List
import apluggy as pluggy
import jwt
import requests
from lyikpluginmanager import ContextModel, getProjectName, StateProcessorSpec, invoke

from lyikpluginmanager.models import (
    OperationResponseModel,
    OperationStatus,
    UCCResponseModel,
    UCCResponseStatus,
    GenericFormRecordModel,
)
from typing_extensions import Annotated, Doc
from lyikpluginmanager.annotation import RequiredEnv
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# States
STATE_SAVE = "SAVE"
STATE_SUBMIT = "SUBMIT"
STATE_DISCREPANCY = "DISCREPANCY"
STATE_APPROVED = "APPROVED"
STATE_ESIGNED = "ESIGNED"
STATE_SIGNATURE_VERIFIED = "SIGNATURE_VERIFIED"
STATE_SIGNATURE_VERIFIED_AND_APPROVED = "SIGNATURE_VERIFIED_AND_APPROVED"
STATE_ACCOUNT_CREATION_FAILURE = "ACCOUNT_CREATION_FAILURE"
STATE_READY_FOR_DP = "READY_FOR_DP"
STATE_DP_CREATED = "DP_CREATED"
STATE_READY_FOR_TRADING = "READY_FOR_TRADING"
STATE_ACCOUNTS_CREATED = "ACCOUNTS_CREATED"
STATE_EXCHANGE_UPLOAD = "EXCHANGE_UPLOAD"
STATE_KRA_UPLOADED = "KRA_UPLOADED"
STATE_KRA_APPROVED = "KRA_APPROVED"
STATE_KRA_REJECTED = "KRA_REJECTED"
STATE_COMPLETED = "COMPLETED"

# State Actions
STATE_ACTION_APPROVE = "approve"
STATE_ACTION_REJECT = "reject"
STATE_ACTION_DEFAULT = "default"
STATE_ACTION_ESIGNED = "esigned"

# Application type
APPLICATION_TYPE_TRADING = "TRADING"
APPLICATION_TYPE_DP = "DP"
APPLICATION_TYPE_TRADING_AND_DP = "TRADING_AND_DP"

# PAN_status
PAN_STATUS_COMPLETE = "COMPLETE"
PAN_STATUS_PENDING = "PENDING"
PAN_STATUS_FAILURE = "FAILURE"

impl = pluggy.HookimplMarker(getProjectName())


class W2WStateProcessor(StateProcessorSpec):
    @impl
    async def process_and_return_state(
        self,
        context: ContextModel | None,
        record: Annotated[
            GenericFormRecordModel, Doc("The entire form record to be state processed")
        ],
        state_action: Annotated[str, Doc("The action to set decide the state flow.")],
    ) -> Annotated[
        Tuple[str, dict],
        RequiredEnv(["TECH_XL_ENDPOINT"]),
        Doc("The new state, and the modified form record (with audit logs)"),
    ]:
        """
        Process the current record with the state action, and return the new state
        """
        encoded_token = context.token
        personas = _get_personas_from_encoded_token(encoded_token)
        if isinstance(record, GenericFormRecordModel):
            record = record.model_dump()
        current_state: str = record.get("state", "")

        # If the submitter is not a checker, then we dont need to perform any state flow.
        if (
            current_state == STATE_SUBMIT
            and personas
            and "CKR" not in personas
            and state_action not in {STATE_ACTION_DEFAULT, STATE_ACTION_ESIGNED}
        ):
            return current_state, record

        if state_action == STATE_ACTION_APPROVE:
            new_state = STATE_APPROVED
            current_state = _change_and_add_state(record=record, new_state=new_state)

            return current_state, record

        if state_action == STATE_ACTION_REJECT:
            new_state = STATE_DISCREPANCY
            current_state = _change_and_add_state(record=record, new_state=new_state)

            return current_state, record

        if state_action == STATE_ACTION_ESIGNED:
            new_state = STATE_ESIGNED
            current_state = _change_and_add_state(record=record, new_state=new_state)

        if current_state == STATE_ESIGNED:
            new_state = STATE_SIGNATURE_VERIFIED
            current_state = _change_and_add_state(record=record, new_state=new_state)

        if current_state == STATE_SIGNATURE_VERIFIED:
            new_state = STATE_SIGNATURE_VERIFIED_AND_APPROVED
            current_state = _change_and_add_state(record=record, new_state=new_state)

        application_type = get_application_type(record)
        if not application_type:
            return current_state, record

        # If APPROVED, READY_FOR_DP
        if (
            current_state == STATE_SIGNATURE_VERIFIED_AND_APPROVED
            and application_type
            in {
                APPLICATION_TYPE_DP,
                APPLICATION_TYPE_TRADING_AND_DP,
            }
        ):
            new_state = STATE_READY_FOR_DP
            current_state = _change_and_add_state(record=record, new_state=new_state)

        # If READY_FOR_DP, handle dp creation, then DP_CREATED
        if current_state == STATE_READY_FOR_DP:
            new_state = await handle_dp_account_creation(record=record)
            current_state = _change_and_add_state(record=record, new_state=new_state)

        # If DP_CREATED, READY_FOR_TRADING
        if (
            current_state == STATE_DP_CREATED
            or current_state == STATE_SIGNATURE_VERIFIED_AND_APPROVED
        ) and application_type in {
            APPLICATION_TYPE_TRADING,
            APPLICATION_TYPE_TRADING_AND_DP,
        }:
            new_state = STATE_READY_FOR_TRADING
            current_state = _change_and_add_state(record=record, new_state=new_state)

        # If READY_FOR_TRADING, handle trading creation, then ACCOUNTS_CREATED
        if current_state == STATE_READY_FOR_TRADING:
            new_state = await handle_trading_account_creation(record)
            current_state = _change_and_add_state(record=record, new_state=new_state)

        if current_state == STATE_DP_CREATED:
            new_state = STATE_ACCOUNTS_CREATED
            current_state = _change_and_add_state(record=record, new_state=new_state)

        if current_state == STATE_ACCOUNT_CREATION_FAILURE:
            new_state = STATE_DISCREPANCY
            current_state = _change_and_add_state(record=record, new_state=new_state)

            return current_state, record

        # If ACCOUNTS_CREATED, EXCHANGE_UPLOAD
        if current_state == STATE_ACCOUNTS_CREATED:
            new_state = await handle_ucc(record=record, context=context)
            current_state = _change_and_add_state(record=record, new_state=new_state)

        if current_state == STATE_EXCHANGE_UPLOAD:
            new_state = await handle_kra_upload(record, context=context)
            current_state = _change_and_add_state(record=record, new_state=new_state)

        # If KRA_UPLOADED, KRA_APPROVED or KRA_REJECTED
        if current_state == STATE_KRA_UPLOADED:
            new_state = await handle_kra_upload_status(record, context=context)
            current_state = _change_and_add_state(record=record, new_state=new_state)

        if current_state == STATE_KRA_APPROVED:
            new_state = STATE_COMPLETED
            current_state = _change_and_add_state(record=record, new_state=new_state)

        return current_state, record


def get_application_type(record: dict) -> str | None:
    # return APPLICATION_TYPE_TRADING_AND_DP
    application_type_str = (
        record.get("application_details", {})
        .get("general_application_details", {})
        .get("application_type")
    )

    if application_type_str and application_type_str in {
        APPLICATION_TYPE_TRADING,
        APPLICATION_TYPE_DP,
        APPLICATION_TYPE_TRADING_AND_DP,
    }:
        return application_type_str
    return None


def _change_and_add_state(record: Dict[str, Any], new_state: str) -> None:
    current_state = record.get("state")

    # Incase the new state is the same, nothing is added to audit logs.
    if current_state == new_state:
        return current_state

    record["state"] = new_state

    if "_audit_log" not in record:
        record["_audit_log"] = {}

    if not isinstance(record["_audit_log"], dict):
        raise ValueError("_audit_log must be a dictionary")
    record["_audit_log"][current_state] = datetime.now(tz=timezone.utc).isoformat()
    current_state = new_state
    return current_state


async def handle_dp_account_creation(record: dict) -> str:
    # Logic to create dp. When successful, return the approprate state.
    # Return ACCOUNT_CREATION_FAILURE if it fails
    return STATE_DP_CREATED


async def handle_trading_account_creation(record: dict) -> str:
    # Logic to create trading account, When successful, return the approprate state.
    try:
        await TechXLPlugin.create_demat(record)
        return STATE_ACCOUNTS_CREATED
    except Exception as e:
        return STATE_READY_FOR_TRADING


async def handle_ucc(record: dict, context: ContextModel) -> str:
    try:
        # Logic for creation of UCC
        generic_model_record = GenericFormRecordModel.model_validate(record)
        response: UCCResponseModel = await invoke.upload_ucc(
            config=context.config,
            form_record=generic_model_record,
        )
        if response.status == UCCResponseStatus.SUCCESS:
            return STATE_EXCHANGE_UPLOAD
        else:
            return STATE_DISCREPANCY
    except Exception as e:
        return STATE_EXCHANGE_UPLOAD


async def handle_kra_upload(record: dict, context: ContextModel) -> str:
    # Logic for KRA upload
    try:
        KRA_PLUGIN_NAME = "KRA"

        record_id = record.get("_id")
        generic_model_record = GenericFormRecordModel.model_validate(record)
        response: OperationResponseModel = await invoke.process_operation(
            config=context.config,
            operation_plugin=KRA_PLUGIN_NAME,
            form_id=context.form_id,
            org_id=context.org_id,
            form_name=context.form_name,
            record_id=record_id,
            status=STATE_EXCHANGE_UPLOAD,
            form_record=generic_model_record,
        )
        if response.status == OperationStatus.SUCCESS:
            return STATE_KRA_UPLOADED
        else:
            return STATE_DISCREPANCY
    except Exception as e:
        return STATE_KRA_APPROVED


async def handle_kra_upload_status(record: dict, context: ContextModel) -> str:
    # Logic to check for the KRA upload status.
    record_pan_status = await _get_pan_status_of_entire_record(
        record=record, context=context
    )
    if record_pan_status == PAN_STATUS_COMPLETE:
        return STATE_KRA_APPROVED
    if record_pan_status == PAN_STATUS_PENDING:
        return STATE_EXCHANGE_UPLOAD
    if record_pan_status == PAN_STATUS_FAILURE:
        return STATE_DISCREPANCY


def _get_personas_from_encoded_token(token: str) -> List[str] | None:
    try:
        # Decode the JWT token
        decoded_token = jwt.decode(token, options={"verify_signature": False})

        # Extract the personas from user_metadata
        personas = (
            decoded_token.get("user_metadata", {})
            .get("permissions", {})
            .get("persona", [])
        )

        return personas
    except Exception as e:
        return None


async def _get_pan_status_of_entire_record(record: dict, context: ContextModel) -> str:
    pan_number_list = _get_pan_numbers(record=record)
    if not pan_number_list:
        return PAN_STATUS_FAILURE
    for pan in pan_number_list:
        pan_status = await invoke.get_pan_status(config=context.config, pan=pan)
        if pan_status == "FAILED":
            return PAN_STATUS_FAILURE
        if pan_status == "PENDING":
            return PAN_STATUS_PENDING
    return PAN_STATUS_COMPLETE


def _get_pan_numbers(record: dict) -> List[str]:
    pan_list = []
    kyc_holders = record.get("kyc_holders", [])
    for kyc_holder in kyc_holders:
        pan = kyc_holder["kyc_holder"]["pan_verification"]["pan_details"]["pan_number"]
        pan_list.append(pan)
    return pan_list


# todo : move to a more appropriate location


class TechXLPlugin:
    @staticmethod
    async def create_demat(
        form_record: dict,
    ) -> Annotated[str, Doc("response text")]:
        # todo: 1. parse form record to create TechXL payload
        payload = {}
        files = {}
        try:
            endpoint = os.getenv("TECH_XL_ENDPOINT")
            if not endpoint:
                raise ValueError("TechXL endpoint not set")
            response = requests.post(endpoint, data=payload, files=files)
            print(response.status_code)
            print(response.text)
            return response.text

        except Exception as e:
            logger.error(f"Error tech xl submission : {str(e)}")
            raise
