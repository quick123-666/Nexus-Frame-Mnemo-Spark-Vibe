#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Duplicate Function Scanner
Checks JS files for multiple definitions of the same function.
"""
import os
import re
import sys

def scan_js_files(directory):
    """Scan all JS files in the directory for duplicate function definitions."""
    print(f"Scanning for duplicate functions in {directory}...")
    found_issues = False
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.js') or file.endswith('.html'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Find function definitions (e.g., function foo() or const foo = () =>)
                # This is a simplified regex check
                pattern = r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\(.*?\)\s*=>)'
                matches = re.findall(pattern, content)
                
                # Extract names
                names = [m[0] or m[1] for m in matches]
                
                # Find duplicates
                seen = set()
                duplicates = set()
                for name in names:
                    if name in seen:
                        duplicates.add(name)
                    seen.add(name)
                
                if duplicates:
                    print(f"  [WARN] {file}: Found duplicates: {', '.join(duplicates)}")
                    found_issues = True
                    
    if not found_issues:
        print("  [OK] No duplicate function definitions found.")
    return found_issues

if __name__ == "__main__":
    # Default to the web directory
    scan_dir = os.path.join(os.path.dirname(__file__), "..", "web")
    if len(sys.argv) > 1:
        scan_dir = sys.argv[1]
        
    if not os.path.exists(scan_dir):
        print(f"❌ Directory {scan_dir} does not exist.")
        sys.exit(1)
        
    issues = scan_js_files(scan_dir)
    sys.exit(1 if issues else 0)
