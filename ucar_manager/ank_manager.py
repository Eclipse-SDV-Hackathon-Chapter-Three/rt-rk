#!/home/sdv-hacker/tmp/sdv_lab/carla-setup/examples/carla_setup/.venv/bin/python

import subprocess
import json
import sys
import signal
import argparse
import re
from tabulate import tabulate

def run_ank_command(command):
    """Run ank CLI command and return the output"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error running command '{command}': {result.stderr}")
            return None
        return result.stdout.strip()
    except Exception as e:
        print(f"Exception running command '{command}': {e}")
        return None

def bytes_to_gb(bytes_str):
    """Convert bytes string to GB format"""
    try:
        # Remove 'B' suffix if present
        bytes_value = bytes_str.replace('B', '')
        bytes_int = int(bytes_value)
        gb_value = bytes_int / (1024 ** 3)  # Convert to GB
        return f"{gb_value:.2f} GB"
    except (ValueError, AttributeError):
        return bytes_str  # Return original if conversion fails

def parse_agents_output(output):
    """Parse agents output and return structured data"""
    if not output:
        return []
    
    lines = output.strip().split('\n')
    if len(lines) < 2:
        return []
    
    # Skip header line
    agents = []
    for line in lines[1:]:
        parts = line.split()
        if len(parts) >= 4:
            free_memory_gb = bytes_to_gb(parts[3])
            agents.append({
                'Name': parts[0],
                'Workloads': parts[1],
                'CPU Usage': parts[2],
                'Free Memory': free_memory_gb
            })
    return agents

def parse_workloads_output(output):
    """Parse workloads output and return structured data"""
    if not output:
        return []
    
    lines = output.strip().split('\n')
    if len(lines) < 2:
        return []
    
    # Skip header line
    workloads = []
    for line in lines[1:]:
        parts = line.split()
        if len(parts) >= 4:
            workload_name = parts[0]
            agent = parts[1]
            runtime = parts[2]
            execution_state = parts[3]
            additional_info = ' '.join(parts[4:]) if len(parts) > 4 else ''
            
            workloads.append({
                'Workload Name': workload_name,
                'Agent': agent,
                'Runtime': runtime,
                'Execution State': execution_state,
                'Additional Info': additional_info
            })
    return workloads

def display_agents_table(agents_data):
    """Display agents in a formatted table"""
    if not agents_data:
        print("No agents found.")
        return
    
    headers = ['Name', 'Workloads', 'CPU Usage', 'Free Memory']
    table_data = [[agent[header] for header in headers] for agent in agents_data]
    
    print("\n" + "="*60)
    print("AVAILABLE AGENTS")
    print("="*60)
    print(tabulate(table_data, headers=headers, tablefmt='grid'))

def display_workloads_table(workloads_data):
    """Display workloads in a formatted table"""
    if not workloads_data:
        print("No workloads found.")
        return
    
    headers = ['Workload Name', 'Agent', 'Runtime', 'Execution State', 'Additional Info']
    table_data = [[workload[header] for header in headers] for workload in workloads_data]
    
    print("\n" + "="*80)
    print("WORKLOAD CONFIGURATIONS")
    print("="*80)
    print(tabulate(table_data, headers=headers, tablefmt='grid'))

def signal_handler(sig, frame):
    print("\nShutting down...")
    sys.exit(0)

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Ankaios Workload Manager - Get information about agents and workloads')
    parser.add_argument('--agents', action='store_true', help='Show only agents information')
    parser.add_argument('--workloads', action='store_true', help='Show only workloads information')
    parser.add_argument('--all', action='store_true', help='Show all information (default)')
    
    args = parser.parse_args()
    
    # If no specific flags are provided, show all
    if not args.agents and not args.workloads:
        args.all = True
    
    # Add a SIGTERM handler to allow a clean shutdown
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("Getting information from Ankaios...")
    
    # Get and display agents
    if args.agents or args.all:
        agents_output = run_ank_command("ank -k get agents")
        agents_data = parse_agents_output(agents_output)
        display_agents_table(agents_data)
    
    # Get and display workloads
    if args.workloads or args.all:
        workloads_output = run_ank_command("ank -k get workloads")
        workloads_data = parse_workloads_output(workloads_output)
        display_workloads_table(workloads_data)
    
    print("\nScript completed successfully!")

if __name__ == "__main__":
    main()
