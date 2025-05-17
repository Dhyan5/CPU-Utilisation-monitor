import psutil
import GPUtil
import time
import logging
from datetime import datetime

CPU_THRESHOLD = 85
GPU_THRESHOLD = 85
CHECK_INTERVAL = 5
LOG_FILE = "full_system_monitor.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def get_gpu_info():
    gpus = GPUtil.getGPUs()
    for gpu in gpus:
        return {
            "name": gpu.name,
            "load": gpu.load * 100,
            "memory_used": gpu.memoryUsed,
            "memory_total": gpu.memoryTotal,
            "temperature": gpu.temperature
        }
    return None

def get_network_info():
    net = psutil.net_io_counters()
    return {
        "bytes_sent": net.bytes_sent,
        "bytes_recv": net.bytes_recv
    }

def monitor_system():
    print("📊 Starting system monitor. Press Ctrl+C to stop.")
    try:
        while True:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            gpu_info = get_gpu_info()
            net_info = get_network_info()

            print(f"\n🕒 {timestamp}")
            print(f"CPU Usage: {cpu:.2f}%")
            print(f"Memory Usage: {memory:.2f}%")
            print(f"Disk Usage: {disk:.2f}%")

            if gpu_info:
                print(f"GPU: {gpu_info['name']}")
                print(f"  GPU Load: {gpu_info['load']:.2f}%")
                print(f"  GPU Memory: {gpu_info['memory_used']} / {gpu_info['memory_total']} MB")
                print(f"  Temperature: {gpu_info['temperature']}°C")
            else:
                print("No GPU detected.")

            print(f"Network - Sent: {net_info['bytes_sent']} bytes, Received: {net_info['bytes_recv']} bytes")

            log_msg = (
                f"CPU: {cpu}%, Memory: {memory}%, Disk: {disk}%, "
                f"Net Sent: {net_info['bytes_sent']} B, Recv: {net_info['bytes_recv']} B"
            )
            if gpu_info:
                log_msg += f", GPU Load: {gpu_info['load']}%, Temp: {gpu_info['temperature']}°C"
            logging.info(log_msg)

            if cpu > CPU_THRESHOLD:
                logging.warning(f"⚠️ High CPU usage: {cpu}%")
            if gpu_info and gpu_info["load"] > GPU_THRESHOLD:
                logging.warning(f"⚠️ High GPU usage: {gpu_info['load']}%")

            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped.")
        logging.info("Monitoring stopped manually.")

if __name__ == "__main__":
    monitor_system()
