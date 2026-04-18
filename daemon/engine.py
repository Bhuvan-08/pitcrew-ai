import docker
import time
import importlib
import random
from pathlib import Path

# Connect to the local Docker socket
client = docker.from_env()
EXPERIMENTS_DIR = Path(__file__).parent / "experiments"

def get_chaos_targets():
    """Queries the Docker API for any container labeled as chaos eligible."""
    targets = []
    for container in client.containers.list():
        # Look for the exact label we added to docker-compose.yml
        if container.labels.get("pitcrew.chaos.eligible") == "true":
            targets.append(container)
    return targets

def load_experiments():
    """Dynamically imports every python file in the experiments folder."""
    experiments = []
    for file in EXPERIMENTS_DIR.glob("*.py"):
        if file.name.startswith("__"): continue
        
        module_name = f"experiments.{file.stem}"
        module = importlib.import_module(module_name)
        
        # Find the class inside the file and instantiate it
        for attr_name in dir(module):
            if attr_name.endswith("Experiment") and attr_name != "Experiment":
                experiment_class = getattr(module, attr_name)
                experiments.append(experiment_class())
    return experiments

def run_chaos_loop():
    print("😈 Chaos Daemon Initialized. Scanning for targets...")
    
    while True:
        # Roll the dice every 60 seconds
        time.sleep(60) 
        
        targets = get_chaos_targets()
        if not targets:
            print("💤 No eligible targets found (Check your docker-compose labels).")
            continue

        roll = random.randint(1, 20)
        print(f"🎲 Rolled a {roll}")

        # Rolls 11-20 trigger an attack
        if roll >= 11:
            experiments = load_experiments()
            if not experiments:
                print("No experiment plugins found in the directory.")
                continue

            target = random.choice(targets)
            experiment = random.choice(experiments)

            print(f"🔥 INJECTING CHAOS: '{experiment.name}' into [{target.name}]")
            try:
                experiment.inject(target)
                print(f"⚠️ Attack successful. Check your PitCrew dashboard!")
            except Exception as e:
                print(f"❌ Attack failed to execute: {e}")
        else:
            print("🟢 System safe this round.")

if __name__ == "__main__":
    run_chaos_loop()