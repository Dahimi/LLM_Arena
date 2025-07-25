"""Agent data models for the Intelligence Arena System."""

from enum import Enum
from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class Division(Enum):
    """Agent division levels in the arena."""
    NOVICE = "novice"
    EXPERT = "expert" 
    MASTER = "master"
    KING = "king"


class AgentStats(BaseModel):
    """Statistical tracking for agent performance."""
    elo_rating: float = Field(default=1200.0, description="ELO rating score")
    total_matches: int = Field(default=0, description="Total matches played")
    wins: int = Field(default=0, description="Total wins")
    losses: int = Field(default=0, description="Total losses")
    draws: int = Field(default=0, description="Total draws")
    current_streak: int = Field(default=0, description="Current win/loss streak (positive=wins, negative=losses)")
    best_streak: int = Field(default=0, description="Best win streak achieved")
    consistency_score: float = Field(default=0.0, description="Performance consistency metric (0-1)")
    innovation_index: float = Field(default=0.0, description="Creativity/originality score (0-1)")
    challenges_created: int = Field(default=0, description="Number of challenges created")
    challenge_quality_avg: float = Field(default=0.0, description="Average quality of created challenges")
    judge_accuracy: float = Field(default=0.0, description="Accuracy when acting as judge")
    judge_reliability: float = Field(default=1.0, description="Reliability weight for judging (0-1)")
    
    @property
    def win_rate(self) -> float:
        """Calculate win rate percentage."""
        if self.total_matches == 0:
            return 0.0
        return (self.wins / self.total_matches) * 100
    
    @property
    def loss_rate(self) -> float:
        """Calculate loss rate percentage."""
        if self.total_matches == 0:
            return 0.0
        return (self.losses / self.total_matches) * 100


class AgentProfile(BaseModel):
    """Profile information for an agent."""
    agent_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique agent identifier")
    name: str = Field(description="Agent display name")
    description: str = Field(default="", description="Agent description or bio")
    specializations: List[str] = Field(default_factory=list, description="Areas of expertise")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    last_active: datetime = Field(default_factory=datetime.utcnow, description="Last activity timestamp")
    is_active: bool = Field(default=True, description="Whether agent is currently active")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional agent metadata")


class Agent(BaseModel):
    """Main agent class representing a competitor in the arena."""
    profile: AgentProfile = Field(description="Agent profile information")
    division: Division = Field(default=Division.NOVICE, description="Current division")
    stats: AgentStats = Field(default_factory=AgentStats, description="Performance statistics")
    match_history: List[str] = Field(default_factory=list, description="List of match IDs")
    challenge_history: List[str] = Field(default_factory=list, description="List of challenge IDs created")
    division_change_history: List[Dict[str, Any]] = Field(default_factory=list, description="Division promotion/demotion history")
    
    def __str__(self) -> str:
        """String representation of the agent."""
        return f"Agent({self.profile.name}, {self.division.value}, ELO: {self.stats.elo_rating:.0f})"
    
    def __repr__(self) -> str:
        """Detailed representation of the agent."""
        return f"Agent(id={self.profile.agent_id}, name={self.profile.name}, division={self.division.value}, elo={self.stats.elo_rating})"
    
    def update_last_active(self) -> None:
        """Update the last active timestamp."""
        self.profile.last_active = datetime.utcnow()
    
    def add_match(self, match_id: str) -> None:
        """Add a match to the agent's history."""
        self.match_history.append(match_id)
        self.update_last_active()
    
    def add_challenge(self, challenge_id: str) -> None:
        """Add a created challenge to the agent's history."""
        self.challenge_history.append(challenge_id)
        self.stats.challenges_created += 1
        self.update_last_active()
    
    def promote_division(self, new_division: Division, reason: str = "") -> None:
        """Promote agent to a higher division."""
        old_division = self.division
        self.division = new_division
        self.division_change_history.append({
            "from_division": old_division.value,
            "to_division": new_division.value,
            "timestamp": datetime.utcnow(),
            "reason": reason,
            "type": "promotion"
        })
        self.update_last_active()
    
    def demote_division(self, new_division: Division, reason: str = "") -> None:
        """Demote agent to a lower division."""
        old_division = self.division
        self.division = new_division
        self.division_change_history.append({
            "from_division": old_division.value,
            "to_division": new_division.value,
            "timestamp": datetime.utcnow(),
            "reason": reason,
            "type": "demotion"
        })
        self.update_last_active()
    
    def is_eligible_for_promotion(self) -> bool:
        """Check if agent is eligible for promotion based on performance."""
        # Promotion criteria: 
        # - Win streak >= 3
        # - Win rate > 60%
        # - At least 5 matches played
        return (
            self.stats.current_streak >= 3 and
            self.stats.win_rate > 60 and
            self.stats.total_matches >= 5
        )
    
    def should_be_demoted(self) -> bool:
        """Check if agent should be demoted based on poor performance."""
        # Demotion criteria:
        # - Loss streak >= 5
        # - Win rate < 30% (with at least 10 matches)
        return (
            self.stats.current_streak <= -5 or
            (self.stats.win_rate < 30 and self.stats.total_matches >= 10)
        ) 