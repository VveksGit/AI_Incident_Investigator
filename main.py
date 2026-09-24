from investigator import investigate_incident


def main():
    incident = {
        "service": "Payment API",
        "timestamp": "2026-09-22 10:42:00",
        "description": "Users began receiving payment failures.",
        "logs": [
            "Database connection timeout.",
            "Retry attempt 1.",
            "Retry attempt 2.",
            "Request failed.",
        ],
        "deployment": {"version": "2.4.1", "deployed_at": "2026-09-22 10:30:00"},
    }

    investigation = investigate_incident(incident)

    if investigation is not None:
        print("Investigation output is valid!")
        print(investigation)
    else:
        print("Investigation failed!")


if __name__ == "__main__":
    main()
