"""
Visual Interface Manager
Handles drawing of separation lines, overlays, and real-time information display
"""

import cv2
import numpy as np
import time
from datetime import datetime
from collections import deque

class InterfaceManager:
    """Visual interface management class"""
    
    def __init__(self, config):
        self.config = config
        self.visual_config = config["visual"]
        self.counter_config = config["counters"]
        
        # Visual settings
        self.line_thickness = self.visual_config.get("line_thickness", 3)
        self.colors = self.visual_config.get("colors", {})
        self.font_scale = self.visual_config.get("font_scale", 0.7)
        self.font_thickness = self.visual_config.get("font_thickness", 2)
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        
        # Default colors if not specified
        self.default_colors = {
            "current_customer": [0, 255, 0],      # Green
            "waiting_line": [255, 0, 0],          # Blue
            "queue_boundary": [0, 0, 255],        # Red
            "alert": [0, 165, 255],               # Orange
            "text": [255, 255, 255],              # White
            "background": [0, 0, 0],              # Black
            "warning": [0, 255, 255],             # Yellow
            "good": [0, 255, 0],                  # Green
            "critical": [0, 0, 255]               # Red
        }
        
        # Merge with config colors
        for key, value in self.default_colors.items():
            if key not in self.colors:
                self.colors[key] = value
        
        # Alert management
        self.active_alerts = []
        self.alert_history = deque(maxlen=100)
        
        # Performance overlay
        self.show_performance = True
        self.show_queue_info = True
        self.show_separation_lines = True
        
        print("Interface Manager initialized")
    
    def draw_interface(self, frame, detections, queue_data, performance_metrics):
        """Main interface drawing method"""
        # Create a copy of the frame to work with
        display_frame = frame.copy()
        
        # Draw separation lines for all queues
        if self.show_separation_lines:
            display_frame = self.draw_separation_lines(display_frame, queue_data)
        
        # Draw customer bounding boxes and IDs
        display_frame = self.draw_customer_boxes(display_frame, detections, queue_data)
        
        # Draw queue information overlays
        if self.show_queue_info:
            display_frame = self.draw_queue_overlays(display_frame, queue_data)
        
        # Draw performance metrics
        if self.show_performance:
            display_frame = self.draw_performance_overlay(display_frame, performance_metrics)
        
        # Draw alerts
        display_frame = self.draw_alerts(display_frame)
        
        # Draw timestamp and system info
        display_frame = self.draw_system_info(display_frame)
        
        return display_frame
    
    def draw_separation_lines(self, frame, queue_data):
        """Draw visual separation lines between current and waiting customers"""
        for queue_id, queue_info in queue_data.items():
            if str(queue_id) not in self.counter_config["counter_positions"]:
                continue
            
            position = self.counter_config["counter_positions"][str(queue_id)]
            x, y, w, h = position["x"], position["y"], position["width"], position["height"]
            
            # Draw queue boundary rectangle
            boundary_color = tuple(self.colors["queue_boundary"])
            cv2.rectangle(frame, (x, y), (x + w, y + h), boundary_color, 2)
            
            # Draw vertical service separation line (customers line up behind this)
            service_line_x = x + w // 3  # Vertical line at 1/3 of counter width
            service_line_color = tuple(self.colors["current_customer"])
            
            # Make line thicker and more visible
            cv2.line(frame, (service_line_x, y), (service_line_x, y + h), 
                    service_line_color, self.line_thickness + 2)
            
            # Add service line label
            cv2.putText(frame, "SERVICE", (service_line_x + 5, y + 25),
                       self.font, 0.5, service_line_color, 2)
            cv2.putText(frame, "LINE", (service_line_x + 5, y + 45),
                       self.font, 0.5, service_line_color, 2)
            
            # Draw vertical waiting area separator lines
            if queue_info["queue_length"] > 1:
                waiting_area_start = service_line_x + 50
                customer_spacing = max(30, (x + w - waiting_area_start) // max(1, queue_info["queue_length"] - 1))
                
                for i in range(queue_info["queue_length"] - 1):
                    line_x = waiting_area_start + (i * customer_spacing)
                    if line_x < x + w - 20:  # Don't draw beyond queue area
                        waiting_color = tuple(self.colors["waiting_line"])
                        cv2.line(frame, (line_x, y + 10), (line_x, y + h - 10),
                                waiting_color, 2)
            
            # Draw queue status indicator
            status_color = self.get_status_color(queue_info.get("queue_status", "good"))
            cv2.circle(frame, (x + w - 20, y + 20), 10, status_color, -1)
        
        return frame
    
    def draw_customer_boxes(self, frame, detections, queue_data):
        """Draw bounding boxes around detected customers"""
        for detection in detections:
            bbox = detection.get('bbox', [0, 0, 0, 0])
            confidence = detection.get('confidence', 0)
            center = detection.get('center', [0, 0])
            
            x, y, w, h = bbox
            
            # Determine if customer is current or waiting
            customer_type = self.get_customer_type_at_position(center, queue_data)
            
            # Choose color based on customer status
            if customer_type == "current":
                box_color = tuple(self.colors["current_customer"])
                label = "SERVING"
            elif customer_type == "waiting":
                box_color = tuple(self.colors["waiting_line"])
                label = "WAITING"
            else:
                box_color = tuple(self.colors["text"])
                label = "PERSON"
            
            # Draw bounding box
            cv2.rectangle(frame, (x, y), (x + w, y + h), box_color, 2)
            
            # Draw confidence and label
            label_text = f"{label} ({confidence:.2f})"
            text_size = cv2.getTextSize(label_text, self.font, 0.5, 1)[0]
            
            # Draw background for text
            cv2.rectangle(frame, (x, y - text_size[1] - 10), 
                         (x + text_size[0] + 10, y), box_color, -1)
            
            # Draw text
            cv2.putText(frame, label_text, (x + 5, y - 5),
                       self.font, 0.5, (255, 255, 255), 1)
            
            # Draw center point
            cv2.circle(frame, tuple(center), 5, box_color, -1)
        
        return frame
    
    def draw_queue_overlays(self, frame, queue_data):
        """Draw queue information overlays"""
        overlay_y = 30
        
        for queue_id, queue_info in queue_data.items():
            if str(queue_id) not in self.counter_config["counter_positions"]:
                continue
            
            position = self.counter_config["counter_positions"][str(queue_id)]
            x, y = position["x"], position["y"]
            
            # Queue header
            queue_type = "EXPRESS" if queue_id in self.counter_config.get("express_lanes", []) else "REGULAR"
            header_text = f"COUNTER {queue_id} ({queue_type})"
            
            # Draw header background
            header_size = cv2.getTextSize(header_text, self.font, 0.6, 2)[0]
            cv2.rectangle(frame, (x, y - 30), (x + header_size[0] + 10, y - 5),
                         (0, 0, 0), -1)
            
            # Draw header text
            cv2.putText(frame, header_text, (x + 5, y - 10),
                       self.font, 0.6, (255, 255, 255), 2)
            
            # Queue statistics
            stats = [
                f"Queue Length: {queue_info['queue_length']}",
                f"Est. Wait: {queue_info['estimated_wait_time']:.0f}s",
                f"Avg Service: {queue_info['average_service_time']:.0f}s",
                f"Served Today: {queue_info['total_customers_served']}"
            ]
            
            # Draw statistics
            for i, stat in enumerate(stats):
                stat_y = y + 20 + (i * 20)
                
                # Background for readability
                stat_size = cv2.getTextSize(stat, self.font, 0.4, 1)[0]
                cv2.rectangle(frame, (x, stat_y - 15), (x + stat_size[0] + 10, stat_y + 5),
                             (0, 0, 0, 128), -1)
                
                cv2.putText(frame, stat, (x + 5, stat_y),
                           self.font, 0.4, (255, 255, 255), 1)
            
            # Current customer timer
            if queue_info["current_customer"]:
                current_customer = queue_info["current_customer"]
                if current_customer["service_start_time"]:
                    elapsed_time = time.time() - current_customer["service_start_time"]
                    timer_text = f"Service Time: {elapsed_time:.0f}s"
                    
                    # Draw timer with color based on performance
                    timer_color = (0, 255, 0) if elapsed_time < 120 else (0, 255, 255) if elapsed_time < 180 else (0, 0, 255)
                    
                    cv2.putText(frame, timer_text, (x + 5, y + 120),
                               self.font, 0.5, timer_color, 2)
        
        return frame
    
    def draw_performance_overlay(self, frame, performance_metrics):
        """Draw system performance overlay"""
        overlay_x = frame.shape[1] - 300
        overlay_y = 30
        
        # Performance metrics background
        cv2.rectangle(frame, (overlay_x - 10, overlay_y - 20),
                     (frame.shape[1] - 10, overlay_y + 200),
                     (0, 0, 0, 180), -1)
        
        # Title
        cv2.putText(frame, "SYSTEM PERFORMANCE", (overlay_x, overlay_y),
                   self.font, 0.6, (255, 255, 255), 2)
        
        # Performance metrics
        metrics_text = [
            f"Total Served: {performance_metrics.get('total_customers_served', 0)}",
            f"Avg Service: {performance_metrics.get('average_service_time', 0):.1f}s",
            f"Avg Wait: {performance_metrics.get('average_wait_time', 0):.1f}s",
            f"Currently Waiting: {performance_metrics.get('total_customers_waiting', 0)}",
            f"Efficiency: {performance_metrics.get('queue_efficiency', 0):.1%}",
            f"FPS: {performance_metrics.get('fps', 0):.1f}"
        ]
        
        for i, metric in enumerate(metrics_text):
            metric_y = overlay_y + 30 + (i * 25)
            cv2.putText(frame, metric, (overlay_x, metric_y),
                       self.font, 0.5, (255, 255, 255), 1)
        
        # Efficiency indicator
        efficiency = performance_metrics.get('queue_efficiency', 0)
        indicator_color = (0, 255, 0) if efficiency > 0.8 else (0, 255, 255) if efficiency > 0.6 else (0, 0, 255)
        cv2.circle(frame, (overlay_x + 250, overlay_y + 130), 15, indicator_color, -1)
        
        return frame
    
    def draw_alerts(self, frame):
        """Draw active alerts"""
        if not self.active_alerts:
            return frame
        
        alert_y = 100
        for alert in self.active_alerts[-5:]:  # Show last 5 alerts
            alert_text = alert.get('message', 'Alert')
            priority = alert.get('priority', 'medium')
            
            # Choose color based on priority
            if priority == 'high':
                alert_color = tuple(self.colors["critical"])
            elif priority == 'medium':
                alert_color = tuple(self.colors["warning"])
            else:
                alert_color = tuple(self.colors["text"])
            
            # Draw alert background
            text_size = cv2.getTextSize(alert_text, self.font, 0.6, 2)[0]
            cv2.rectangle(frame, (10, alert_y - 20), (text_size[0] + 30, alert_y + 10),
                         alert_color, -1)
            
            # Draw alert text
            cv2.putText(frame, alert_text, (20, alert_y),
                       self.font, 0.6, (255, 255, 255), 2)
            
            alert_y += 40
        
        return frame
    
    def draw_system_info(self, frame):
        """Draw system timestamp and info"""
        # Current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # System info
        info_text = f"Queue Management System - {timestamp}"
        
        # Draw background
        text_size = cv2.getTextSize(info_text, self.font, 0.5, 1)[0]
        cv2.rectangle(frame, (10, frame.shape[0] - 30), 
                     (text_size[0] + 20, frame.shape[0] - 5),
                     (0, 0, 0, 180), -1)
        
        # Draw text
        cv2.putText(frame, info_text, (15, frame.shape[0] - 15),
                   self.font, 0.5, (255, 255, 255), 1)
        
        # Controls hint
        controls_text = "Controls: Q-Quit | S-Save Report | R-Reset | H-Help"
        controls_size = cv2.getTextSize(controls_text, self.font, 0.4, 1)[0]
        
        cv2.rectangle(frame, (frame.shape[1] - controls_size[0] - 20, frame.shape[0] - 30),
                     (frame.shape[1] - 10, frame.shape[0] - 5),
                     (0, 0, 0, 180), -1)
        
        cv2.putText(frame, controls_text, 
                   (frame.shape[1] - controls_size[0] - 15, frame.shape[0] - 15),
                   self.font, 0.4, (255, 255, 255), 1)
        
        return frame
    
    def get_customer_type_at_position(self, position, queue_data):
        """Determine if customer at position is current or waiting"""
        for queue_id, queue_info in queue_data.items():
            if str(queue_id) not in self.counter_config["counter_positions"]:
                continue
            
            queue_pos = self.counter_config["counter_positions"][str(queue_id)]
            x, y, w, h = queue_pos["x"], queue_pos["y"], queue_pos["width"], queue_pos["height"]
            
            # Check if position is in this queue area
            if x <= position[0] <= x + w and y <= position[1] <= y + h:
                # Check if in service area (top 1/4 of queue)
                service_area_end = y + h // 4
                if position[1] <= service_area_end:
                    return "current"
                else:
                    return "waiting"
        
        return "unknown"
    
    def get_status_color(self, status):
        """Get color based on queue status"""
        status_colors = {
            "good": self.colors["good"],
            "warning": self.colors["warning"],
            "critical": self.colors["critical"],
            "slow": self.colors["alert"]
        }
        return tuple(status_colors.get(status, self.colors["text"]))
    
    def add_alerts(self, alerts):
        """Add new alerts to display"""
        for alert in alerts:
            alert['timestamp'] = time.time()
            self.active_alerts.append(alert)
            self.alert_history.append(alert)
        
        # Remove old alerts (older than 10 seconds)
        current_time = time.time()
        self.active_alerts = [
            alert for alert in self.active_alerts
            if current_time - alert.get('timestamp', 0) < 10
        ]
    
    def toggle_performance_display(self):
        """Toggle performance overlay display"""
        self.show_performance = not self.show_performance
        return self.show_performance
    
    def toggle_queue_info_display(self):
        """Toggle queue information display"""
        self.show_queue_info = not self.show_queue_info
        return self.show_queue_info
    
    def toggle_separation_lines(self):
        """Toggle separation lines display"""
        self.show_separation_lines = not self.show_separation_lines
        return self.show_separation_lines
    
    def clear_alerts(self):
        """Clear all active alerts"""
        self.active_alerts.clear()
    
    def create_dashboard_image(self, queue_data, performance_metrics):
        """Create a dashboard image for reporting"""
        dashboard = np.zeros((600, 800, 3), dtype=np.uint8)
        
        # Title
        cv2.putText(dashboard, "QUEUE MANAGEMENT DASHBOARD", (50, 50),
                   self.font, 1.0, (255, 255, 255), 2)
        
        # Current time
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(dashboard, f"Generated: {timestamp}", (50, 80),
                   self.font, 0.5, (200, 200, 200), 1)
        
        # Queue summary
        y_pos = 120
        for queue_id, queue_info in queue_data.items():
            queue_text = f"Counter {queue_id}: {queue_info['queue_length']} customers, {queue_info['estimated_wait_time']:.0f}s wait"
            cv2.putText(dashboard, queue_text, (50, y_pos),
                       self.font, 0.6, (255, 255, 255), 1)
            y_pos += 30
        
        # Performance metrics
        y_pos += 30
        cv2.putText(dashboard, "PERFORMANCE METRICS", (50, y_pos),
                   self.font, 0.8, (255, 255, 255), 2)
        y_pos += 40
        
        metrics_text = [
            f"Total Customers Served: {performance_metrics.get('total_customers_served', 0)}",
            f"Average Service Time: {performance_metrics.get('average_service_time', 0):.1f} seconds",
            f"Average Wait Time: {performance_metrics.get('average_wait_time', 0):.1f} seconds",
            f"Queue Efficiency: {performance_metrics.get('queue_efficiency', 0):.1%}"
        ]
        
        for metric in metrics_text:
            cv2.putText(dashboard, metric, (50, y_pos),
                       self.font, 0.5, (255, 255, 255), 1)
            y_pos += 25
        
        return dashboard
