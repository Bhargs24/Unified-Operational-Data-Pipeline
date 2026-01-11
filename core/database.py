"""
Database Schema for Operational Control System
SQLite implementation with full conflict resolution logic
"""
import sqlite3
from datetime import datetime
from pathlib import Path
import json

class ControlSystemDB:
    def __init__(self, db_path="control_system.db"):
        self.db_path = db_path
        self.conn = None
        self.initialize_database()
    
    def get_connection(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def initialize_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Canonical entities - single source of truth
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS canonical_entities (
                id TEXT PRIMARY KEY,
                entity_type TEXT NOT NULL,
                data TEXT NOT NULL,
                version INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        """)
        
        # Source records - raw data from each system
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS source_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_id TEXT NOT NULL,
                source_system TEXT NOT NULL,
                data TEXT NOT NULL,
                synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (entity_id) REFERENCES canonical_entities(id)
            )
        """)
        
        # Conflicts - detected mismatches
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conflicts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_id TEXT NOT NULL,
                conflict_type TEXT NOT NULL,
                fields TEXT NOT NULL,
                sources TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP,
                resolution_method TEXT,
                FOREIGN KEY (entity_id) REFERENCES canonical_entities(id)
            )
        """)
        
        # Ownership rules - business logic for conflict resolution
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ownership_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_type TEXT NOT NULL,
                field_name TEXT NOT NULL,
                owning_system TEXT NOT NULL,
                resolution_type TEXT NOT NULL,
                business_rationale TEXT,
                priority INTEGER DEFAULT 100,
                active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Audit log - complete history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                entity_id TEXT,
                action TEXT NOT NULL,
                actor TEXT NOT NULL,
                systems_affected TEXT,
                details TEXT,
                justification TEXT
            )
        """)
        
        # System state - track automation status
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                automation_status TEXT DEFAULT 'running',
                active_conflicts INTEGER DEFAULT 0,
                last_sync TIMESTAMP,
                failure_count_24h INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # System connections - track external systems
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_connections (
                system_name TEXT PRIMARY KEY,
                status TEXT DEFAULT 'connected',
                entity_count INTEGER DEFAULT 0,
                last_sync TIMESTAMP,
                failure_count INTEGER DEFAULT 0,
                retry_scheduled TIMESTAMP
            )
        """)
        
        conn.commit()
        
        # Initialize system state if not exists
        cursor.execute("INSERT OR IGNORE INTO system_state (id) VALUES (1)")
        
        # Initialize default system connections
        systems = ['hubspot', 'quickbooks', 'asana']
        for system in systems:
            cursor.execute("""
                INSERT OR IGNORE INTO system_connections (system_name, status, last_sync)
                VALUES (?, 'connected', CURRENT_TIMESTAMP)
            """, (system,))
        
        conn.commit()
        
        # Initialize default ownership rules
        self._initialize_default_rules(cursor)
        conn.commit()
    
    def _initialize_default_rules(self, cursor):
        rules = [
            ('deal', 'invoice_status', 'quickbooks', 'auto', 'Finance owns payment state - revenue recognition compliance'),
            ('deal', 'contact_info', 'hubspot', 'auto', 'CRM is source of truth for customer data'),
            ('deal', 'deal_status', 'hubspot', 'manual', 'Revenue recognition requires manual review'),
            ('deal', 'amount', 'quickbooks', 'auto', 'Financial records are authoritative for amounts'),
            ('project', 'timeline', 'asana', 'auto', 'Delivery team owns scheduling'),
            ('customer', 'contact_details', 'hubspot', 'auto', 'CRM manages customer relationships'),
        ]
        
        for rule in rules:
            cursor.execute("""
                INSERT OR IGNORE INTO ownership_rules 
                (entity_type, field_name, owning_system, resolution_type, business_rationale)
                VALUES (?, ?, ?, ?, ?)
            """, rule)
    
    def log_action(self, entity_id, action, actor, systems_affected=None, details=None, justification=None):
        """Log all actions to audit trail"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO audit_log 
            (entity_id, action, actor, systems_affected, details, justification)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (entity_id, action, actor, systems_affected, details, justification))
        
        conn.commit()
        return cursor.lastrowid
    
    def get_system_state(self):
        """Get current system state"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM system_state WHERE id = 1")
        state = cursor.fetchone()
        
        if state:
            return dict(state)
        return None
    
    def update_system_state(self, **kwargs):
        """Update system state"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values())
        
        cursor.execute(f"""
            UPDATE system_state 
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE id = 1
        """, values)
        
        conn.commit()
    
    def pause_automation(self, reason):
        """Pause automation due to conflicts or failures"""
        self.update_system_state(automation_status='paused')
        self.log_action(None, 'automation_paused', 'system', details=reason)
    
    def resume_automation(self):
        """Resume automation after conflicts resolved"""
        self.update_system_state(automation_status='running')
        self.log_action(None, 'automation_resumed', 'system')
    
    def get_pending_conflicts(self):
        """Get all unresolved conflicts"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.*, ce.entity_type, ce.data as entity_data
            FROM conflicts c
            JOIN canonical_entities ce ON c.entity_id = ce.id
            WHERE c.status = 'pending'
            ORDER BY 
                CASE c.risk_level 
                    WHEN 'HIGH' THEN 1 
                    WHEN 'MEDIUM' THEN 2 
                    ELSE 3 
                END,
                c.detected_at DESC
        """)
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_ownership_rules(self):
        """Get all active ownership rules"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM ownership_rules 
            WHERE active = 1 
            ORDER BY priority ASC
        """)
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_audit_log(self, limit=50):
        """Get recent audit log entries"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM audit_log 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_system_connections(self):
        """Get all system connection statuses"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM system_connections")
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_source_records(self, source_system=None):
        """Get source records, optionally filtered by system"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if source_system:
            cursor.execute("""
                SELECT * FROM source_records 
                WHERE source_system = ?
                ORDER BY synced_at DESC
            """, (source_system,))
        else:
            cursor.execute("""
                SELECT * FROM source_records 
                ORDER BY source_system, synced_at DESC
            """)
        
        results = []
        for row in cursor.fetchall():
            row_dict = dict(row)
            # Parse JSON data field
            row_dict['data'] = json.loads(row_dict['data'])
            results.append(row_dict)
        
        return results
    
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None


# Singleton instance
_db_instance = None

def get_db():
    global _db_instance
    if _db_instance is None:
        _db_instance = ControlSystemDB()
    return _db_instance
