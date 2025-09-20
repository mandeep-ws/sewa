# SEWA Logging System

The SEWA application includes a comprehensive logging system that allows you to control the verbosity of log messages through command-line arguments.

## Quick Start

### Using the Launcher Script (Recommended)

```bash
# Start with default INFO level
python3 run_sewa.py

# Start with DEBUG level for detailed logging
python3 run_sewa.py --log-level DEBUG

# Start with WARNING level (minimal output)
python3 run_sewa.py --log-level WARNING

# Start with custom log file
python3 run_sewa.py --log-level INFO --log-file logs/my_session.log

# Start in quiet mode (ERROR level only)
python3 run_sewa.py --quiet
```

### Using Streamlit Directly

```bash
# Start with DEBUG level
streamlit run app.py -- --log-level DEBUG

# Start with custom log file
streamlit run app.py -- --log-level INFO --log-file logs/sewa.log

# Start with WARNING level
streamlit run app.py -- --log-level WARNING
```

## Log Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| **DEBUG** | Detailed diagnostic information | Development, troubleshooting |
| **INFO** | General information about program execution | Normal operation |
| **WARNING** | Something unexpected happened, but the program is still working | Monitoring issues |
| **ERROR** | A serious problem occurred | Error tracking |
| **CRITICAL** | A very serious error occurred | System failures |

## Command-Line Options

### Logging Options

- `--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}`: Set the logging level (default: INFO)
- `--log-file LOG_FILE`: Log file path (default: console only)
- `--quiet`: Suppress all console output (ERROR level only)

### Application Options

- `--port PORT`: Streamlit server port (default: 8501)
- `--headless`: Run Streamlit in headless mode

## Examples

### Development and Debugging
```bash
# Full debug output with log file
python3 run_sewa.py --log-level DEBUG --log-file logs/debug_session.log
```

### Production Monitoring
```bash
# Only warnings and errors
python3 run_sewa.py --log-level WARNING --log-file logs/production.log
```

### Quiet Operation
```bash
# Minimal output, only errors
python3 run_sewa.py --quiet
```

### Custom Port
```bash
# Run on different port with debug logging
python3 run_sewa.py --port 8502 --log-level DEBUG
```

## Log File Locations

- **Default**: `logs/sewa_YYYYMMDD_HHMMSS.log`
- **Custom**: Specify with `--log-file` option
- **Console Only**: Don't specify `--log-file` option

## Log Message Format

```
2025-09-20 08:07:00 - sewa - INFO - Phone validation completed for 150 records
2025-09-20 08:07:15 - sewa - DEBUG - Processing record 1/150: John Doe
2025-09-20 08:07:30 - sewa - WARNING - API rate limit approaching
2025-09-20 08:07:45 - sewa - ERROR - Failed to validate address: Invalid API key
```

## Module-Specific Logging

Each module uses the centralized logging system:

- **Phone Validator**: Logs validation progress and API calls
- **Address Validator**: Logs geocoding requests and rate limiting
- **Duplicate Detector**: Logs matching algorithms and results
- **Message Sender**: Logs SMS/WhatsApp sending attempts
- **UI Components**: Logs user interactions and data processing

## Best Practices

### For Development
- Use `DEBUG` level to see detailed execution flow
- Enable log files to track issues over time
- Monitor API rate limits and validation errors

### For Production
- Use `WARNING` or `ERROR` level to reduce noise
- Always enable log files for audit trails
- Monitor error rates and system performance

### For Troubleshooting
- Start with `DEBUG` level to identify issues
- Check log files for patterns in errors
- Use `INFO` level for normal operation monitoring

## Log File Management

Log files are automatically created in the `logs/` directory with timestamps. Consider:

- **Rotation**: Implement log rotation for long-running systems
- **Cleanup**: Regularly clean old log files
- **Monitoring**: Set up alerts for ERROR and CRITICAL messages
- **Backup**: Include log files in your backup strategy

## Integration with Streamlit

The logging system integrates seamlessly with Streamlit:

- Log messages appear in the console where Streamlit is running
- Log files are created in the background
- No impact on Streamlit's built-in logging
- Compatible with Streamlit's rerun behavior
