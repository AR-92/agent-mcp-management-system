# Troubleshooting MCP Servers

This guide helps diagnose and resolve common issues with MCP servers.

## Connection Issues

### Server Not Starting
- **Symptom**: Server fails to start or crashes immediately
- **Causes**:
  - Port already in use
  - Insufficient permissions
  - Configuration errors
- **Solutions**:
  - Check if the configured port is already in use: `netstat -tuln | grep :3000`
  - Verify configuration file syntax
  - Check file permissions for required files

### Clients Cannot Connect
- **Symptom**: Clients receive connection refused errors
- **Causes**:
  - Server not listening on the correct interface
  - Firewall blocking the port
  - Incorrect host configuration
- **Solutions**:
  - Verify server is listening on the correct interface (use `0.0.0.0` for all interfaces)
  - Check firewall rules: `sudo ufw status`
  - Confirm client is connecting to the right host/port

## Performance Issues

### High Memory Usage
- **Symptom**: Server memory usage grows over time
- **Causes**:
  - Memory leaks
  - Large message buffers
  - Excessive connections
- **Solutions**:
  - Monitor memory usage over time
  - Reduce buffer sizes if set too high
  - Implement connection limits

### Slow Response Times
- **Symptom**: Requests taking longer than expected
- **Causes**:
  - Overloaded server
  - Network latency
  - Blocking operations
- **Solutions**:
  - Monitor server CPU and memory usage
  - Check for blocking operations in message handlers
  - Consider scaling horizontally

## Protocol Issues

### Invalid Message Format
- **Symptom**: Receiving error code 1001
- **Causes**:
  - Malformed JSON message
  - Missing required fields
  - Incorrect message structure
- **Solutions**:
  - Validate message structure against protocol specification
  - Check JSON formatting
  - Ensure all required fields are present

### Authentication Failures
- **Symptom**: Receiving error code 1002
- **Causes**:
  - Incorrect API key
  - Expired credentials
  - Missing authentication headers
- **Solutions**:
  - Verify API key is correct
  - Check if credentials have expired
  - Ensure authentication headers are properly set

## Monitoring and Logging

### Enable Debug Logging
To troubleshoot issues, enable debug logging:

```env
MCP_LOG_LEVEL=DEBUG
```

This will provide more detailed information about server operations.

### Log Analysis
Look for these patterns in logs:
- Connection attempts and failures
- Request/response cycles
- Error messages and stack traces
- Performance metrics

### Common Log Entries
- `CONNECTION_OPENED`: New client connection
- `CONNECTION_CLOSED`: Client disconnected
- `MESSAGE_RECEIVED`: Message received
- `MESSAGE_SENT`: Message sent
- `ERROR_*`: Various error conditions

## Diagnostic Commands

### Check Server Status
```bash
# Check if server process is running
ps aux | grep mcp-server

# Check if server is listening on expected port
netstat -tuln | grep :3000

# Check network connections
ss -tuln | grep :3000
```

### Resource Usage
```bash
# Check memory usage
free -h

# Check CPU usage
top -p $(pgrep mcp-server)

# Check disk space
df -h
```

## Recovery Steps

### Restart Server Safely
1. Allow existing connections to complete or time out
2. Send shutdown signal: `kill -TERM <server_pid>`
3. Wait for graceful shutdown (check logs)
4. Restart the server

### Rollback Configuration
If a configuration change caused issues:
1. Keep the old configuration file as backup
2. Revert to the previous configuration
3. Restart the server
4. Monitor for resolution of issues