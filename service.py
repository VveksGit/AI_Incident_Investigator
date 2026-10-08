import logging

from database import get_connection, save_incident, save_investigation
from investigator import investigate_incident

# Important note from transaction part whoever owns the connection manages commit and rollback. WHOEVER OWNS IT IN THIS CASE IT'S SERVICE.PY'S FUNCTION.
logger = logging.getLogger(__name__)


def investigate_and_store_incident(incident):
    connection = get_connection()

    try:
        incident_id = save_incident(incident, connection)
        logger.info("Incident saved with ID %s", incident_id)

        investigation = investigate_incident(incident)

        investigation_id = save_investigation(investigation, incident_id, connection)
        logger.info(
            "Investigation saved with ID %s for incident %s",
            investigation_id,
            incident_id,
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    return {
        "incident_id": incident_id,
        "investigation_id": investigation_id,
        **investigation,  # type: ignore
    }
