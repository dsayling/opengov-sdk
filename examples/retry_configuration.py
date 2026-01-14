"""
Example: Configuring Retry Behavior

This example demonstrates how to configure the retry behavior for API calls,
including exponential backoff settings and maximum retry attempts.
"""

import opengov_api

# Configure client
opengov_api.set_api_key("your-api-key")
opengov_api.set_community("yourcommunity")


# Example 1: Use default retry settings
# - max_retries: 3
# - initial_delay: 1.0 seconds
# - max_delay: 60.0 seconds
# - backoff_multiplier: 2.0 (delays: 1s, 2s, 4s, ...)
# - jitter_factor: 0.1 (10% random jitter)
print("Using default retry settings:")
try:
    response = opengov_api.list_records()
    data = response.data
    count = len(data) if isinstance(data, list) else 1
    print(f"Retrieved {count} records")
except (opengov_api.OpenGovAPIStatusError, opengov_api.OpenGovAPIConnectionError) as e:
    print(f"Error: {e}")
    print(f"Failed after {e.attempts} attempts")
except opengov_api.OpenGovAPIError as e:
    print(f"Error: {e}")


# Example 2: Configure for more aggressive retries
# Useful for rate-limited APIs or flaky connections
opengov_api.configure_retries(
    max_retries=5,  # Try up to 5 times
    initial_delay=0.5,  # Start with shorter delay
    backoff_multiplier=1.5,  # Slower growth (0.5s, 0.75s, 1.125s, ...)
)

print("\nUsing aggressive retry settings:")
try:
    response = opengov_api.list_records()
    data = response.data
    count = len(data) if isinstance(data, list) else 1
    print(f"Retrieved {count} records")
except (opengov_api.OpenGovAPIStatusError, opengov_api.OpenGovAPIConnectionError) as e:
    print(f"Error: {e}")
    print(f"Failed after {e.attempts} attempts")
except opengov_api.OpenGovAPIError as e:
    print(f"Error: {e}")


# Example 3: Configure for production with longer delays
# Better for production to avoid overwhelming servers
opengov_api.configure_retries(
    max_retries=3,
    initial_delay=2.0,  # Start with longer delay
    max_delay=120.0,  # Allow longer maximum delays
    backoff_multiplier=3.0,  # Faster growth (2s, 6s, 18s, ...)
    jitter_factor=0.2,  # More jitter (20%)
)

print("\nUsing production retry settings:")
try:
    response = opengov_api.list_records()
    data = response.data
    count = len(data) if isinstance(data, list) else 1
    print(f"Retrieved {count} records")
except (opengov_api.OpenGovAPIStatusError, opengov_api.OpenGovAPIConnectionError) as e:
    print(f"Error: {e}")
    print(f"Failed after {e.attempts} attempts")
except opengov_api.OpenGovAPIError as e:
    print(f"Error: {e}")


# Example 4: Disable retries entirely
# Useful for debugging or when you want fast failures
opengov_api.configure_retries(max_retries=0)

print("\nWith retries disabled:")
try:
    response = opengov_api.list_records()
    data = response.data
    count = len(data) if isinstance(data, list) else 1
    print(f"Retrieved {count} records")
except (opengov_api.OpenGovAPIStatusError, opengov_api.OpenGovAPIConnectionError) as e:
    print(f"Error: {e}")
    print(f"Failed after {e.attempts} attempts (no retries)")
except opengov_api.OpenGovAPIError as e:
    print(f"Error: {e}")


# Example 5: Get current retry configuration
config = opengov_api.get_retry_config()
print("\nCurrent retry configuration:")
print(f"  max_retries: {config.max_retries}")
print(f"  initial_delay: {config.initial_delay}s")
print(f"  max_delay: {config.max_delay}s")
print(f"  backoff_multiplier: {config.backoff_multiplier}")
print(f"  jitter_factor: {config.jitter_factor}")


# Example 6: Configure only specific settings
# Other settings remain at their current values
opengov_api.configure_retries(
    max_retries=2,  # Only change max_retries
    # initial_delay, max_delay, etc. keep their current values
)

print("\nPartially updated configuration:")
config = opengov_api.get_retry_config()
print(f"  max_retries: {config.max_retries}")
print(f"  initial_delay: {config.initial_delay}s")


# Note: Retries apply to:
# - HTTP 429 (Rate Limit) errors
# - HTTP 500+ (Server Error) errors
# - Network timeouts
# - Connection errors
#
# Non-retryable errors (fail immediately):
# - HTTP 400 (Bad Request)
# - HTTP 401 (Unauthorized)
# - HTTP 403 (Forbidden)
# - HTTP 404 (Not Found)
