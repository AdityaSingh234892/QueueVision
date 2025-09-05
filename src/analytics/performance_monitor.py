"""
Performance Monitor Module
Tracks cashier performance, service times, and system metrics
"""

import time
import json
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict, deque
import os

class CashierPerformance:
    """Individual cashier performance tracking"""
    
    def __init__(self, cashier_id):
        self.cashier_id = cashier_id
        self.shift_start = time.time()
        self.total_customers_served = 0
        self.total_service_time = 0
        self.service_times = deque(maxlen=100)
        self.break_times = []
        self.current_break_start = None
        self.performance_score = 1.0
        self.efficiency_trend = deque(maxlen=20)
        
    def add_service_time(self, service_time):
        """Add a service time record"""
        self.service_times.append(service_time)
        self.total_service_time += service_time
        self.total_customers_served += 1
        self.calculate_performance_score()
    
    def start_break(self):
        """Mark start of break"""
        self.current_break_start = time.time()
    
    def end_break(self):
        """Mark end of break"""
        if self.current_break_start:
            break_duration = time.time() - self.current_break_start
            self.break_times.append({
                'start': self.current_break_start,
                'duration': break_duration
            })
            self.current_break_start = None
    
    def calculate_performance_score(self):
        """Calculate performance score based on service times"""
        if not self.service_times:
            return
        
        avg_service_time = sum(self.service_times) / len(self.service_times)
        target_time = 120  # 2 minutes target
        
        # Score based on how close to target time
        if avg_service_time <= target_time:
            score = 1.0
        else:
            score = max(0.1, target_time / avg_service_time)
        
        self.performance_score = score
        self.efficiency_trend.append(score)
    
    def get_efficiency_trend(self):
        """Get efficiency trend over time"""
        if len(self.efficiency_trend) < 2:
            return "stable"
        
        recent_avg = sum(list(self.efficiency_trend)[-5:]) / min(5, len(self.efficiency_trend))
        older_avg = sum(list(self.efficiency_trend)[:-5]) / max(1, len(self.efficiency_trend) - 5)
        
        if recent_avg > older_avg * 1.1:
            return "improving"
        elif recent_avg < older_avg * 0.9:
            return "declining"
        else:
            return "stable"
    
    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            'cashier_id': self.cashier_id,
            'shift_start': self.shift_start,
            'total_customers_served': self.total_customers_served,
            'average_service_time': sum(self.service_times) / len(self.service_times) if self.service_times else 0,
            'performance_score': self.performance_score,
            'efficiency_trend': self.get_efficiency_trend(),
            'break_count': len(self.break_times),
            'total_break_time': sum(b['duration'] for b in self.break_times),
            'on_break': self.current_break_start is not None
        }

class PerformanceMonitor:
    """Main performance monitoring class"""
    
    def __init__(self, config):
        self.config = config
        self.performance_config = config["performance"]
        
        # Cashier tracking
        self.cashiers = {}
        self.queue_cashier_mapping = {}
        
        # System metrics
        self.system_metrics = {
            'total_customers_processed': 0,
            'total_service_time': 0,
            'peak_queue_length': 0,
            'system_uptime': time.time(),
            'fps': 0,
            'detection_accuracy': 0
        }
        
        # Performance history
        self.hourly_performance = defaultdict(list)
        self.daily_performance = defaultdict(list)
        
        # Alert thresholds
        self.target_service_time = self.performance_config.get("target_service_time", 120)
        self.performance_threshold = self.performance_config.get("performance_threshold", 0.8)
        self.alert_delay = self.performance_config.get("alert_delay", 5)
        
        # Alert tracking
        self.alert_history = deque(maxlen=1000)
        self.last_alert_time = defaultdict(float)
        
        # Data storage
        self.data_dir = "data/performance"
        os.makedirs(self.data_dir, exist_ok=True)
        
        print("Performance Monitor initialized")
    
    def update_metrics(self):
        """Update performance metrics"""
        current_time = time.time()
        hour = datetime.now().hour
        
        # Update system uptime
        uptime = current_time - self.system_metrics['system_uptime']
        
        # Calculate system-wide averages
        total_service_time = 0
        total_customers = 0
        active_cashiers = 0
        
        for cashier in self.cashiers.values():
            if cashier.service_times:
                total_service_time += sum(cashier.service_times)
                total_customers += len(cashier.service_times)
                active_cashiers += 1
        
        # Update system metrics
        if total_customers > 0:
            self.system_metrics['average_service_time'] = total_service_time / total_customers
        
        self.system_metrics['active_cashiers'] = active_cashiers
        self.system_metrics['uptime_hours'] = uptime / 3600
        
        # Store hourly performance
        self.hourly_performance[hour].append({
            'timestamp': current_time,
            'customers_served': total_customers,
            'average_service_time': self.system_metrics.get('average_service_time', 0),
            'active_cashiers': active_cashiers
        })
    
    def update_frame_data(self, queue_data, detections):
        """Update metrics based on frame data"""
        # Update peak queue length
        total_queue_length = sum(q.get('queue_length', 0) for q in queue_data.values())
        self.system_metrics['peak_queue_length'] = max(
            self.system_metrics['peak_queue_length'], 
            total_queue_length
        )
        
        # Update detection count
        self.system_metrics['current_detections'] = len(detections)
        
        # Update cashier assignments
        for queue_id, queue_info in queue_data.items():
            cashier_id = queue_info.get('cashier_id')
            if cashier_id and cashier_id not in self.cashiers:
                self.cashiers[cashier_id] = CashierPerformance(cashier_id)
            
            # Update service times if customer completed service
            if queue_info.get('current_customer'):
                current_customer = queue_info['current_customer']
                if (current_customer.get('status') == 'served' and 
                    current_customer.get('service_time', 0) > 0):
                    
                    if cashier_id and cashier_id in self.cashiers:
                        self.cashiers[cashier_id].add_service_time(
                            current_customer['service_time']
                        )
    
    def check_alerts(self):
        """Check for performance alerts"""
        alerts = []
        current_time = time.time()
        
        # Check cashier performance
        for cashier_id, cashier in self.cashiers.items():
            if cashier.performance_score < self.performance_threshold:
                alert_key = f"cashier_performance_{cashier_id}"
                if current_time - self.last_alert_time[alert_key] > self.alert_delay * 60:
                    alerts.append({
                        'type': 'cashier_performance',
                        'message': f'Cashier {cashier_id} performance below threshold ({cashier.performance_score:.1%})',
                        'priority': 'medium',
                        'cashier_id': cashier_id
                    })
                    self.last_alert_time[alert_key] = current_time
            
            # Check for long service times
            if cashier.service_times:
                recent_avg = sum(list(cashier.service_times)[-5:]) / min(5, len(cashier.service_times))
                if recent_avg > self.target_service_time * 1.5:
                    alert_key = f"slow_service_{cashier_id}"
                    if current_time - self.last_alert_time[alert_key] > self.alert_delay * 60:
                        alerts.append({
                            'type': 'slow_service',
                            'message': f'Cashier {cashier_id} service time too high ({recent_avg:.0f}s)',
                            'priority': 'high',
                            'cashier_id': cashier_id
                        })
                        self.last_alert_time[alert_key] = current_time
        
        # Check system performance
        if len(self.cashiers) > 0:
            avg_system_performance = sum(c.performance_score for c in self.cashiers.values()) / len(self.cashiers)
            if avg_system_performance < self.performance_threshold:
                alert_key = "system_performance"
                if current_time - self.last_alert_time[alert_key] > self.alert_delay * 60:
                    alerts.append({
                        'type': 'system_performance',
                        'message': f'Overall system performance low ({avg_system_performance:.1%})',
                        'priority': 'high'
                    })
                    self.last_alert_time[alert_key] = current_time
        
        # Store alerts in history
        for alert in alerts:
            alert['timestamp'] = current_time
            self.alert_history.append(alert)
        
        return alerts
    
    def get_current_metrics(self):
        """Get current performance metrics"""
        metrics = self.system_metrics.copy()
        
        # Add cashier metrics
        if self.cashiers:
            cashier_scores = [c.performance_score for c in self.cashiers.values()]
            metrics['average_cashier_performance'] = sum(cashier_scores) / len(cashier_scores)
            metrics['total_cashiers'] = len(self.cashiers)
            
            # Calculate service time statistics
            all_service_times = []
            for cashier in self.cashiers.values():
                all_service_times.extend(cashier.service_times)
            
            if all_service_times:
                metrics['min_service_time'] = min(all_service_times)
                metrics['max_service_time'] = max(all_service_times)
                metrics['median_service_time'] = np.median(all_service_times)
                metrics['std_service_time'] = np.std(all_service_times)
        else:
            metrics['average_cashier_performance'] = 0
            metrics['total_cashiers'] = 0
        
        # Calculate efficiency metrics
        total_customers = sum(c.total_customers_served for c in self.cashiers.values())
        uptime_hours = (time.time() - metrics['system_uptime']) / 3600
        
        if uptime_hours > 0:
            metrics['customers_per_hour'] = total_customers / uptime_hours
        else:
            metrics['customers_per_hour'] = 0
        
        metrics['total_customers_served'] = total_customers
        metrics['queue_efficiency'] = min(1.0, total_customers / max(1, total_customers + metrics.get('total_customers_waiting', 0)))
        
        return metrics
    
    def get_cashier_rankings(self):
        """Get cashier performance rankings"""
        rankings = []
        
        for cashier in self.cashiers.values():
            if cashier.total_customers_served > 0:
                avg_service_time = sum(cashier.service_times) / len(cashier.service_times)
                rankings.append({
                    'cashier_id': cashier.cashier_id,
                    'customers_served': cashier.total_customers_served,
                    'average_service_time': avg_service_time,
                    'performance_score': cashier.performance_score,
                    'efficiency_trend': cashier.get_efficiency_trend()
                })
        
        # Sort by performance score (highest first)
        rankings.sort(key=lambda x: x['performance_score'], reverse=True)
        
        return rankings
    
    def get_hourly_trends(self):
        """Get hourly performance trends"""
        trends = {}
        
        for hour, data_points in self.hourly_performance.items():
            if data_points:
                avg_customers = sum(d['customers_served'] for d in data_points) / len(data_points)
                avg_service_time = sum(d['average_service_time'] for d in data_points) / len(data_points)
                
                trends[hour] = {
                    'average_customers_served': avg_customers,
                    'average_service_time': avg_service_time,
                    'data_points': len(data_points)
                }
        
        return trends
    
    def generate_performance_report(self):
        """Generate comprehensive performance report"""
        current_metrics = self.get_current_metrics()
        cashier_rankings = self.get_cashier_rankings()
        hourly_trends = self.get_hourly_trends()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_metrics': current_metrics,
            'cashier_performance': {
                'rankings': cashier_rankings,
                'total_cashiers': len(self.cashiers),
                'average_performance': current_metrics.get('average_cashier_performance', 0)
            },
            'trends': {
                'hourly': hourly_trends
            },
            'alerts': {
                'recent_alerts': list(self.alert_history)[-10:],
                'total_alerts': len(self.alert_history)
            },
            'recommendations': self.generate_recommendations()
        }
        
        return report
    
    def generate_recommendations(self):
        """Generate performance improvement recommendations"""
        recommendations = []
        current_metrics = self.get_current_metrics()
        
        # Check overall performance
        avg_performance = current_metrics.get('average_cashier_performance', 0)
        if avg_performance < 0.8:
            recommendations.append({
                'type': 'training',
                'message': 'Consider additional training for cashiers to improve service speed',
                'priority': 'high'
            })
        
        # Check service time variance
        if current_metrics.get('std_service_time', 0) > 60:
            recommendations.append({
                'type': 'standardization',
                'message': 'High variance in service times. Consider standardizing checkout procedures',
                'priority': 'medium'
            })
        
        # Check queue efficiency
        if current_metrics.get('queue_efficiency', 0) < 0.7:
            recommendations.append({
                'type': 'staffing',
                'message': 'Low queue efficiency. Consider adjusting staffing levels',
                'priority': 'high'
            })
        
        # Individual cashier recommendations
        for cashier in self.cashiers.values():
            if cashier.performance_score < 0.6:
                recommendations.append({
                    'type': 'individual_coaching',
                    'message': f'Cashier {cashier.cashier_id} needs individual coaching',
                    'priority': 'medium',
                    'cashier_id': cashier.cashier_id
                })
        
        return recommendations
    
    def save_performance_data(self):
        """Save performance data to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.data_dir, f"performance_{timestamp}.json")
        
        data = self.generate_performance_report()
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def reset_metrics(self):
        """Reset all performance metrics"""
        self.cashiers.clear()
        self.queue_cashier_mapping.clear()
        self.system_metrics = {
            'total_customers_processed': 0,
            'total_service_time': 0,
            'peak_queue_length': 0,
            'system_uptime': time.time(),
            'fps': 0,
            'detection_accuracy': 0
        }
        self.hourly_performance.clear()
        self.daily_performance.clear()
        self.alert_history.clear()
        self.last_alert_time.clear()
        
        print("Performance metrics reset")
    
    def assign_cashier_to_queue(self, cashier_id, queue_id):
        """Assign cashier to specific queue"""
        if cashier_id not in self.cashiers:
            self.cashiers[cashier_id] = CashierPerformance(cashier_id)
        
        self.queue_cashier_mapping[queue_id] = cashier_id
    
    def mark_cashier_break(self, cashier_id, break_type="start"):
        """Mark cashier break start/end"""
        if cashier_id in self.cashiers:
            if break_type == "start":
                self.cashiers[cashier_id].start_break()
            elif break_type == "end":
                self.cashiers[cashier_id].end_break()
