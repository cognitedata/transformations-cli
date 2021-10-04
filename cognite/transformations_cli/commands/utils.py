from typing import Optional
import sys

def check_exclusive_id(id: Optional[int], externalId: Optional[str]) -> bool:
    if id and externalId:
        sys.exit("Please only provide one of id and external id.")

def exit_with_id_not_found(e: Exception) -> None:
    sys.exit(f"Id not found: {e}")

def exit_with_cognite_api_error(e: Exception) -> None:
    sys.exit(f"Cognite API error has occurred: {e}")
