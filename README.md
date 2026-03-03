# Cloud_AIModelDownloader


RUN scripts/install_docker_debian11.sh

# Setup swap (prevents OOM kill on low-RAM cloud instances)
sudo bash scripts/setup_swap.sh 8G

Add HF Token in .env file


RUN docker compose build


# Ensure host models directory is writable by uid 1000
mkdir -p models
sudo chown -R 1000:1000 models


RUN ONE SHOT
docker compose run --rm hfdl download openai-community/gpt2

# Skip failed files and continue
docker compose run --rm hfdl download openai-community/gpt2 --skip-errors

# Note: downloads are stored in the Hugging Face cache structure
# under the mounted ./models directory (blobs/refs/snapshots).