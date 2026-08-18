class GoalBasedAgent:
    """
    A Goal-Based Intelligent Agent using Hysteresis (Deadband) Control.
    Protects the Air Conditioner compressor from rapid toggling (short-cycling)
    and allows user-defined comfort bounds.
    """
    def __init__(self, target_min: float = 22.0, target_max: float = 26.0):
        self.update_targets(target_min, target_max)

    def update_targets(self, target_min: float, target_max: float):
        """
        Dynamically update comfort boundary limits and calculate the target setpoint.
        """
        self.target_min = round(target_min, 2)
        self.target_max = round(target_max, 2)
        # The comfortable setpoint is the midpoint of the comfort range
        self.target_midpoint = round((self.target_min + self.target_max) / 2.0, 2)
        self.goal_description = (
            f"Maintain temp between {self.target_min}°C and {self.target_max}°C "
            f"(Target Setpoint: {self.target_midpoint}°C)."
        )

    def perceive_and_act(self, current_temp: float, current_ac_status: str) -> dict:
        """
        Hysteresis-based Perception -> Reasoning -> Action Loop.
        
        - If AC is OFF: Remains OFF until temp rises ABOVE target_max.
        - If AC is ON: Remains ON (cooling) until temp drops BELOW OR EQUAL TO target_midpoint.
        """
        temp = round(current_temp, 2)
        new_ac_status = current_ac_status
        analysis = ""
        decision = ""
        action_desc = ""

        # Hysteresis cognitive evaluation
        if current_ac_status == "OFF":
            if temp > self.target_max:
                analysis = f"Current temperature ({temp}°C) exceeds the comfort threshold of {self.target_max}°C."
                new_ac_status = "ON"
                decision = "Turning ON Air Conditioner to cool the room."
                action_desc = "Completed Successfully."
            else:
                analysis = f"Current temperature ({temp}°C) is below the maximum activation threshold ({self.target_max}°C) while AC is OFF."
                decision = "Keep Air Conditioner OFF."
                action_desc = "Monitoring continues. Waiting for temperature to rise."
        else: # AC is ON
            if temp <= self.target_midpoint:
                analysis = f"Current temperature ({temp}°C) has reached the comfortable setpoint ({self.target_midpoint}°C)."
                new_ac_status = "OFF"
                decision = "Turning OFF Air Conditioner. Comfortable setpoint reached."
                action_desc = "Completed Successfully."
            else:
                analysis = f"Current temperature ({temp}°C) is cooling down but still above the comfortable setpoint ({self.target_midpoint}°C)."
                decision = "Keep Air Conditioner ON."
                action_desc = "Monitoring continues. Cooling in progress."

        return {
            "current_temp": f"{temp}°C",
            "goal": self.goal_description,
            "analysis": analysis,
            "decision": decision,
            "action": action_desc,
            "new_ac_status": new_ac_status,
            "state_changed": new_ac_status != current_ac_status
        }
