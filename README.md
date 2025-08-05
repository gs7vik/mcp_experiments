Just a weekend exploration on MCP. 
# System Information MCP Server

This MCP (Management and Control Protocol) server provides a set of tools and resources for retrieving real-time system information, including time, memory, CPU, and disk usage.

## Features

  * **Current Time:** Get the current time in both IST (India Standard Time) and UTC.
  * **Memory Stats:** Check total, used, and available system memory.
  * **CPU Info:** Monitor CPU usage percentage, core count, frequency, and load average.
  * **Disk Usage:** See disk space statistics for the root partition.
  * **Platform Info:** Retrieve detailed platform and OS information.
  * **Port Monitoring:** Use `netstat` to find the process using a specific port (Windows only).
  * **System Uptime:** Get the total time the system has been running.

## Demo

Watch a short video demonstrating how to set up and use the System Info MCP Server.

[Working Demo](https://youtu.be/3i-mZcZJQHg)


## Getting Started

### 1\. Prerequisites

Make sure you have `uv` installed, as it's used for managing dependencies and running the server.

### 2\. Installation and Setup

1.  Save the provided code as a Python file named `system_info_server.py`.

2.  Install the necessary dependencies using `uv`. The `mcp[cli]` package provides the command-line interface for the server, `psutil` is used for system stats, and `pytz` handles timezone information.

    ```bash
    uv add "mcp[cli]" psutil pytz
    ```

### 3\. Running the Server

You have two options for running the server:

#### **Option A: Run in Development Mode**

This is the best option for testing and development. The server will run locally and you can interact with it using the MCP CLI.

```bash
uv run mcp dev system_info_server.py
```

#### **Option B: Install in Claude Desktop**

If you are using Claude Desktop, you can install the server as an available tool.

```bash
uv run mcp install system_info_server.py
```
#### **Option C: Use in VS Code Copilot**

If you are using VS copilot then go to copilot->Agent mode->Configure tools icon and check if your tools are present, if they are not present go to extensions in VS code, there you should be able to see your MCP server. right click and start/restart the server.

## How to Use

Once the server is running, you can interact with its tools and resources.

### Example Commands

  * **Get comprehensive system info:**

    ```bash
    mcp system_info_server get_system_info
    ```

  * **Get current memory usage:**

    ```bash
    mcp system_info_server get_memory_usage
    ```

  * **Get system uptime:**

    ```bash
    mcp system_info_server get_system_uptime
    ```

  * **Check which process is using a specific port (e.g., port 8080):**

    ```bash
    mcp system_info_server get_port_info_netstat --port 8080
    ```

## Code Reference

The server exposes the following tools and resources:

### Tools

  * `get_current_time()`: Gets the current time and timestamp.
  * `get_memory_usage()`: Gets detailed memory statistics.
  * `get_cpu_usage()`: Gets CPU usage, core count, and frequency.
  * `get_disk_usage()`: Gets disk usage for the root partition.
  * `get_system_info()`: A comprehensive tool that combines all of the above.
  * `get_port_info_netstat(port: int)`: Uses `netstat` to find the process ID (PID) for a given port.

### Resources

  * `system://platform`: Provides static platform and OS information.
  * `system://uptime`: Provides a human-readable string of the system's uptime.
  * `greeting://{name}`: Provides a personalized greeting.

### Prompts

  * `system_status_prompt()`: Generates a prompt for a comprehensive status report.
  * `performance_check_prompt()`: Generates a prompt for a performance analysis.