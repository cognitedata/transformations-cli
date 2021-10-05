import sys
from typing import Optional


def is_id_exclusive(id: Optional[int], externalId: Optional[str], should_exit: bool = True) -> bool:
    if id and externalId:
        if should_exit:
            sys.exit("Please only provide one of id and external id.")
        return False
    return True


def exit_with_id_not_found(e: Exception) -> None:
    sys.exit(f"Id not found: {e}")
    return None  # To suppress mypy error


def exit_with_cognite_api_error(e: Exception) -> None:
    sys.exit(f"Cognite API error has occurred: {e}")
    return None  # To suppress mypy error
