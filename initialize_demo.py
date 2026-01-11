"""
Initialize demo data and run system
"""
from core.database import get_db
from core.conflict_detector import detect_conflicts_for_demo
from core.external_systems import SystemOrchestrator

def initialize_demo():
    """Set up demo environment with realistic conflicts"""
    print("Initializing Operational Control System...")
    
    # Initialize database
    db = get_db()
    print("✓ Database initialized")
    
    # Set up system connections
    orchestrator = SystemOrchestrator()
    print("✓ External systems connected")
    
    # Generate realistic conflicts
    print("Detecting conflicts...")
    conflicts = detect_conflicts_for_demo()
    print(f"✓ {len(conflicts)} conflicts detected")
    
    # Update system state
    state = db.get_system_state()
    print(f"\nSystem Status:")
    print(f"  Automation: {state['automation_status']}")
    print(f"  Active Conflicts: {state['active_conflicts']}")
    
    print("\n✓ Demo environment ready")
    return db, orchestrator

if __name__ == "__main__":
    initialize_demo()
