#!/usr/bin/env python3
"""
UCAR Manager CLI - Command Line Interface for managing ADAS workers
Supports starting, stopping, and monitoring various ADAS worker processes.
"""

import argparse
import sys
import os
import time
import logging
import subprocess
import signal
from pathlib import Path
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('UCARManager')

class UCARManager:
    """Main UCAR Manager class for handling ADAS workers"""
    
    def __init__(self):
        self.workers_dir = Path(__file__).parent.parent / "workers"
        self.available_workers = {
            'emergency': {
                'name': 'Emergency Stop System', 
                'script': 'workers/emergency/worker_emergency.py',
                'description': 'High-frequency emergency stop and collision avoidance system'
            },
            'lane': {
                'name': 'Lane Keeping Assistance',
                'script': 'workers/lane/worker_lane.py', 
                'description': 'Camera-based lane detection and keeping assistance'
            },
            'pedestrian': {
                'name': 'Pedestrian Detection',
                'script': 'workers/pedestrian/worker_pedestrian.py',
                'description': 'Camera-based pedestrian detection and safety system'
            }
        }
        self.running_processes = {}
        
    def show_help(self):
        """Display comprehensive help information"""
        print("\n🚗 UCAR Manager - Advanced Driver Assistance System (ADAS) Manager")
        print("=" * 70)
        print("\nAVAILABLE COMMANDS:")
        print("  help              Show this help message")
        print("  start             Start ADAS workers")
        print("  stop              Stop running workers")
        print("  status            Show status of all workers")
        print("  list              List available workers")
        print("\nSTART COMMAND OPTIONS:")
        print("  start all         Start all available workers")
        print("  start emergency   Start emergency stop system")
        print("  start lane        Start lane keeping assistance")  
        print("  start pedestrian  Start pedestrian detection")
        print("\nEXAMPLES:")
        print("  python3 -m ucar_manager.cli start all")
        print("  python3 -m ucar_manager.cli start emergency")
        print("  python3 -m ucar_manager.cli status")
        print("  python3 -m ucar_manager.cli help")
        print("\nAVAILABLE WORKERS:")
        for worker_id, worker_info in self.available_workers.items():
            print(f"  {worker_id:<12} - {worker_info['name']}")
            print(f"               {worker_info['description']}")
        print("\n" + "=" * 70)
        
    def list_workers(self):
        """List all available workers with details"""
        print("\n🔧 Available ADAS Workers:")
        print("-" * 50)
        for worker_id, worker_info in self.available_workers.items():
            status = "✅ Running" if worker_id in self.running_processes else "⭕ Stopped"
            print(f"ID: {worker_id}")
            print(f"Name: {worker_info['name']}")
            print(f"Description: {worker_info['description']}")
            print(f"Script: {worker_info['script']}")
            print(f"Status: {status}")
            print("-" * 50)
            
    def start_worker(self, worker_id: str) -> bool:
        """Start a specific worker"""
        if worker_id not in self.available_workers:
            logger.error(f"Unknown worker: {worker_id}")
            return False
            
        if worker_id in self.running_processes:
            logger.warning(f"Worker {worker_id} is already running")
            return True
            
        worker_info = self.available_workers[worker_id]
        script_path = Path(__file__).parent.parent / worker_info['script']
        
        if not script_path.exists():
            logger.error(f"Worker script not found: {script_path}")
            return False
            
        try:
            logger.info(f"Starting {worker_info['name']}...")
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give the process a moment to start
            time.sleep(0.5)
            
            # Check if process started successfully
            if process.poll() is None:
                self.running_processes[worker_id] = {
                    'process': process,
                    'info': worker_info,
                    'start_time': time.time()
                }
                logger.info(f"✅ {worker_info['name']} started successfully (PID: {process.pid})")
                return True
            else:
                stdout, stderr = process.communicate()
                logger.error(f"❌ Failed to start {worker_info['name']}")
                if stderr:
                    logger.error(f"Error: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting {worker_info['name']}: {e}")
            return False
            
    def start_all_workers(self) -> bool:
        """Start all available workers"""
        logger.info("🚀 Starting all ADAS workers...")
        success_count = 0
        
        for worker_id in self.available_workers.keys():
            if self.start_worker(worker_id):
                success_count += 1
                
        total_workers = len(self.available_workers)
        logger.info(f"Started {success_count}/{total_workers} workers successfully")
        return success_count == total_workers
        
    def stop_worker(self, worker_id: str) -> bool:
        """Stop a specific worker"""
        if worker_id not in self.running_processes:
            logger.warning(f"Worker {worker_id} is not running")
            return True
            
        try:
            worker_data = self.running_processes[worker_id]
            process = worker_data['process']
            worker_name = worker_data['info']['name']
            
            logger.info(f"Stopping {worker_name}...")
            
            # Send SIGTERM for graceful shutdown
            process.terminate()
            
            # Wait for graceful shutdown
            try:
                process.wait(timeout=5)
                logger.info(f"✅ {worker_name} stopped gracefully")
            except subprocess.TimeoutExpired:
                logger.warning(f"Force killing {worker_name}...")
                process.kill()
                process.wait()
                logger.info(f"✅ {worker_name} force stopped")
                
            del self.running_processes[worker_id]
            return True
            
        except Exception as e:
            logger.error(f"❌ Error stopping worker {worker_id}: {e}")
            return False
            
    def stop_all_workers(self) -> bool:
        """Stop all running workers"""
        if not self.running_processes:
            logger.info("No workers are currently running")
            return True
            
        logger.info("🛑 Stopping all running workers...")
        success_count = 0
        
        for worker_id in list(self.running_processes.keys()):
            if self.stop_worker(worker_id):
                success_count += 1
                
        total_running = len(self.running_processes)
        logger.info(f"Stopped {success_count} workers")
        return success_count == total_running
        
    def show_status(self):
        """Show status of all workers"""
        print("\n📊 UCAR Manager Status:")
        print("=" * 60)
        
        if not self.running_processes:
            print("⭕ No workers are currently running")
        else:
            print(f"✅ {len(self.running_processes)} worker(s) running:")
            
        for worker_id, worker_info in self.available_workers.items():
            if worker_id in self.running_processes:
                worker_data = self.running_processes[worker_id]
                uptime = time.time() - worker_data['start_time']
                pid = worker_data['process'].pid
                print(f"  🟢 {worker_info['name']}")
                print(f"      PID: {pid} | Uptime: {uptime:.1f}s")
            else:
                print(f"  🔴 {worker_info['name']} - Stopped")
                
        print("=" * 60)


def create_parser():
    """Create and configure the argument parser"""
    parser = argparse.ArgumentParser(
        prog='ucar_manager',
        description='UCAR Manager - Command Line Interface for ADAS workers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s help
  %(prog)s start all
  %(prog)s start emergency
  %(prog)s status
  %(prog)s stop all
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Help command
    help_parser = subparsers.add_parser('help', help='Show help information')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start ADAS workers')
    start_parser.add_argument(
        'worker', 
        nargs='?',
        choices=['all', 'emergency', 'lane', 'pedestrian'],
        default='all',
        help='Worker to start (default: all)'
    )
    
    # Stop command  
    stop_parser = subparsers.add_parser('stop', help='Stop running workers')
    stop_parser.add_argument(
        'worker',
        nargs='?', 
        choices=['all', 'emergency', 'lane', 'pedestrian'],
        default='all',
        help='Worker to stop (default: all)'
    )
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show worker status')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available workers')
    
    return parser


def main():
    """Main entry point for the CLI application"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Create UCAR manager instance
    manager = UCARManager()
    
    # Handle commands
    try:
        if not args.command or args.command == 'help':
            manager.show_help()
            
        elif args.command == 'start':
            if args.worker == 'all':
                success = manager.start_all_workers()
                sys.exit(0 if success else 1)
            else:
                success = manager.start_worker(args.worker)
                sys.exit(0 if success else 1)
                
        elif args.command == 'stop':
            if args.worker == 'all':
                success = manager.stop_all_workers()
                sys.exit(0 if success else 1)
            else:
                success = manager.stop_worker(args.worker)
                sys.exit(0 if success else 1)
                
        elif args.command == 'status':
            manager.show_status()
            
        elif args.command == 'list':
            manager.list_workers()
            
        else:
            parser.print_help()
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("\n🛑 Interrupted by user")
        manager.stop_all_workers()
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()