import time
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.simulator import TemperatureSimulator

# Global simulator instance
simulator = TemperatureSimulator()
stop_event = threading.Event()
tick_thread = None

def run_simulation_ticks():
    """
    Background worker thread that triggers the simulator tick every 2 seconds.
    """
    while not stop_event.is_set():
        status = simulator.get_status()
        if status["simulation_active"]:
            simulator.tick()
        
        # Sleep for 2 seconds in small increments to allow rapid shutdown
        for _ in range(20):
            if stop_event.is_set():
                break
            time.sleep(0.1)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager to handle backend application startup and shutdown lifecycle.
    """
    global tick_thread
    stop_event.clear()
    tick_thread = threading.Thread(target=run_simulation_ticks, daemon=True)
    tick_thread.start()
    
    yield  # Runs the application
    
    stop_event.set()
    if tick_thread:
        tick_thread.join(timeout=2.0)

# Initialize FastAPI App
app = FastAPI(
    title="Smart Home Temperature Control Agent API",
    description="Backend services for simulated temperature sensing and goal-based agent control.",
    version="1.1.0",
    lifespan=lifespan
)

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TemperatureUpdate(BaseModel):
    temperature: float

class TargetRangeUpdate(BaseModel):
    target_min: float
    target_max: float

@app.get("/api/status")
def get_status():
    """
    Retrieve current room temperature, AC status, agent reasoning, and simulation state.
    """
    return simulator.get_status()

@app.post("/api/simulation/start")
def start_simulation():
    """
    Start the automatic temperature drift and fluctuation simulation.
    """
    simulator.set_simulation_active(True)
    return {"message": "Simulation started successfully", "status": simulator.get_status()}

@app.post("/api/simulation/stop")
def stop_simulation():
    """
    Pause/Stop the automatic simulation.
    """
    simulator.set_simulation_active(False)
    return {"message": "Simulation stopped successfully", "status": simulator.get_status()}

@app.post("/api/simulation/reset")
def reset_simulation():
    """
    Reset simulation parameters, clear records, and re-initialise temperature.
    """
    simulator.reset()
    return {"message": "Simulation reset successfully", "status": simulator.get_status()}

@app.post("/api/temperature/update")
def update_temperature(payload: TemperatureUpdate):
    """
    Manually update room temperature (user manual override).
    """
    if payload.temperature < 10.0 or payload.temperature > 45.0:
        raise HTTPException(
            status_code=400, 
            detail="Invalid temperature setting. Must be between 10.0°C and 45.0°C."
        )
    simulator.update_temperature_manually(payload.temperature)
    return {"message": "Temperature updated successfully", "status": simulator.get_status()}

@app.post("/api/target-range")
def update_target_range(payload: TargetRangeUpdate):
    """
    Dynamically configure the agent's target comfort boundaries.
    """
    if payload.target_min >= payload.target_max:
        raise HTTPException(
            status_code=400,
            detail="Minimum target temperature must be strictly less than maximum target temperature."
        )
    if payload.target_min < 15.0 or payload.target_max > 35.0:
        raise HTTPException(
            status_code=400,
            detail="Target boundaries must be within a realistic safety envelope of 15.0°C to 35.0°C."
        )
    simulator.update_target_range(payload.target_min, payload.target_max)
    return {"message": "Target comfort range updated successfully", "status": simulator.get_status()}

@app.get("/api/history")
def get_history():
    """
    Retrieve temperature logs for graph plotting.
    """
    return simulator.get_history()

@app.get("/api/logs")
def get_logs():
    """
    Retrieve audit history log containing timestamps and decisions.
    """
    return simulator.get_logs()
