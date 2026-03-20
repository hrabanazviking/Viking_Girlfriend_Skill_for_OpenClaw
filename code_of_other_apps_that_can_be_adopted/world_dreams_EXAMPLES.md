# world_dreams_EXAMPLES.md

## Basic Usage

### Import and Initialize
```python
from systems.world_dreams import WorldDreams

# Initialize with default config
instance = WorldDreams(data_path="data")

# Or with custom config
config = {"key": "value"}
instance = WorldDreams(config=config)
```

### Common Operations
```python
# Basic operation
result = instance.process(data)

# With options
result = instance.process(
    data,
    option1=True,
    option2="value"
)

# Error handling
try:
    result = instance.process(data)
except Exception as e:
    logger.error(f"Processing failed: {e}")
```

## Advanced Patterns

### Batch Processing
```python
# Process multiple items
results = []
for item in items:
    result = instance.process(item)
    results.append(result)
```

### Context Manager
```python
# Use with context manager
with WorldDreams() as instance:
    result = instance.process(data)
    # Auto-cleanup on exit
```
