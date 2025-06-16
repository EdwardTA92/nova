from fastapi import FastAPI
from pydantic import BaseModel
import redis
import pickle
import uuid
from langgraph.graph import StateGraph

app = FastAPI()
r = redis.Redis.from_url("redis://redis:6379")

class CompileRequest(BaseModel):
    graph_id: str

@app.post("/compile")
async def compile_graph(req: CompileRequest):
    # Get the plan from Redis
    plan_str = r.get(f"plans:{req.graph_id}")
    if not plan_str:
        return {"error": "Plan not found"}
    
    plan = json.loads(plan_str)
    
    # Create a simple workflow (in production this would be more complex)
    workflow = StateGraph()
    
    # Add nodes for each domain
    for domain in plan["domains"]:
        workflow.add_node(domain, lambda state: {
            "result": f"Processed {domain} tasks",
            "status": "completed"
        })
    
    # Set entry point
    workflow.set_entry_point(plan["domains"][0])
    
    # Add edges between domains
    for i in range(len(plan["domains"])-1):
        workflow.add_edge(plan["domains"][i], plan["domains"][i+1])
    
    # Set finish point
    workflow.set_finish_point(plan["domains"][-1])
    
    # Compile the graph
    compiled_graph = workflow.compile()
    
    # Store the compiled graph in Redis
    r.set(f"graphs:{req.graph_id}", pickle.dumps(compiled_graph))
    
    return {"status": "success", "graph_id": req.graph_id}
