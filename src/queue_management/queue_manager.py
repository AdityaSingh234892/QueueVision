"""
Queue Management Module
Handles queue tracking, customer flow, and service time calculations
"""

import time
import json
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict, deque
import os

class Customer:
    """Individual customer tracking class"""
    
    def __init__(self, person_id, queue_id, entry_time=None):
        self.person_id = person_id
        self.queue_id = queue_id
        self.entry_time = entry_time or time.time()
        self.service_start_time = None
        self.service_end_time = None
        self.position = 0
        self.status = "waiting"  # waiting, current, served
        self.estimated_wait_time = 0
        self.actual_wait_time = 0
        self.service_time = 0
        self.customer_type = "regular"  # regular, express
    
    def start_service(self):
        """Mark customer as starting service"""
        self.service_start_time = time.time()
        self.actual_wait_time = self.service_start_time - self.entry_time
        self.status = "current"
    
    def complete_service(self):
        """Mark customer service as complete"""
        self.service_end_time = time.time()
        if self.service_start_time:
            self.service_time = self.service_end_time - self.service_start_time
        self.status = "served"
    
    def get_current_wait_time(self):
        """Get current wait time"""
        if self.service_start_time:
            return self.actual_wait_time
        return time.time() - self.entry_time
    
    def to_dict(self):
        """Convert customer to dictionary for serialization"""
        return {
            'person_id': self.person_id,
            'queue_id': self.queue_id,
            'entry_time': self.entry_time,
            'service_start_time': self.service_start_time,
            'service_end_time': self.service_end_time,
            'position': self.position,
            'status': self.status,
            'estimated_wait_time': self.estimated_wait_time,
            'actual_wait_time': self.actual_wait_time,
            'service_time': self.service_time,
            'customer_type': self.customer_type
        }

class Queue:
    """Individual queue tracking class"""
    
    def __init__(self, queue_id, queue_type="regular", position_coords=None):
        self.queue_id = queue_id
        self.queue_type = queue_type  # regular, express
        self.position_coords = position_coords or {}
        
        # Queue state
        self.customers = []
        self.current_customer = None
        self.served_customers = []
        
        # Performance metrics
        self.total_customers_served = 0
        self.average_service_time = 0
        self.average_wait_time = 0
        self.service_times = deque(maxlen=100)
        self.wait_times = deque(maxlen=100)
        
        # Cashier tracking
        self.cashier_id = None
        self.cashier_break_start = None
        self.cashier_performance = 1.0
        
        # Queue optimization
        self.optimal_length = 3
        self.max_wait_time = 300  # 5 minutes
        self.status = "active"  # active, closed, break
    
    def add_customer(self, customer):
        """Add customer to queue"""
        customer.position = len(self.customers) + 1
        customer.queue_id = self.queue_id
        
        # Determine customer type based on queue
        if self.queue_type == "express":
            customer.customer_type = "express"
        
        # Calculate estimated wait time
        customer.estimated_wait_time = self.calculate_estimated_wait_time()
        
        self.customers.append(customer)
        return True
    
    def serve_next_customer(self):
        """Move next customer to service position"""
        if self.customers and not self.current_customer:
            self.current_customer = self.customers.pop(0)
            self.current_customer.start_service()
            
            # Update positions for remaining customers
            for i, customer in enumerate(self.customers):
                customer.position = i + 1
            
            return self.current_customer
        return None
    
    def complete_current_service(self):
        """Complete service for current customer"""
        if self.current_customer:
            self.current_customer.complete_service()
            
            # Update metrics
            self.service_times.append(self.current_customer.service_time)
            self.wait_times.append(self.current_customer.actual_wait_time)
            self.total_customers_served += 1
            
            # Calculate averages
            if self.service_times:
                self.average_service_time = sum(self.service_times) / len(self.service_times)
            if self.wait_times:
                self.average_wait_time = sum(self.wait_times) / len(self.wait_times)
            
            # Archive served customer
            self.served_customers.append(self.current_customer)
            completed_customer = self.current_customer
            self.current_customer = None
            
            return completed_customer
        return None
    
    def calculate_estimated_wait_time(self):
        """Calculate estimated wait time for new customer"""
        if not self.customers and not self.current_customer:
            return 0
        
        # Base estimate on average service time and queue length
        avg_service = self.average_service_time if self.average_service_time > 0 else 120
        queue_length = len(self.customers)
        
        # Add current customer remaining time if any
        current_remaining = 0
        if self.current_customer and self.current_customer.service_start_time:
            elapsed = time.time() - self.current_customer.service_start_time
            current_remaining = max(0, avg_service - elapsed)
        
        return current_remaining + (queue_length * avg_service)
    
    def get_queue_length(self):
        """Get current queue length"""
        length = len(self.customers)
        if self.current_customer:
            length += 1
        return length
    
    def get_queue_status(self):
        """Get queue status for alerts"""
        length = self.get_queue_length()
        avg_wait = self.calculate_estimated_wait_time()
        
        if length > self.optimal_length * 2:
            return "critical"
        elif length > self.optimal_length:
            return "warning"
        elif avg_wait > self.max_wait_time:
            return "slow"
        else:
            return "good"
    
    def to_dict(self):
        """Convert queue to dictionary"""
        return {
            'queue_id': self.queue_id,
            'queue_type': self.queue_type,
            'customers': [c.to_dict() for c in self.customers],
            'current_customer': self.current_customer.to_dict() if self.current_customer else None,
            'total_customers_served': self.total_customers_served,
            'average_service_time': self.average_service_time,
            'average_wait_time': self.average_wait_time,
            'queue_length': self.get_queue_length(),
            'queue_status': self.get_queue_status(),
            'estimated_wait_time': self.calculate_estimated_wait_time(),
            'cashier_id': self.cashier_id,
            'status': self.status
        }

class QueueManager:
    """Main queue management class"""
    
    def __init__(self, config):
        self.config = config
        self.queue_config = config["queue"]
        self.counter_config = config["counters"]
        
        # Initialize queues
        self.queues = {}
        self.initialize_queues()
        
        # Customer tracking
        self.all_customers = {}
        self.customer_queue_mapping = {}
        
        # Data storage
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Performance tracking
        self.daily_stats = defaultdict(list)
        self.hourly_stats = defaultdict(lambda: defaultdict(list))
        
        print(f"Queue Manager initialized with {len(self.queues)} queues")
    
    def initialize_queues(self):
        """Initialize all checkout queues"""
        express_lanes = self.counter_config.get("express_lanes", [])
        counter_positions = self.counter_config.get("counter_positions", {})
        
        for counter_id in range(1, self.counter_config["total_counters"] + 1):
            queue_type = "express" if counter_id in express_lanes else "regular"
            position_coords = counter_positions.get(str(counter_id), {})
            
            self.queues[counter_id] = Queue(
                queue_id=counter_id,
                queue_type=queue_type,
                position_coords=position_coords
            )
    
    def update_queues(self, detections, frame_shape):
        """Update queue information based on detections"""
        current_time = time.time()
        
        # Track persons in each queue area
        for queue_id, queue in self.queues.items():
            persons_in_queue = self.get_persons_in_queue_area(detections, queue_id, frame_shape)
            self.update_queue_customers(queue, persons_in_queue, current_time)
        
        # Update customer-queue mapping
        self.update_customer_mapping()
        
        # Generate queue data for visualization
        queue_data = {}
        for queue_id, queue in self.queues.items():
            queue_data[queue_id] = queue.to_dict()
        
        return queue_data
    
    def get_persons_in_queue_area(self, detections, queue_id, frame_shape):
        """Get persons detected in specific queue area"""
        if str(queue_id) not in self.counter_config["counter_positions"]:
            return []
        
        position = self.counter_config["counter_positions"][str(queue_id)]
        x, y, w, h = position["x"], position["y"], position["width"], position["height"]
        
        persons_in_area = []
        for detection in detections:
            center_x, center_y = detection.get('center', [0, 0])
            
            if x <= center_x <= x + w and y <= center_y <= y + h:
                persons_in_area.append(detection)
        
        return persons_in_area
    
    def update_queue_customers(self, queue, persons_in_area, current_time):
        """Update customers in a specific queue"""
        # Sort persons by y-coordinate (front to back)
        persons_in_area.sort(key=lambda p: p.get('center', [0, 0])[1])
        
        # Determine current customer (closest to checkout)
        if persons_in_area:
            # First person is likely being served
            current_detection = persons_in_area[0]
            
            # Check if we need to start service for a new customer
            if not queue.current_customer:
                # Look for existing customer or create new one
                customer_id = self.get_or_create_customer_id(current_detection, queue.queue_id)
                customer = Customer(customer_id, queue.queue_id)
                queue.current_customer = customer
                queue.current_customer.start_service()
                self.all_customers[customer_id] = customer
            
            # Handle waiting customers
            waiting_detections = persons_in_area[1:] if len(persons_in_area) > 1 else []
            self.update_waiting_customers(queue, waiting_detections, current_time)
        
        else:
            # No one in queue area - complete current service if any
            if queue.current_customer:
                completed = queue.complete_current_service()
                if completed:
                    # Serve next customer if any
                    queue.serve_next_customer()
    
    def update_waiting_customers(self, queue, waiting_detections, current_time):
        """Update waiting customers in queue"""
        # Remove customers who are no longer in queue
        current_customer_ids = set()
        
        for detection in waiting_detections:
            customer_id = self.get_or_create_customer_id(detection, queue.queue_id)
            current_customer_ids.add(customer_id)
            
            # Check if customer is already in queue
            existing_customer = None
            for customer in queue.customers:
                if customer.person_id == customer_id:
                    existing_customer = customer
                    break
            
            if not existing_customer:
                # New customer joining queue
                new_customer = Customer(customer_id, queue.queue_id, current_time)
                queue.add_customer(new_customer)
                self.all_customers[customer_id] = new_customer
        
        # Remove customers who left the queue
        queue.customers = [c for c in queue.customers if c.person_id in current_customer_ids]
        
        # Update positions
        for i, customer in enumerate(queue.customers):
            customer.position = i + 1
    
    def get_or_create_customer_id(self, detection, queue_id):
        """Get or create unique customer ID"""
        # Use detection center as a simple ID (in real implementation, use proper tracking)
        center = detection.get('center', [0, 0])
        return f"customer_{queue_id}_{center[0]}_{center[1]}"
    
    def update_customer_mapping(self):
        """Update customer-queue mapping"""
        self.customer_queue_mapping.clear()
        
        for queue_id, queue in self.queues.items():
            if queue.current_customer:
                self.customer_queue_mapping[queue.current_customer.person_id] = queue_id
            
            for customer in queue.customers:
                self.customer_queue_mapping[customer.person_id] = queue_id
    
    def get_queue_recommendations(self):
        """Get recommendations for queue optimization"""
        recommendations = []
        
        # Analyze queue lengths
        queue_lengths = {qid: q.get_queue_length() for qid, q in self.queues.items()}
        avg_length = sum(queue_lengths.values()) / len(queue_lengths) if queue_lengths else 0
        
        # Find imbalanced queues
        for queue_id, length in queue_lengths.items():
            if length > avg_length * 1.5:
                recommendations.append({
                    'type': 'queue_redirect',
                    'message': f'Queue {queue_id} is overcrowded. Redirect customers to other counters.',
                    'priority': 'high'
                })
        
        # Check if additional counters needed
        total_customers = sum(queue_lengths.values())
        if total_customers > len(self.queues) * 3:
            recommendations.append({
                'type': 'open_counter',
                'message': 'Consider opening additional checkout counters.',
                'priority': 'medium'
            })
        
        return recommendations
    
    def get_performance_metrics(self):
        """Get overall performance metrics"""
        metrics = {
            'total_customers_served': 0,
            'average_service_time': 0,
            'average_wait_time': 0,
            'total_customers_waiting': 0,
            'queue_efficiency': 0
        }
        
        total_served = 0
        total_service_time = 0
        total_wait_time = 0
        total_waiting = 0
        
        for queue in self.queues.values():
            total_served += queue.total_customers_served
            if queue.average_service_time > 0:
                total_service_time += queue.average_service_time
            if queue.average_wait_time > 0:
                total_wait_time += queue.average_wait_time
            total_waiting += len(queue.customers)
        
        if total_served > 0:
            metrics['total_customers_served'] = total_served
            metrics['average_service_time'] = total_service_time / len(self.queues)
            metrics['average_wait_time'] = total_wait_time / len(self.queues)
        
        metrics['total_customers_waiting'] = total_waiting
        metrics['queue_efficiency'] = min(1.0, total_served / max(1, total_served + total_waiting))
        
        return metrics
    
    def save_queue_data(self):
        """Save queue data to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.data_dir, f"queue_data_{timestamp}.json")
        
        data = {
            'timestamp': timestamp,
            'queues': {qid: q.to_dict() for qid, q in self.queues.items()},
            'performance_metrics': self.get_performance_metrics(),
            'recommendations': self.get_queue_recommendations()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def reset_counters(self):
        """Reset all queue counters"""
        for queue in self.queues.values():
            queue.customers.clear()
            queue.current_customer = None
            queue.served_customers.clear()
            queue.total_customers_served = 0
            queue.service_times.clear()
            queue.wait_times.clear()
            queue.average_service_time = 0
            queue.average_wait_time = 0
        
        self.all_customers.clear()
        self.customer_queue_mapping.clear()
        print("All queue counters reset")
    
    def get_queue_separation_lines(self, queue_id, frame_shape):
        """Get separation line coordinates for visual display"""
        if str(queue_id) not in self.counter_config["counter_positions"]:
            return []
        
        position = self.counter_config["counter_positions"][str(queue_id)]
        x, y, w, h = position["x"], position["y"], position["width"], position["height"]
        
        lines = []
        
        # Service line (between current customer and waiting customers)
        service_line_y = y + h // 3
        lines.append({
            'type': 'service_line',
            'start': (x, service_line_y),
            'end': (x + w, service_line_y),
            'color': [0, 255, 0],  # Green
            'thickness': 3
        })
        
        # Queue boundary lines
        lines.extend([
            {
                'type': 'boundary',
                'start': (x, y),
                'end': (x, y + h),
                'color': [255, 0, 0],  # Red
                'thickness': 2
            },
            {
                'type': 'boundary',
                'start': (x + w, y),
                'end': (x + w, y + h),
                'color': [255, 0, 0],  # Red
                'thickness': 2
            }
        ])
        
        return lines
