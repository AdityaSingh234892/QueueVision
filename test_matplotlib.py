#!/usr/bin/env python3
"""
Test matplotlib import
"""

print("Testing matplotlib...")

try:
    import matplotlib
    print("✓ matplotlib imported")
    
    print("Setting backend...")
    matplotlib.use('Agg')  # Non-interactive backend
    print("✓ Backend set to Agg")
    
    import matplotlib.pyplot as plt
    print("✓ pyplot imported")
    
    print("Creating simple plot...")
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 4, 9])
    print("✓ Plot created")
    
    print("Matplotlib working correctly!")
    
except Exception as e:
    print(f"✗ Matplotlib error: {e}")

print("Test complete!")
