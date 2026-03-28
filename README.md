# Mission Assurance Dashboard

## Overview
Mission Assurance Dashboard is a prototype decision-support tool for mission-critical systems. It helps a human reviewer assess operational readiness using requirements traceability, integration-test status, anomaly logs, subsystem health, and risk signals.

This version uses mock data to simulate a communications / mission-support environment.

## Purpose
The goal of this project is not full automation. The goal is to support human judgment in determining whether a system is ready for operations.

The dashboard answers a simple question:

**Are we ready to operate, and if not, what is blocking readiness?**

## Why this project exists
Mission-critical systems are not judged only by whether code runs. They are judged by whether:
- requirements are accounted for
- tests have passed
- anomalies are understood
- risks are controlled
- leadership can trust the readiness recommendation

This tool is meant to demonstrate a structured approach to mission assurance, readiness review, and operational decision support.

## Why this is human-gated?
As of now there is no automation on the backend but in a future version there will be. To assure that humans will be involved in the decision process there will fail safes or checks tbat require a human to continue the automated process or deploy a certain part involved on the dashboard itself. 

## Why this is a mission assurance tool, not just a dashboard?
The title is misleading but in the future this will become a tool vital to multiple different organizations and industries. 

## MVP Scope
This MVP includes:
- requirements traceability view
- test and verification status
- anomaly log review
- subsystem health summary
- simple risk register
- overall readiness recommendation

This MVP does **not** include:
- live telemetry
- real authentication
- external APIs
- machine learning
- production deployment

## Readiness Logic
The initial readiness logic is intentionally simple:

- **No-Go** if any critical blocking anomaly is open
- **No-Go** if any mission-critical subsystem is red
- **No-Go** if requirements verified is below 85%

- **Conditional Go** if there are no critical blockers, but some medium risks remain or requirements verified is between 85% and 95%

- **Go** if there are no critical blockers, mission-critical tests are passing, and requirements verified is above 95%

## Data Model
The dashboard uses mock CSV files:
- `requirements.csv`
- `tests.csv`
- `anomalies.csv`
- `risks.csv`
- `subsystems.csv`
- `decision_log.csv`

## Intended Audience
This project is intended as:
1. a portfolio artifact
2. a systems-thinking demonstration
3. an example of human-gated readiness support for mission-critical environments

## Future Versions
Potential future improvements:
- PostgreSQL backend
- Dockerized deployment
- role-based reviewer notes
- more advanced scoring logic
- interface dependency maps
- anomaly trend analysis
- evidence links for verification artifacts

## Author Notes
This project is part of a broader systems / mission-assurance / decision-support portfolio focused on high-consequence technical environments.
