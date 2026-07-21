# Add metadata labels
LABEL maintainer="MCP SAP GUI" \
      description="MCP SAP GUI Server Container" \
      version="0.1.3"

# Set shell to PowerShell
SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'SilentlyContinue';"]

# Install Python 3.11
RUN Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe' -OutFile 'python-installer.exe'; `
    Start-Process python-installer.exe -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -Wait; `
    Remove-Item python-installer.exe

# Install Node.js LTS
RUN Invoke-WebRequest -Uri 'https://nodejs.org/dist/v20.11.1/node-v20.11.1-x64.msi' -OutFile 'node-installer.msi'; `
    Start-Process msiexec.exe -ArgumentList '/i node-installer.msi /quiet /norestart' -Wait; `
    Remove-Item node-installer.msi

# Create non-root user
RUN net user /add mcp_user && `
    net localgroup administrators mcp_user /add

# Set working directory
WORKDIR /app

# Install the published package
RUN pip install mcp-sap-gui && `
    npm install -g @modelcontextprotocol/inspector && `
    icacls "C:\app" /grant "mcp_user:(OI)(CI)F"

# Copy only the credentials template
COPY credentials.env.example ./credentials.env

# Note: SAP GUI installation should be handled separately as it requires licensing
# The container should be run on a host with SAP GUI installed

# Switch to non-root user
USER mcp_user

# # Add healthcheck
# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 `
#     CMD powershell -Command `
#     try { `
#         $process = Get-Process -Name "python" -ErrorAction Stop; `
#         if ($process.MainWindowTitle -match "sap_gui_server") { exit 0 } else { exit 1 } `
#     } catch { exit 1 }

# Run the server
CMD ["python", "-m", "sap_gui_server.server"]
