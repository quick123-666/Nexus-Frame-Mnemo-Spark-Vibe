import asyncio
import websockets
import json
import sys
import os
import signal
import time
import subprocess

# NFM-SV Server Configuration
SERVER_URL = "ws://localhost:8000/ws/smoke_test_session_123"
API_URL = "http://localhost:8000/api/mercury/status"
SERVER_CMD = [sys.executable, os.path.join(os.path.dirname(__file__), "..", "web", "server.py")]

async def test_websocket_connection():
    """Test 1: Verify WebSocket connection can be established and receives init message."""
    print("[TEST 1] Connecting to WebSocket...", end=" ")
    try:
        async with websockets.connect(SERVER_URL) as ws:
            # Wait for initialization message
            msg = await asyncio.wait_for(ws.recv(), timeout=5)
            data = json.loads(msg)
            if data.get("type") == "message":
                print("✅ PASSED")
                return True
            else:
                print(f"❌ FAILED: Unexpected message type {data.get('type')}")
                return False
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

async def test_chat_interaction():
    """Test 2: Verify chat loop handles user input without crashing."""
    print("[TEST 2] Sending chat message...", end=" ")
    try:
        async with websockets.connect(SERVER_URL) as ws:
            # Wait for init
            await asyncio.wait_for(ws.recv(), timeout=5)
            
            # Send chat
            await ws.send(json.dumps({"type": "chat", "text": "Hello NFM-SV!"}))
            
            # Expect a 'thinking' or 'message' response
            response = await asyncio.wait_for(ws.recv(), timeout=10)
            data = json.loads(response)
            
            # Check if it's a valid response type
            valid_types = ["thinking", "message", "routing"]
            if data.get("type") in valid_types:
                print("✅ PASSED")
                return True
            else:
                print(f"❌ FAILED: Invalid response {data.get('type')}")
                return False
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

async def test_mercury_api():
    """Test 3: Verify Mercury Status API."""
    print("[TEST 3] Checking Mercury API...", end=" ")
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if "status" in data:
                        print("✅ PASSED")
                        return True
                    else:
                        print("❌ FAILED: Invalid JSON structure")
                        return False
                else:
                    print(f"❌ FAILED: Status {resp.status}")
                    return False
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

async def main():
    print("=" * 50)
    print("  NFM-SV Smoke Test Suite")
    print("=" * 50)
    
    # Start server
    print("\nStarting NFM-SV server...")
    process = subprocess.Popen(
        SERVER_CMD,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    await asyncio.sleep(3) # Wait for server to boot
    
    # Run tests
    results = []
    results.append(await test_websocket_connection())
    results.append(await test_chat_interaction())
    results.append(await test_mercury_api())
    
    # Stop server
    print("\nStopping server...")
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        
    print("\n" + "=" * 50)
    if all(results):
        print("ALL TESTS PASSED ✅")
    else:
        print(f"TESTS FAILED ❌ ({results.count(False)} failed)")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
