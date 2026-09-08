"""Main evolution engine orchestrator for MERCURY-AEL."""
import time
import json
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

from core.generator import Generator
from core.validator import Validator
from core.scorer import Scorer
from core.benchmark import Benchmark
from core.resource_monitor import ResourceMonitor
from core.sandbox import Sandbox
from core.snapshot_manager import SnapshotManager
from core.rollback_manager import RollbackManager
from core.failure_analyzer import FailureAnalyzer
from core.project_router import ProjectRouter
from core.evolution_logger import EvolutionLogger
from core.data_structures import Candidate, ValidationResult, CampaignResult


class EvolutionEngine:
    """Orchestrates the complete evolution loop for autonomous algorithm generation."""

    def __init__(self, config: Dict, hardware: Dict, logger: EvolutionLogger = None):
        self.config = config
        self.hardware = hardware
        self.logger = logger or EvolutionLogger()
        
        # Initialize all subsystems
        self.generator = Generator(config, self.logger)
        self.validator = Validator(config, self.logger)
        self.scorer = Scorer(config, self.logger)
        self.sandbox = Sandbox(config, self.logger)
        self.benchmark = Benchmark(config, self.sandbox, self.logger)
        self.resource_monitor = ResourceMonitor(config, self.logger)
        self.snapshot_mgr = SnapshotManager(logger=self.logger)
        self.rollback_mgr = RollbackManager(self.snapshot_mgr, logger=self.logger)
        self.failure_analyzer = FailureAnalyzer(logger=self.logger)
        self.project_router = ProjectRouter(self.logger)
        
        # Campaign state
        self.generations_data = []
        self.accepted_candidates = []
        self.rejected_candidates = []
        self.campaign_start_time = None
        self.stop_requested = False

    def run_campaign(self, num_generations: int) -> CampaignResult:
        """Run autonomous evolution campaign.
        
        Args:
            num_generations: Number of generations to run
            
        Returns:
            CampaignResult with complete statistics
        """
        self.campaign_start_time = time.time()
        self.logger.info(f"Starting campaign: {num_generations} generations")
        self.logger.info(f"Hardware: {self.hardware['cpu_architecture']} ({self.hardware['cpu_count']} cores), {self.hardware['ram_mb']} MB RAM")
        self.logger.info(f"Policy minimum score: {self.config['policies'].get('minimum_score', 0.80)}")
        
        accepted_count = 0
        rejected_count = 0
        failed_count = 0
        best_score = 0.0
        best_candidate = None
        total_scores = []
        
        try:
            for generation in range(1, num_generations + 1):
                # Check resource limits
                if self.resource_monitor.exceeded_limits():
                    self.logger.warning("Resource limits exceeded. Stopping campaign.")
                    break
                
                if self.stop_requested:
                    self.logger.warning("Stop requested. Halting campaign.")
                    break
                
                # Log resource status
                self.resource_monitor.log_resource_usage()
                
                # Execute single generation
                gen_result = self._run_generation(generation)
                
                if gen_result:
                    candidate, validation, score, accepted = gen_result
                    
                    # Update statistics
                    self.generations_data.append({
                        'generation': generation,
                        'candidate_hash': candidate.hash,
                        'score': score,
                        'accepted': accepted,
                        'validation': validation.to_dict()
                    })
                    
                    if accepted:
                        accepted_count += 1
                        self.accepted_candidates.append(candidate)
                        self.snapshot_mgr.create_snapshot(candidate, generation, validation, score)
                    else:
                        rejected_count += 1
                        self.rejected_candidates.append(candidate)
                        self._save_rejected(candidate, validation, generation)
                    
                    total_scores.append(score)
                    
                    if score > best_score:
                        best_score = score
                        best_candidate = candidate
                    
                    self.logger.info(f"Gen {generation:06d} | Score: {score:.4f} | Status: {'ACCEPT' if accepted else 'REJECT'} | Best: {best_score:.4f}")
                else:
                    failed_count += 1
        
        except KeyboardInterrupt:
            self.logger.warning("Campaign interrupted by user")
        except Exception as e:
            self.logger.error(f"Campaign error: {e}")
        
        finally:
            self.sandbox.cleanup()
        
        # Generate final report
        duration_sec = time.time() - self.campaign_start_time
        average_score = sum(total_scores) / len(total_scores) if total_scores else 0.0
        
        result = CampaignResult(
            total_generations=num_generations,
            accepted_count=accepted_count,
            rejected_count=rejected_count,
            failed_count=failed_count,
            best_score=best_score,
            best_candidate=best_candidate,
            average_score=average_score,
            snapshots=self.snapshot_mgr.list_snapshots(),
            duration_sec=duration_sec,
            timestamp=datetime.now(),
            hardware_info=self.hardware,
            policy_config=self.config.get('policies', {}),
            generations_data=self.generations_data
        )
        
        # Generate reports
        report_path = self._generate_reports(result)
        result.report_path = report_path
        
        self.logger.info(f"Campaign complete: {accepted_count} accepted, {rejected_count} rejected, {failed_count} failed")
        self.logger.info(f"Best score: {best_score:.4f}")
        self.logger.info(f"Reports: {report_path}")
        
        return result

    def _run_generation(self, generation: int) -> Optional[tuple]:
        """Execute single generation cycle.
        
        Args:
            generation: Generation number
            
        Returns:
            Tuple of (candidate, validation, score, accepted) or None
        """
        try:
            # 1. Analyze failure history
            failure_context = self.failure_analyzer.analyze()
            context = {
                'generation': generation,
                'failure_patterns': failure_context,
                'hardware': self.hardware,
                'project_type': self.project_router.project_type
            }
            
            # 2. Generate candidate
            candidate = self.generator.generate(context)
            
            # 3. Validate candidate
            validation = self.validator.validate(candidate)
            
            # 4. Run benchmark if validation passed core gates
            benchmark_data = {}
            if validation.syntax_pass and validation.unit_tests_pass:
                benchmark_result = self.benchmark.run_benchmark(candidate)
                benchmark_data = benchmark_result.to_dict()
                validation.benchmark_pass = benchmark_result.passed
            
            # 5. Score candidate
            score = self.scorer.score(candidate, validation, benchmark_data)
            
            # 6. Apply policy gates and make accept/reject decision
            accepted = self._apply_policy(candidate, score, validation)
            
            return candidate, validation, score, accepted
        
        except Exception as e:
            self.logger.error(f"Generation {generation} error: {e}")
            return None

    def _apply_policy(self, candidate: Candidate, score: float, validation: ValidationResult) -> bool:
        """Apply configurable acceptance policy gates.
        
        Args:
            candidate: Candidate to evaluate
            score: Candidate score
            validation: Validation result
            
        Returns:
            True if accepted, False if rejected
        """
        policy = self.config.get('policies', {})
        minimum_score = policy.get('minimum_score', 0.80)
        
        # All mandatory gates must pass
        gates = policy.get('gates', {})
        
        if gates.get('syntax') == 'required' and not validation.syntax_pass:
            return False
        if gates.get('compilation') == 'required' and not validation.compilation_pass:
            return False
        if gates.get('unit_tests') == 'required' and not validation.unit_tests_pass:
            return False
        if gates.get('property_tests') == 'required' and not validation.property_tests_pass:
            return False
        if gates.get('edge_tests') == 'required' and not validation.edge_tests_pass:
            return False
        if gates.get('security_checks') == 'required' and not validation.security_pass:
            return False
        if gates.get('resource_limits') == 'required' and not validation.resource_pass:
            return False
        if gates.get('benchmark') == 'required' and not validation.benchmark_pass:
            return False
        
        # Check minimum score
        if score < minimum_score:
            return False
        
        return True

    def _save_rejected(self, candidate: Candidate, validation: ValidationResult, generation: int):
        """Save rejected candidate metadata.
        
        Args:
            candidate: Rejected candidate
            validation: Validation result
            generation: Generation number
        """
        rejected_dir = Path('rejected')
        rejected_dir.mkdir(exist_ok=True)
        
        candidate_id = f"gen-{generation:06d}-{candidate.hash[:8]}"
        candidate_dir = rejected_dir / candidate_id
        candidate_dir.mkdir(exist_ok=True)
        
        # Save rejection metadata
        metadata = {
            'generation': generation,
            'candidate_hash': candidate.hash,
            'timestamp': candidate.timestamp.isoformat(),
            'validation': validation.to_dict(),
            'failure_type': self._determine_failure_type(validation),
            'project_type': candidate.project_type
        }
        
        with open(candidate_dir / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)

    @staticmethod
    def _determine_failure_type(validation: ValidationResult) -> str:
        """Determine primary failure type from validation result.
        
        Args:
            validation: Validation result
            
        Returns:
            Failure type string
        """
        if not validation.syntax_pass:
            return 'syntax_errors'
        if not validation.compilation_pass:
            return 'compilation_errors'
        if not validation.unit_tests_pass or not validation.property_tests_pass:
            return 'test_failures'
        if not validation.security_pass:
            return 'security_issues'
        if not validation.benchmark_pass:
            return 'performance_degradation'
        return 'unknown'

    def _generate_reports(self, result: CampaignResult) -> str:
        """Generate JSON and Markdown reports.
        
        Args:
            result: Campaign result
            
        Returns:
            Path to generated report directory
        """
        from core.report_generator import ReportGenerator
        
        generator = ReportGenerator()
        report_path = generator.generate(result)
        return report_path

    def request_stop(self):
        """Request graceful campaign stop."""
        self.stop_requested = True
        self.logger.info("Stop requested - campaign will halt at next generation")
