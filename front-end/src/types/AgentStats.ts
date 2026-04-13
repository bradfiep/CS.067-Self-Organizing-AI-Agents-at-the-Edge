export interface AgentStats {
  agent_name: string;
  agent_id: number;
  tiles_explored: number;
  tiles_discovered_directly: number;
  tiles_learned_from_peers: number;
  steps_taken: number;
  unique_tiles_walked: number;
  redundant_steps: number;
  efficiency_percentage: number;
  exploration_rate: number;
  remaining_frontiers: number;
  frontiers_claimed_by_agent: number;
  walls_boundaries_hit: number;
  maps_merged_from_peers: number;
  ticks_elapsed: number;
  reached_goal: boolean;
  goal_tick: number | null;
}
