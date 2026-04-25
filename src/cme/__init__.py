"""Multi-Agent CFO Operating System.

A CHP-hardened, shared-context platform where Finance, Strategy, and Compliance
agents collaborate on forecasts, investment cases, and board outputs with a
single auditable reasoning trail.

Composes four well-specified subsystems:
    - CognitiveMeshProtocol  (expansion/compression reasoning cycles)
    - ContextEngine          (layered memory + entity/event/task schema)
    - Playbook               (ACE evolving playbooks with delta updates)
    - Consensus Hardening Protocol (foundation hardening + lock progression)
"""

from cme.protocol import CognitiveMeshProtocol, ReasoningTrace, ProblemType
from cme.context import ContextEngine, Entity, Event, Task
from cme.playbook import Playbook, Bullet, Reflector, Curator
from cme.bridge import BridgeFramework, Workflow, Statement
from cme.agent import MeshAgent, AgentCapability
from cme.orchestrator import EnterpriseOrchestrator
from cme.chp import CHPOrchestrator, DecisionCase, Dossier
from cme.cfo_os import (
    BoardBrief,
    CFOOperatingSystem,
    CFOTaskType,
    ForecastBrief,
    InvestmentBrief,
)

__version__ = "0.1.0"

__all__ = [
    "CognitiveMeshProtocol",
    "ReasoningTrace",
    "ProblemType",
    "ContextEngine",
    "Entity",
    "Event",
    "Task",
    "Playbook",
    "Bullet",
    "Reflector",
    "Curator",
    "BridgeFramework",
    "Workflow",
    "Statement",
    "MeshAgent",
    "AgentCapability",
    "EnterpriseOrchestrator",
    "CHPOrchestrator",
    "DecisionCase",
    "Dossier",
    "BoardBrief",
    "CFOOperatingSystem",
    "CFOTaskType",
    "ForecastBrief",
    "InvestmentBrief",
]
