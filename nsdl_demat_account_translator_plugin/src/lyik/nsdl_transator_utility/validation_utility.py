from pydantic import ValidationError

from pydantic import ValidationError

def get_readable_validation_error(e: ValidationError) -> str:
    """
    Parse a Pydantic ValidationError and return a human-readable message.

    Args:
        e (ValidationError): The validation error to process.

    Returns:
        str: A summarised and readable error message.
    """
    missing_fields = []
    data_errors = []

    for error in e.errors():
        error_attribute_list = list(map(str, error.get("loc", [])))
        error_attribute_list = [a.capitalize().replace("_", " ") for a  in error_attribute_list]
        attribute = " -> ".join(error_attribute_list)
        error_message = error.get("msg", "Invalid input")

        if "field required" in error_message:
            missing_fields.append(attribute)
        else:
            data_errors.append(f"'{attribute}': {error_message}")

    missing_part = "Missing fields:\n" + {'\n'.join(missing_fields)} if missing_fields else ""
    data_errors_part = "\n".join(data_errors) if data_errors else ""

    return "\n".join(filter(None, [missing_part, data_errors_part]))

