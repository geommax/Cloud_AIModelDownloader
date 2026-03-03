# Cloud_AIModelDownloader


RUN scripts/install_docker_debian11.sh

Add HF TOken in .env file


RUN docker compose build


# Ensure host models directory is writable by uid 1000
mkdir -p models
sudo chown -R 1000:1000 models


RUN ONE SHOT 
docker compose run --rm hfdl download openai-community/gpt2