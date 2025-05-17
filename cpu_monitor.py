import psutil
import time

def monitor_cpu(threshold=90):
    while True:
        cpu_usage = psutil.cpu_percent(interval=1)
        print(f"CPU Usage: {cpu_usage}%")
        if cpu_usage > threshold:
            print("ALERT: CPU usage is above threshold!")
        time.sleep(5)

if __name__ == "__main__":
    monitor_cpu()
