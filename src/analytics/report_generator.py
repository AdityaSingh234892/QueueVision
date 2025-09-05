"""
Report Generator Module
Generates comprehensive reports and analytics for queue management
"""

import json
import os
import time
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict

# Import matplotlib with backend configuration for headless operation
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt

# Try to import additional packages, but continue without them if not available
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    print("Warning: pandas not available, some report features disabled")

try:
    import seaborn as sns
    HAS_SEABORN = True
except ImportError:
    HAS_SEABORN = False
    print("Warning: seaborn not available, advanced plotting disabled")

class ReportGenerator:
    """Report generation and analytics class"""
    
    def __init__(self, config):
        self.config = config
        self.analytics_config = config["analytics"]
        
        # Report settings
        self.save_interval = self.analytics_config.get("save_interval", 60)
        self.report_generation = self.analytics_config.get("report_generation", True)
        self.data_retention_days = self.analytics_config.get("data_retention_days", 30)
        
        # Data directories
        self.reports_dir = "data/reports"
        self.charts_dir = "data/charts"
        self.data_dir = "data"
        
        for directory in [self.reports_dir, self.charts_dir, self.data_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Data collection
        self.historical_data = []
        self.load_historical_data()
        
        print("Report Generator initialized")
    
    def load_historical_data(self):
        """Load historical data from saved files"""
        try:
            # Load queue data files
            queue_files = [f for f in os.listdir(self.data_dir) if f.startswith('queue_data_')]
            performance_files = [f for f in os.listdir("data/performance") if f.startswith('performance_')]
            
            for filename in queue_files[-50:]:  # Load last 50 files
                filepath = os.path.join(self.data_dir, filename)
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    data['data_type'] = 'queue'
                    self.historical_data.append(data)
            
            print(f"Loaded {len(self.historical_data)} historical data points")
            
        except Exception as e:
            print(f"Error loading historical data: {e}")
    
    def generate_hourly_report(self):
        """Generate hourly performance report"""
        if not self.report_generation:
            return
        
        current_hour = datetime.now().hour
        timestamp = datetime.now().strftime("%Y%m%d_%H")
        
        try:
            # Collect hourly data
            hourly_data = self.collect_hourly_data()
            
            # Generate report
            report = {
                'report_type': 'hourly',
                'timestamp': datetime.now().isoformat(),
                'hour': current_hour,
                'summary': self.generate_hourly_summary(hourly_data),
                'queue_performance': self.analyze_queue_performance(hourly_data),
                'cashier_performance': self.analyze_cashier_performance(hourly_data),
                'customer_flow': self.analyze_customer_flow(hourly_data),
                'recommendations': self.generate_hourly_recommendations(hourly_data)
            }
            
            # Save report
            filename = os.path.join(self.reports_dir, f"hourly_report_{timestamp}.json")
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            
            # Generate charts
            self.generate_hourly_charts(hourly_data, timestamp)
            
            print(f"Hourly report generated: {filename}")
            
        except Exception as e:
            print(f"Error generating hourly report: {e}")
    
    def generate_daily_report(self):
        """Generate daily performance report"""
        timestamp = datetime.now().strftime("%Y%m%d")
        
        try:
            # Collect daily data
            daily_data = self.collect_daily_data()
            
            # Generate comprehensive report
            report = {
                'report_type': 'daily',
                'timestamp': datetime.now().isoformat(),
                'date': datetime.now().strftime("%Y-%m-%d"),
                'executive_summary': self.generate_executive_summary(daily_data),
                'detailed_analysis': {
                    'queue_metrics': self.analyze_daily_queue_metrics(daily_data),
                    'performance_metrics': self.analyze_daily_performance_metrics(daily_data),
                    'customer_satisfaction': self.analyze_customer_satisfaction(daily_data),
                    'operational_efficiency': self.analyze_operational_efficiency(daily_data)
                },
                'trends': self.analyze_daily_trends(daily_data),
                'alerts_summary': self.summarize_daily_alerts(daily_data),
                'recommendations': self.generate_daily_recommendations(daily_data),
                'action_items': self.generate_action_items(daily_data)
            }
            
            # Save report
            filename = os.path.join(self.reports_dir, f"daily_report_{timestamp}.json")
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            
            # Generate comprehensive charts
            self.generate_daily_charts(daily_data, timestamp)
            
            # Generate PDF report if possible
            self.generate_pdf_report(report, timestamp)
            
            print(f"Daily report generated: {filename}")
            
        except Exception as e:
            print(f"Error generating daily report: {e}")
    
    def generate_manual_report(self):
        """Generate manual report on demand"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # Collect recent data
            recent_data = self.collect_recent_data(hours=4)
            
            # Generate manual report
            report = {
                'report_type': 'manual',
                'timestamp': datetime.now().isoformat(),
                'data_period': '4 hours',
                'current_status': self.get_current_system_status(),
                'performance_snapshot': self.get_performance_snapshot(recent_data),
                'queue_analysis': self.get_queue_analysis_snapshot(recent_data),
                'immediate_recommendations': self.get_immediate_recommendations(recent_data)
            }
            
            # Save report
            filename = os.path.join(self.reports_dir, f"manual_report_{timestamp}.json")
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"Manual report generated: {filename}")
            return filename
            
        except Exception as e:
            print(f"Error generating manual report: {e}")
            return None
    
    def generate_final_report(self):
        """Generate final system report on shutdown"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # Collect all session data
            session_data = self.collect_session_data()
            
            # Generate final report
            report = {
                'report_type': 'final',
                'timestamp': datetime.now().isoformat(),
                'session_summary': self.generate_session_summary(session_data),
                'total_metrics': self.calculate_total_metrics(session_data),
                'performance_analysis': self.analyze_session_performance(session_data),
                'efficiency_report': self.generate_efficiency_report(session_data),
                'recommendations': self.generate_final_recommendations(session_data)
            }
            
            # Save report
            filename = os.path.join(self.reports_dir, f"final_report_{timestamp}.json")
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"Final report generated: {filename}")
            
        except Exception as e:
            print(f"Error generating final report: {e}")
    
    def collect_hourly_data(self):
        """Collect data for hourly reporting"""
        current_time = time.time()
        hour_ago = current_time - 3600
        
        hourly_data = []
        for data_point in self.historical_data:
            data_timestamp = data_point.get('timestamp')
            if data_timestamp and self.parse_timestamp(data_timestamp) >= hour_ago:
                hourly_data.append(data_point)
        
        return hourly_data
    
    def collect_daily_data(self):
        """Collect data for daily reporting"""
        current_time = time.time()
        day_ago = current_time - 86400  # 24 hours
        
        daily_data = []
        for data_point in self.historical_data:
            data_timestamp = data_point.get('timestamp')
            if data_timestamp and self.parse_timestamp(data_timestamp) >= day_ago:
                daily_data.append(data_point)
        
        return daily_data
    
    def collect_recent_data(self, hours=4):
        """Collect recent data for specified hours"""
        current_time = time.time()
        cutoff_time = current_time - (hours * 3600)
        
        recent_data = []
        for data_point in self.historical_data:
            data_timestamp = data_point.get('timestamp')
            if data_timestamp and self.parse_timestamp(data_timestamp) >= cutoff_time:
                recent_data.append(data_point)
        
        return recent_data
    
    def generate_hourly_summary(self, hourly_data):
        """Generate hourly summary statistics"""
        if not hourly_data:
            return {'message': 'No data available for hourly summary'}
        
        # Extract metrics from hourly data
        total_customers = 0
        total_service_time = 0
        total_wait_time = 0
        queue_lengths = []
        
        for data_point in hourly_data:
            if 'performance_metrics' in data_point:
                metrics = data_point['performance_metrics']
                total_customers += metrics.get('total_customers_served', 0)
                
            if 'queues' in data_point:
                for queue_info in data_point['queues'].values():
                    queue_lengths.append(queue_info.get('queue_length', 0))
                    if queue_info.get('average_service_time', 0) > 0:
                        total_service_time += queue_info['average_service_time']
                    if queue_info.get('average_wait_time', 0) > 0:
                        total_wait_time += queue_info['average_wait_time']
        
        return {
            'total_customers_served': total_customers,
            'average_service_time': total_service_time / max(1, len(hourly_data)),
            'average_wait_time': total_wait_time / max(1, len(hourly_data)),
            'peak_queue_length': max(queue_lengths) if queue_lengths else 0,
            'average_queue_length': sum(queue_lengths) / len(queue_lengths) if queue_lengths else 0,
            'data_points': len(hourly_data)
        }
    
    def analyze_queue_performance(self, data):
        """Analyze queue performance metrics"""
        queue_metrics = defaultdict(list)
        
        for data_point in data:
            if 'queues' in data_point:
                for queue_id, queue_info in data_point['queues'].items():
                    queue_metrics[queue_id].append({
                        'length': queue_info.get('queue_length', 0),
                        'wait_time': queue_info.get('estimated_wait_time', 0),
                        'service_time': queue_info.get('average_service_time', 0),
                        'customers_served': queue_info.get('total_customers_served', 0)
                    })
        
        analysis = {}
        for queue_id, metrics in queue_metrics.items():
            if metrics:
                analysis[queue_id] = {
                    'average_length': sum(m['length'] for m in metrics) / len(metrics),
                    'average_wait_time': sum(m['wait_time'] for m in metrics) / len(metrics),
                    'average_service_time': sum(m['service_time'] for m in metrics) / len(metrics),
                    'total_customers_served': sum(m['customers_served'] for m in metrics),
                    'efficiency_score': self.calculate_queue_efficiency(metrics)
                }
        
        return analysis
    
    def generate_hourly_charts(self, hourly_data, timestamp):
        """Generate charts for hourly data"""
        try:
            # Set up plotting style
            if HAS_SEABORN:
                plt.style.use('seaborn-v0_8')
            else:
                plt.style.use('default')
            
            # Create figure with subplots
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle(f'Hourly Performance Report - {timestamp}', fontsize=16)
            
            # Chart 1: Queue lengths over time
            self.plot_queue_lengths_over_time(hourly_data, axes[0, 0])
            
            # Chart 2: Service time distribution
            self.plot_service_time_distribution(hourly_data, axes[0, 1])
            
            # Chart 3: Customer flow
            self.plot_customer_flow(hourly_data, axes[1, 0])
            
            # Chart 4: Performance metrics
            self.plot_performance_metrics(hourly_data, axes[1, 1])
            
            plt.tight_layout()
            chart_filename = os.path.join(self.charts_dir, f"hourly_chart_{timestamp}.png")
            plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"Hourly chart generated: {chart_filename}")
            
        except Exception as e:
            print(f"Error generating hourly charts: {e}")
    
    def generate_daily_charts(self, daily_data, timestamp):
        """Generate comprehensive daily charts"""
        try:
            # Create multiple chart files for different aspects
            
            # Performance overview chart
            self.create_performance_overview_chart(daily_data, timestamp)
            
            # Queue analysis chart
            self.create_queue_analysis_chart(daily_data, timestamp)
            
            # Trend analysis chart
            self.create_trend_analysis_chart(daily_data, timestamp)
            
            # Efficiency dashboard
            self.create_efficiency_dashboard(daily_data, timestamp)
            
        except Exception as e:
            print(f"Error generating daily charts: {e}")
    
    def create_performance_overview_chart(self, data, timestamp):
        """Create performance overview chart"""
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle(f'Daily Performance Overview - {timestamp}', fontsize=16)
        
        # Extract time series data
        timestamps = []
        customers_served = []
        service_times = []
        queue_lengths = []
        
        for data_point in data:
            if 'timestamp' in data_point:
                timestamps.append(self.parse_timestamp(data_point['timestamp']))
            
            if 'performance_metrics' in data_point:
                metrics = data_point['performance_metrics']
                customers_served.append(metrics.get('total_customers_served', 0))
            
            if 'queues' in data_point:
                avg_service_time = 0
                total_queue_length = 0
                queue_count = 0
                
                for queue_info in data_point['queues'].values():
                    if queue_info.get('average_service_time', 0) > 0:
                        avg_service_time += queue_info['average_service_time']
                        queue_count += 1
                    total_queue_length += queue_info.get('queue_length', 0)
                
                if queue_count > 0:
                    service_times.append(avg_service_time / queue_count)
                else:
                    service_times.append(0)
                
                queue_lengths.append(total_queue_length)
        
        # Plot charts
        if timestamps and customers_served:
            axes[0, 0].plot(timestamps, customers_served)
            axes[0, 0].set_title('Customers Served Over Time')
            axes[0, 0].set_ylabel('Customers')
        
        if timestamps and service_times:
            axes[0, 1].plot(timestamps, service_times)
            axes[0, 1].set_title('Average Service Time')
            axes[0, 1].set_ylabel('Seconds')
        
        if timestamps and queue_lengths:
            axes[0, 2].plot(timestamps, queue_lengths)
            axes[0, 2].set_title('Total Queue Length')
            axes[0, 2].set_ylabel('Customers')
        
        # Add distribution plots
        if service_times:
            axes[1, 0].hist(service_times, bins=20, alpha=0.7)
            axes[1, 0].set_title('Service Time Distribution')
        
        if queue_lengths:
            axes[1, 1].hist(queue_lengths, bins=15, alpha=0.7)
            axes[1, 1].set_title('Queue Length Distribution')
        
        # Performance score over time
        performance_scores = self.calculate_hourly_performance_scores(data)
        if performance_scores:
            axes[1, 2].plot(range(len(performance_scores)), performance_scores)
            axes[1, 2].set_title('Performance Score Over Time')
            axes[1, 2].set_ylabel('Score')
        
        plt.tight_layout()
        chart_filename = os.path.join(self.charts_dir, f"daily_performance_{timestamp}.png")
        plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
        plt.close()
    
    def parse_timestamp(self, timestamp_str):
        """Parse timestamp string to float"""
        try:
            if isinstance(timestamp_str, str):
                # Try to parse ISO format
                dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                return dt.timestamp()
            else:
                return float(timestamp_str)
        except:
            return time.time()
    
    def calculate_queue_efficiency(self, metrics):
        """Calculate queue efficiency score"""
        if not metrics:
            return 0
        
        # Calculate efficiency based on wait time and service time
        avg_wait = sum(m['wait_time'] for m in metrics) / len(metrics)
        avg_service = sum(m['service_time'] for m in metrics) / len(metrics)
        
        if avg_service == 0:
            return 0
        
        # Efficiency is better when wait time is low relative to service time
        efficiency = max(0, 1 - (avg_wait / (avg_service * 3)))  # Target: wait time < 3x service time
        return min(1, efficiency)
    
    def calculate_hourly_performance_scores(self, data):
        """Calculate performance scores by hour"""
        hourly_scores = {}
        
        for data_point in data:
            if 'timestamp' in data_point:
                timestamp = self.parse_timestamp(data_point['timestamp'])
                hour = datetime.fromtimestamp(timestamp).hour
                
                # Calculate performance score for this data point
                score = self.calculate_data_point_performance_score(data_point)
                
                if hour not in hourly_scores:
                    hourly_scores[hour] = []
                hourly_scores[hour].append(score)
        
        # Average scores by hour
        avg_scores = []
        for hour in sorted(hourly_scores.keys()):
            avg_score = sum(hourly_scores[hour]) / len(hourly_scores[hour])
            avg_scores.append(avg_score)
        
        return avg_scores
    
    def calculate_data_point_performance_score(self, data_point):
        """Calculate performance score for a single data point"""
        score = 0.5  # Default neutral score
        
        if 'performance_metrics' in data_point:
            metrics = data_point['performance_metrics']
            efficiency = metrics.get('queue_efficiency', 0.5)
            score = efficiency
        
        return score
    
    def plot_queue_lengths_over_time(self, data, ax):
        """Plot queue lengths over time"""
        # Implementation for queue length plotting
        ax.set_title('Queue Lengths Over Time')
        ax.set_xlabel('Time')
        ax.set_ylabel('Queue Length')
    
    def plot_service_time_distribution(self, data, ax):
        """Plot service time distribution"""
        # Implementation for service time distribution
        ax.set_title('Service Time Distribution')
        ax.set_xlabel('Service Time (seconds)')
        ax.set_ylabel('Frequency')
    
    def plot_customer_flow(self, data, ax):
        """Plot customer flow"""
        # Implementation for customer flow plotting
        ax.set_title('Customer Flow')
        ax.set_xlabel('Time')
        ax.set_ylabel('Customers/Hour')
    
    def plot_performance_metrics(self, data, ax):
        """Plot performance metrics"""
        # Implementation for performance metrics plotting
        ax.set_title('Performance Metrics')
        ax.set_xlabel('Metric')
        ax.set_ylabel('Value')
    
    def get_current_system_status(self):
        """Get current system status snapshot"""
        return {
            'timestamp': datetime.now().isoformat(),
            'status': 'operational',
            'uptime': time.time(),
            'message': 'System running normally'
        }
    
    def get_performance_snapshot(self, data):
        """Get performance snapshot from recent data"""
        if not data:
            return {'message': 'No recent data available'}
        
        latest_data = data[-1] if data else {}
        return {
            'latest_metrics': latest_data.get('performance_metrics', {}),
            'data_freshness': 'current'
        }
    
    def get_queue_analysis_snapshot(self, data):
        """Get queue analysis snapshot"""
        return self.analyze_queue_performance(data)
    
    def get_immediate_recommendations(self, data):
        """Get immediate recommendations based on recent data"""
        recommendations = []
        
        if not data:
            recommendations.append({
                'type': 'system',
                'message': 'No recent data available for analysis',
                'priority': 'low'
            })
        
        return recommendations
    
    # Additional method stubs for comprehensive reporting
    def analyze_cashier_performance(self, data):
        """Analyze cashier performance from data"""
        return {'message': 'Cashier performance analysis'}
    
    def analyze_customer_flow(self, data):
        """Analyze customer flow patterns"""
        return {'message': 'Customer flow analysis'}
    
    def generate_hourly_recommendations(self, data):
        """Generate recommendations based on hourly data"""
        return []
    
    def collect_session_data(self):
        """Collect all session data"""
        return self.historical_data
    
    def generate_session_summary(self, data):
        """Generate session summary"""
        return {'message': 'Session summary'}
    
    def calculate_total_metrics(self, data):
        """Calculate total session metrics"""
        return {'message': 'Total metrics calculation'}
    
    def analyze_session_performance(self, data):
        """Analyze overall session performance"""
        return {'message': 'Session performance analysis'}
    
    def generate_efficiency_report(self, data):
        """Generate efficiency report"""
        return {'message': 'Efficiency report'}
    
    def generate_final_recommendations(self, data):
        """Generate final recommendations"""
        return []
