"""Rollback functionality for restoring previous generations."""
from pathlib import Path
from typing import Optional

from core.snapshot_manager import SnapshotManager
from core.evolution_logger import EvolutionLogger


class RollbackManager:
    """Manages rollback to previous verified generations."""

    def __init__(self, snapshot_mgr: SnapshotManager, verified_dir: str = 'verified', 
                 logger: EvolutionLogger = None):
        self.snapshot_mgr = snapshot_mgr
        self.verified_dir = Path(verified_dir)
        self.verified_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logger or EvolutionLogger()

    def rollback_to_generation(self, generation: int) -> bool:
        """Restore state to specified generation.
        
        Args:
            generation: Generation number to rollback to
            
        Returns:
            True if successful, False otherwise
        """
        snapshot = self.snapshot_mgr.get_snapshot_by_generation(generation)
        
        if not snapshot:
            self.logger.error(f"No snapshot found for generation {generation}")
            return False
        
        # Copy verified candidate back to verified/
        snapshot_id = snapshot['id']
        dst = self.verified_dir / f"{snapshot_id}.py"
        
        try:
            with open(dst, 'w') as f:
                f.write(snapshot['source'])
            
            self.logger.info(f"Rolled back to generation {generation} ({snapshot_id})")
            return True
        except Exception as e:
            self.logger.error(f"Rollback failed: {e}")
            return False

    def rollback_to_latest(self) -> bool:
        """Restore to most recent verified snapshot.
        
        Returns:
            True if successful, False otherwise
        """
        latest = self.snapshot_mgr.get_latest_snapshot()
        
        if not latest:
            self.logger.error("No snapshots available for rollback")
            return False
        
        generation_str = latest['id'].split('-')[1]
        try:
            generation = int(generation_str)
            return self.rollback_to_generation(generation)
        except (ValueError, IndexError) as e:
            self.logger.error(f"Could not parse generation from snapshot: {e}")
            return False
