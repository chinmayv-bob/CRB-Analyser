# CRB-Analyser: AI-Powered Jira Ticket Automation

**Automated Jira CRB analysis pipeline using AI agents, reducing 25 man-hours of manual work to 5 minutes. Engineered for linear scalability to handle high-volume tickets without increasing operational overhead.**

## Overview

CRB-Analyser is an AI-driven agentic system designed to automate the triage, diagnosis, and summarization of Customer Reported Bugs (CRB) in Jira. By leveraging the Sim.AI platform and a multi-agent orchestration layer, it significantly reduces the operational burden on engineering and product teams.

### 🚀 Key Efficiency & Scalability
*   **Manual Effort**: 20-25 man-hours per monthly batch (scales linearly with ticket volume).
*   **Automated Effort**: ~5 minutes (highly parallelizable and scalable).
*   **Speedup**: ~240x faster than manual processing.
*   **Scalability**: Unlike manual analysis which becomes a major bottleneck as volume grows, this AI-driven pipeline handles increasing load seamlessly, preventing operational overhead from ballooning.

## Architecture & Workers

The project utilizes specialized workers to handle the end-to-end pipeline:

1.  **Jira Worker (`fetch_jira_tickets.py`)**: Connects to the Jira Cloud API to pull recent Customer Reported Bugs and Feedback based on customizable JQL queries.
2.  **Analysis Orchestrator (`summarize_jira_ticket.py`)**: Interfaces with the **Sim.AI** agentic workflow. It orchestrates a multi-agent pipeline:
    *   **Diagnosis Agent**: Analyzes ticket content and diagnosis the root cause.
    *   **KB Retrieval**: Fetches similar past internal comments for context.
    *   **Response Agent**: Generates a professional, one-line internal comment formatted for Jira.
3.  **GSheet Worker (`update_gsheet.py`)**: Syncs the AI-generated analysis back to a central Google Sheet for stakeholder review.
4.  **Main Entry Point (`main.py`)**: Manages the concurrent execution (ThreadPool) of the workers for maximum throughput.

## Getting Started

### Prerequisites
*   Python 3.8+
*   Jira Cloud API Credentials
*   Sim.AI API Key and Workflow ID
*   Google Cloud Service Account (for Sheets integration)

### Installation
1.  Clone the repository.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Set up environment variables:
    *   Copy `template.env` to `.env`.
    *   Fill in your API keys and credentials.

### Usage
Run the main analysis pipeline:
```bash
python main.py
```

## AI Workflow Definition
The core agent logic is defined in `CRB.json`, which can be imported into the Sim.AI platform to replicate the agentic diagnostic pipeline.
