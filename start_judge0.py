# start_judge0.py - Helper script to start local Judge0 instance
import subprocess
import sys
import time
import requests

def check_docker():
    """Check if Docker is installed and running"""
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✅ Docker is installed:", result.stdout.strip())
            return True
        else:
            print("❌ Docker not found")
            return False
    except FileNotFoundError:
        print("❌ Docker is not installed")
        print("\n📥 Install Docker Desktop from: https://www.docker.com/products/docker-desktop")
        return False
    except Exception as e:
        print(f"❌ Error checking Docker: {e}")
        return False

def check_docker_running():
    """Check if Docker daemon is running"""
    try:
        result = subprocess.run(
            ["docker", "ps"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✅ Docker daemon is running")
            return True
        else:
            print("❌ Docker daemon is not running")
            print("\n💡 Start Docker Desktop application first!")
            return False
    except Exception as e:
        print(f"❌ Docker daemon not accessible: {e}")
        return False

def check_judge0_running():
    """Check if Judge0 is already running"""
    try:
        response = requests.get("http://localhost:2358", timeout=2)
        print("✅ Judge0 is already running on port 2358!")
        return True
    except:
        return False

def start_judge0():
    """Start Judge0 using docker-compose"""
    print("\n" + "=" * 60)
    print("🚀 Starting Judge0 Local Instance")
    print("=" * 60)
    print()
    
    # Check Docker
    if not check_docker():
        return False
    
    if not check_docker_running():
        return False
    
    # Check if already running
    if check_judge0_running():
        return True
    
    print("\n📦 Starting Judge0 containers...")
    print("   This may take a few minutes on first run...")
    print()
    
    try:
        # Change to Judge0 directory and start
        import os
        judge0_dir = os.path.join(os.path.dirname(__file__), 'Judge0')
        
        result = subprocess.run(
            ["docker-compose", "up", "-d"],
            cwd=judge0_dir,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print("✅ Docker containers started!")
            print()
            print("⏳ Waiting for Judge0 API to be ready...")
            
            # Wait for API to be ready
            for i in range(30):
                time.sleep(2)
                try:
                    response = requests.get("http://localhost:2358/about", timeout=2)
                    if response.status_code == 200:
                        print("✅ Judge0 API is ready!")
                        print()
                        print("=" * 60)
                        print("🎉 Judge0 is running on http://localhost:2358")
                        print("=" * 60)
                        print()
                        print("You can now run code in CODEX without internet!")
                        print()
                        return True
                except:
                    print(f"   Waiting... ({i+1}/30)")
            
            print("⚠️  Judge0 started but API not responding yet")
            print("   Give it a minute and try running code")
            return True
        else:
            print("❌ Failed to start Docker containers")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout starting Docker containers")
        return False
    except Exception as e:
        print(f"❌ Error starting Judge0: {e}")
        return False

def stop_judge0():
    """Stop Judge0 containers"""
    print("\n🛑 Stopping Judge0...")
    try:
        import os
        judge0_dir = os.path.join(os.path.dirname(__file__), 'Judge0')
        
        result = subprocess.run(
            ["docker-compose", "down"],
            cwd=judge0_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ Judge0 stopped")
            return True
        else:
            print("❌ Error stopping Judge0")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def show_status():
    """Show Judge0 status"""
    print("\n" + "=" * 60)
    print("📊 Judge0 Status")
    print("=" * 60)
    print()
    
    if check_judge0_running():
        print("✅ Judge0 is RUNNING on http://localhost:2358")
        print()
        print("You can now:")
        print("  • Run code without internet")
        print("  • Stop with: python start_judge0.py stop")
    else:
        print("❌ Judge0 is NOT running")
        print()
        print("To start Judge0:")
        print("  • Run: python start_judge0.py")
        print("  • Or: python start_judge0.py start")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "stop":
            stop_judge0()
        elif command == "status":
            show_status()
        elif command == "start":
            start_judge0()
        else:
            print("Usage: python start_judge0.py [start|stop|status]")
    else:
        # Default: start
        success = start_judge0()
        if not success:
            print("\n💡 Troubleshooting:")
            print("  • Make sure Docker Desktop is running")
            print("  • Try: docker-compose up -d (in Judge0 folder)")
            print("  • Check: docker ps")
