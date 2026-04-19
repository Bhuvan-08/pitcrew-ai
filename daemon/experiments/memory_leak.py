class MemoryLeakExperiment:
    name = "Memory Exhaustion (OOM Target)"
    
    def inject(self, container):
        """Writes massive amounts of data directly into the container's Shared Memory (RAM)."""
        container.exec_run("dd if=/dev/zero of=/dev/shm/memory_leak_dummy bs=1M count=512", detach=True)
        return "Memory leak injected."

    def rollback(self, container):
        """Flushes the RAM by restarting the container."""
        container.restart()
        return "Memory leak mitigated."