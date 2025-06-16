from fastapi import FastAPI
import uuid
from pydantic import BaseModel
import os
import redis
import json

app = FastAPI()
r = redis.Redis.from_url("redis://redis:6379")

class UserPrompt(BaseModel):
    prompt: str

class SettingsUpdate(BaseModel):
    modelId: str
    apiKey: str

@app.post("/plan")
async def plan(inp: UserPrompt):
    # Generate a unique graph ID
    graph_id = str(uuid.uuid4())
    
    # Example plan structure (in production this would come from LLM)
    plan = {
        "domains": ["materials_science", "physics"],
        "tasks": {
            "materials_science": {
                "subtasks": ["research existing materials", "identify potential compounds"],
                "tools": ["materials_db", "simulation"]
            },
            "physics": {
                "subtasks": ["analyze quantum properties", "validate theoretical models"],
                "tools": ["quantum_simulator", "math_engine"]
            }
        }
    }
    
    # Store the plan in Redis
    r.set(f"plans:{graph_id}", json.dumps(plan))
    
    return {"graph_id": graph_id, "plan": plan}

@app.post("/settings")
async def update_settings(settings: SettingsUpdate):
    # Store settings in Redis
    r.set(f"settings:model", settings.modelId)
    r.set(f"settings:api_key", settings.apiKey)
    
    return {"status": "success"}
