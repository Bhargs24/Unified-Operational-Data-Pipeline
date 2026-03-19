# Architecture Diagram for Video

**How to use:**
1. Copy the Mermaid code below
2. Go to https://mermaid.live
3. Paste and click "Download PNG"
4. Save as `demo-assets/architecture.png`
5. Show in video at 0:17 for 2 seconds

---

## Operational Control System Architecture

```mermaid
graph TB
    subgraph Sources["Operational Reality Layer"]
        HS[HubSpot CRM<br/>Deal Status<br/>Contact Data<br/>Sales Pipeline]
        QB[QuickBooks<br/>Invoice Status<br/>Payment State<br/>Financial Records]
        AS[Asana<br/>Project Status<br/>Task Assignments<br/>Delivery Timeline]
    end
    
    subgraph Ingestion["Data Ingestion & Monitoring"]
        API[API Connectors<br/>Real-time Polling<br/>Webhook Ingest]
        Parser[Data Parser<br/>Schema Validation<br/>Field Mapping]
        Buffer[Staging Buffer<br/>Pre-Processing<br/>Deduplication]
    end
    
    subgraph Detection["Conflict Detection Engine"]
        Scanner[State Scanner<br/>Cross-System Compare<br/>Field-level Diff]
        Risk[Risk Classifier<br/>Business Impact Analysis<br/>Priority Scoring]
        Alert[Alert Generator<br/>Real-time Notification<br/>Automation Pause]
    end
    
    subgraph Core["Canonical Truth Engine"]
        Rules[(Ownership Rules<br/>Business Logic<br/>Resolution Policies)]
        DB[(SQLite Database<br/>Canonical Entities<br/>Source Records<br/>Conflict Log)]
        Cache[State Cache<br/>Version Control<br/>Rollback Support]
    end
    
    subgraph Policy["Policy & Decision Engine"]
        Eval[Policy Evaluator<br/>Rule Matching<br/>Auto/Manual Mode]
        Resolve[Resolution Engine<br/>Field Reconciliation<br/>Update Orchestration]
        Override[Override Manager<br/>Justification Required<br/>Manual Review]
    end
    
    subgraph Governance["Governance & Trust Layer"]
        Audit[(Audit Log<br/>Complete History<br/>Who/What/When/Why)]
        Track[Resolution Tracker<br/>Status Monitoring<br/>Success Metrics]
        Failure[Failure Detection<br/>System Isolation<br/>Retry Logic]
    end
    
    subgraph Interface["Control Interface"]
        Reality[Operational Reality<br/>Live System Views<br/>Contradiction Display]
        Inbox[Conflict Inbox<br/>Priority Queue<br/>Risk Assessment]
        Decision[Decision Review<br/>Side-by-Side Compare<br/>Policy Application]
        Admin[Policy Admin<br/>Rule Configuration<br/>System Status]
    end
    
    subgraph External["Orchestration Layer"]
        Sync[State Propagation<br/>Multi-System Update<br/>Transaction Rollback]
        Health[Health Monitor<br/>Connection Status<br/>Failure Recovery]
        Report[Reporting Engine<br/>Executive Summary<br/>Metrics Dashboard]
    end
    
    HS --> API
    QB --> API
    AS --> API
    
    API --> Parser
    Parser --> Buffer
    Buffer --> Scanner
    
    Scanner --> Risk
    Risk --> Alert
    Alert --> DB
    
    Scanner --> DB
    DB <--> Rules
    DB <--> Cache
    
    DB --> Eval
    Rules --> Eval
    Eval --> Resolve
    Resolve --> Override
    
    Resolve --> Audit
    Override --> Audit
    Alert --> Track
    Track --> Failure
    
    Failure --> Health
    Audit --> Report
    
    Reality --> Interface
    Inbox --> Interface
    Decision --> Interface
    Admin --> Interface
    
    Interface --> Eval
    Interface --> DB
    Interface --> Audit
    
    Resolve --> Sync
    Sync --> HS
    Sync --> QB
    Sync --> AS
    
    Health --> Alert
    DB -.Failed Sync.-> Failure
    Failure -.Recovery.-> Sync
    
    style Sources fill:#fff3e0,stroke:#f57c00,stroke-width:3px
    style Ingestion fill:#e3f2fd,stroke:#1976d2,stroke-width:3px
    style Detection fill:#fce4ec,stroke:#c2185b,stroke-width:3px
    style Core fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px
    style Policy fill:#e8f5e9,stroke:#388e3c,stroke-width:3px
    style Governance fill:#fff9c4,stroke:#f9a825,stroke-width:3px
    style Interface fill:#e0f2f1,stroke:#00897b,stroke-width:3px
    style External fill:#f1f8e9,stroke:#689f38,stroke-width:3px
```

**Save as:** `demo-assets/architecture.png`

**When to show in video:** Timestamp 0:17 (flash for 2 seconds while explaining the system)

**Duration:** 2 seconds, then return to demo

---

## Key Architecture Highlights to Mention:

1. **Multi-Source Ingestion** - Continuously monitors HubSpot, QuickBooks, and Asana
2. **Real-time Conflict Detection** - Automatically identifies data inconsistencies 
3. **Canonical Truth Engine** - Single authoritative database with version control
4. **Policy-Driven Resolution** - Business rules determine conflict resolution (auto/manual)
5. **Complete Audit Trail** - Every decision tracked with justification
6. **Failure Isolation** - System failures don't corrupt data or cause silent errors
7. **Decision Control Interface** - Prevents wrong business decisions before they happen

**Positioning Statement:**
> "This isn't a dashboard or sync tool - it's a **decision control system** that prevents your business from making expensive mistakes based on inconsistent data."
