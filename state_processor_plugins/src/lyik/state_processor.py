import apluggy as pluggy
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from typing import Dict, Any, Tuple
from enum import Enum
from lyikpluginmanager import (
    getProjectName,
    StateProcessorSpec,
    ContextModel,
)
from datetime import datetime, timezone


class StateEnum(str, Enum):
    SAVE = "SAVE"
    SUBMIT = "SUBMIT"
    DISCREPANCY = "DISCREPANCY"
    APPROVED = "APPROVED"
    READY_FOR_DP = "READY_FOR_DP"
    DP_CREATED = "DP_CREATED"
    READY_FOR_TRADING = "READY_FOR_TRADING"
    ACCOUNTS_CREATED = "ACCOUNTS_CREATED"
    EXCHANGE_UPLOAD = "EXCHANGE_UPLOAD"
    KRA_UPLOADED = "KRA_UPLOADED"
    KRA_APPROVED = "KRA_APPROVED"
    KRA_REJECTED = "KRA_REJECTED"


class StateActionEnum(str, Enum):
    APPROVE = "approve"
    AUTO_ACTION = "auto_action"


class ApplicationTypeEnum(str, Enum):
    TRADING = "TRADING"
    DP = "DP"
    TRADING_AND_DP = "TRADING_AND_DP"


impl = pluggy.HookimplMarker(getProjectName())


class W2WStateProcessor(StateProcessorSpec):
    @impl
    async def process_and_return_state(
        self, context: ContextModel | None, record: Dict, state_action: str
    ) -> Tuple[str, dict]:
        """
        Process the current record with the state action, and return the new state
        """
        current_state: str = record.get("state", "")

        if isinstance(current_state, Enum):
            current_state = current_state.value

        application_type = get_application_type(record)
        if not application_type:
            return current_state, record

        if current_state == StateEnum.SUBMIT.value:
            if state_action == StateActionEnum.APPROVE.value:
                new_state = handle_submit_for_approve(record)
                _change_and_add_state(record=record, new_state=new_state)
                current_state = new_state

        # If APPROVED, READY_FOR_DP
        if current_state == StateEnum.APPROVED.value and application_type in {
            ApplicationTypeEnum.DP,
            ApplicationTypeEnum.TRADING_AND_DP,
        }:
            new_state = StateEnum.READY_FOR_DP.value
            _change_and_add_state(record=record, new_state=new_state)
            current_state = new_state

        # If READY_FOR_DP, handle dp creation, then DP_CREATED
        if current_state == StateEnum.READY_FOR_DP.value:
            new_state = handle_dp_account_creation(record=record)
            _change_and_add_state(record=record, new_state=new_state)
            current_state = new_state

        # If DP_CREATED, READY_FOR_TRADING
        if (
            current_state == StateEnum.DP_CREATED.value
            or current_state == StateEnum.APPROVED.value
        ) and application_type in {
            ApplicationTypeEnum.TRADING,
            ApplicationTypeEnum.TRADING_AND_DP,
        }:
            new_state = StateEnum.READY_FOR_TRADING.value
            _change_and_add_state(record=record, new_state=new_state)
            current_state = new_state

        # If READY_FOR_TRADING, handle trading creation, then ACCOUNTS_CREATED
        if current_state == StateEnum.READY_FOR_TRADING.value:
            new_state = handle_trading_account_creation(record)
            _change_and_add_state(record=record, new_state=new_state)
            current_state = new_state

        if current_state == StateEnum.DP_CREATED.value:
            new_state = StateEnum.ACCOUNTS_CREATED.value
            _change_and_add_state(record=record, new_state=new_state)
            current_state = new_state

        # If ACCOUNTS_CREATED, EXCHANGE_UPLOAD
        if current_state == StateEnum.ACCOUNTS_CREATED.value:
            new_state = StateEnum.EXCHANGE_UPLOAD.value
            _change_and_add_state(record=record, new_state=new_state)
            current_state = new_state

        if current_state == StateEnum.EXCHANGE_UPLOAD.value:
            new_state = StateEnum.KRA_APPROVED.value
            _change_and_add_state(record=record, new_state=new_state)
            current_state = new_state

        # If KRA_UPLOADED, KRA_APPROVED or KRA_REJECTED
        if current_state == StateEnum.KRA_UPLOADED.value:
            new_state = StateEnum.KRA_APPROVED.value
            _change_and_add_state(record=record, new_state=new_state)
            current_state = new_state

        return current_state, record

def get_application_type(record: dict) -> ApplicationTypeEnum | None:

    return ApplicationTypeEnum.TRADING_AND_DP
    application_type_str = (
        record.get("application_details", {})
        .get("general_application_details", {})
        .get("application_type")
    )

    if application_type_str and application_type_str in ApplicationTypeEnum.__members__:
        return ApplicationTypeEnum[application_type_str]
    return None


def _change_and_add_state(record: Dict[str, Any], new_state: str) -> None:
    current_state = record.get("state")
    record["state"] = new_state

    if "_audit_log" not in record:
        record["_audit_log"] = {}

    if not isinstance(record["_audit_log"], dict):
        raise ValueError("_audit_log must be a dictionary")
    record["_audit_log"][current_state] = datetime.now(tz=timezone.utc).isoformat()


def handle_submit_for_approve(record: dict) -> str:
    """
    Processes record from submit state for approve.
    """

    def traverse_and_check(record: dict) -> str:
        """
        Recursively traverse the record to check `_check_status` for rejected. If not found, returns 'approved'. Else 'discrepancy'
        """
        for key, value in record.items():
            # If the key ends with '_check_status' and value is a dictionary
            if key.endswith("_check_status") and isinstance(value, dict):
                state = value.get("state")
                if state == "rejected":
                    return StateEnum.DISCREPANCY
                elif state != "approved":
                    # Any state other than 'approved' or 'rejected'.
                    return StateEnum.DISCREPANCY
            # If the value is a nested dictionary, recurse
            elif isinstance(value, dict):
                result = traverse_and_check(value)
                if result == StateEnum.DISCREPANCY:
                    return result
            # If the value is a list, iterate through it
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        result = traverse_and_check(item)
                        if result == StateEnum.DISCREPANCY:
                            return result
        return StateEnum.APPROVED

    # Start traversal and return the final state
    new_state: Enum = traverse_and_check(record)
    return new_state.value


def handle_dp_account_creation(record: dict) -> str:
    # Add logic to create dp. When successful, return the approprate state.
    return StateEnum.DP_CREATED.value

def handle_trading_account_creation(record: dict) -> str:
    # Add logic to create trading account, When successful, return the approprate state.
    return StateEnum.ACCOUNTS_CREATED.value
