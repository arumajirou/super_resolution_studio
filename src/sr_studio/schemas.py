from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ModelStatus(StrEnum):
    VERIFIED_BASELINE = "VERIFIED_BASELINE"
    READY_TO_INSTALL = "READY_TO_INSTALL"
    EXPERIMENTAL = "EXPERIMENTAL"
    EXPERIMENTAL_HEAVY = "EXPERIMENTAL_HEAVY"
    BLOCKED_CHECKPOINT = "BLOCKED_CHECKPOINT"


class ResultStatus(StrEnum):
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    BLOCKED = "BLOCKED"
    REJECTED = "REJECTED"


class RuntimeKind(StrEnum):
    NATIVE = "native"
    EXTERNAL = "external"


class ModelSpec(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    display_name: str
    family: str
    status: ModelStatus
    source_repo: str | None = None
    hf_repo: str | None = None
    license: str | None = None
    runtime_kind: RuntimeKind
    supported_scales: tuple[int, ...] = (4,)
    default_scale: int = 4
    supports_tile: bool = False
    hardware_notes: str = ""
    command_profile: str | None = None
    notes: str = ""

    @model_validator(mode="after")
    def validate_scale(self) -> ModelSpec:
        if not self.supported_scales:
            raise ValueError("supported_scales must not be empty")
        if self.default_scale not in self.supported_scales:
            raise ValueError("default_scale must be present in supported_scales")
        if self.runtime_kind is RuntimeKind.EXTERNAL and not self.command_profile:
            raise ValueError("external model requires command_profile")
        return self


class RuntimeConfig(BaseModel):
    model_id: str
    workdir: Path
    python_executable: Path
    paths: dict[str, str] = Field(default_factory=dict)
    timeout_seconds: int = Field(default=3600, ge=1, le=86400)


class UpscaleRequest(BaseModel):
    model_id: str
    inputs: list[Path]
    output_dir: Path
    scale: int = Field(default=4, ge=1, le=16)
    tile_size: int | None = Field(default=None, ge=32, le=4096)
    precision: str = "fp16"
    device: str = "cuda"
    seed: int = 42
    extra_options: dict[str, Any] = Field(default_factory=dict)


class ProviderHealth(BaseModel):
    model_id: str
    ready: bool
    status: str
    details: list[str] = Field(default_factory=list)


class ProviderResult(BaseModel):
    output_path: Path | None = None
    exit_code: int | None = None
    stdout: str = ""
    stderr: str = ""
    argv: list[str] | None = None


class FileResult(BaseModel):
    input_path: Path
    output_path: Path | None = None
    status: ResultStatus
    input_sha256: str | None = None
    output_sha256: str | None = None
    elapsed_seconds: float = 0.0
    exit_code: int | None = None
    error: str | None = None
    stdout_log: Path | None = None
    stderr_log: Path | None = None


class RunManifest(BaseModel):
    run_id: str
    started_at: datetime
    finished_at: datetime | None = None
    request: UpscaleRequest
    model: ModelSpec
    provider_argv: list[str] | None = None
    environment: dict[str, str | None] = Field(default_factory=dict)
    results: list[FileResult] = Field(default_factory=list)
    status: str = "RUNNING"
