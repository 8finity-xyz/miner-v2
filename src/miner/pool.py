import asyncio
import json

import aiohttp
from eth_typing import HexAddress

from .base import BaseMiner


class PoolMiner(BaseMiner):
    def __init__(self, solver, miner_address: HexAddress, pool_url: str):
        super().__init__(solver)
        self.miner_address = miner_address
        self.pool_url = pool_url

        self.current_problem = (0, 0)
        self.problem_queue = asyncio.Queue()
        self._poll_problem_task = asyncio.create_task(self._poll_problem())

        self.claim_info = None
        self.update_claim_info_task = asyncio.create_task(self._update_claim_info())

    async def get_problems(self):
        while True:
            new_problem = await self.problem_queue.get()
            if self.current_problem != new_problem:
                self.current_problem = new_problem
                yield (0, *self.current_problem)

    async def _submit_solution(self, _, private_key_b):
        async with aiohttp.ClientSession(self.pool_url) as session:
            async with session.get(
                "/submit",
                params={
                    "miner": self.miner_address,
                    "private_key_b": hex(private_key_b)[2:],
                },
            ) as r:
                if r.status != 200:
                    self.logger.warning(f"Can't submit - status: {r.status}")
                    self.logger.debug(f"/submit response - {await r.text()}")
                    return

                data = await r.json()
                await self.problem_queue.put(
                    (int(data["private_key_a"]), int(data["difficulty"]))
                )

    async def flush_stats(self):
        _, current_difficulty = self.current_problem
        current_difficulty_str = current_difficulty.to_bytes(20, byteorder="big").hex()
        leading_zeros = len(current_difficulty_str) - len(
            current_difficulty_str.lstrip("0")
        )

        self.logger.info("| STATS")
        if self.solver.get_speed() > 0:
            self.logger.info(f"├ hashrate: {self.solver.hashrate()}")
        self.logger.info(
            f"├ current difficulty: 0x{current_difficulty_str} ({leading_zeros} leading zeros)"
        )
        if self.claim_info is not None:
            self.logger.info(
                f"├ total finalized rewards: {self.claim_info['total_reward'] / 1e18} $8"
            )

        self.logger.info(f"| ")
        self.logger.info(f"└ Pool url: {self.pool_url}")

    async def _poll_problem(self):
        async with aiohttp.ClientSession(self.pool_url) as session:
            while True:
                async with session.get(
                    "/problem", params={"miner": self.miner_address}
                ) as r:
                    if r.status != 200:
                        self.logger.warning(f"Can't get problem - status: {r.status}")
                        self.logger.debug(f"/problem response - {await r.text()}")
                        continue

                    data = await r.json()
                    await self.problem_queue.put(
                        (int(data["private_key_a"]), int(data["difficulty"]))
                    )
                await asyncio.sleep(0.1)

    async def _update_claim_info(self):
        async with aiohttp.ClientSession(self.pool_url) as session:
            while True:
                async with session.get(
                    "/claim", params={"miner": self.miner_address}
                ) as r:
                    if r.status != 200:
                        self.logger.warning(
                            f"Can't get claim info - status: {r.status}"
                        )
                        self.logger.debug(f"/claim response - {await r.text()}")
                        continue

                    data = await r.json()
                    self.claim_info = {
                        "pool_id": data["pool_id"],
                        "miner": self.miner_address,
                        "total_reward": int(data["total_reward"]),
                        "signature": data["signature"],
                    }
                    with open("claim_info.json", "w") as f:
                        json.dump(self.claim_info, f, indent=4)
                await asyncio.sleep(60)
