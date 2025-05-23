## Mining on Linux with Docker

## Prerequisites
- Linux machine with NVIDIA GPU
- Docker - [how to install](https://docs.docker.com/engine/install/)
- NVIDIA Container Toolkit - [how to install](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)


1. **Configure Environment**
Create a `.env` file:
```bash
# Required: Your private key for mining (64 characters after 0x). You need to have some Sonic (S) balance to start mining.
INFINITY_MINER_PRIVATE_KEY=your_private_key_here

# Optional: RPC and WebSocket endpoints
# INFINITY_RPC=https://rpc.soniclabs.com
# INFINITY_WS=wss://rpc.soniclabs.com

# Optional: Mining rewards recipient
# INFINITY_REWARDS_RECIPIENT_ADDRESS=your_address_here

# Optional: Logging level
# LOGLEVEL=DEBUG
```
2. **Run docker container**
```
docker run --gpus all --env-file .env 8finity/miner-v2
```

3. **Optional: build docker container from code**
```
git clone https://github.com/8finity-xyz/miner-v2.git
cd miner-v2
docker build -t miner-v2 .
docker run --gpus all --env-file .env miner-v2
```


## Configuration Options
you can paste it to your .env file
- `INFINITY_MINER_PRIVATE_KEY`: Your private key for mining (required)
- `INFINITY_RPC`: Custom RPC endpoint (optional)
- `INFINITY_WS`: Custom WebSocket endpoint (optional)
- `INFINITY_REWARDS_RECIPIENT_ADDRESS`: Address to receive mining rewards (optional)
- `LOGLEVEL`: Set logging verbosity (optional)
