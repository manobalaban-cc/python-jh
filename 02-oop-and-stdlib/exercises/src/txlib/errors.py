"""Exception hierarchy — TODO.

TxError                base class for everything txlib raises
├── SourceError        the input could not be read / is not a transaction file
└── ValidationError    one field of one row is wrong
                       attributes: field, reason, row_number
                       str(e) should identify the row and the field
"""
