"""
Test Real-Time Engine
"""
import time
import threading
from simulation.real_time_engine import RealTimeEngine

def test_realtime():
    print("--- Testing RealTimeEngine ---")
    
    # 1. Initialize Engine (Fast tick for testing: 10Hz)
    engine = RealTimeEngine(tick_rate_hz=10.0)
    
    # 2. Define a handler
    ticks_captured = []
    
    def my_handler(tick, delta):
        ticks_captured.append((tick, time.monotonic()))
        # print(f"Tick {tick}, delta={delta:.4f}")
        
    engine.register_tick_handler(my_handler)
    
    # 3. Run in a thread so we can stop it
    t = threading.Thread(target=engine.start)
    t.start()
    
    # Let it run for 0.5 seconds (expect ~5 ticks)
    time.sleep(0.55)
    
    # 4. Stop
    engine.stop()
    t.join()
    
    count = len(ticks_captured)
    print(f"Captured {count} ticks in ~0.55s (Target: ~5)")
    
    # Verify count is reasonable (allowing for slight thread scheduling jitter)
    if 4 <= count <= 7:
        print("✅ SUCCESS: Tick count within expected range.")
    else:
        print("❌ FAILURE: Tick count inaccurate.")
        
    # Verify intervals
    intervals = []
    for i in range(1, len(ticks_captured)):
        dt = ticks_captured[i][1] - ticks_captured[i-1][1]
        intervals.append(dt)
        
    avg_interval = sum(intervals) / len(intervals) if intervals else 0
    print(f"Average Interval: {avg_interval:.4f}s (Target: 0.1000s)")
    
    if 0.09 < avg_interval < 0.11:
         print("✅ SUCCESS: Timing is precise.")
    else:
         print("❌ FAILURE: Timing drifted too much.")

if __name__ == "__main__":
    test_realtime()
