# Cloud_AIModelDownloader


RUN scripts/install_docker_debian11.sh

Add HF TOken in .env file


RUN docker compose build


# Ensure host models directory is writable by uid 1000
mkdir -p models
sudo chown -R 1000:1000 models


RUN ONE SHOT 
docker compose run --rm hfdl download openai-community/gpt2

# Reduce RAM usage (avoid OOM kill)
docker compose run --rm hfdl download openai-community/gpt2 --max-workers 1

# Note: downloads are stored in the Hugging Face cache structure
# under the mounted ./models directory (blobs/refs/snapshots).