import asyncio

import config
from miner.pool import PoolMiner
from miner.solo import SoloMiner
from solver.opencl import OpenCLSolver


async def main():
    if config.POOL_MODE:
        miner = PoolMiner(
            OpenCLSolver(),
            pool_url=config.POOL_URL,
            miner_address=config.REWARDS_RECIPIENT_ADDRESS,
        )
    else:
        miner = SoloMiner(
            OpenCLSolver(),
            rpc=config.RPC,
            ws=config.WS,
            miner_pk=config.MINER_PRIVATE_KEY,
            reward_recipient=config.REWARDS_RECIPIENT_ADDRESS,
        )

    miner.logger.info(f"Running in {'pool' if config.POOL_MODE else 'solo'} mode")
    await miner.mine()


asyncio.run(main())
