"""
Conflict Detection Engine
Analyzes data from multiple sources and detects contradictions
"""
import json
from datetime import datetime
from core.database import get_db

class ConflictDetector:
    def __init__(self):
        self.db = get_db()
    
    def detect_conflicts(self, entity_id, source_data):
        """
        Analyze data from multiple sources and detect conflicts
        
        source_data: {
            'hubspot': {...},
            'quickbooks': {...},
            'asana': {...}
        }
        """
        conflicts = []
        
        # Compare critical fields across sources
        critical_fields = self._get_critical_fields(source_data)
        
        for field in critical_fields:
            field_conflict = self._check_field_conflict(field, source_data)
            if field_conflict:
                conflicts.append(field_conflict)
        
        # If conflicts found, log them and pause automation
        if conflicts:
            for conflict in conflicts:
                self._log_conflict(entity_id, conflict)
            
            self.db.pause_automation(f"Conflicts detected in entity {entity_id}")
            self.db.update_system_state(active_conflicts=len(self.db.get_pending_conflicts()))
        
        return conflicts
    
    def _get_critical_fields(self, source_data):
        """Extract all unique fields across sources"""
        fields = set()
        for source, data in source_data.items():
            if isinstance(data, dict):
                fields.update(data.keys())
        return fields
    
    def _check_field_conflict(self, field, source_data):
        """Check if a field has conflicting values across sources"""
        values = {}
        
        for source, data in source_data.items():
            if isinstance(data, dict) and field in data:
                values[source] = data[field]
        
        # If we have values from multiple sources
        if len(values) > 1:
            unique_values = set(str(v) for v in values.values())
            
            # If values differ, we have a conflict
            if len(unique_values) > 1:
                risk_level = self._assess_risk_level(field, values)
                
                return {
                    'field': field,
                    'values': values,
                    'sources': list(values.keys()),
                    'risk_level': risk_level
                }
        
        return None
    
    def _assess_risk_level(self, field, values):
        """Assess risk level based on field type and business impact"""
        high_risk_fields = ['status', 'invoice_status', 'deal_status', 'payment_status', 'amount']
        medium_risk_fields = ['date', 'timeline', 'owner', 'contact']
        
        if field in high_risk_fields:
            return 'HIGH'
        elif field in medium_risk_fields:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _log_conflict(self, entity_id, conflict):
        """Log detected conflict to database"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO conflicts 
            (entity_id, conflict_type, fields, sources, risk_level, status)
            VALUES (?, ?, ?, ?, ?, 'pending')
        """, (
            entity_id,
            f"{conflict['field']}_mismatch",
            json.dumps([conflict['field']]),
            json.dumps(conflict['sources']),
            conflict['risk_level']
        ))
        
        conn.commit()
        
        # Log to audit trail
        self.db.log_action(
            entity_id,
            'conflict_detected',
            'system',
            systems_affected=json.dumps(conflict['sources']),
            details=json.dumps(conflict)
        )
    
    def get_conflict_details(self, conflict_id):
        """Get detailed information about a specific conflict"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.*, ce.data as entity_data, ce.entity_type
            FROM conflicts c
            JOIN canonical_entities ce ON c.entity_id = ce.id
            WHERE c.id = ?
        """, (conflict_id,))
        
        conflict = cursor.fetchone()
        if conflict:
            conflict_dict = dict(conflict)
            
            # Get source records for comparison
            cursor.execute("""
                SELECT source_system, data, synced_at
                FROM source_records
                WHERE entity_id = ?
                ORDER BY synced_at DESC
            """, (conflict_dict['entity_id'],))
            
            conflict_dict['source_records'] = [dict(row) for row in cursor.fetchall()]
            
            return conflict_dict
        
        return None


def detect_conflicts_for_demo():
    """Generate realistic conflicts for demo"""
    db = get_db()
    detector = ConflictDetector()
    
    # Entity D-1042 - Deal with status mismatch
    entity_id = "D-1042"
    
    # Create canonical entity
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO canonical_entities (id, entity_type, data, version)
        VALUES (?, 'deal', ?, 1)
    """, (entity_id, json.dumps({
        'deal_id': 'D-1042',
        'amount': 24500,
        'customer': 'john_smith',
        'status': 'pending_review'
    })))
    
    # Insert source records
    source_data = {
        'hubspot': {
            'status': 'closed_won',
            'amount': 24500,
            'date': '2026-01-08',
            'contact': 'john_smith'
        },
        'quickbooks': {
            'status': 'unpaid',
            'amount': 24500,
            'date': '2026-01-15',
            'contact': 'john_smith'
        },
        'asana': {
            'status': 'started',
            'amount': 24500,
            'date': '2026-01-09',
            'contact': 'delivery_team'
        }
    }
    
    for source, data in source_data.items():
        cursor.execute("""
            INSERT INTO source_records (entity_id, source_system, data)
            VALUES (?, ?, ?)
        """, (entity_id, source, json.dumps(data)))
    
    conn.commit()
    
    # Detect conflicts
    conflicts = detector.detect_conflicts(entity_id, source_data)
    
    # Create additional demo conflicts
    _create_additional_demo_conflicts(db)
    
    return conflicts


def _create_additional_demo_conflicts(db):
    """Create additional realistic conflicts for demo"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # D-0987 - Amount discrepancy
    cursor.execute("""
        INSERT OR IGNORE INTO canonical_entities (id, entity_type, data)
        VALUES ('D-0987', 'deal', ?)
    """, (json.dumps({'deal_id': 'D-0987', 'amount': 18000}),))
    
    cursor.execute("""
        INSERT OR IGNORE INTO conflicts 
        (entity_id, conflict_type, fields, sources, risk_level, status)
        VALUES ('D-0987', 'amount_discrepancy', '["amount"]', '["hubspot", "quickbooks"]', 'MEDIUM', 'pending')
    """)
    
    # C-2341 - Contact info mismatch
    cursor.execute("""
        INSERT OR IGNORE INTO canonical_entities (id, entity_type, data)
        VALUES ('C-2341', 'customer', ?)
    """, (json.dumps({'customer_id': 'C-2341', 'name': 'Acme Corp'}),))
    
    cursor.execute("""
        INSERT OR IGNORE INTO conflicts 
        (entity_id, conflict_type, fields, sources, risk_level, status)
        VALUES ('C-2341', 'contact_info', '["email", "phone"]', '["hubspot", "asana"]', 'LOW', 'pending')
    """)
    
    conn.commit()
