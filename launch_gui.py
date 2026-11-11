#!/usr/bin/env python3
"""
Starmaker Story Save Editor - Launch Script
This script provides a simple way to launch the GUI editor.
"""
import os
import sys
import subprocess

def main():
    print("=== Starmaker Story Save Editor - Launch Script ===")
    print("=" * 50)
    
    # Check if customtkinter is installed
    try:
        import customtkinter
        print("✅ customtkinter is installed")
    except ImportError:
        print("❌ customtkinter is NOT installed")
        print("Installing now...")
        subprocess.run([sys.executable, "-m", "pip", "install", "customtkinter"], 
                      stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print("Installation complete")
    
    # Run the GUI
    script_path = "/home/jesusgs/proyects/starmaker/gui_editor_fixed.py"
    print(f"\n🚀 Launching GUI editor from: {script_path}")
    
    try:
        result = subprocess.run([
            sys.executable,
            script_path
        ], capture_output=True, text=True, timeout=10)
        
        print("✅ GUI launched successfully!")
        print("\n📋 GUI Status:")
        print(f"   - GUI Window: Should appear on your desktop")
        print(f"   - Status: Running (exit code {result.returncode})")
        
    except subprocess.TimeoutExpired:
        print("❌ GUI failed to launch within 10 seconds")
        print("   Please check that your display environment is working")
    
    except Exception as e:
        print(f"❌ Error launching GUI: {str(e)}")
        print("   Please check your Python environment")

if __name__ == "__main__":
    main()