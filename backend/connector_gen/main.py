import redis
import os
import docker
import uuid
import json
from fastapi_mcp import FastAPI_MCP

r = redis.Redis.from_url("redis://redis:6379")
docker_client = docker.from_env()

def generate_connector(tool_name: str, spec: dict):
    # Generate FastAPI app code
    app_code = f'''
from fastapi_mcp import FastAPI_MCP
import os

app = FastAPI_MCP()

@app.on_event("startup")
async def startup():
    print("{tool_name} connector started")

@app.mcp_tool()
async def {tool_name}(input: dict):
    # Implementation would vary based on tool spec
    return {{"result": "Processed by {tool_name}", "input": input}}
'''

    # Save to temporary file
    file_path = f"/tmp/{tool_name}.py"
    with open(file_path, "w") as f:
        f.write(app_code)

    # Build Docker image
    image, _ = docker_client.images.build(
        path="/tmp",
        dockerfile=f'''FROM python:3.11-slim
WORKDIR /app
COPY {tool_name}.py .
RUN pip install fastapi-mcp uvicorn
CMD ["uvicorn", "{tool_name}:app", "--host", "0.0.0.0", "--port", "8000"]
''',
        tag=f"nova-connector-{tool_name}"
    )

    # Run container
    container = docker_client.containers.run(
        image.id,
        ports={'8000/tcp': None},
        detach=True
    )

    # Get assigned port
    port = docker_client.api.inspect_container(container.id)['NetworkSettings']['Ports']['8000/tcp'][0]['HostPort']

    # Register in Redis
    r.hset("connectors", tool_name, f"http://localhost:{port}")

    return {"status": "success", "url": f"http://localhost:{port}"}

if __name__ == "__main__":
    # Subscribe to Redis channel
    pubsub = r.pubsub()
    pubsub.subscribe("connector:req")

    for message in pubsub.listen():
        if message["type"] == "message":
            data = json.loads(message["data"])
            generate_connector(data["tool_name"], data["spec_json"])