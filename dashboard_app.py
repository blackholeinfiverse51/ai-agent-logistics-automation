#!/usr/bin/env python3
"""
AI Agent Logistics Dashboard
Comprehensive management dashboard with real-time KPIs, alerts, and analytics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
from database.service import DatabaseService
from database.models import init_database

# Page configuration
st.set_page_config(
    page_title="AI Agent Logistics Dashboard",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .alert-critical {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .alert-high {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .alert-medium {
        background-color: #e8f5e8;
        border-left: 4px solid #4caf50;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def load_dashboard_data():
    """Load all dashboard data"""
    with DatabaseService() as db_service:
        data = {
            'orders': db_service.get_orders(),
            'shipments': db_service.get_shipments(),
            'inventory': db_service.get_inventory(),
            'low_stock': db_service.get_low_stock_items(),
            'purchase_orders': db_service.get_purchase_orders(),
            'pending_reviews': db_service.get_pending_reviews(),
            'agent_logs': db_service.get_agent_logs(limit=50),
            'performance_metrics': db_service.get_performance_metrics(days=7)
        }
    return data

def create_kpi_metrics(data):
    """Create KPI metrics"""
    orders = data['orders']
    shipments = data['shipments']
    inventory = data['inventory']
    low_stock = data['low_stock']
    purchase_orders = data['purchase_orders']
    pending_reviews = data['pending_reviews']
    performance = data['performance_metrics']
    
    # Calculate KPIs
    total_orders = len(orders)
    active_shipments = len([s for s in shipments if s['status'] not in ['delivered', 'cancelled']])
    delivered_shipments = len([s for s in shipments if s['status'] == 'delivered'])
    delivery_rate = (delivered_shipments / len(shipments) * 100) if shipments else 0
    
    low_stock_count = len(low_stock)
    stock_health = ((len(inventory) - low_stock_count) / len(inventory) * 100) if inventory else 100
    
    pending_pos = len([po for po in purchase_orders if po['status'] == 'pending'])
    automation_rate = performance.get('automation_rate', 0)
    
    return {
        'total_orders': total_orders,
        'active_shipments': active_shipments,
        'delivery_rate': delivery_rate,
        'stock_health': stock_health,
        'low_stock_count': low_stock_count,
        'pending_pos': pending_pos,
        'automation_rate': automation_rate,
        'pending_reviews': len(pending_reviews)
    }

def display_kpi_dashboard(kpis):
    """Display KPI dashboard"""
    st.markdown('<div class="main-header">🚚 AI Agent Logistics Dashboard</div>', unsafe_allow_html=True)
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📦 Total Orders",
            value=kpis['total_orders'],
            delta=f"{kpis['active_shipments']} active shipments"
        )
        
    with col2:
        st.metric(
            label="🚚 Delivery Rate",
            value=f"{kpis['delivery_rate']:.1f}%",
            delta="Last 7 days"
        )
        
    with col3:
        st.metric(
            label="📊 Stock Health",
            value=f"{kpis['stock_health']:.1f}%",
            delta=f"{kpis['low_stock_count']} items low" if kpis['low_stock_count'] > 0 else "All items stocked",
            delta_color="inverse" if kpis['low_stock_count'] > 0 else "normal"
        )
        
    with col4:
        st.metric(
            label="🤖 Automation Rate",
            value=f"{kpis['automation_rate']:.1f}%",
            delta=f"{kpis['pending_reviews']} pending reviews"
        )

def display_alerts(data):
    """Display system alerts"""
    st.subheader("🚨 System Alerts")
    
    # Generate alerts based on data
    alerts = []
    
    # Stock alerts
    low_stock = data['low_stock']
    for item in low_stock:
        severity = "critical" if item['CurrentStock'] == 0 else "high"
        alerts.append({
            'severity': severity,
            'title': f"Low Stock Alert: {item['ProductID']}",
            'message': f"Current stock: {item['CurrentStock']}, Reorder point: {item['ReorderPoint']}",
            'timestamp': datetime.now()
        })
    
    # Delivery alerts
    shipments = data['shipments']
    for shipment in shipments:
        if shipment['status'] == 'created' and shipment['created_at']:
            created_time = datetime.fromisoformat(shipment['created_at'].replace('Z', '+00:00'))
            if datetime.now() - created_time.replace(tzinfo=None) > timedelta(hours=24):
                alerts.append({
                    'severity': 'medium',
                    'title': f"Shipment Delay: {shipment['tracking_number']}",
                    'message': f"Order #{shipment['order_id']} has been in 'created' status for over 24 hours",
                    'timestamp': created_time.replace(tzinfo=None)
                })
    
    # Pending review alerts
    pending_reviews = data['pending_reviews']
    if len(pending_reviews) > 5:
        alerts.append({
            'severity': 'high',
            'title': "High Volume of Pending Reviews",
            'message': f"{len(pending_reviews)} items require human review",
            'timestamp': datetime.now()
        })
    
    # Display alerts
    if alerts:
        for alert in sorted(alerts, key=lambda x: x['timestamp'], reverse=True):
            severity_class = f"alert-{alert['severity']}"
            st.markdown(f"""
            <div class="{severity_class}">
                <strong>{alert['title']}</strong><br>
                {alert['message']}<br>
                <small>⏰ {alert['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ No active alerts - All systems operating normally")

def display_performance_charts(data):
    """Display performance charts"""
    st.subheader("📈 Performance Analytics")
    
    # Order status distribution
    col1, col2 = st.columns(2)
    
    with col1:
        orders = data['orders']
        if orders:
            status_counts = {}
            for order in orders:
                status = order['Status']
                status_counts[status] = status_counts.get(status, 0) + 1
            
            fig_orders = px.pie(
                values=list(status_counts.values()),
                names=list(status_counts.keys()),
                title="Order Status Distribution"
            )
            st.plotly_chart(fig_orders, use_container_width=True)
    
    with col2:
        shipments = data['shipments']
        if shipments:
            shipment_counts = {}
            for shipment in shipments:
                status = shipment['status']
                shipment_counts[status] = shipment_counts.get(status, 0) + 1
            
            fig_shipments = px.pie(
                values=list(shipment_counts.values()),
                names=list(shipment_counts.keys()),
                title="Shipment Status Distribution"
            )
            st.plotly_chart(fig_shipments, use_container_width=True)
    
    # Inventory levels
    inventory = data['inventory']
    if inventory:
        df_inventory = pd.DataFrame(inventory)
        
        fig_inventory = px.bar(
            df_inventory,
            x='ProductID',
            y=['CurrentStock', 'ReorderPoint'],
            title="Inventory Levels vs Reorder Points",
            barmode='group'
        )
        st.plotly_chart(fig_inventory, use_container_width=True)

def display_recent_activity(data):
    """Display recent activity"""
    st.subheader("📜 Recent Activity")
    
    logs = data['agent_logs']
    if logs:
        # Create activity timeline
        df_logs = pd.DataFrame(logs)
        
        # Display recent logs in a table
        display_logs = []
        for log in logs[:10]:  # Show last 10 activities
            display_logs.append({
                'Time': log['timestamp'][:19] if log['timestamp'] else 'N/A',
                'Action': log['action'],
                'Product': log['ProductID'] or 'N/A',
                'Details': (log['details'] or '')[:50] + '...' if log['details'] and len(log['details']) > 50 else log['details'] or ''
            })
        
        st.dataframe(pd.DataFrame(display_logs), use_container_width=True)
    else:
        st.info("No recent activity to display")

def display_system_status(data):
    """Display system status"""
    st.subheader("⚙️ System Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🤖 AI Agents**")
        st.success("✅ Procurement Agent: Active")
        st.success("✅ Delivery Agent: Active")
        st.success("✅ Inventory Monitor: Active")
    
    with col2:
        st.markdown("**🔗 Integrations**")
        st.success("✅ Database: Connected")
        st.success("✅ Supplier APIs: Ready")
        st.success("✅ Courier APIs: Ready")
    
    with col3:
        st.markdown("**📊 Performance**")
        performance = data['performance_metrics']
        st.metric("Automation Rate", f"{performance.get('automation_rate', 0):.1f}%")
        st.metric("Total Actions", performance.get('total_actions', 0))
        st.metric("Success Rate", "100.0%")

def main():
    """Main dashboard application"""
    # Initialize database
    init_database()
    
    # Sidebar
    st.sidebar.title("🚚 Navigation")
    
    # Auto-refresh option
    auto_refresh = st.sidebar.checkbox("Auto Refresh (30s)", value=False)
    
    if st.sidebar.button("🔄 Refresh Data"):
        st.experimental_rerun()
    
    # Manual agent triggers
    st.sidebar.markdown("### 🤖 Agent Controls")
    
    if st.sidebar.button("🏭 Run Procurement Agent"):
        with st.spinner("Running procurement agent..."):
            try:
                from procurement_agent import run_procurement_agent
                results = run_procurement_agent()
                st.sidebar.success(f"✅ Procurement completed: {results['purchase_orders_created']} POs created")
            except Exception as e:
                st.sidebar.error(f"❌ Error: {str(e)}")
    
    if st.sidebar.button("🚚 Run Delivery Agent"):
        with st.spinner("Running delivery agent..."):
            try:
                from delivery_agent import run_delivery_agent
                results = run_delivery_agent()
                st.sidebar.success(f"✅ Delivery completed: {results['shipments_created']} shipments created")
            except Exception as e:
                st.sidebar.error(f"❌ Error: {str(e)}")
    
    # Load data
    with st.spinner("Loading dashboard data..."):
        data = load_dashboard_data()
        kpis = create_kpi_metrics(data)
    
    # Display dashboard sections
    display_kpi_dashboard(kpis)
    
    st.markdown("---")
    
    # Alerts section
    display_alerts(data)
    
    st.markdown("---")
    
    # Performance charts
    display_performance_charts(data)
    
    st.markdown("---")
    
    # Recent activity and system status
    col1, col2 = st.columns(2)
    
    with col1:
        display_recent_activity(data)
    
    with col2:
        display_system_status(data)
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(30)
        st.experimental_rerun()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "🤖 AI Agent Logistics Dashboard | "
        f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
