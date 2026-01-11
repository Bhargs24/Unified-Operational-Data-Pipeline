"""
Simulated External Systems
Mock HubSpot, QuickBooks, Asana with realistic behavior
"""
import time
import random
from datetime import datetime
from core.database import get_db

class SimulatedSystem:
    def __init__(self, system_name):
        self.system_name = system_name
        self.db = get_db()
        self.failure_rate = 0.0  # Can be adjusted for testing
    
    def sync_data(self):
        """Simulate API call with potential failure"""
        # Check if we should simulate a failure
        if random.random() < self.failure_rate:
            self._handle_failure()
            return None
        
        # Simulate network latency
        time.sleep(random.uniform(0.1, 0.3))
        
        # Update connection status
        self._update_connection_status('connected')
        
        return self._fetch_mock_data()
    
    def _handle_failure(self):
        """Handle simulated API failure"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Update system connection status
        cursor.execute("""
            UPDATE system_connections
            SET status = 'connection_timeout',
                failure_count = failure_count + 1,
                retry_scheduled = datetime('now', '+30 seconds')
            WHERE system_name = ?
        """, (self.system_name,))
        
        conn.commit()
        
        # Log failure
        self.db.log_action(
            None,
            'api_failure',
            'system',
            systems_affected=self.system_name,
            details=f"{self.system_name} connection timeout"
        )
        
        # Pause automation on failure
        self.db.pause_automation(f"{self.system_name} connection failure")
        
        # Update 24h failure count
        state = self.db.get_system_state()
        self.db.update_system_state(
            failure_count_24h=state['failure_count_24h'] + 1
        )
    
    def _update_connection_status(self, status):
        """Update system connection status"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE system_connections
            SET status = ?,
                last_sync = CURRENT_TIMESTAMP
            WHERE system_name = ?
        """, (status, self.system_name))
        
        conn.commit()
    
    def _fetch_mock_data(self):
        """Return mock data specific to system"""
        # Override in subclasses
        return {}


class HubSpotSystem(SimulatedSystem):
    def __init__(self):
        super().__init__('hubspot')
    
    def _fetch_mock_data(self):
        return {
            'D-1042': {
                'status': 'closed_won',
                'amount': 24500,
                'date': '2026-01-08',
                'contact': 'john_smith',
                'owner': 'sales_rep_1'
            },
            'D-0987': {
                'status': 'closed_won',
                'amount': 18000,
                'date': '2026-01-07',
                'contact': 'jane_doe'
            }
        }


class QuickBooksSystem(SimulatedSystem):
    def __init__(self):
        super().__init__('quickbooks')
    
    def _fetch_mock_data(self):
        return {
            'D-1042': {
                'status': 'unpaid',
                'amount': 24500,
                'date': '2026-01-15',
                'contact': 'john_smith',
                'invoice_number': 'INV-1042'
            },
            'D-0987': {
                'status': 'paid',
                'amount': 17500,  # Different amount - conflict!
                'date': '2026-01-10',
                'contact': 'jane_doe',
                'invoice_number': 'INV-0987'
            }
        }


class AsanaSystem(SimulatedSystem):
    def __init__(self):
        super().__init__('asana')
    
    def _fetch_mock_data(self):
        return {
            'D-1042': {
                'status': 'started',
                'amount': 24500,
                'date': '2026-01-09',
                'contact': 'delivery_team',
                'project_id': 'PRJ-1042'
            }
        }


class SystemOrchestrator:
    """Orchestrates sync across all systems"""
    
    def __init__(self):
        self.systems = {
            'hubspot': HubSpotSystem(),
            'quickbooks': QuickBooksSystem(),
            'asana': AsanaSystem()
        }
        self.db = get_db()
    
    def sync_all_systems(self):
        """Sync data from all systems"""
        all_data = {}
        failures = []
        
        for system_name, system in self.systems.items():
            data = system.sync_data()
            
            if data is None:
                failures.append(system_name)
            else:
                all_data[system_name] = data
                
                # Update entity count
                self._update_entity_count(system_name, len(data))
        
        if failures:
            return {'success': False, 'failures': failures}
        
        # Update last sync time
        self.db.update_system_state(last_sync=datetime.now().isoformat())
        
        return {'success': True, 'data': all_data}
    
    def simulate_failure(self, system_name):
        """Manually trigger a failure for demo purposes"""
        if system_name in self.systems:
            self.systems[system_name].failure_rate = 1.0
            result = self.systems[system_name].sync_data()
            self.systems[system_name].failure_rate = 0.0
            return True
        return False
    
    def recover_system(self, system_name):
        """Recover a failed system"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE system_connections
            SET status = 'connected',
                failure_count = 0,
                retry_scheduled = NULL,
                last_sync = CURRENT_TIMESTAMP
            WHERE system_name = ?
        """, (system_name,))
        
        conn.commit()
        
        self.db.log_action(
            None,
            'system_recovered',
            'system',
            systems_affected=system_name,
            details=f"{system_name} connection restored"
        )
        
        # Check if we can resume automation
        connections = self.db.get_system_connections()
        all_ok = all(c['status'] == 'connected' for c in connections)
        
        pending_conflicts = self.db.get_pending_conflicts()
        
        if all_ok and not pending_conflicts:
            self.db.resume_automation()
    
    def _update_entity_count(self, system_name, count):
        """Update entity count for a system"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE system_connections
            SET entity_count = ?
            WHERE system_name = ?
        """, (count, system_name))
        
        conn.commit()
