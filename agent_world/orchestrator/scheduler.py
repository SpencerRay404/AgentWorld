from __future__ import annotations

import random
from collections import defaultdict
from typing import Dict, List, Set, Tuple

from agent_world.config import SimConfig
from agent_world.models.agent import Agent, AgentState, AgentStatus
from agent_world.world import World


class Scheduler:
    def __init__(self, config: SimConfig):
        self.config = config
        self.work_queue: List[str] = []  # agent_ids waiting for a slot
        self.ticks_worked_this_cycle: Dict[str, int] = defaultdict(int)
        self._consecutive_exhausted: Dict[str, int] = defaultdict(int)
        self._anomalies: List[str] = []  # agent_ids flagged this tick

    def assign_actions(
        self,
        agents: List[Agent],
        states: Dict[str, AgentState],
        world: World,
    ) -> List[Tuple[str, AgentStatus]]:
        """Returns list of (agent_id, new_status) for the current tick."""
        assignments: List[Tuple[str, AgentStatus]] = []
        self._anomalies = []

        # Reset active_workers each tick — rebuilt fresh from assignments below
        world.active_workers.clear()

        # Note: ticks_worked_this_cycle is reset by engine AFTER pay is distributed

        # Try to promote queued workers if slots opened
        slots_available = world.max_concurrent_workers - len(world.active_workers)
        promoted = []
        while self.work_queue and slots_available > 0:
            aid = self.work_queue.pop(0)
            if aid in {a.agent_id for a in agents}:
                promoted.append(aid)
                slots_available -= 1

        for agent in agents:
            state = states[agent.agent_id]
            if state.status == AgentStatus.TERMINATED:
                continue

            new_status = self._decide(agent, state, world, pre_promoted=agent.agent_id in promoted)
            assignments.append((agent.agent_id, new_status))

            # Track exhaustion streaks for anomaly detection
            if new_status == AgentStatus.EXHAUSTED:
                self._consecutive_exhausted[agent.agent_id] += 1
                if self._consecutive_exhausted[agent.agent_id] > 3:
                    self._anomalies.append(agent.agent_id)
            else:
                self._consecutive_exhausted[agent.agent_id] = 0

        return assignments

    def _decide(
        self, agent: Agent, state: AgentState, world: World, pre_promoted: bool
    ) -> AgentStatus:
        cfg = self.config

        # Force rest if energy critical
        if state.energy < cfg.auto_rest_threshold:
            world.active_workers.discard(agent.agent_id)
            return AgentStatus.EXHAUSTED if state.energy <= 0 else AgentStatus.RESTING

        # Pre-promoted from work queue — honour it if slot is available
        if pre_promoted:
            world.active_workers.add(agent.agent_id)
            return AgentStatus.WORKING

        # Strong bias toward work when broke
        if state.balance < 10.0 and state.energy >= cfg.exhaustion_threshold:
            if len(world.active_workers) < world.max_concurrent_workers:
                world.active_workers.add(agent.agent_id)
                return AgentStatus.WORKING
            else:
                if agent.agent_id not in self.work_queue:
                    self.work_queue.append(agent.agent_id)
                return AgentStatus.RESTING

        # Can't afford to play
        can_play = state.balance >= cfg.play_minimum_balance

        # Personality-weighted random choice
        w = agent.personality_weights
        work_w = w["efficiency"]
        rest_w = w["rest_preference"]
        play_w = w["risk_tolerance"] if can_play else 0.0
        total = work_w + rest_w + play_w
        if total == 0:
            total = 1.0

        roll = random.random() * total
        if roll < work_w:
            chosen = AgentStatus.WORKING
        elif roll < work_w + rest_w:
            chosen = AgentStatus.RESTING
        else:
            chosen = AgentStatus.PLAYING

        # Apply capacity constraints
        if chosen == AgentStatus.WORKING:
            if len(world.active_workers) < world.max_concurrent_workers:
                world.active_workers.add(agent.agent_id)
            else:
                if agent.agent_id not in self.work_queue:
                    self.work_queue.append(agent.agent_id)
                chosen = AgentStatus.RESTING
        else:
            world.active_workers.discard(agent.agent_id)

        return chosen

    def record_work_tick(self, agent_id: str) -> None:
        self.ticks_worked_this_cycle[agent_id] += 1

    @property
    def anomalies(self) -> List[str]:
        return list(self._anomalies)
