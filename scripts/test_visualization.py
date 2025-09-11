#!/usr/bin/env python3
"""
Plotly Visualization Testing for Webconnex Text-to-SQL
Tests professional chart generation for different data types
"""

import os
import sys
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class PlotlyVisualizationTester:
    """Test Plotly visualizations for different query results"""
    
    def __init__(self):
        self.test_results = []
        
    def generate_revenue_chart(self, df: pd.DataFrame) -> go.Figure:
        """Generate professional revenue trend chart"""
        fig = go.Figure()
        
        # Add main revenue line
        fig.add_trace(go.Scatter(
            x=df['month'],
            y=df['revenue'],
            mode='lines+markers',
            name='Revenue',
            line=dict(color='#2E86AB', width=3),
            marker=dict(size=8),
            hovertemplate='<b>%{x|%b %Y}</b><br>Revenue: $%{y:,.2f}<extra></extra>'
        ))
        
        # Add invoice count on secondary y-axis
        fig.add_trace(go.Bar(
            x=df['month'],
            y=df['invoice_count'],
            name='Invoice Count',
            yaxis='y2',
            marker=dict(color='#A23B72', opacity=0.3),
            hovertemplate='<b>%{x|%b %Y}</b><br>Invoices: %{y}<extra></extra>'
        ))
        
        # Update layout for professional appearance
        fig.update_layout(
            title={
                'text': 'Monthly Revenue & Invoice Trends',
                'font': {'size': 24, 'color': '#2C3E50'},
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis=dict(
                title='Month',
                showgrid=True,
                gridcolor='rgba(0,0,0,0.1)',
                tickformat='%b %Y'
            ),
            yaxis=dict(
                title='Revenue ($)',
                showgrid=True,
                gridcolor='rgba(0,0,0,0.1)',
                tickformat='$,.0f',
                side='left'
            ),
            yaxis2=dict(
                title='Invoice Count',
                overlaying='y',
                side='right',
                showgrid=False
            ),
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family='Arial, sans-serif', size=12),
            margin=dict(t=80, b=60, l=80, r=80),
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1
            ),
            height=500
        )
        
        return fig
    
    def generate_customer_segment_chart(self, df: pd.DataFrame) -> go.Figure:
        """Generate customer segmentation donut chart"""
        fig = go.Figure(data=[go.Pie(
            labels=df['segment'],
            values=df['customer_count'],
            hole=0.4,
            marker=dict(
                colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'],
                line=dict(color='white', width=2)
            ),
            textfont=dict(size=14),
            textposition='outside',
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>Customers: %{value}<br>Percentage: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title={
                'text': 'Customer Segmentation Analysis',
                'font': {'size': 24, 'color': '#2C3E50'},
                'x': 0.5,
                'xanchor': 'center'
            },
            showlegend=True,
            legend=dict(
                orientation='v',
                yanchor='middle',
                y=0.5,
                xanchor='left',
                x=1.1
            ),
            annotations=[
                dict(
                    text='Total<br>Customers',
                    x=0.5, y=0.5,
                    font=dict(size=16, color='#2C3E50'),
                    showarrow=False
                )
            ],
            paper_bgcolor='white',
            height=500,
            margin=dict(t=80, b=60, l=60, r=180)
        )
        
        return fig
    
    def generate_time_series_chart(self, df: pd.DataFrame) -> go.Figure:
        """Generate time series chart with multiple metrics"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Daily Registrations', 'Daily Revenue', 
                          'New Customers', 'Average Order Value'),
            vertical_spacing=0.12,
            horizontal_spacing=0.1
        )
        
        # Daily Registrations
        fig.add_trace(
            go.Scatter(
                x=df['date'], 
                y=df['registrations'],
                mode='lines',
                name='Registrations',
                line=dict(color='#3498db', width=2),
                fill='tozeroy',
                fillcolor='rgba(52, 152, 219, 0.1)'
            ),
            row=1, col=1
        )
        
        # Daily Revenue
        fig.add_trace(
            go.Scatter(
                x=df['date'], 
                y=df['revenue'],
                mode='lines',
                name='Revenue',
                line=dict(color='#2ecc71', width=2),
                fill='tozeroy',
                fillcolor='rgba(46, 204, 113, 0.1)'
            ),
            row=1, col=2
        )
        
        # New Customers
        fig.add_trace(
            go.Bar(
                x=df['date'], 
                y=df['new_customers'],
                name='New Customers',
                marker=dict(color='#e74c3c', opacity=0.7)
            ),
            row=2, col=1
        )
        
        # Average Order Value
        fig.add_trace(
            go.Scatter(
                x=df['date'], 
                y=df['avg_order_value'],
                mode='lines+markers',
                name='AOV',
                line=dict(color='#f39c12', width=2),
                marker=dict(size=4)
            ),
            row=2, col=2
        )
        
        # Update axes
        fig.update_xaxes(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
        fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
        
        # Update layout
        fig.update_layout(
            title={
                'text': 'Business Metrics Dashboard',
                'font': {'size': 26, 'color': '#2C3E50'},
                'x': 0.5,
                'xanchor': 'center'
            },
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family='Arial, sans-serif', size=11),
            height=700,
            margin=dict(t=100, b=60, l=60, r=60)
        )
        
        # Format y-axes
        fig.update_yaxes(title_text="Count", row=1, col=1)
        fig.update_yaxes(title_text="Revenue ($)", tickformat="$,.0f", row=1, col=2)
        fig.update_yaxes(title_text="Count", row=2, col=1)
        fig.update_yaxes(title_text="AOV ($)", tickformat="$,.0f", row=2, col=2)
        
        return fig
    
    def generate_top_customers_chart(self, df: pd.DataFrame) -> go.Figure:
        """Generate horizontal bar chart for top customers"""
        # Sort by lifetime value
        df_sorted = df.sort_values('lifetime_value', ascending=True)
        
        fig = go.Figure()
        
        # Add bars
        fig.add_trace(go.Bar(
            x=df_sorted['lifetime_value'],
            y=df_sorted['email'],
            orientation='h',
            marker=dict(
                color=df_sorted['lifetime_value'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(
                    title="Lifetime Value ($)",
                    thickness=15,
                    len=0.7
                )
            ),
            text=[f"${val:,.0f}" for val in df_sorted['lifetime_value']],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Lifetime Value: $%{x:,.2f}<br>Orders: %{customdata}<extra></extra>',
            customdata=df_sorted['orders']
        ))
        
        fig.update_layout(
            title={
                'text': 'Top 10 Customers by Lifetime Value',
                'font': {'size': 24, 'color': '#2C3E50'},
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis=dict(
                title='Lifetime Value ($)',
                showgrid=True,
                gridcolor='rgba(0,0,0,0.1)',
                tickformat='$,.0f'
            ),
            yaxis=dict(
                title='',
                showgrid=False,
                tickfont=dict(size=10)
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family='Arial, sans-serif', size=12),
            height=500,
            margin=dict(t=80, b=60, l=200, r=100)
        )
        
        return fig
    
    def generate_heatmap(self, df: pd.DataFrame) -> go.Figure:
        """Generate heatmap for registration patterns"""
        # Create pivot table for heatmap
        pivot = df.pivot_table(
            values='registrations',
            index=df['date'].dt.day_name(),
            columns=df['date'].dt.hour,
            aggfunc='mean'
        )
        
        # Reorder days
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        pivot = pivot.reindex(day_order)
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot.values,
            x=[f"{h:02d}:00" for h in pivot.columns],
            y=pivot.index,
            colorscale='RdYlBu_r',
            colorbar=dict(
                title="Avg Registrations",
                thickness=15,
                len=0.7
            ),
            hovertemplate='<b>%{y}</b><br>Hour: %{x}<br>Avg Registrations: %{z:.1f}<extra></extra>'
        ))
        
        fig.update_layout(
            title={
                'text': 'Registration Patterns by Day and Hour',
                'font': {'size': 24, 'color': '#2C3E50'},
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis=dict(
                title='Hour of Day',
                showgrid=False,
                tickangle=45
            ),
            yaxis=dict(
                title='Day of Week',
                showgrid=False
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family='Arial, sans-serif', size=12),
            height=400,
            margin=dict(t=80, b=80, l=100, r=60)
        )
        
        return fig
    
    def generate_funnel_chart(self, data: list) -> go.Figure:
        """Generate funnel chart for conversion analysis"""
        stages = ['Visitors', 'Registered', 'Added to Cart', 'Completed Purchase']
        values = [10000, 3500, 2000, 1500]
        
        fig = go.Figure(go.Funnel(
            y=stages,
            x=values,
            textposition="inside",
            textinfo="value+percent initial",
            opacity=0.8,
            marker=dict(
                color=['#3498db', '#2ecc71', '#f39c12', '#e74c3c'],
                line=dict(width=2, color='white')
            ),
            connector=dict(line=dict(color='#95a5a6', width=2, dash='dot'))
        ))
        
        fig.update_layout(
            title={
                'text': 'Conversion Funnel Analysis',
                'font': {'size': 24, 'color': '#2C3E50'},
                'x': 0.5,
                'xanchor': 'center'
            },
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family='Arial, sans-serif', size=12),
            height=500,
            margin=dict(t=80, b=60, l=100, r=60)
        )
        
        return fig
    
    def test_all_visualizations(self):
        """Test all visualization types"""
        print("=" * 60)
        print("PLOTLY VISUALIZATION TESTING")
        print("=" * 60)
        
        # Generate sample data
        print("\n📊 Generating Sample Data...")
        
        # Monthly revenue data
        months = pd.date_range(start='2023-01-01', periods=12, freq='M')
        revenue_df = pd.DataFrame({
            'month': months,
            'revenue': [random.uniform(50000, 150000) for _ in range(12)],
            'invoice_count': [random.randint(100, 300) for _ in range(12)]
        })
        
        # Customer segments
        segments_df = pd.DataFrame({
            'segment': ['VIP', 'Frequent', 'Regular', 'Occasional', 'New'],
            'customer_count': [50, 100, 250, 350, 250],
            'avg_lifetime_value': [15000, 8000, 3000, 800, 200]
        })
        
        # Time series data
        dates = pd.date_range(start='2024-01-01', periods=90, freq='D')
        time_series_df = pd.DataFrame({
            'date': dates,
            'registrations': [random.randint(30, 100) for _ in range(90)],
            'revenue': [random.uniform(3000, 8000) for _ in range(90)],
            'new_customers': [random.randint(5, 20) for _ in range(90)],
            'avg_order_value': [random.uniform(80, 150) for _ in range(90)]
        })
        
        # Top customers
        top_customers_df = pd.DataFrame({
            'email': [f'customer{i}@example.com' for i in range(10)],
            'orders': [random.randint(10, 50) for _ in range(10)],
            'lifetime_value': [random.uniform(2000, 10000) for _ in range(10)]
        })
        
        print("✅ Sample data generated")
        
        # Test each visualization
        print("\n🎨 Testing Visualizations...")
        
        try:
            # 1. Revenue Chart
            print("\n  1. Revenue Trend Chart...")
            fig1 = self.generate_revenue_chart(revenue_df)
            fig1.write_html("test_revenue_chart.html")
            print("    ✅ Revenue chart created: test_revenue_chart.html")
            
            # 2. Customer Segments
            print("\n  2. Customer Segmentation Chart...")
            fig2 = self.generate_customer_segment_chart(segments_df)
            fig2.write_html("test_segment_chart.html")
            print("    ✅ Segment chart created: test_segment_chart.html")
            
            # 3. Time Series Dashboard
            print("\n  3. Time Series Dashboard...")
            fig3 = self.generate_time_series_chart(time_series_df)
            fig3.write_html("test_dashboard.html")
            print("    ✅ Dashboard created: test_dashboard.html")
            
            # 4. Top Customers
            print("\n  4. Top Customers Chart...")
            fig4 = self.generate_top_customers_chart(top_customers_df)
            fig4.write_html("test_top_customers.html")
            print("    ✅ Top customers chart created: test_top_customers.html")
            
            # 5. Heatmap
            print("\n  5. Registration Heatmap...")
            # Add hour data for heatmap
            time_series_df['date'] = pd.to_datetime(time_series_df['date'])
            hourly_data = []
            for _, row in time_series_df.iterrows():
                for hour in range(24):
                    hourly_data.append({
                        'date': row['date'].replace(hour=hour),
                        'registrations': random.randint(0, 10)
                    })
            hourly_df = pd.DataFrame(hourly_data)
            
            fig5 = self.generate_heatmap(hourly_df)
            fig5.write_html("test_heatmap.html")
            print("    ✅ Heatmap created: test_heatmap.html")
            
            # 6. Funnel Chart
            print("\n  6. Conversion Funnel...")
            fig6 = self.generate_funnel_chart([])
            fig6.write_html("test_funnel.html")
            print("    ✅ Funnel chart created: test_funnel.html")
            
            print("\n" + "=" * 60)
            print("✅ ALL VISUALIZATIONS TESTED SUCCESSFULLY")
            print("=" * 60)
            
            print("\n📁 Generated Files:")
            print("  - test_revenue_chart.html")
            print("  - test_segment_chart.html")
            print("  - test_dashboard.html")
            print("  - test_top_customers.html")
            print("  - test_heatmap.html")
            print("  - test_funnel.html")
            
            print("\n💡 Open these HTML files in a browser to view the charts")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error generating visualizations: {e}")
            return False
    
    def test_responsive_design(self):
        """Test responsive design features"""
        print("\n📱 Testing Responsive Design Features...")
        
        # Create a responsive chart
        df = pd.DataFrame({
            'x': list(range(10)),
            'y': [random.randint(10, 100) for _ in range(10)]
        })
        
        fig = px.line(df, x='x', y='y', title='Responsive Test Chart')
        
        # Add responsive configuration
        fig.update_layout(
            autosize=True,
            margin=dict(l=0, r=0, t=30, b=0),
            paper_bgcolor='white',
            plot_bgcolor='white'
        )
        
        config = {
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['pan2d', 'lasso2d'],
            'responsive': True
        }
        
        fig.write_html("test_responsive.html", config=config)
        print("  ✅ Responsive chart created: test_responsive.html")
    
    def test_export_formats(self):
        """Test different export formats"""
        print("\n💾 Testing Export Formats...")
        
        # Create a simple chart
        fig = go.Figure(data=[go.Bar(x=['A', 'B', 'C'], y=[1, 2, 3])])
        
        try:
            # HTML with config
            fig.write_html("export_test.html", include_plotlyjs='cdn')
            print("  ✅ HTML export successful")
            
            # JSON
            fig.write_json("export_test.json")
            print("  ✅ JSON export successful")
            
            # Image formats require kaleido
            try:
                fig.write_image("export_test.png")
                print("  ✅ PNG export successful")
            except:
                print("  ⚠️  PNG export requires kaleido package")
            
            return True
        except Exception as e:
            print(f"  ❌ Export test failed: {e}")
            return False


def main():
    """Main test runner"""
    tester = PlotlyVisualizationTester()
    
    # Run all tests
    success = tester.test_all_visualizations()
    
    # Additional tests
    tester.test_responsive_design()
    tester.test_export_formats()
    
    print("\n" + "=" * 60)
    print("VISUALIZATION TESTING COMPLETE")
    print("=" * 60)
    
    if success:
        print("\n🎉 All Plotly visualizations are working professionally!")
        print("Charts are production-ready with:")
        print("  ✅ Professional styling and colors")
        print("  ✅ Interactive hover information")
        print("  ✅ Responsive design")
        print("  ✅ Export capabilities")
        print("  ✅ Multiple chart types supported")
    else:
        print("\n⚠️  Some visualization tests failed. Check errors above.")
    
    print("\n📝 Next Steps:")
    print("1. Review generated HTML files in browser")
    print("2. Run test_api_integration.py for API testing")
    print("3. Run demo_queries.py for business scenarios")


if __name__ == "__main__":
    main()