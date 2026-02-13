# Runbook: Payment Gateway Failures

## Error: MemoryAllocationFailure

**Symptoms:**
- Memory usage above 90%
- Increased latency
- Container instability

**Root Cause:**
Typically caused by traffic spikes or memory leaks.

**Resolution Steps:**
1. Remove failure trigger if present.
2. Restart the container.
3. Verify service health endpoint.
4. Monitor memory usage.

**Severity:** HIGH  
**Automation Approved:** YES  
