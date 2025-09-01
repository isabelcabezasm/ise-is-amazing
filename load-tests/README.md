# Load Testing for Amazing API

This directory contains comprehensive load testing tools for the `/api/amazing` POST endpoint.

## 🎯 Overview

The load tests simulate real user behavior by sending positive messages (that should be accepted) and negative messages (that should be rejected by semantic validation) to test the API's performance and reliability.

## 📋 Available Test Scripts

### 1. Simple Load Test (`load_test_simple.py`)

- ✅ **No additional dependencies** (uses built-in `requests` library)
- 🔄 Multi-threaded execution
- 📊 Detailed performance metrics
- 🏥 Built-in health check

### 2. Async Load Test (`load_test_async.py`)

- 🚀 High-performance async execution using `aiohttp`
- ⚡ Better for high concurrency scenarios
- 📈 Advanced metrics and reporting
- Requires: `pip install aiohttp`

### 3. Locust Load Test (`load_test_locust.py`)

- 🌐 Web-based GUI for test configuration
- 📊 Real-time metrics dashboard
- 🔄 Dynamic scaling during tests
- Requires: `pip install locust`

## 🚀 Quick Start

### Option 1: Use the Runner Script (Recommended)

```bash
# Run simple test with defaults (5 users, 10 requests each)
./run_load_test.sh

# Run with custom parameters
./run_load_test.sh -c 20 -r 50

# Run async test for higher performance
./run_load_test.sh -t async -c 50 -r 100

# Start Locust web interface
./run_load_test.sh -t locust
```

### Option 2: Run Tests Directly

```bash
# Simple test (no extra dependencies)
python load_test_simple.py --users 10 --requests 20 --health

# Async test (requires aiohttp)
python load_test_async.py --users 50 --requests 100

# Locust test (requires locust)
locust -f load_test_locust.py --host=http://localhost:8000
```

## 🎯 Test Scenarios

The load tests simulate realistic usage patterns:

### Positive Messages (80% of requests) ✅

- Should be accepted by the API
- Various languages: English, Spanish, French, German, Italian, Portuguese, Dutch, Japanese, Chinese, Hebrew, Arabic
- Examples: "You are amazing!", "Eres increíble!", "Tu es fantastique!"

### Negative Messages (20% of requests) ❌

- Should be rejected by semantic validation
- Examples: "Hello world", "What time is it?", "I like pizza"

### Edge Cases

- Empty strings
- Very long messages
- Messages with emojis
- All caps messages
- Repeated content

## 📊 Metrics Collected

- **Response Times**: Mean, median, min, max, standard deviation, 95th/99th percentiles
- **Success Rate**: Percentage of requests that behaved as expected
- **Status Code Distribution**: Breakdown of HTTP response codes
- **Throughput**: Requests per second
- **Error Analysis**: Detailed error categorization
- **Concurrency Performance**: How the API handles concurrent requests

## 🔧 Configuration Options

### Environment Variables

```bash
export API_URL="http://localhost:8000"  # API base URL
export LOAD_TEST_USERS=10              # Number of concurrent users
export LOAD_TEST_REQUESTS=50           # Requests per user
```

### Command Line Arguments

```bash
--url           # API base URL (default: http://localhost:8000)
--users         # Number of concurrent users (default: 5-10)
--requests      # Number of requests per user (default: 10)
--duration      # Maximum test duration in seconds (async only)
--health        # Perform health check before tests (simple only)
```

## 📈 Expected Results

### Healthy API Performance

- ✅ Success rate: >95%
- ⏱️ Response time: <2 seconds (95th percentile)
- 🚀 Throughput: >10 requests/second
- 📊 Status codes: 200 (success), 400 (semantic validation failures)

### Performance Bottlenecks to Watch

- 🐌 High response times may indicate:
  - Azure AI service latency
  - Font loading delays for multilingual support
  - Database/storage bottlenecks
- 💥 High error rates may indicate:
  - Azure credential issues
  - Service rate limiting
  - Memory/CPU constraints

## 🛠️ Installation

### Install All Dependencies

```bash
pip install -r requirements.txt
```

### Install Individual Tools

```bash
# For async tests
pip install aiohttp

# For Locust tests
pip install locust
```

## 🎮 Usage Examples

### Basic Load Test

```bash
# Test with 10 concurrent users, 20 requests each
./run_load_test.sh -c 10 -r 20
```

### High Load Test

```bash
# Stress test with 100 concurrent users
./run_load_test.sh -t async -c 100 -r 50
```

### Interactive Testing with Locust

```bash
# Start Locust web UI at http://localhost:8089
./run_load_test.sh -t locust
```

### Custom API Endpoint

```bash
# Test against deployed API
./run_load_test.sh -u "https://your-api.azurewebsites.net" -c 20 -r 30
```

## 📋 Prerequisites

1. **API Server Running**: The Amazing API must be running at the target URL

   ```bash
   cd ../api-python
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

2. **Python Environment**: Python 3.7+ with required packages

3. **Network Access**: Ability to make HTTP requests to the API endpoint

## 🔍 Troubleshooting

### Common Issues

1. **API Not Running**

   ```
   ❌ API is not running or not healthy at http://localhost:8000
   ```

   **Solution**: Start the FastAPI server first

2. **Import Errors**

   ```
   ImportError: No module named 'aiohttp'
   ```

   **Solution**: Install dependencies with `pip install -r requirements.txt`

3. **Low Success Rate**

   - Check Azure AI credentials in `.env` file
   - Verify API is properly configured
   - Check for rate limiting

4. **High Response Times**
   - Azure AI service may be slow
   - Consider increasing timeout values
   - Check network connectivity

### Debug Mode

```bash
# Run with verbose output
python load_test_simple.py --users 1 --requests 5 --health
```

## 📊 Report Generation

Test results are automatically saved to timestamped report files:

- `load_test_report_YYYYMMDD_HHMMSS.txt`

Reports include:

- Test configuration
- Performance metrics
- Error analysis
- Recommendations

## 🎯 Next Steps

1. **Baseline Testing**: Run tests with current configuration
2. **Performance Tuning**: Identify and address bottlenecks
3. **Capacity Planning**: Determine optimal user load limits
4. **Monitoring**: Set up continuous performance monitoring
5. **Scaling**: Plan for horizontal scaling if needed

## 🤝 Contributing

To add new test scenarios or improve the load testing tools:

1. Add new test cases to the message arrays
2. Implement new metrics collection
3. Add performance visualization
4. Create automated regression tests
