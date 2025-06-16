from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import redis
import uuid
import pickle
from langgraph.graph import StateGraph

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection
r = redis.Redis.from_url("redis://redis:6379")

@app.post("/run")
async def run_graph(graph_id: str):
    run_id = str(uuid.uuid4())
    
    # Load graph from Redis
    serialized_graph = r.get(f"graphs:{graph_id}")
    if not serialized_graph:
        return {"error": "Graph not found"}
    
    graph = pickle.loads(serialized_graph)
    
    # Execute graph and stream events
    async for event in graph.stream():
        r.xadd(f"nova:events:{run_id}", {"data": str(event)})
    
    return {"run_id": run_id}

@app.websocket("/ws/events")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    run_id = await websocket.receive_text()
    
    # Subscribe to Redis stream
    pubsub = r.pubsub()
    pubsub.subscribe(f"nova:events:{run_id}")
    
    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                await websocket.send_text(message["data"])
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()