"""Snapshot management for immutable generation storage."""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict

from core.data_structures import Candidate, ValidationResult
from core.evolution_logger import EvolutionLogger


class SnapshotManager:
    """Creates and manages immutable snapshots of accepted candidates."""

    def __init__(self, base_dir: str = 'snapshots', logger: EvolutionLogger = None):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logger or EvolutionLogger()

    def create_snapshot(self, candidate: Candidate, generation: int, 
                       validation: ValidationResult, score: float) -> str:
        """Create immutable snapshot of accepted candidate.
        
        Args:
            candidate: Candidate to snapshot
            generation: Generation number
            validation: Validation result
            score: Candidate score
            
        Returns:
            Snapshot ID
        """
        snapshot_id = f"gen-{generation:06d}-{candidate.hash[:8]}"
        snapshot_dir = self.base_dir / snapshot_id
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        # Write candidate source
        source_file = snapshot_dir / 'source.py'
        with open(source_file, 'w') as f:
            f.write(candidate.source_code)
        
        # Write metadata
        metadata = {
            'snapshot_id': snapshot_id,
            'generation': generation,
            'timestamp': candidate.timestamp.isoformat(),
            'candidate_hash': candidate.hash,
            'score': score,
            'validation': validation.to_dict(),
            'project_type': candidate.project_type,
            'language': candidate.language,
            'immutable': True
        }
        
        metadata_file = snapshot_dir / 'metadata.json'
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Make files read-only
        os.chmod(source_file, 0o444)
        os.chmod(metadata_file, 0o444)
        
        self.logger.info(f"Snapshot created: {snapshot_id}")
        return snapshot_id

    def list_snapshots(self) -> List[str]:
        """List all snapshots in order.
        
        Returns:
            List of snapshot IDs sorted by generation
        """
        snapshots = []
        if self.base_dir.exists():
            for item in sorted(self.base_dir.iterdir()):
                if item.is_dir():
                    snapshots.append(item.name)
        return snapshots

    def get_latest_snapshot(self) -> Optional[Dict]:
        """Retrieve most recent snapshot.
        
        Returns:
            Snapshot dict or None if no snapshots exist
        """
        snapshots = self.list_snapshots()
        if not snapshots:
            return None
        latest_id = snapshots[-1]
        return self.load_snapshot(latest_id)

    def load_snapshot(self, snapshot_id: str) -> Dict:
        """Load snapshot metadata and source.
        
        Args:
            snapshot_id: Snapshot identifier
            
        Returns:
            Dictionary with 'id', 'metadata', 'source'
        """
        snapshot_dir = self.base_dir / snapshot_id
        
        # Load metadata
        metadata_file = snapshot_dir / 'metadata.json'
        with open(metadata_file) as f:
            metadata = json.load(f)
        
        # Load source
        source_file = snapshot_dir / 'source.py'
        with open(source_file) as f:
            source = f.read()
        
        return {
            'id': snapshot_id,
            'metadata': metadata,
            'source': source
        }

    def get_snapshot_by_generation(self, generation: int) -> Optional[Dict]:
        """Get snapshot for specific generation.
        
        Args:
            generation: Generation number
            
        Returns:
            Snapshot dict or None if not found
        """
        snapshots = self.list_snapshots()
        for snapshot_id in snapshots:
            if snapshot_id.startswith(f"gen-{generation:06d}"):
                return self.load_snapshot(snapshot_id)
        return None
