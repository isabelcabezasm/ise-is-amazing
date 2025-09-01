#!/usr/bin/env python3
"""
Performance monitoring and visualization script
Runs continuous load tests and generates performance graphs
"""

import time
import json
import requests
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime, timedelta
import threading
import argparse
from typing import List, Dict
import os


class PerformanceMonitor:
    """
    Continuous performance monitoring for the Amazing API
    """

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.metrics_data = []
        self.monitoring = False

        # Set up plotting style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")

    def single_request_benchmark(self) -> Dict:
        """
        Perform a single request and measure performance

        Returns:
            Dict with performance metrics
        """
        start_time = time.time()

        # Use a simple positive message
        payload = {"text": "You are amazing!"}

        try:
            response = self.session.post(
                f"{self.base_url}/api/amazing",
                json=payload,
                timeout=30
            )

            end_time = time.time()
            response_time = end_time - start_time

            return {
                'timestamp': datetime.now(),
                'response_time': response_time,
                'status_code': response.status_code,
                # 400 is ok for duplicates
                'success': response.status_code in [200, 400],
                'error': None
            }

        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time

            return {
                'timestamp': datetime.now(),
                'response_time': response_time,
                'status_code': None,
                'success': False,
                'error': str(e)
            }

    def monitor_performance(self, duration_minutes: int = 10, interval_seconds: int = 5):
        """
        Monitor API performance continuously

        Args:
            duration_minutes: How long to monitor in minutes
            interval_seconds: Seconds between requests
        """
        print(
            f"🔍 Starting performance monitoring for {duration_minutes} minutes")
        print(f"⏱️  Making request every {interval_seconds} seconds")
        print(f"🎯 Target: {self.base_url}/api/amazing")
        print("-" * 50)

        self.monitoring = True
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        request_count = 0

        while datetime.now() < end_time and self.monitoring:
            request_count += 1
            metric = self.single_request_benchmark()
            self.metrics_data.append(metric)

            # Print real-time status
            status = "✅" if metric['success'] else "❌"
            print(f"{status} Request {request_count}: "
                  f"{metric['response_time']:.3f}s -> {metric['status_code']}")

            # Wait for next interval
            time.sleep(interval_seconds)

        self.monitoring = False
        print(
            f"\n📊 Monitoring completed. Collected {len(self.metrics_data)} data points")

    def generate_performance_report(self, save_plots: bool = True):
        """
        Generate detailed performance report with visualizations

        Args:
            save_plots: Whether to save plot images
        """
        if not self.metrics_data:
            print("❌ No performance data collected")
            return

        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(self.metrics_data)

        print("\n" + "=" * 60)
        print("📈 PERFORMANCE MONITORING REPORT")
        print("=" * 60)

        # Basic statistics
        total_requests = len(df)
        successful_requests = df['success'].sum()
        success_rate = (successful_requests / total_requests) * 100

        print(f"📊 Total Requests: {total_requests}")
        print(f"✅ Successful: {successful_requests}")
        print(f"❌ Failed: {total_requests - successful_requests}")
        print(f"📈 Success Rate: {success_rate:.2f}%")

        # Response time statistics
        response_times = df['response_time']
        print(f"\n⏱️  Response Time Statistics:")
        print(f"   • Mean: {response_times.mean():.3f}s")
        print(f"   • Median: {response_times.median():.3f}s")
        print(f"   • Min: {response_times.min():.3f}s")
        print(f"   • Max: {response_times.max():.3f}s")
        print(f"   • Std Dev: {response_times.std():.3f}s")
        print(f"   • 95th percentile: {response_times.quantile(0.95):.3f}s")
        print(f"   • 99th percentile: {response_times.quantile(0.99):.3f}s")

        # Status code distribution
        status_counts = df['status_code'].value_counts()
        print(f"\n📋 Status Code Distribution:")
        for status, count in status_counts.items():
            percentage = (count / total_requests) * 100
            print(f"   • {status}: {count} ({percentage:.1f}%)")

        if save_plots:
            self.create_performance_plots(df)

        print("=" * 60)

    def create_performance_plots(self, df: pd.DataFrame):
        """
        Create and save performance visualization plots

        Args:
            df: DataFrame with performance metrics
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Amazing API Performance Monitoring Report', fontsize=16)

        # 1. Response Time Over Time
        ax1.plot(df.index, df['response_time'],
                 marker='o', markersize=3, alpha=0.7)
        ax1.set_title('Response Time Over Time')
        ax1.set_xlabel('Request Number')
        ax1.set_ylabel('Response Time (seconds)')
        ax1.grid(True, alpha=0.3)

        # Add trend line
        z = np.polyfit(df.index, df['response_time'], 1)
        p = np.poly1d(z)
        ax1.plot(df.index, p(df.index), "r--", alpha=0.8, label=f'Trend')
        ax1.legend()

        # 2. Response Time Distribution
        ax2.hist(df['response_time'], bins=20, alpha=0.7, edgecolor='black')
        ax2.axvline(df['response_time'].mean(), color='red', linestyle='--',
                    label=f'Mean: {df["response_time"].mean():.3f}s')
        ax2.axvline(df['response_time'].median(), color='green', linestyle='--',
                    label=f'Median: {df["response_time"].median():.3f}s')
        ax2.set_title('Response Time Distribution')
        ax2.set_xlabel('Response Time (seconds)')
        ax2.set_ylabel('Frequency')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # 3. Success Rate Over Time (rolling window)
        window_size = max(1, len(df) // 10)  # 10% window
        rolling_success = df['success'].rolling(
            window=window_size).mean() * 100
        ax3.plot(df.index, rolling_success, marker='o', markersize=3)
        ax3.set_title(
            f'Success Rate Over Time (Rolling {window_size}-request window)')
        ax3.set_xlabel('Request Number')
        ax3.set_ylabel('Success Rate (%)')
        ax3.set_ylim(0, 105)
        ax3.grid(True, alpha=0.3)

        # 4. Status Code Distribution (Pie Chart)
        status_counts = df['status_code'].value_counts()
        colors = plt.cm.Set3(range(len(status_counts)))
        ax4.pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%',
                colors=colors)
        ax4.set_title('Status Code Distribution')

        # Adjust layout and save
        plt.tight_layout()

        plot_filename = f'performance_report_{timestamp}.png'
        plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
        print(f"📊 Performance plots saved to: {plot_filename}")

        # Also save as PDF
        pdf_filename = f'performance_report_{timestamp}.pdf'
        plt.savefig(pdf_filename, dpi=300, bbox_inches='tight')
        print(f"📄 Performance report PDF saved to: {pdf_filename}")

        plt.close()

    def save_metrics_data(self):
        """Save metrics data to JSON file for later analysis"""
        if not self.metrics_data:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'performance_metrics_{timestamp}.json'

        # Convert datetime objects to strings for JSON serialization
        json_data = []
        for metric in self.metrics_data:
            json_metric = metric.copy()
            json_metric['timestamp'] = metric['timestamp'].isoformat()
            json_data.append(json_metric)

        with open(filename, 'w') as f:
            json.dump(json_data, f, indent=2)

        print(f"💾 Metrics data saved to: {filename}")


def main():
    """Main function to run performance monitoring"""
    parser = argparse.ArgumentParser(
        description="Performance monitoring for Amazing API")
    parser.add_argument("--url", default="http://localhost:8000",
                        help="Base URL for the API (default: http://localhost:8000)")
    parser.add_argument("--duration", type=int, default=5,
                        help="Monitoring duration in minutes (default: 5)")
    parser.add_argument("--interval", type=int, default=3,
                        help="Seconds between requests (default: 3)")
    parser.add_argument("--no-plots", action="store_true",
                        help="Skip generating performance plots")

    args = parser.parse_args()

    monitor = PerformanceMonitor(args.url)

    try:
        # Run performance monitoring
        monitor.monitor_performance(
            duration_minutes=args.duration,
            interval_seconds=args.interval
        )

        # Generate report
        monitor.generate_performance_report(save_plots=not args.no_plots)

        # Save raw data
        monitor.save_metrics_data()

    except KeyboardInterrupt:
        print("\n⏹️  Monitoring stopped by user")
        monitor.monitoring = False

        if monitor.metrics_data:
            print("📊 Generating report for collected data...")
            monitor.generate_performance_report(save_plots=not args.no_plots)
            monitor.save_metrics_data()


if __name__ == "__main__":
    try:
        import numpy as np
        main()
    except ImportError:
        print("❌ Missing required dependencies. Install with:")
        print("pip install matplotlib seaborn pandas numpy")
        exit(1)
