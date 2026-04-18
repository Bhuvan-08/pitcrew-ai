class CPUStarvationExperiment:
    name = "CPU Starvation"
    
    def inject(self, container):
        """Spawns an invisible background loop to peg the CPU at 100%."""
        # detach=True is critical so it runs in the background and doesn't freeze the daemon
        container.exec_run("sh -c 'while true; do :; done'", detach=True)
        return "CPU spike injected."

    def rollback(self, container):
        """Kills the rogue process by restarting the container."""
        container.restart()
        return "CPU spike mitigated."