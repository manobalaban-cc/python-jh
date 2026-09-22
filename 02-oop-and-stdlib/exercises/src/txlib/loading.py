"""The use case — TODO.

    @dataclass(slots=True)
    class ImportResult:
        imported: int = 0
        skipped: int = 0
        errors: list[ValidationError] = field(default_factory=list)

    def load_file(path: Path, repository: Repository) -> ImportResult

Rules:
  - open with encoding="utf-8" and newline=""
  - a missing file or an unreadable one raises SourceError, chained
  - a header without the required columns raises SourceError
  - a bad row is counted and recorded, never fatal
  - process the file row by row (streaming), not by reading it all into memory
"""
