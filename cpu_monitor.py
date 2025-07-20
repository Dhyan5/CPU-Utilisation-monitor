import psutil
import GPUtil
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from collections import deque
import time

# === Configuration ===
UPDATE_INTERVAL = 1000  # milliseconds
DATA_POINTS = 60

def get_gpu_load():
    try:
        gpus = GPUtil.getGPUs()
        if gpus:
            return gpus[0].load * 100
    except Exception:
        pass
    return None

def format_speed(value_kb):
    if value_kb >= 1024:
        return f"{value_kb/1024:.2f} MB/s"
    return f"{value_kb:.1f} KB/s"

def format_total_data(bytes_total):
    gb = bytes_total / (1024 ** 3)
    if gb >= 1:
        return f"{gb:.2f} GB"
    mb = bytes_total / (1024 ** 2)
    return f"{mb:.1f} MB"

class SystemMonitorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Real-Time System Monitor")
        self.geometry("1200x900")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title_label = ctk.CTkLabel(self, text="Real-Time System Monitor", font=("Helvetica", 26, "bold"))
        self.title_label.pack(pady=10)

        # Network Summary Panel
        self.net_summary = ctk.CTkLabel(self, text="Initializing network monitor...",
                                        font=("Consolas", 20, "bold"))
        self.net_summary.pack(pady=10)

        self.cpu_data = deque([0]*DATA_POINTS, maxlen=DATA_POINTS)
        self.memory_data = deque([0]*DATA_POINTS, maxlen=DATA_POINTS)
        self.disk_data = deque([0]*DATA_POINTS, maxlen=DATA_POINTS)
        self.gpu_data = deque([0]*DATA_POINTS, maxlen=DATA_POINTS)
        self.upload_data = deque([0]*DATA_POINTS, maxlen=DATA_POINTS)
        self.download_data = deque([0]*DATA_POINTS, maxlen=DATA_POINTS)

        self.last_net_io = psutil.net_io_counters()
        self.last_time = time.time()
        self.total_uploaded = 0
        self.total_downloaded = 0

        self.fig, self.axs = plt.subplots(6, 1, figsize=(12, 12), sharex=True)
        plt.subplots_adjust(hspace=0.6)
        plt.style.use('seaborn-v0_8-dark-palette')
        self.fig.patch.set_facecolor('#222222')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=10)

        self.update_graph()

    def update_graph(self):
        self.cpu_data.append(psutil.cpu_percent())
        self.memory_data.append(psutil.virtual_memory().percent)
        self.disk_data.append(psutil.disk_usage('/').percent)
        gpu_load = get_gpu_load()
        self.gpu_data.append(gpu_load if gpu_load is not None else 0)

        current_net_io = psutil.net_io_counters()
        current_time = time.time()
        time_diff = current_time - self.last_time

        upload_speed = (current_net_io.bytes_sent - self.last_net_io.bytes_sent) / time_diff / 1024
        download_speed = (current_net_io.bytes_recv - self.last_net_io.bytes_recv) / time_diff / 1024

        self.upload_data.append(upload_speed)
        self.download_data.append(download_speed)

        self.total_uploaded = current_net_io.bytes_sent
        self.total_downloaded = current_net_io.bytes_recv

        self.last_net_io = current_net_io
        self.last_time = current_time

        summary_text = (
            f"⬆ Upload: {format_speed(upload_speed)}   Total: {format_total_data(self.total_uploaded)}\n"
            f"⬇ Download: {format_speed(download_speed)}   Total: {format_total_data(self.total_downloaded)}"
        )
        self.net_summary.configure(text=summary_text)

        for ax in self.axs:
            ax.clear()
            ax.set_facecolor('#1c1c1c')
            ax.tick_params(axis='x', colors='white', labelsize=10)
            ax.tick_params(axis='y', colors='white', labelsize=10)

        self.plot_graph(self.axs[0], self.cpu_data, "CPU Usage (%)", 'red')
        self.plot_graph(self.axs[1], self.memory_data, "Memory Usage (%)", 'blue')
        self.plot_graph(self.axs[2], self.disk_data, "Disk Usage (%)", 'green')
        self.plot_graph(self.axs[3], self.gpu_data,
                        "GPU Load (%)" if gpu_load is not None else "GPU Load (Not Detected)",
                        'purple')
        self.plot_graph(self.axs[4], self.upload_data, "Upload Speed", 'orange', unit=format_speed(upload_speed))
        self.plot_graph(self.axs[5], self.download_data, "Download Speed", 'cyan', unit=format_speed(download_speed))

        self.canvas.draw()
        self.after(UPDATE_INTERVAL, self.update_graph)

    def plot_graph(self, ax, data, title, color, unit=None):
        ax.plot(list(data), color=color, linewidth=3)
        ax.set_title(title, fontsize=14, color='white', pad=12)
        ax.grid(True, linestyle='--', alpha=0.3)

        latest_value = data[-1]
        display_text = f"{latest_value:.1f}"

        if unit:
            display_text = unit

        ax.text(len(data) - 1, latest_value + (latest_value * 0.05) + 1,
                display_text,
                color='white', fontsize=10, fontweight='bold', ha='right')

        if "Usage" in title or "Load" in title:
            ax.set_ylim(0, 100)

if __name__ == "__main__":
    app = SystemMonitorApp()
    app.mainloop()
