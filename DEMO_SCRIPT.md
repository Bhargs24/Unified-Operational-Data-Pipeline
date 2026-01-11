# 12-Minute Demo Script - Operational Control System

## PRE-RECORDING SETUP (2 minutes)
1. Open 3 browser tabs: `mock_hubspot.html`, `mock_quickbooks.html`, `mock_asana.html`
2. Run: `streamlit run control_system.py`
3. Navigate to "Operational Reality" screen in Streamlit
4. Close all notifications, clear desktop clutter

---

## SCENE 1: The Problem (90 seconds)
**SHOW:** 3 browser tabs with mockups

**SAY:**
"According to Gartner research, poor data quality costs companies $12.9 million per year. Let me show you why. This is Deal D-1042 - same deal, three different systems."

**DO:** Switch between tabs, use Loom pen to circle contradictions:
- HubSpot: CLOSED WON, $24,500, Jan 8
- QuickBooks: UNPAID, $24,500, warning message
- Asana: IN PROGRESS, work started Jan 9

**SAY:**
"Sales says it's won. Finance says we haven't been paid. Delivery is doing work we might never get paid for. This happens constantly - IDC found employees waste 2.5 hours every day searching for accurate data."

---

## SCENE 2: The Solution (30 seconds)
**SHOW:** Switch to Streamlit - System Overview screen

**SAY:**
"This is my operational control system. It sits on top of your existing tools - doesn't replace anything. Watch what it does."

---

## SCENE 3: Conflicts Detected (60 seconds)
**SHOW:** Navigate to "Operational Reality" screen

**SAY:**
"It automatically detected these three conflicts in Deal 1042. Look at this risk assessment - it's flagged as HIGH RISK because we're doing work for a customer who hasn't paid. That's a $22,000 problem."

**DO:** Point to specific conflicts showing:
- Status contradiction (won vs unpaid vs in_progress)
- Data source (HubSpot vs QuickBooks vs Asana)
- Risk level (HIGH)

**SAY:**
"Without this system, someone in delivery starts hiring contractors, ordering equipment. Three months later finance realizes the customer never paid. You've lost $22,000 in labor and onboarding costs."

---

## SCENE 4: Policy Engine (90 seconds) - MOST IMPORTANT
**SHOW:** Navigate to "Decision Review" screen

**SAY:**
"Here's what makes this different from a dashboard. This is a GOVERNANCE system - it doesn't just show you problems, it STOPS bad decisions."

**DO:** Show the policy:
- IF invoice unpaid in QuickBooks
- THEN block project work in Asana
- Auto-resolution available

**SAY:**
"See this auto-resolution? The system knows QuickBooks is the source of truth for payment status. It can automatically update HubSpot and pause Asana work until payment clears. No manual fixes, no Slack messages, no meetings."

**DO:** Click "Approve & Apply" button - show success animation

**SAY:**
"There. In 2 seconds, it updated three systems, prevented $22K in losses, and logged the entire decision chain for compliance."

---

## SCENE 5: Audit Trail (30 seconds)
**SHOW:** Navigate to "Audit Log" screen

**SAY:**
"Every change is tracked. Who approved it, when, why, which policy triggered it. Your auditors will love this. When finance asks 'why did we stop this project?' you have a complete decision trail."

---

## SCENE 6: Ownership Rules (45 seconds)
**SHOW:** Navigate to "Ownership Rules" screen

**SAY:**
"You define the rules once. QuickBooks owns payment status. HubSpot owns deal stages. Asana owns project status. When they conflict, the system knows which one wins. No more 'my data versus your data' arguments."

---

## SCENE 7: System Resilience (45 seconds)
**SHOW:** Navigate to "Failure Simulation" screen

**SAY:**
"What happens when QuickBooks goes down? Watch this."

**DO:** Click "Simulate QuickBooks Failure" button

**SAY:**
"See that? System immediately detected the failure, logged it, and would alert your team. No silent failures. No wondering why data stopped syncing."

---

## SCENE 8: Pricing & ROI (90 seconds)
**SHOW:** Keep Streamlit visible or show PRICING notes

**SAY:**
"Three tiers. Base implementation is $8,000 - covers three systems, 10 ownership rules, conflict detection and resolution. Everything you just saw."

"Mid-tier is $12,000 - adds daily monitoring reports, Slack alerts when conflicts arise, quarterly policy reviews."

"Enterprise at $18,000 - unlimited systems, API access, custom integrations."

**SAY:**
"ROI is simple: that one hiring mistake we prevented? $22,000. System pays for itself if it catches just ONE bad decision. My clients typically see 5-10 conflicts like this per month."

---

## SCENE 9: Close (30 seconds)

**SAY:**
"This isn't a dashboard. It's not a sync tool. It's operational CONTROL - automated governance that stops expensive mistakes before they happen. If you're running multiple systems and making decisions based on contradictory data, we should talk. Want me to run this analysis on your actual systems?"

---

## KEY STATISTICS (HAVE READY)
- **Gartner (2021):** $12.9M annual cost of poor data quality
- **IDC (2019):** 2.5 hours/day wasted searching for information
- **Aberdeen (2020):** 30-40% of time spent on manual reconciliation
- **Salesforce (2020):** 25-30% of CRM data contains errors

## PRICING BREAKDOWN
| Tier | Price | Includes |
|------|-------|----------|
| **Base** | $8,000 | 3 systems, 10 rules, conflict detection |
| **Plus** | $12,000 | Base + monitoring, Slack alerts, reports |
| **Enterprise** | $18,000 | Plus + unlimited systems, API access |

**ROI Example:** One prevented hiring mistake = $22,250 (3 months @ $75K salary + $3,500 onboarding)
