"""
Rich Demo Data Generator
Creates 30+ realistic entities with varied conflict scenarios
"""
import random
import sqlite3
import json
from datetime import datetime, timedelta

def generate_rich_demo_data():
    """Generate comprehensive demo data with realistic scenarios"""
    
    # Connect to database
    conn = sqlite3.connect('control_system.db')
    cursor = conn.cursor()
    
    # Clear existing data (except system config)
    cursor.execute("DELETE FROM canonical_entities")
    cursor.execute("DELETE FROM source_records")
    cursor.execute("DELETE FROM conflicts")
    cursor.execute("DELETE FROM audit_log WHERE entity_id IS NOT NULL")
    
    # Company names for variety
    companies = [
        "Acme Corp", "TechStart Inc", "Global Solutions Ltd", "DataCo",
        "InnovateLabs", "CloudFirst Systems", "SecureNet Inc", "FastGrow",
        "Enterprise Dynamics", "Digital Ventures", "Summit Technologies",
        "Apex Industries", "Quantum Systems", "Bright Future Co",
        "NextGen Software", "Prime Enterprises"
    ]
    
    # Contact names
    first_names = ["John", "Jane", "Michael", "Sarah", "David", "Emily", 
                   "Robert", "Lisa", "James", "Maria", "William", "Jennifer"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
                  "Miller", "Davis", "Rodriguez", "Martinez", "Wilson", "Anderson"]
    
    # Sales reps
    sales_reps = ["Sarah Mitchell", "Tom Anderson", "Lisa Chen", "Mike Roberts", 
                  "Amy Williams", "Chris Taylor"]
    
    # Project managers
    pms = ["Mike Torres", "Jane Davidson", "Ryan Kim", "Amy Lopez", "David Park"]
    
    # Generate 30 deals with realistic variety
    print("🔄 Generating 30 realistic deal records...")
    
    for i in range(1030, 1060):
        company = random.choice(companies)
        contact_first = random.choice(first_names)
        contact_last = random.choice(last_names)
        contact_name = f"{contact_first} {contact_last}"
        sales_rep = random.choice(sales_reps)
        pm = random.choice(pms)
        
        # Vary deal amounts realistically
        amount = random.choice([
            12500, 15000, 18500, 22000, 24500, 28000, 
            32000, 35000, 42000, 48000, 55000
        ])
        
        # Vary dates - some recent, some older
        days_ago = random.randint(1, 90)
        close_date = datetime.now() - timedelta(days=days_ago)
        close_date_str = close_date.strftime("%Y-%m-%d")
        
        # Determine if this deal has a conflict
        has_conflict = random.random() < 0.35  # 35% have conflicts
        
        if has_conflict:
            # Create conflicting data scenarios
            scenario = random.choice([
                "payment_issue",  # Won but unpaid
                "status_mismatch",  # Different stages
                "amount_discrepancy",  # Different amounts
                "timeline_conflict"  # Work started but not paid
            ])
            
            if scenario == "payment_issue":
                # CRM says won, accounting says unpaid
                crm_stage = "Closed Won"
                invoice_status = "unpaid"
                project_status = random.choice(["in_progress", "not_started"])
                risk_level = "HIGH"
                
            elif scenario == "status_mismatch":
                # Status doesn't match across systems
                crm_stage = random.choice(["Closed Won", "In Negotiation"])
                invoice_status = random.choice(["paid", "unpaid", "partial"])
                project_status = random.choice(["in_progress", "completed", "not_started"])
                risk_level = random.choice(["MEDIUM", "HIGH"])
                
            elif scenario == "amount_discrepancy":
                # Amounts don't match
                crm_stage = "Closed Won"
                invoice_status = "paid"
                project_status = "in_progress"
                # Will create different amounts
                risk_level = "MEDIUM"
                
            else:  # timeline_conflict
                # Work started before payment
                crm_stage = "In Negotiation"
                invoice_status = "unpaid"
                project_status = "in_progress"
                risk_level = "HIGH"
                
        else:
            # No conflict - all systems agree
            status_choice = random.choice([
                ("Closed Won", "paid", "completed"),
                ("Closed Won", "paid", "in_progress"),
                ("In Negotiation", "unpaid", "not_started"),
                ("Proposal Sent", "unpaid", "not_started")
            ])
            crm_stage, invoice_status, project_status = status_choice
            risk_level = "NONE"
        
        # Create canonical entity
        canonical_data = {
            "deal_name": f"Enterprise Implementation - {company}",
            "company": company,
            "contact_name": contact_name,
            "amount": amount,
            "stage": crm_stage,
            "close_date": close_date_str,
            "owner": sales_rep
        }
        
        cursor.execute("""
            INSERT INTO canonical_entities (id, entity_type, data, status)
            VALUES (?, 'deal', ?, ?)
        """, (f"D-{i}", json.dumps(canonical_data), 
              'conflict' if has_conflict else 'active'))
        
        # Create CRM source record (SalesFlow)
        crm_data = {
            "deal_name": canonical_data["deal_name"],
            "company": company,
            "contact_name": contact_name,
            "amount": amount if scenario != "amount_discrepancy" else amount + random.randint(-2000, 2000),
            "stage": crm_stage,
            "close_date": close_date_str,
            "owner": sales_rep,
            "pipeline": "Sales Pipeline",
            "deal_type": random.choice(["New Business", "Expansion", "Renewal"])
        }
        
        cursor.execute("""
            INSERT INTO source_records (entity_id, source_system, data)
            VALUES (?, 'hubspot', ?)
        """, (f"D-{i}", json.dumps(crm_data)))
        
        # Create accounting source record (FinanceHub - stored as quickbooks for compatibility)
        accounting_data = {
            "invoice_number": f"INV-{i}",
            "company": company,
            "contact_name": contact_name,
            "billed_amount": amount,
            "invoice_status": invoice_status,
            "invoice_date": close_date_str,
            "due_date": (close_date + timedelta(days=30)).strftime("%Y-%m-%d"),
            "payment_terms": "Net 30"
        }
        
        cursor.execute("""
            INSERT INTO source_records (entity_id, source_system, data)
            VALUES (?, 'quickbooks', ?)
        """, (f"D-{i}", json.dumps(accounting_data)))
        
        # Create project management source record (TaskFlow - stored as asana for compatibility)
        project_data = {
            "project_id": f"PRJ-{i}",
            "client": company,
            "project_status": project_status,
            "assigned_pm": pm,
            "start_date": (close_date + timedelta(days=1)).strftime("%Y-%m-%d") if project_status != "not_started" else None,
            "team_size": random.randint(3, 8),
            "next_milestone": "Requirements Gathering" if project_status == "in_progress" else None
        }
        
        cursor.execute("""
            INSERT INTO source_records (entity_id, source_system, data)
            VALUES (?, 'asana', ?)
        """, (f"D-{i}", json.dumps(project_data)))
        
        # Create conflict if needed
        if has_conflict:
            # Determine age of conflict
            conflict_age_mins = random.choice([2, 15, 45, 120, 240, 1440])  # 2m to 24h
            conflict_time = datetime.now() - timedelta(minutes=conflict_age_mins)
            
            # Determine conflicting fields
            if scenario == "payment_issue":
                fields = ["invoice_status", "project_status"]
                conflicting_systems = ["quickbooks", "asana"]
            elif scenario == "status_mismatch":
                fields = ["stage", "project_status"]
                conflicting_systems = ["hubspot", "asana"]
            elif scenario == "amount_discrepancy":
                fields = ["amount"]
                conflicting_systems = ["hubspot", "quickbooks"]
            else:  # timeline_conflict
                fields = ["invoice_status", "project_status", "stage"]
                conflicting_systems = ["hubspot", "quickbooks", "asana"]
            
            cursor.execute("""
                INSERT INTO conflicts (
                    entity_id, conflict_type, fields, sources, 
                    risk_level, status, detected_at
                ) VALUES (?, ?, ?, ?, ?, 'pending', ?)
            """, (
                f"D-{i}",
                scenario,
                json.dumps(fields),
                json.dumps(conflicting_systems),
                risk_level,
                conflict_time.strftime("%Y-%m-%d %H:%M:%S")
            ))
            
            print(f"  ⚠️  Conflict created for D-{i}: {scenario} ({risk_level})")
        else:
            print(f"  ✓  Clean record created for D-{i}")
    
    # Generate some historical resolutions (past 30 days)
    print("\n🔄 Generating historical resolution data...")
    
    for i in range(1000, 1030):
        company = random.choice(companies)
        amount = random.choice([15000, 22000, 28000, 35000])
        
        resolution_days_ago = random.randint(1, 30)
        resolution_time = datetime.now() - timedelta(days=resolution_days_ago)
        
        # Create a resolved conflict
        cursor.execute("""
            INSERT INTO conflicts (
                entity_id, conflict_type, fields, sources,
                risk_level, status, detected_at, resolved_at, resolution_method
            ) VALUES (?, ?, ?, ?, ?, 'resolved', ?, ?, ?)
        """, (
            f"D-{i}",
            random.choice(["payment_issue", "status_mismatch", "amount_discrepancy"]),
            json.dumps(["invoice_status"]),
            json.dumps(["quickbooks", "hubspot"]),
            random.choice(["HIGH", "MEDIUM", "LOW"]),
            (resolution_time - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
            resolution_time.strftime("%Y-%m-%d %H:%M:%S"),
            random.choice(["policy:quickbooks", "policy:hubspot", "manual_override"])
        ))
        
        # Create audit log entry
        cursor.execute("""
            INSERT INTO audit_log (
                timestamp, entity_id, action, actor, systems_affected, details
            ) VALUES (?, ?, 'conflict_resolved', ?, ?, ?)
        """, (
            resolution_time.strftime("%Y-%m-%d %H:%M:%S"),
            f"D-{i}",
            random.choice(["system", "operator"]),
            json.dumps(["quickbooks"]),
            json.dumps({"resolution": "auto-applied", "risk_prevented": amount * 0.9})
        ))
        
        print(f"  ✓  Historical resolution: D-{i} ({resolution_days_ago}d ago)")
    
    # Update system state
    pending_count = cursor.execute(
        "SELECT COUNT(*) FROM conflicts WHERE status = 'pending'"
    ).fetchone()[0]
    
    cursor.execute("""
        UPDATE system_state 
        SET active_conflicts = ?,
            automation_status = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = 1
    """, (pending_count, 'paused' if pending_count > 0 else 'running'))
    
    # Update system connections
    for system in ['hubspot', 'quickbooks', 'asana']:
        entity_count = cursor.execute(
            "SELECT COUNT(DISTINCT entity_id) FROM source_records WHERE source_system = ?",
            (system,)
        ).fetchone()[0]
        
        cursor.execute("""
            UPDATE system_connections
            SET entity_count = ?, last_sync = CURRENT_TIMESTAMP
            WHERE system_name = ?
        """, (entity_count, system))
    
    conn.commit()
    conn.close()
    
    # Print summary
    print("\n" + "="*60)
    print("📊 DEMO DATA GENERATION COMPLETE")
    print("="*60)
    print(f"✓ Created 30 canonical entities (deal records)")
    print(f"✓ Created 90 source records (3 systems × 30 entities)")
    print(f"✓ Created ~10 active conflicts with varied risk levels")
    print(f"✓ Created 30 historical resolutions (past 30 days)")
    print(f"✓ Updated system state and connection status")
    print("\n🎯 Database is now ready for $20K+ demo!\n")

if __name__ == "__main__":
    print("\n🚀 Starting Rich Demo Data Generation...\n")
    generate_rich_demo_data()
