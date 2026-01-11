"""
Policy Engine
Evaluates ownership rules and applies business logic for conflict resolution
"""
import json
from datetime import datetime
from core.database import get_db

class PolicyEngine:
    def __init__(self):
        self.db = get_db()
    
    def evaluate_conflict(self, conflict_id):
        """
        Evaluate a conflict against ownership rules
        Returns recommended resolution and applicable policy
        """
        conflict = self._get_conflict_details(conflict_id)
        if not conflict:
            return None
        
        # Get the conflicting field
        fields = json.loads(conflict['fields'])
        if not fields:
            return None
        
        field = fields[0]  # Primary conflicting field
        
        # Find applicable ownership rule
        rule = self._find_ownership_rule(conflict['entity_type'], field)
        
        if not rule:
            return {
                'conflict_id': conflict_id,
                'resolution_type': 'manual',
                'reason': 'No ownership rule defined',
                'recommended_action': 'escalate'
            }
        
        # Get source data to determine winning value
        source_records = self._get_source_records(conflict['entity_id'])
        winning_value = self._get_winning_value(field, rule['owning_system'], source_records)
        
        return {
            'conflict_id': conflict_id,
            'field': field,
            'owning_system': rule['owning_system'],
            'resolution_type': rule['resolution_type'],
            'business_rationale': rule['business_rationale'],
            'winning_value': winning_value,
            'recommended_action': 'auto' if rule['resolution_type'] == 'auto' else 'manual_review'
        }
    
    def apply_policy(self, conflict_id, approved_by='system'):
        """
        Apply the ownership policy to resolve conflict
        Updates canonical entity and logs resolution
        """
        evaluation = self.evaluate_conflict(conflict_id)
        if not evaluation:
            return False
        
        if evaluation['resolution_type'] == 'manual' and approved_by == 'system':
            # Cannot auto-resolve manual conflicts
            return False
        
        conflict = self._get_conflict_details(conflict_id)
        
        # Update canonical entity with winning value
        self._update_canonical_entity(
            conflict['entity_id'],
            evaluation['field'],
            evaluation['winning_value']
        )
        
        # Mark conflict as resolved
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE conflicts
            SET status = 'resolved',
                resolved_at = CURRENT_TIMESTAMP,
                resolution_method = ?
            WHERE id = ?
        """, (f"policy:{evaluation['owning_system']}", conflict_id))
        
        conn.commit()
        
        # Log resolution to audit trail
        self.db.log_action(
            conflict['entity_id'],
            'policy_applied',
            f"policy:{evaluation['owning_system']}",
            systems_affected=json.dumps([evaluation['owning_system']]),
            details=json.dumps(evaluation)
        )
        
        # Check if all conflicts resolved
        pending = self.db.get_pending_conflicts()
        if not pending:
            self.db.resume_automation()
        
        self.db.update_system_state(active_conflicts=len(pending))
        
        return True
    
    def manual_override(self, conflict_id, field, value, approved_by, justification):
        """
        Manually override policy for special cases
        Requires explicit justification
        """
        conflict = self._get_conflict_details(conflict_id)
        if not conflict:
            return False
        
        # Update canonical entity
        self._update_canonical_entity(conflict['entity_id'], field, value)
        
        # Mark conflict as resolved
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE conflicts
            SET status = 'resolved',
                resolved_at = CURRENT_TIMESTAMP,
                resolution_method = 'manual_override'
            WHERE id = ?
        """, (conflict_id,))
        
        conn.commit()
        
        # Log override with justification
        self.db.log_action(
            conflict['entity_id'],
            'manual_override',
            approved_by,
            details=json.dumps({'field': field, 'value': value}),
            justification=justification
        )
        
        # Check if all conflicts resolved
        pending = self.db.get_pending_conflicts()
        if not pending:
            self.db.resume_automation()
        
        self.db.update_system_state(active_conflicts=len(pending))
        
        return True
    
    def _get_conflict_details(self, conflict_id):
        """Get conflict with entity type info"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.*, ce.entity_type
            FROM conflicts c
            JOIN canonical_entities ce ON c.entity_id = ce.id
            WHERE c.id = ?
        """, (conflict_id,))
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def _find_ownership_rule(self, entity_type, field_name):
        """Find applicable ownership rule for entity type and field"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM ownership_rules
            WHERE entity_type = ? AND field_name = ? AND active = 1
            ORDER BY priority ASC
            LIMIT 1
        """, (entity_type, field_name))
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def _get_source_records(self, entity_id):
        """Get all source records for an entity"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT source_system, data, synced_at
            FROM source_records
            WHERE entity_id = ?
            ORDER BY synced_at DESC
        """, (entity_id,))
        
        records = {}
        for row in cursor.fetchall():
            records[row['source_system']] = json.loads(row['data'])
        
        return records
    
    def _get_winning_value(self, field, owning_system, source_records):
        """Extract the value from the owning system"""
        if owning_system in source_records:
            data = source_records[owning_system]
            if isinstance(data, dict) and field in data:
                return data[field]
        return None
    
    def _update_canonical_entity(self, entity_id, field, value):
        """Update canonical entity with resolved value"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Get current data
        cursor.execute("SELECT data, version FROM canonical_entities WHERE id = ?", (entity_id,))
        row = cursor.fetchone()
        
        if row:
            current_data = json.loads(row['data'])
            current_data[field] = value
            
            # Update with incremented version
            cursor.execute("""
                UPDATE canonical_entities
                SET data = ?, version = version + 1, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (json.dumps(current_data), entity_id))
            
            conn.commit()
            return True
        
        return False
    
    def get_applicable_rules(self, entity_type):
        """Get all rules applicable to an entity type"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM ownership_rules
            WHERE entity_type = ? AND active = 1
            ORDER BY priority ASC
        """, (entity_type,))
        
        return [dict(row) for row in cursor.fetchall()]
