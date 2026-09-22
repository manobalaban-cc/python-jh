"""Row -> domain object — TODO.

    REQUIRED_COLUMNS = ("Timestamp", "Amount", "Currency", "Recipient")

    def parse_row(row: Mapping[str, str], row_number: int) -> Transaction

Rules:
  - every field is required and is stripped before use
  - an unparseable timestamp / amount raises ValidationError chained from the
    original exception (``raise ... from exc``)
  - an unknown currency raises ValidationError listing the accepted values
"""
