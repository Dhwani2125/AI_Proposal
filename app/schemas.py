from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

class DraftRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    notes: str = Field(min_length=10, max_length=15000)
    package_id: str = Field(max_length=80)
    template_id: str = Field(default="neutral", max_length=80)
    client_name: str = Field(default="", max_length=150)
    target_timeline: str = Field(default="", max_length=200)
    approver: str = Field(default="", max_length=150)

    @field_validator("notes", "client_name", "target_timeline", "approver")
    @classmethod
    def safe_text(cls, value):
        if any(ord(c) < 32 and c not in "\n\r\t" for c in value):
            raise ValueError("Unsupported control character")
        return value

class Proposal(BaseModel):
    schema_version: Literal["1.0"] = "1.0"
    draft_status: Literal["draft"] = "draft"
    title: str
    client_name: str | None
    template_id: str
    template_version: str
    template_approved: bool
    fixed_wording: str
    section_order: list[str]
    sections: dict[str, list[str]]
    classified_notes: list[dict[str, str]]
    source_references: list[dict[str, str]]
    model: str = "TF-IDF + LogisticRegression (illustrative training data)"

class ExportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    request: DraftRequest
    reviewer_notes: str = Field(default="", max_length=10000)
    edits: dict[Literal["project_summary", "objectives"], str] = Field(default_factory=dict)

    @field_validator("edits")
    @classmethod
    def validate_edits(cls, values):
        for value in values.values():
            if not value.strip() or len(value) > 5000:
                raise ValueError("Edits must contain 1 to 5000 characters")
            DraftRequest.safe_text(value)
        return values

    _safe = field_validator("reviewer_notes")(DraftRequest.safe_text.__func__)
