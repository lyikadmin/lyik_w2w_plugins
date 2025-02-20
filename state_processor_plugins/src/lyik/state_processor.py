import apluggy as pluggy
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from typing import Dict, Any, Tuple, List, Annotated
from typing_extensions import Doc
from lyikpluginmanager import (
    getProjectName,
    StateProcessorSpec,
    ContextModel,
)
from lyikpluginmanager.models import GenericFormRecordModel
import jwt
from datetime import datetime, timezone

# States
STATE_SAVE = "SAVE"
STATE_SUBMIT = "SUBMIT"
STATE_DISCREPANCY = "DISCREPANCY"
STATE_APPROVED = "APPROVED"
STATE_ACCOUNT_CREATION_FAILURE = "ACCOUNT_CREATION_FAILURE"
STATE_READY_FOR_DP = "READY_FOR_DP"
STATE_DP_CREATED = "DP_CREATED"
STATE_READY_FOR_TRADING = "READY_FOR_TRADING"
STATE_ACCOUNTS_CREATED = "ACCOUNTS_CREATED"
STATE_EXCHANGE_UPLOAD = "EXCHANGE_UPLOAD"
STATE_KRA_UPLOADED = "KRA_UPLOADED"
STATE_KRA_APPROVED = "KRA_APPROVED"
STATE_KRA_REJECTED = "KRA_REJECTED"

# State Actions
STATE_ACTION_APPROVE = "approve"
STATE_ACTION_REJECT = "reject"
STATE_ACTION_DEFAULT = "default"

# Application type
APPLICATION_TYPE_TRADING = "TRADING"
APPLICATION_TYPE_DP = "DP"
APPLICATION_TYPE_TRADING_AND_DP = "TRADING_AND_DP"

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
            and state_action != STATE_ACTION_DEFAULT
        ):
            return current_state, record

        if state_action == STATE_ACTION_APPROVE:
            new_state = STATE_APPROVED
            current_state = _change_and_add_state(record=record, new_state=new_state)

        if state_action == STATE_ACTION_REJECT:
            new_state = STATE_DISCREPANCY
            current_state = _change_and_add_state(record=record, new_state=new_state)

            return current_state, record

        application_type = get_application_type(record)
        if not application_type:
            return current_state, record

        # If APPROVED, READY_FOR_DP
        if current_state == STATE_APPROVED and application_type in {
            APPLICATION_TYPE_DP,
            APPLICATION_TYPE_TRADING_AND_DP,
        }:
            new_state = STATE_READY_FOR_DP
            current_state = _change_and_add_state(record=record, new_state=new_state)

        # If READY_FOR_DP, handle dp creation, then DP_CREATED
        if current_state == STATE_READY_FOR_DP:
            new_state = handle_dp_account_creation(record=record)
            current_state = _change_and_add_state(record=record, new_state=new_state)

        # If DP_CREATED, READY_FOR_TRADING
        if (
            current_state == STATE_DP_CREATED or current_state == STATE_APPROVED
        ) and application_type in {
            APPLICATION_TYPE_TRADING,
            APPLICATION_TYPE_TRADING_AND_DP,
        }:
            new_state = STATE_READY_FOR_TRADING
            current_state = _change_and_add_state(record=record, new_state=new_state)

        # If READY_FOR_TRADING, handle trading creation, then ACCOUNTS_CREATED
        if current_state == STATE_READY_FOR_TRADING:
            new_state = handle_trading_account_creation(record)
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
            new_state = STATE_EXCHANGE_UPLOAD
            current_state = _change_and_add_state(record=record, new_state=new_state)

        if current_state == STATE_EXCHANGE_UPLOAD:
            new_state = STATE_KRA_APPROVED
            current_state = _change_and_add_state(record=record, new_state=new_state)

        # If KRA_UPLOADED, KRA_APPROVED or KRA_REJECTED
        if current_state == STATE_KRA_UPLOADED:
            new_state = STATE_KRA_APPROVED
            current_state = _change_and_add_state(record=record, new_state=new_state)

        return current_state, record


def get_application_type(record: dict) -> str | None:
    return APPLICATION_TYPE_TRADING_AND_DP
    # application_type_str = (
    #     record.get("application_details", {})
    #     .get("general_application_details", {})
    #     .get("application_type")
    # )

    # if application_type_str and application_type_str in {
    #     APPLICATION_TYPE_TRADING,
    #     APPLICATION_TYPE_DP,
    #     APPLICATION_TYPE_TRADING_AND_DP,
    # }:
    #     return application_type_str
    # return None


def _change_and_add_state(record: Dict[str, Any], new_state: str) -> None:
    current_state = record.get("state")
    record["state"] = new_state

    if "_audit_log" not in record:
        record["_audit_log"] = {}

    if not isinstance(record["_audit_log"], dict):
        raise ValueError("_audit_log must be a dictionary")
    record["_audit_log"][current_state] = datetime.now(tz=timezone.utc).isoformat()
    current_state = new_state
    return current_state


def handle_dp_account_creation(record: dict) -> str:
    # Add logic to create dp. When successful, return the approprate state.
    # Return ACCOUNT_CREATION_FAILURE if it fails
    return STATE_DP_CREATED


def handle_trading_account_creation(record: dict) -> str:
    # Add logic to create trading account, When successful, return the approprate state.
    return STATE_ACCOUNTS_CREATED


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
