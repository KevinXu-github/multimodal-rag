@echo off

echo Setting up Docker infrastructure for Multimodal RAG...

cd infrastructure\docker

echo Starting Neo4j and Qdrant containers...
docker-compose up -d

echo Waiting for services to be ready...
timeout /t 10 /nobreak > nul

echo Checking Neo4j status...
curl -s http://localhost:7474 > nul && (
    echo Neo4j is running
) || (
    echo Neo4j failed to start
)

echo Checking Qdrant status...
curl -s http://localhost:6333 > nul && (
    echo Qdrant is running
) || (
    echo Qdrant failed to start
)

echo Docker setup complete
echo Neo4j Browser: http://localhost:7474
echo Qdrant Dashboard: http://localhost:6333/dashboard
