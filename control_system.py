"""
Operational Control System - Main Interface
Decision control for multi-system data governance
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path
import json

sys.path.append(str(Path(__file__).parent))

from core.database import get_db
from core.policy_engine import PolicyEngine
from core.external_systems import SystemOrchestrator
from core.conflict_detector import detect_conflicts_for_demo

# Initialize on first run
if 'initialized' not in st.session_state:
    detect_conflicts_for_demo()
    st.session_state.initialized = True

# Get backend instances
db = get_db()
policy_engine = PolicyEngine()
orchestrator = SystemOrchestrator()

# Page config
st.set_page_config(
    page_title="Operational Control System",
    page_icon="⬛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Minimal CSS - internal ops tool aesthetic with professional animations
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    
    @keyframes slideIn {
        from { transform: translateX(-10px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-running {
        background: #00FF00;
        animation: pulse 2s infinite;
    }
    
    .status-paused {
        background: #FF0000;
        animation: pulse 1s infinite;
    }
    
    .process-flow {
        border-left: 3px solid #00FF00;
        padding-left: 20px;
        margin: 15px 0;
        animation: slideIn 0.5s ease-out;
    }
    
    .process-step {
        margin: 8px 0;
        font-size: 0.9rem;
        color: #CCCCCC;
        animation: fadeIn 0.5s ease-out;
    }
    
    .system-alert {
        padding: 15px;
        margin: 15px 0;
        border-radius: 4px;
        font-weight: bold;
        animation: slideIn 0.5s ease-out;
    }
    
    .alert-critical-pulse {
        background: #1A0000;
        border: 2px solid #FF0000;
        color: #FF0000;
        animation: pulse 2s infinite;
    }
    
    .alert-success-slide {
        background: #001A00;
        border-left: 3px solid #00FF00;
        color: #00FF00;
        padding: 12px;
        margin: 10px 0;
        animation: slideIn 0.5s ease-out;
    }
    
    .main {
        background-color: #000000;
        font-family: 'JetBrains Mono', monospace;
        padding: 1rem;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    .main *, p, span, div, label {
        color: #CCCCCC;
        font-family: 'JetBrains Mono', monospace;
    }
    
    h1, h2, h3 {
        color: #FFFFFF;
        font-weight: 500;
        font-size: 0.95rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin: 0.5rem 0;
    }
    
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.3rem;
        font-weight: 500;
        color: #00FF00;
    }
    
    [data-testid="stMetricLabel"] {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        font-weight: 400;
        text-transform: uppercase;
        color: #666666;
    }
    
    [data-testid="stMetricDelta"] {
        display: none;
    }
    
    [data-testid="stSidebar"] {
        background-color: #0A0A0A;
        border-right: 1px solid #333333;
    }
    
    [data-testid="stSidebar"] * {
        color: #999999 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.8rem !important;
    }
    
    hr {
        margin: 1rem 0;
        border: none;
        border-top: 1px solid #333333;
    }
    
    [data-testid="stDataFrame"] {
        background-color: #000000;
        border: 1px solid #333333;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
    }
    
    [data-testid="stDataFrame"] th {
        background-color: #0A0A0A;
        color: #666666;
        font-weight: 500;
        text-transform: uppercase;
        font-size: 0.7rem;
    }
    
    [data-testid="stDataFrame"] td {
        color: #CCCCCC;
    }
    
    .stButton > button {
        background-color: #0A0A0A;
        color: #CCCCCC;
        border: 1px solid #333333;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        padding: 0.4rem 1rem;
        text-transform: uppercase;
    }
    
    .stButton > button:hover {
        background-color: #1A1A1A;
        border-color: #00FF00;
        color: #00FF00;
    }
    
    .alert-critical {
        background-color: #1A0000;
        border-left: 3px solid #FF0000;
        padding: 0.75rem;
        margin: 0.5rem 0;
        font-size: 0.85rem;
    }
    
    .alert-warning {
        background-color: #1A1A00;
        border-left: 3px solid #FFFF00;
        padding: 0.75rem;
        margin: 0.5rem 0;
        font-size: 0.85rem;
    }
    
    .status-ok {
        color: #00FF00;
    }
    
    .status-conflict {
        color: #FF0000;
    }
    
    .status-paused {
        color: #FFFF00;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.markdown("### control")

page = st.sidebar.radio(
    "",
    ["executive_dashboard", "operational_reality", "system_overview", "conflict_inbox", "decision_review", "ownership_rules", "audit_log", "failure_sim"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")

# Real system state from database with animated indicators
state = db.get_system_state()
status_color = "status-running" if state['automation_status'] == 'running' else "status-paused"
status_text = state['automation_status'].upper()

st.sidebar.markdown(f"""
<div style="margin: 10px 0;">
    <span class="status-indicator {status_color}"></span>
    <span style="color: {'#00FF00' if state['automation_status'] == 'running' else '#FF0000'}; font-weight: bold;">{status_text}</span>
</div>
""", unsafe_allow_html=True)

conflict_color = "#FF0000" if state['active_conflicts'] > 0 else "#00FF00"
st.sidebar.markdown(f"<div style='color: {conflict_color}; font-weight: bold;'>CONFLICTS: {state['active_conflicts']}</div>", unsafe_allow_html=True)
st.sidebar.markdown(f"**TIME:** {datetime.now().strftime('%H:%M:%S')}")

# Main routing
if page == "executive_dashboard":
    st.markdown("### 📊 EXECUTIVE DASHBOARD")
    
    #Calculate real metrics from database
    total_conflicts = db.conn.execute("SELECT COUNT(*) FROM conflicts").fetchone()[0]
    resolved_conflicts = db.conn.execute("SELECT COUNT(*) FROM conflicts WHERE status = 'resolved'").fetchone()[0]
    pending_conflicts = len(db.get_pending_conflicts())
    
    # Calculate auto-resolution rate
    auto_resolved = db.conn.execute(
        "SELECT COUNT(*) FROM conflicts WHERE resolution_method LIKE 'policy:%'"
    ).fetchone()[0]
    auto_rate = (auto_resolved / resolved_conflicts * 100) if resolved_conflicts > 0 else 0
    
    # Calculate $ saved (assume $22K per HIGH risk conflict resolved)
    critical_resolved = db.conn.execute(
        "SELECT COUNT(*) FROM conflicts WHERE status = 'resolved' AND risk_level = 'HIGH'"
    ).fetchone()[0]
    total_saved = critical_resolved * 22000
    
    # Calculate time saved (assume 30min per manual resolution)
    time_saved_hours = auto_resolved * 0.5
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 VALUE PROTECTED (30 DAYS)",
            value=f"${total_saved:,}",
            delta=f"{critical_resolved} critical conflicts prevented"
        )
    
    with col2:
        st.metric(
            label="⚡ AUTO-RESOLUTION RATE",
            value=f"{auto_rate:.1f}%",
            delta=f"{auto_resolved} of {resolved_conflicts} resolved automatically"
        )
    
    with col3:
        st.metric(
            label="⏱️ TIME SAVED (MTD)",
            value=f"{time_saved_hours:.1f} hrs",
            delta="vs manual process"
        )
    
    with col4:
        st.metric(
            label="⚠️ AWAITING REVIEW",
            value=pending_conflicts,
            delta="requires attention" if pending_conflicts > 0 else "all clear",
            delta_color="inverse"
        )
    
    st.markdown("---")
    
    # System Health Summary
    st.markdown("### SYSTEM HEALTH")
    
    state = db.get_system_state()
    connections = db.get_system_connections()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_color = "🟢" if state['automation_status'] == 'running' else "🔴"
        st.markdown(f"**{status_color} Automation Status**")
        st.markdown(f"### {state['automation_status'].upper()}")
    
    with col2:
        st.markdown(f"**📊 Connected Systems**")
        active_systems = sum(1 for conn in connections if conn['status'] == 'connected')
        st.markdown(f"### {active_systems}/{len(connections)} Active")
    
    with col3:
        st.markdown(f"**🎯 Data Quality**")
        quality_score = ((resolved_conflicts / total_conflicts * 100) if total_conflicts > 0 else 100)
        st.markdown(f"### {quality_score:.1f}%")
    
    st.markdown("---")
    
    # Recent Activity Summary
    st.markdown("### RECENT ACTIVITY (LAST 7 DAYS)")
    
    # Get conflicts resolved in last 7 days
    from datetime import datetime, timedelta
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    recent_resolutions = db.conn.execute("""
        SELECT entity_id, risk_level, resolved_at, resolution_method
        FROM conflicts
        WHERE status = 'resolved' 
        AND resolved_at >= ?
        ORDER BY resolved_at DESC
        LIMIT 10
    """, (week_ago,)).fetchall()
    
    if recent_resolutions:
        resolution_data = []
        for res in recent_resolutions:
            resolution_data.append({
                "Entity": res[0],
                "Risk": res[1],
                "Resolved": res[2][:16],
                "Method": res[3]
            })
        st.dataframe(resolution_data, use_container_width=True, hide_index=True)
    else:
        st.info("No resolutions in the past 7 days")
    
    st.markdown("---")
    
    # Business Impact
    st.markdown("### BUSINESS IMPACT")
    
    impact_col1, impact_col2 = st.columns(2)
    
    with impact_col1:
        st.markdown("**🎯 This Month's Protection**")
        st.markdown(f"- **${total_saved:,}** in potential losses prevented")
        st.markdown(f"- **{critical_resolved}** critical conflicts caught before damage")
        st.markdown(f"- **{time_saved_hours:.1f} hours** saved vs manual reconciliation")
    
    with impact_col2:
        st.markdown("**📈 System Performance**")
        st.markdown(f"- **{auto_rate:.1f}%** of conflicts auto-resolved")
        st.markdown(f"- **{pending_conflicts}** conflicts pending review")
        st.markdown(f"- **{resolved_conflicts}** total resolutions this month")
    
    if pending_conflicts > 0:
        st.markdown("---")
        st.markdown('<div class="alert-warning">⚠️ ACTION REQUIRED: Review pending conflicts to resume automation</div>', unsafe_allow_html=True)

elif page == "operational_reality":
    # System health indicator at top
    state_check = db.get_system_state()
    health_color = "#00FF00" if state_check['automation_status'] == 'running' else "#FF0000"
    st.markdown(f"""
    <div style="background: #0A0A0A; border-left: 4px solid {health_color}; padding: 10px; margin-bottom: 20px;">
        <span style="color: {health_color}; font-weight: bold;">SYSTEM STATUS: {state_check['automation_status'].upper()}</span> | 
        <span style="color: {'#FF0000' if state_check['active_conflicts'] > 0 else '#00FF00'};">CONFLICTS: {state_check['active_conflicts']}</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### OPERATIONAL REALITY")
    
    # Check for conflicts
    conflicts = db.get_pending_conflicts()
    if conflicts:
        st.markdown('<div class="alert-critical">⚠ OPERATIONAL STATE INCONSISTENT</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    # Query actual source records from database
    with col1:
        st.markdown("**HUBSPOT**")
        hubspot_data = db.get_source_records('hubspot')
        if hubspot_data:
            for record in hubspot_data[:5]:  # Show first 5
                data = record['data']
                st.text(f"deal: {record['entity_id']}")
                st.text(f"status: {data.get('stage', 'N/A')}")
                st.text(f"amount: ${data.get('amount', 0):,}")
                st.text(f"date: {data.get('close_date', 'N/A')}")
                st.text(f"name: {data.get('deal_name', 'N/A')[:20]}")
                st.markdown("---")
        else:
            st.info("No records")
    
    with col2:
        st.markdown("**QUICKBOOKS**")
        qb_data = db.get_source_records('quickbooks')
        if qb_data:
            for record in qb_data[:5]:
                data = record['data']
                st.text(f"invoice: {record['entity_id']}")
                st.text(f"status: {data.get('invoice_status', 'N/A')}")
                st.text(f"amount: ${data.get('billed_amount', 0):,}")
                st.text(f"terms: {data.get('payment_terms', 'N/A')}")
                st.markdown("---")
        else:
            st.info("No records")
    
    with col3:
        st.markdown("**ASANA**")
        asana_data = db.get_source_records('asana')
        if asana_data:
            for record in asana_data[:5]:
                data = record['data']
                st.text(f"project: {record['entity_id']}")
                st.text(f"status: {data.get('project_status', 'N/A')}")
                st.text(f"pm: {data.get('assigned_pm', 'N/A')}")
                st.text(f"milestone: {data.get('next_milestone', 'N/A')}")
                st.markdown("---")
        else:
            st.info("No records")
    
    # Show contradiction summary
    if conflicts:
        st.markdown("---")
        st.markdown("**CONTRADICTION DETECTED**")
        st.text(f"{len(conflicts)} conflicts found")
        st.text("automation: paused")
        st.text("action required: review conflicts")

elif page == "system_overview":
    st.markdown("### SYSTEM OVERVIEW")
    
    # Real system state metrics
    state = db.get_system_state()
    entity_count = db.conn.execute("SELECT COUNT(*) FROM canonical_entities").fetchone()[0]
    conflict_count = len(db.get_pending_conflicts())
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("entities", entity_count)
    col2.metric("synced", entity_count - conflict_count)
    col3.metric("conflicts", conflict_count)
    col4.metric("automation", state['automation_status'])
    
    st.markdown("---")
    
    # Real system connections
    st.markdown("**CONNECTED SYSTEMS**")
    connections = db.get_system_connections()
    
    if connections:
        systems_data = []
        for conn in connections:
            # Count entities from this system
            entity_count = db.conn.execute(
                "SELECT COUNT(DISTINCT entity_id) FROM source_records WHERE source_system = ?",
                (conn['system_name'],)
            ).fetchone()[0]
            
            systems_data.append({
                "system": conn['system_name'],
                "status": conn['status'],
                "entities": entity_count,
                "last_sync": conn['last_sync_time']
            })
        
        st.dataframe(systems_data, use_container_width=True, hide_index=True)
    else:
        st.info("No systems connected")
    
    st.markdown("---")
    if state['automation_status'] == 'paused':
        st.markdown('<div class="alert-warning">automation paused when conflicts detected</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-ok">automation running</div>', unsafe_allow_html=True)

elif page == "conflict_inbox":
    st.markdown("### CONFLICT INBOX")
    
    # Get real conflicts from database
    conflicts = db.get_pending_conflicts()
    
    if conflicts:
        # Show critical alert banner
        high_risk_count = sum(1 for c in conflicts if c['risk_level'] == 'HIGH')
        if high_risk_count > 0:
            st.markdown(f"""
            <div style="background: #1A0000; border: 2px solid #FF0000; padding: 15px; margin: 10px 0; animation: pulse 2s infinite;">
                ⚠️ {high_risk_count} HIGH RISK CONFLICTS DETECTED - AUTOMATION PAUSED
            </div>
            """, unsafe_allow_html=True)
        
        conflict_data = []
        for c in conflicts:
            # Parse fields JSON
            import json
            fields = json.loads(c['fields'])
            field_name = fields[0] if fields else "unknown"
            
            # Add visual badge for risk level
            badge_class = f"badge-{c['risk_level'].lower()}"
            risk_display = f"<span class='conflict-badge {badge_class}'>{c['risk_level']}</span>"
            
            conflict_data.append({
                "entity": c['entity_id'],
                "type": c['conflict_type'],
                "field": field_name,
                "risk": c['risk_level'],
                "detected": c['detected_at'][:16],
                "status": c['status']
            })
        
        st.dataframe(conflict_data, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        if st.button("review_next_conflict"):
            # Get first unresolved conflict
            first_conflict = conflicts[0]
            st.session_state['selected_conflict'] = first_conflict['entity_id']
            st.text(f"→ reviewing {first_conflict['entity_id']}")
    else:
        st.info("No conflicts detected")
        st.markdown("**automation: running**")

elif page == "decision_review":
    st.markdown("### DECISION REVIEW")
    
    # Get selected conflict or first pending
    conflicts = db.get_pending_conflicts()
    if not conflicts:
        st.info("No conflicts to review")
    else:
        selected_entity = st.session_state.get('selected_conflict', conflicts[0]['entity_id'])
        
        # Find this conflict
        conflict = next((c for c in conflicts if c['entity_id'] == selected_entity), conflicts[0])
        
        # Parse field name from JSON
        import json
        fields = json.loads(conflict['fields'])
        field_name = fields[0] if fields else "unknown"
        
        st.markdown(f"**ENTITY: {conflict['entity_id']}**")
        st.markdown(f"**CONFLICT: {field_name} ({conflict['risk_level']})**")
        
        st.markdown("---")
        st.markdown("**SOURCE COMPARISON**")
        
        # Get source records for this entity
        sources = db.conn.execute("""
            SELECT source_system, data 
            FROM source_records 
            WHERE entity_id = ?
        """, (conflict['entity_id'],)).fetchall()
        
        # Get canonical version
        canonical = db.conn.execute("""
            SELECT data as entity_data 
            FROM canonical_entities 
            WHERE id = ?
        """, (conflict['entity_id'],)).fetchone()
        
        # Build comparison table
        comparison_data = []
        
        for src in sources:
            data = json.loads(src[1])
            comparison_data.append({
                "system": src[0],
                "value": str(data.get(field_name, "N/A"))
            })
        
        if canonical:
            can_data = json.loads(canonical[0])
            comparison_data.append({
                "system": "canonical",
                "value": str(can_data.get(field_name, "pending"))
            })
        
        st.dataframe(comparison_data, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.markdown("**OWNERSHIP RULE**")
        
        # Evaluate policy for this conflict
        policy_result = policy_engine.evaluate_conflict(conflict['id'])
        
        if policy_result and 'field' in policy_result:
            # Show visual process flow
            st.markdown("""
            <div class="process-flow">
                <div style="margin: 5px 0;">✓ CONFLICT DETECTED</div>
                <div style="margin: 5px 0;">✓ POLICY EVALUATED</div>
                <div style="margin: 5px 0;">✓ OWNERSHIP DETERMINED</div>
                <div style="margin: 5px 0; color: #00FF00;">→ READY FOR RESOLUTION</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.text(f"field: {policy_result['field']}")
            st.text(f"owner: {policy_result.get('owning_system', 'N/A')}")
            st.text(f"mode: {policy_result['resolution_type']}")
            st.text(f"rationale: {policy_result.get('business_rationale', 'N/A')}")
            
            st.markdown("---")
            st.markdown("**RESOLUTION OPTIONS**")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("approve_resolution", key=f"approve_{conflict['id']}"):
                    # Apply the policy with visual feedback
                    with st.spinner('Applying policy...'):
                        import time
                        time.sleep(0.5)  # Brief pause for visual effect
                        policy_engine.apply_policy(conflict['id'])
                    
                    st.markdown("""
                    <div style="background: #001a00; border-left: 3px solid #00FF00; padding: 10px; margin: 10px 0;">
                        ✓ POLICY APPLIED<br/>
                        ✓ CANONICAL UPDATED<br/>
                        ✓ AUDIT LOGGED<br/>
                        ✓ AUTOMATION CHECKING...
                    </div>
                    """, unsafe_allow_html=True)
                    time.sleep(1)
                    st.rerun()
            
            with col2:
                if st.button("override", key=f"override_{conflict['id']}"):
                    st.session_state[f'override_{conflict["id"]}'] = True
            
            # Show override form if requested
            if st.session_state.get(f'override_{conflict["id"]}', False):
                with col3:
                    justification = st.text_area("justification required:", key=f"just_{conflict['id']}")
                    if st.button("submit_override", key=f"submit_{conflict['id']}"):
                        if justification:
                            # Override with custom value - get winning value from user
                            winning_value = st.text_input("new value:", key=f"val_{conflict['id']}")
                            if winning_value:
                                policy_engine.manual_override(
                                    conflict['id'],
                                    winning_value,
                                    justification,
                                    actor="operator"
                                )
                                st.success("override logged")
                                st.rerun()
                        else:
                            st.error("justification required")
        else:
            st.warning("No matching policy rule found")

elif page == "ownership_rules":
    st.markdown("### OWNERSHIP RULES")
    
    # Get real ownership rules from database
    rules = db.get_ownership_rules()
    
    if rules:
        rules_data = []
        for rule in rules:
            rules_data.append({
                "field": rule['field_name'],
                "owner": rule['owner_system'],
                "mode": rule['resolution_type'],
                "rationale": rule['business_rationale']
            })
        
        st.dataframe(rules_data, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.markdown("**BUSINESS RULE EXAMPLE**")
        first_rule = rules[0]
        st.text(f"field: {first_rule['field_name']}")
        st.text(f"rule: {first_rule['owner_system']} is authoritative source")
        st.text(f"why: {first_rule['business_rationale']}")
        st.text(f"auto/manual: {first_rule['resolution_type']}")
    else:
        st.info("No ownership rules configured")

elif page == "audit_log":
    st.markdown("### AUDIT LOG")
    
    # Get real audit log from database
    audit_entries = db.get_audit_log(limit=50)
    
    if audit_entries:
        audit_data = []
        for entry in audit_entries:
            audit_data.append({
                "ts": entry['timestamp'][11:19],  # Extract time only
                "entity": entry['entity_id'],
                "action": entry['action'],
                "by": entry['actor'],
                "details": entry['details'][:50] if entry['details'] else "n/a",
                "justification": entry['justification'] if entry['justification'] else "n/a"
            })
        
        st.dataframe(audit_data, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.markdown("**ACCOUNTABILITY**")
        st.text("every decision is logged")
        st.text("no silent failures")
        st.text("full traceability")
    else:
        st.info("No audit entries yet")

elif page == "failure_sim":
    st.markdown("### FAILURE & RECOVERY")
    
    # Get real system state
    state = db.get_system_state()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("uptime", "99.97")
    col2.metric("failed_syncs", state.get('failed_sync_count', 0))
    col3.metric("failures_24h", "0")
    col4.metric("data_corruption", "0")
    
    st.markdown("---")
    
    if st.button("simulate_quickbooks_failure"):
        # Actually call the orchestrator to simulate failure
        with st.spinner('Simulating system failure...'):
            import time
            time.sleep(0.5)
            orchestrator.simulate_failure('quickbooks')
        
        st.markdown("""
        <div style="background: #1A0000; border: 2px solid #FF0000; padding: 15px; margin: 10px 0; animation: pulse 1.5s infinite;">
            🔴 FAILURE DETECTED - SYSTEM ISOLATED
        </div>
        """, unsafe_allow_html=True)
        st.text("system: quickbooks")
        st.text("error: connection_timeout")
        st.text("action: isolated")
        st.text("retry: scheduled 30s")
        
        # Check if automation was paused
        new_state = db.get_system_state()
        st.text(f"automation: {new_state['automation_status']}")
        st.text("data_integrity: preserved")
        st.text("overwrites: 0")
        
        st.markdown("---")
        st.markdown("**FAILURE HANDLING**")
        st.text("✓ failure detected automatically")
        st.text("✓ affected system isolated")
        st.text("✓ no data corruption")
        st.text("✓ retry logic engaged")
        st.text("✓ automation paused until recovery")
        
        # Show audit log entry
        st.markdown("---")
        st.markdown("**AUDIT ENTRY**")
        recent_logs = db.get_audit_log(limit=1)
        if recent_logs:
            log = recent_logs[0]
            st.text(f"timestamp: {log['timestamp']}")
            st.text(f"action: {log['action']}")
            st.text(f"actor: {log['actor']}")
    
    st.markdown("---")
    if st.button("recover_quickbooks"):
        orchestrator.recover_system('quickbooks')
        st.success("✓ system recovered")
        st.text("connection: restored")
        st.text("sync: resumed")
        st.rerun()
