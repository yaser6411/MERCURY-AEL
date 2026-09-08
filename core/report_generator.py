"""Report generation for MERCURY-AEL campaigns."""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict

from core.data_structures import CampaignResult
from core.evolution_logger import EvolutionLogger


class ReportGenerator:
    """Generates JSON and Markdown reports from campaign results."""

    def __init__(self, reports_dir: str = 'reports', logger: EvolutionLogger = None):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logger or EvolutionLogger()

    def generate(self, result: CampaignResult) -> str:
        """Generate both JSON and Markdown reports.
        
        Args:
            result: Campaign result
            
        Returns:
            Path to reports directory
        """
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        
        # Generate JSON report
        json_report = self._generate_json_report(result, timestamp)
        
        # Generate Markdown report
        md_report = self._generate_markdown_report(result, timestamp)
        
        self.logger.info(f"Reports generated: {self.reports_dir}")
        return str(self.reports_dir)

    def _generate_json_report(self, result: CampaignResult, timestamp: str) -> str:
        """Generate machine-readable JSON report.
        
        Args:
            result: Campaign result
            timestamp: Report timestamp
            
        Returns:
            Path to JSON report
        """
        report = {
            'campaign': {
                'timestamp': result.timestamp.isoformat(),
                'duration_sec': result.duration_sec,
                'total_generations': result.total_generations,
                'accepted': result.accepted_count,
                'rejected': result.rejected_count,
                'failed': result.failed_count,
                'acceptance_rate_percent': result.acceptance_rate
            },
            'hardware': result.hardware_info,
            'policy': result.policy_config,
            'generations': result.generations_data,
            'best_candidate': {
                'generation': result.best_candidate.generation if result.best_candidate else None,
                'score': result.best_score,
                'hash': result.best_candidate.hash if result.best_candidate else None
            },
            'snapshots': result.snapshots
        }
        
        json_path = self.reports_dir / f'campaign_{timestamp}.json'
        with open(json_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"JSON report: {json_path}")
        return str(json_path)

    def _generate_markdown_report(self, result: CampaignResult, timestamp: str) -> str:
        """Generate human-readable Markdown report.
        
        Args:
            result: Campaign result
            timestamp: Report timestamp
            
        Returns:
            Path to Markdown report
        """
        md = []
        md.append("# MERCURY-AEL Campaign Report\n")
        md.append(f"**Timestamp:** {result.timestamp.isoformat()}\n")
        md.append(f"**Duration:** {result.duration_sec:.1f}s\n")
        
        # Campaign summary
        md.append("## Campaign Summary\n")
        md.append(f"| Metric | Value |")
        md.append(f"|--------|-------|")
        md.append(f"| Total Generations | {result.total_generations} |")
        md.append(f"| Accepted | {result.accepted_count} |")
        md.append(f"| Rejected | {result.rejected_count} |")
        md.append(f"| Failed | {result.failed_count} |")
        md.append(f"| Acceptance Rate | {result.acceptance_rate:.1f}% |")
        md.append(f"| Best Score | {result.best_score:.4f} |")
        md.append(f"| Average Score | {result.average_score:.4f} |\n")
        
        # Hardware info
        md.append("## Hardware\n")
        hw = result.hardware_info
        md.append(f"| Property | Value |")
        md.append(f"|----------|-------|")
        md.append(f"| CPU | {hw.get('cpu_architecture')} ({hw.get('cpu_count')} cores) |")
        md.append(f"| RAM | {hw.get('ram_mb')} MB |")
        md.append(f"| OS | {hw.get('os')} {hw.get('kernel_version')} |")
        md.append(f"| Disk | {hw.get('disk_mb')} MB |\n")
        
        # Policy gates
        md.append("## Verification Policy\n")
        md.append(f"| Gate | Status |")
        md.append(f"|------|--------|")
        for gate, status in result.policy_config.get('gates', {}).items():
            md.append(f"| {gate} | {status} |")
        md.append(f"| Minimum Score | {result.policy_config.get('minimum_score', 0.80)} |\n")
        
        # Best candidate
        if result.best_candidate:
            md.append("## Best Candidate\n")
            md.append(f"- **Hash:** {result.best_candidate.hash}\n")
            md.append(f"- **Generation:** {result.best_candidate.generation}\n")
            md.append(f"- **Score:** {result.best_score:.4f}\n")
            md.append(f"- **Timestamp:** {result.best_candidate.timestamp.isoformat()}\n")
        
        # Snapshots
        md.append("## Verified Snapshots\n")
        for snapshot in result.snapshots:
            md.append(f"- {snapshot}\n")
        
        # Footer
        md.append("\n---\n")
        md.append(f"*Generated by MERCURY-AEL v0.1*\n")
        
        md_path = self.reports_dir / f'campaign_{timestamp}.md'
        with open(md_path, 'w') as f:
            f.write('\n'.join(md))
        
        self.logger.info(f"Markdown report: {md_path}")
        return str(md_path)
