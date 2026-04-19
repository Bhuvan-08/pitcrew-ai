class DiskExhaustionExperiment:
    name = "Disk Exhaustion (Runaway Log)"
    
    def inject(self, container):
        """Simulates a runaway process filling the container's ephemeral storage."""
        # The 'dd' command is a native Linux tool. 
        # This instantly generates a massive 1GB junk file to max out the disk quota.
        container.exec_run("dd if=/dev/zero of=/tmp/runaway-debug.log bs=1M count=1024", detach=True)
        return "Disk exhaustion injected."

    def rollback(self, container):
        """Deletes the massive junk file to free up system space."""
        # We can safely use 'rm -f' here in the rollback, because if the file doesn't exist, we don't care!
        container.exec_run("rm -f /tmp/runaway-debug.log")
        return "Disk space restored."