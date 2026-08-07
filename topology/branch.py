from dataclasses import dataclass, field

from topology.bone import Bone


@dataclass
class Branch:

    ################################################
    # ESTRUCTURA
    ################################################

    bones: list[Bone] = field(default_factory=list)

    ################################################
    # FEATURES
    ################################################

    bone_count: int = 0

    length: float = 0.0

    ratio: float = 0.0
    
    depth: int = 0