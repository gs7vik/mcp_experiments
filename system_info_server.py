"""
System Information MCP Server

This MCP server provides system information including:
- Current time in IST (India Standard Time)
- System memory usage statistics
- CPU usage information
- Disk usage information

To run this server:
1. Save as system_info_server.py
2. Install dependencies: uv add "mcp[cli]" psutil pytz
3. Run with: uv run mcp dev system_info_server.py
4. Or install in Claude Desktop: uv run mcp install system_info_server.py
"""

import psutil
import platform
from datetime import datetime
from typing import TypedDict
import pytz
from pydantic import BaseModel, Field
import subprocess
import re

from mcp.server.fastmcp import FastMCP

# Create the MCP server
mcp = FastMCP("System Info Server")


# Structured output models
class TimeInfo(BaseModel):
    """Current time information"""
    current_time_ist: str = Field(description="Current time in IST format")
    current_time_utc: str = Field(description="Current time in UTC format")
    timezone: str = Field(description="Timezone identifier")
    timestamp: float = Field(description="Unix timestamp")


class MemoryInfo(BaseModel):
    """System memory usage information"""
    total_gb: float = Field(description="Total memory in GB")
    available_gb: float = Field(description="Available memory in GB")
    used_gb: float = Field(description="Used memory in GB")
    percentage_used: float = Field(description="Memory usage percentage")
    free_gb: float = Field(description="Free memory in GB")


class CPUInfo(BaseModel):
    """CPU usage information"""
    cpu_percent: float = Field(description="CPU usage percentage")
    cpu_count: int = Field(description="Number of CPU cores")
    cpu_freq_current: float = Field(description="Current CPU frequency in MHz")
    load_average: list[float] = Field(description="Load average (1, 5, 15 minutes)")


class DiskInfo(BaseModel):
    """Disk usage information"""
    total_gb: float = Field(description="Total disk space in GB")
    used_gb: float = Field(description="Used disk space in GB")
    free_gb: float = Field(description="Free disk space in GB")
    percentage_used: float = Field(description="Disk usage percentage")


class SystemInfo(BaseModel):
    """Complete system information"""
    time_info: TimeInfo
    memory_info: MemoryInfo
    cpu_info: CPUInfo
    disk_info: DiskInfo
    platform_info: dict[str, str] = Field(description="Platform and OS information")
    
class NetstatPortInfo(BaseModel):
    """Information extracted from netstat for a given port"""
    port: int
    pid: int | None
    protocol: str | None
    local_address: str | None
    foreign_address: str | None
    state: str | None
    raw_line: str


def bytes_to_gb(bytes_value: int) -> float:
    """Convert bytes to gigabytes with 2 decimal precision"""
    return round(bytes_value / (1024**3), 2)




@mcp.tool()
def get_current_time() -> TimeInfo:
    """Get the current time in IST (India Standard Time) and UTC"""
    # Get current time
    utc_now = datetime.now(pytz.UTC)
    ist_tz = pytz.timezone('Asia/Kolkata')
    ist_now = utc_now.astimezone(ist_tz)
    
    return TimeInfo(
        current_time_ist=ist_now.strftime("%Y-%m-%d %H:%M:%S %Z"),
        current_time_utc=utc_now.strftime("%Y-%m-%d %H:%M:%S %Z"),
        timezone="Asia/Kolkata (IST)",
        timestamp=utc_now.timestamp()
    )


@mcp.tool()
def get_memory_usage() -> MemoryInfo:
    """Get current system memory usage statistics"""
    memory = psutil.virtual_memory()
    
    return MemoryInfo(
        total_gb=bytes_to_gb(memory.total),
        available_gb=bytes_to_gb(memory.available),
        used_gb=bytes_to_gb(memory.used),
        percentage_used=round(memory.percent, 1),
        free_gb=bytes_to_gb(memory.free)
    )


@mcp.tool()
def get_cpu_usage() -> CPUInfo:
    """Get current CPU usage and information"""
    # Get CPU percentage (1 second interval for accuracy)
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()
    
    # Get CPU frequency
    cpu_freq = psutil.cpu_freq()
    current_freq = cpu_freq.current if cpu_freq else 0.0
    
    # Get load average (Unix-like systems only)
    try:
        load_avg = list(psutil.getloadavg())
    except (AttributeError, OSError):
        # Windows doesn't have load average
        load_avg = [0.0, 0.0, 0.0]
    
    return CPUInfo(
        cpu_percent=round(cpu_percent, 1),
        cpu_count=cpu_count,
        cpu_freq_current=round(current_freq, 1),
        load_average=[round(x, 2) for x in load_avg]
    )


@mcp.tool()
def get_disk_usage() -> DiskInfo:
    """Get disk usage for the root partition"""
    disk_usage = psutil.disk_usage('/')
    
    return DiskInfo(
        total_gb=bytes_to_gb(disk_usage.total),
        used_gb=bytes_to_gb(disk_usage.used),
        free_gb=bytes_to_gb(disk_usage.free),
        percentage_used=round((disk_usage.used / disk_usage.total) * 100, 1)
    )


@mcp.tool()
def get_system_info() -> SystemInfo:
    """Get comprehensive system information including time, memory, CPU, and disk usage"""
    return SystemInfo(
        time_info=get_current_time(),
        memory_info=get_memory_usage(),
        cpu_info=get_cpu_usage(),
        disk_info=get_disk_usage(),
        platform_info={
            "system": platform.system(),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "hostname": platform.node()
        }
    )


# Resources for static information
@mcp.resource("system://platform")
def get_platform_info() -> str:
    """Get platform and system information"""
    info = {
        "System": platform.system(),
        "Platform": platform.platform(),
        "Machine": platform.machine(),
        "Processor": platform.processor(),
        "Python Version": platform.python_version(),
        "Hostname": platform.node()
    }
    
    return "\n".join(f"{key}: {value}" for key, value in info.items())






@mcp.tool()
def get_port_info_netstat(port: int) -> NetstatPortInfo:
    """Use netstat -ano to find the process using a given port on Windows"""
    try:
        # Run netstat command
        result = subprocess.run(["netstat", "-ano"], capture_output=True, text=True, shell=True)
        output = result.stdout

        # Match lines with the port
        for line in output.splitlines():
            if f":{port} " in line:  # Ensure space after port to avoid partial matches
                parts = re.split(r"\s+", line.strip())
                if len(parts) >= 5:
                    proto = parts[0]
                    local_address = parts[1]
                    foreign_address = parts[2]
                    state = parts[3] if proto.lower() == "tcp" else ""
                    pid = int(parts[-1])
                    return NetstatPortInfo(
                        port=port,
                        pid=pid,
                        protocol=proto,
                        local_address=local_address,
                        foreign_address=foreign_address,
                        state=state,
                        raw_line=line.strip()
                    )

        return NetstatPortInfo(
            port=port,
            pid=None,
            protocol=None,
            local_address=None,
            foreign_address=None,
            state=None,
            raw_line="Not found"
        )

    except Exception as e:
        return NetstatPortInfo(
            port=port,
            pid=None,
            protocol=None,
            local_address=None,
            foreign_address=None,
            state=None,
            raw_line=f"Error: {str(e)}"
        )


@mcp.resource("system://uptime")
def get_system_uptime() -> str:
    """Get system uptime"""
    try:
        boot_time = psutil.boot_time()
        uptime_seconds = datetime.now().timestamp() - boot_time
        
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        
        return f"System uptime: {days} days, {hours} hours, {minutes} minutes"
    except Exception as e:
        return f"Unable to get uptime: {e}"


# Prompts for common queries
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello unga bunga, {name}!"


@mcp.prompt()
def system_status_prompt() -> str:
    """Generate a prompt for getting comprehensive system status"""
    return """Please provide a comprehensive system status report including:
1. Current date and time in IST
2. Memory usage statistics
3. CPU usage and load
4. Disk space availability
5. System uptime and platform information

Format the response in a clear, readable manner with proper sections."""


@mcp.prompt()
def performance_check_prompt() -> str:
    """Generate a prompt for performance monitoring"""
    return """Check the current system performance and provide analysis on:
1. Is the memory usage within acceptable limits?
2. Is the CPU usage normal?
3. Is there sufficient disk space available?
4. Any performance concerns or recommendations?"""


def main():
    """Entry point for direct execution"""
    mcp.run()


if __name__ == "__main__":
    main()