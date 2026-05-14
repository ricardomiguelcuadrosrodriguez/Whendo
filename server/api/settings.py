"""REST endpoints for the settings store."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from server import settings_service

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class SettingItem(BaseModel):
    key: str
    label: str
    category: str
    is_secret: bool
    default: str | None
    description: str | None
    placeholder: str | None
    is_set: bool
    value: str | None  # masked for secrets


class SettingsListResponse(BaseModel):
    items: list[SettingItem]
    status: "StatusResponse"


class SettingUpsert(BaseModel):
    value: str = Field(..., description="Setting value. Pass empty string to keep current.")


class StatusResponse(BaseModel):
    has_master_password: bool
    is_unlocked: bool
    secret_count: int
    encrypted_count: int


class PasswordPayload(BaseModel):
    password: str = Field(..., min_length=1)


class ChangePasswordPayload(BaseModel):
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=1)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("", response_model=SettingsListResponse)
def list_settings() -> SettingsListResponse:
    return SettingsListResponse(
        items=[SettingItem(**item) for item in settings_service.list_visible()],
        status=StatusResponse(**settings_service.get_status()),
    )


@router.get("/_status", response_model=StatusResponse)
def get_status() -> StatusResponse:
    return StatusResponse(**settings_service.get_status())


@router.put("/{key}")
def upsert_setting(key: str, payload: SettingUpsert) -> dict:
    if settings_service.get_def(key) is None:
        raise HTTPException(status_code=404, detail=f"Unknown setting key '{key}'")
    try:
        settings_service.set(key, payload.value)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "ok", "key": key}


@router.delete("/{key}")
def delete_setting(key: str) -> dict:
    if settings_service.get_def(key) is None:
        raise HTTPException(status_code=404, detail=f"Unknown setting key '{key}'")
    settings_service.delete(key)
    return {"status": "ok", "key": key}


@router.post("/_set-master")
def set_master(payload: PasswordPayload) -> dict:
    try:
        settings_service.init_master_password(payload.password)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "ok"}


@router.post("/_unlock")
def unlock(payload: PasswordPayload) -> dict:
    try:
        settings_service.unlock(payload.password)
    except RuntimeError as e:
        raise HTTPException(status_code=401, detail=str(e))
    return {"status": "ok"}


@router.post("/_lock")
def lock() -> dict:
    settings_service.lock()
    return {"status": "ok"}


@router.post("/_change-master")
def change_master(payload: ChangePasswordPayload) -> dict:
    try:
        settings_service.change_master_password(payload.old_password, payload.new_password)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "ok"}


SettingsListResponse.model_rebuild()
