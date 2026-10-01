from datetime import datetime
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from database import (
    get_incident_by_id,
    get_incidents,
    get_investigation_by_incident_id,
)
from service import investigate_and_store_incident

app = FastAPI()


class IncidentRequest(BaseModel):
    service: str
    timestamp: str
    description: str
    logs: list[str]
    deployment: dict


class HypothesisResponse(BaseModel):
    cause: str
    evidence: list[str]
    confidence: Literal["low", "medium", "high"]


class InvestigationResponse(BaseModel):
    incident_id: int
    investigation_id: int
    incident_type: str
    summary: str
    hypotheses: list[HypothesisResponse]
    missing_information: list[str]


class IncidentResponse(BaseModel):
    id: int
    service: str
    timestamp: datetime
    description: str
    created_at: datetime


class StoredInvestigationResponse(BaseModel):
    id: int
    incident_id: int
    incident_type: str
    summary: str
    hypotheses: list[HypothesisResponse]
    missing_information: list[str]
    created_at: datetime


@app.get("/")
def root():
    return {"message": "Incident Investigator API is running"}


@app.post("/incidents/investigate", response_model=InvestigationResponse)
def investigate_incident_endpoint(incident_data: IncidentRequest):
    try:
        incident = incident_data.model_dump()
        return investigate_and_store_incident(incident)
    except Exception as e:
        print("ERROR:", e)
        raise


@app.get("/incidents", response_model=list[IncidentResponse])
def get_incidents_endpoint():
    try:
        return get_incidents()

    except Exception:
        raise HTTPException(status_code=502, detail="Failed to retrieve incidents.")


@app.get("/incidents/{incident_id}", response_model=IncidentResponse)
def get_incident_endpoint(incident_id: int):
    incident = get_incident_by_id(incident_id)

    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found.")

    return incident


@app.get(
    "/incidents/{incident_id}/investigation", response_model=StoredInvestigationResponse
)
def get_investigation_endpoint(incident_id: int):
    investigation = get_investigation_by_incident_id(incident_id)

    if investigation is None:
        raise HTTPException(status_code=404, detail="Investigation not found.")

    return investigation
