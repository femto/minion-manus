# Minion-Manus Logging System

The Minion-Manus project provides a flexible, powerful logging system that builds on the [Loguru](https://github.com/Delgan/loguru) library while maintaining compatibility with the patterns from the original Minion project.

## Basic Usage

```python
from loguru import logger
from minion_manus.utils import setup_logging

# Initialize logging
setup_logging()

# Log at various levels
logger.debug("This is a debug message")
logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")
logger.critical("This is a critical message")
```

## Module-Specific Logging

For module-specific logging with custom configuration, use the `define_log_level` function:

```python
from minion_manus.utils import define_log_level

# Create a module-specific logger
logger = define_log_level(
    print_level="DEBUG",
    logfile_level="INFO",
    name="browser_use"
)

# Now use this logger
logger.info("Browser module initialized")
```

This will:
1. Configure console logging at DEBUG level
2. Configure file logging at INFO level
3. Create a log file with the prefix "browser_use_" followed by the date
4. Return a logger instance you can use in your module

## LLM Stream Logging

For handling streaming output from Large Language Models (LLMs), the library provides special functions:

```python
from minion_manus.utils import log_llm_stream, set_llm_stream_logfunc

# Optional: Define a custom function for streaming logs
def custom_stream_log(msg):
    print(f"🤖 {msg}", end="")

# Set the custom function (optional)
set_llm_stream_logfunc(custom_stream_log)

# Log streaming chunks without line breaks
log_llm_stream("Hello, ")
log_llm_stream("world!")
```

## Configuration via Environment Variables

The logging system can be configured using these environment variables:

| Variable | Purpose | Default |
|----------|---------|---------|
| `MINION_MANUS_LOG_LEVEL` | Set the default logging level | `"INFO"` |
| `MINION_MANUS_LOG_FORMAT` | Define the log format | See below |
| `MINION_MANUS_LOG_FILE` | Path to log file (optional) | None |

The default format is:
```
<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>
```

This provides:
- Green timestamps with millisecond precision
- Padded, colored log levels for alignment
- Cyan module/function/line information
- Colored message based on log level

## Full Example

See the [logging example](../examples/logging_example.py) for a complete demonstration of all the logging features.

## Advanced Configuration

For more advanced configuration options, refer to the [Loguru documentation](https://loguru.readthedocs.io/en/stable/api/logger.html). 