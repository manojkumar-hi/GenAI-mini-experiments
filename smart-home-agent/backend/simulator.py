import random
import datetime
import threading
from typing import List, Dict, Any
from backend.agent import GoalBasedAgent

class TemperatureSimulator:
    """
    A Virtual Temperature Sensor and Environment simulator.
    Keeps track of current temperature, history, logs, AC status, and agent reasoning.
    Runs updates periodically when simulation is active.
    """
    def __init__(self):
        self.lock = threading.Lock()
        self.agent = GoalBasedAgent()
        self.reset()

    def reset(self):
        with self.lock:
            # Start with random temperature between 20°C and 32°C
            self.temperature = round(random.uniform(20.0, 32.0), 2)
            self.ac_status = "OFF"
            self.simulation_active = False
            self.history: List[Dict[str, Any]] = []
            self.logs: List[Dict[str, Any]] = []
            
            # Initialise agent reasoning
            self.agent_reasoning = self.agent.perceive_and_act(self.temperature, self.ac_status)
            
            # Initial logs
            self.add_log(f"Simulation reset. Initial room temperature set to {self.temperature}°C")
            self.add_log(f"Initial Air Conditioner status is {self.ac_status}")
            self.add_history()

    def add_log(self, message: str):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.logs.append({
            "timestamp": timestamp,
            "message": message
        })
        if len(self.logs) > 100:
            self.logs.pop(0)

    def add_history(self):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.history.append({
            "timestamp": timestamp,
            "temperature": self.temperature,
            "ac_status": self.ac_status
        })
        if len(self.history) > 50:
            self.history.pop(0)

    def update_temperature_manually(self, temp: float):
        with self.lock:
            old_temp = self.temperature
            self.temperature = round(temp, 2)
            self.add_log(f"Temperature manually adjusted: {old_temp}°C -> {self.temperature}°C")
            self.run_agent_step()

    def update_target_range(self, target_min: float, target_max: float):
        """
        Thread-safe method to adjust the comfort range limits.
        """
        with self.lock:
            self.agent.update_targets(target_min, target_max)
            self.add_log(f"Comfort range goals adjusted by user: {target_min}°C - {target_max}°C")
            self.run_agent_step()

    def set_simulation_active(self, active: bool):
        with self.lock:
            self.simulation_active = active
            status_str = "started" if active else "stopped"
            self.add_log(f"Simulation {status_str} by user")

    def run_agent_step(self):
        # Perception -> Reasoning -> Action Loop
        reasoning = self.agent.perceive_and_act(self.temperature, self.ac_status)
        self.agent_reasoning = reasoning
        
        # If Agent decided to change the AC status
        if reasoning["state_changed"]:
            old_status = self.ac_status
            self.ac_status = reasoning["new_ac_status"]
            self.add_log(f"Agent reasoning decision: Toggle AC to {self.ac_status}")
            self.add_log(f"Action: Switched {self.ac_status} Air Conditioner")
        else:
            self.add_log(f"Agent decision: Maintain current state")
            
        self.add_history()

    def tick(self):
        """
        Calculates temperature changes every tick (2 seconds) and triggers agent execution.
        """
        with self.lock:
            if not self.simulation_active:
                return
            
            # Base temperature change depends on AC status
            if self.ac_status == "ON":
                # Cools down by -0.8°C to -1.5°C with small random jitter
                change = random.uniform(-1.5, -0.8)
            else:
                # Warms up by +0.4°C to +1.0°C due to ambient heating
                change = random.uniform(0.4, 1.0)
            
            # Add minor realistic fluctuation (random noise)
            fluctuation = random.uniform(-0.2, 0.2)
            change += fluctuation
            
            # Calculate new temperature
            self.temperature = round(self.temperature + change, 2)
            
            # Bound temperature within realistic environmental safety limits (12°C to 40°C)
            self.temperature = max(12.0, min(40.0, self.temperature))
            
            self.add_log(f"Temperature updated: {self.temperature}°C")
            self.run_agent_step()

    def get_status(self) -> dict:
        with self.lock:
            return {
                "temperature": self.temperature,
                "ac_status": self.ac_status,
                "simulation_active": self.simulation_active,
                "target_min": self.agent.target_min,
                "target_max": self.agent.target_max,
                "target_midpoint": self.agent.target_midpoint,
                "agent_reasoning": self.agent_reasoning
            }

    def get_history(self) -> List[Dict[str, Any]]:
        with self.lock:
            return list(self.history)

    def get_logs(self) -> List[Dict[str, Any]]:
        with self.lock:
            return list(self.logs)
