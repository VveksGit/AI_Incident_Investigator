from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from investigator import investigate_incident

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
    incident_type: str
    summary: str
    hypotheses: list[HypothesisResponse]
    missing_information: list[str]


@app.get("/")
def root():
    return {"message": "Incident Investigator API is running"}


@app.post("/incidents/investigate", response_model=InvestigationResponse)
def investigate_incident_endpoint(incident_data: IncidentRequest):
    try:
        incident = incident_data.model_dump()
        result = investigate_incident(incident)
        return result
    except Exception:
        raise HTTPException(
            status_code=502, detail="Incident investigation service failed."
        )
