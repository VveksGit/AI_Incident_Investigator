import logging
import os
import time

import psycopg
from dotenv import load_dotenv
from psycopg.types.json import Jsonb

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_connection():
    for attempt in range(3):
        try:
            return psycopg.connect(
                dbname=os.getenv("POSTGRES_DB"),
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD"),
                host=os.getenv("POSTGRES_HOST"),
                port=int(os.getenv("POSTGRES_PORT")),
                connect_timeout=int(os.getenv("DB_CONNECT_TIMEOUT")),
            )

        except psycopg.OperationalError as e:
            logger.error(
                "DB CONNECTION ERROR (attempt %s/3): %s",
                attempt + 1,
                e,
            )

            if attempt == 2:
                raise

            time.sleep(2)

    raise RuntimeError("Failed to establish database connection")


def save_incident(incident, connection=None):
    own_connection = connection is None

    if own_connection:
        connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO incidents (
                service,
                timestamp,
                description,
                logs,
                deployment
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
            """,
            (
                incident["service"],
                incident["timestamp"],
                incident["description"],
                Jsonb(incident["logs"]),
                Jsonb(incident["deployment"]),
            ),
        )

        row = cursor.fetchone()
        if row is None:
            raise RuntimeError("Failed to retrieve inserted incident ID")

        incident_id = row[0]

        cursor.close()

        if own_connection:
            connection.commit()

        return incident_id

    except Exception:
        if own_connection:
            connection.rollback()
        raise

    finally:
        if own_connection:
            connection.close()


def save_investigation(investigation, incident_id, connection=None):

    own_connection = connection is None

    if own_connection:
        connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO investigations (
                incident_id,
                incident_type,
                summary,
                hypotheses,
                missing_information
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
            """,
            (
                incident_id,
                investigation["incident_type"],
                investigation["summary"],
                Jsonb(investigation["hypotheses"]),
                Jsonb(investigation["missing_information"]),
            ),
        )

        row = cursor.fetchone()
        if row is None:
            raise RuntimeError("Failed to retrieve inserted investigation ID")

        investigation_id = row[0]

        cursor.close()

        if own_connection:
            connection.commit()

        return investigation_id
    except Exception:
        if own_connection:
            connection.rollback()
        raise
    finally:
        if own_connection:
            connection.close()


def get_incidents():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, service, timestamp, description, created_at
                FROM incidents
                ORDER BY id;
            """)

            rows = cursor.fetchall()

        incidents = []

        for row in rows:
            incidents.append(
                {
                    "id": row[0],
                    "service": row[1],
                    "timestamp": row[2],
                    "description": row[3],
                    "created_at": row[4],
                }
            )

        return incidents

    finally:
        connection.close()


def get_incident_by_id(incident_id):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, service, timestamp, description, logs, deployment, created_at
                FROM incidents
                WHERE id = %s;
                """,
                (incident_id,),
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return {
            "id": row[0],
            "service": row[1],
            "timestamp": row[2],
            "description": row[3],
            "logs": row[4],
            "deployment": row[5],
            "created_at": row[6],
        }

    finally:
        connection.close()


def get_investigation_by_incident_id(incident_id):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, incident_id, incident_type, summary,
                       hypotheses, missing_information, created_at
                FROM investigations
                WHERE incident_id = %s
                ORDER BY id DESC
                LIMIT 1;
                """,
                (incident_id,),
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return {
            "id": row[0],
            "incident_id": row[1],
            "incident_type": row[2],
            "summary": row[3],
            "hypotheses": row[4],
            "missing_information": row[5],
            "created_at": row[6],
        }

    finally:
        connection.close()
