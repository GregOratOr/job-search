"""
resume/cv_utils.py
------------------
Dataclass definitions and Enum helpers for the CV system.

RULE: No personal data here. All personal content lives in profile/master_data.py.
      This file defines STRUCTURE, not content.
"""

from dataclasses import dataclass, field
from typing import List, Optional, TypeVar, Generic, Type
from enum import Enum


# ==============================================================================
# DATACLASS DEFINITIONS
# ==============================================================================

@dataclass
class SectionConfig:
    """Controls which sections are rendered in the final PDF.
    All flags default to the most common case (experience + projects + skills + education).
    Override in your tailoring file as needed.
    """
    show_position_applied: bool = False
    show_summary:          bool = False
    show_skills:           bool = True
    show_experience:       bool = True
    show_projects:         bool = True
    show_research:         bool = False
    show_education:        bool = True
    show_coursework:       bool = False


@dataclass
class HeaderInfo:
    """Sender / applicant contact information."""
    name:           str
    email:          Optional[str]
    phone_primary:  Optional[str]
    location:       str
    linkedin_url:   Optional[str]
    github_url:     Optional[str]
    phone_secondary: Optional[str] = None
    website_url:     Optional[str] = None
    leetcode_url:    Optional[str] = None


@dataclass
class PositionInfo:
    """Target role details (only shown if show_position_applied=True)."""
    role: str = ""


@dataclass
class EducationEntry:
    institution: str
    location:    str
    date:        str
    degree:      str
    gpa:         str = ""
    details:     List[str] = field(default_factory=list)
    achievements: List[str] = field(default_factory=list)


@dataclass
class SkillCategory:
    name:  str   # e.g. "Languages"
    items: str   # e.g. "Python3, C++, Java"


@dataclass
class ExperienceEntry:
    """Work experience or internship entry."""
    role:       str
    company:    str
    date:       str
    highlights: List[str] = field(default_factory=list)
    active:     bool = True  # kept for backwards compatibility; prefer selection in tailoring


@dataclass
class ProjectEntry:
    title:        str
    organization: str
    date:         str
    aim:          Optional[str] = None
    highlights:   List[str] = field(default_factory=list)
    active:       bool = True


@dataclass
class CourseworkEntry:
    title:       str
    courses:     List[str] = field(default_factory=list)
    use_multicol: bool = False
    active:      bool = True


@dataclass
class ResearchEntry:
    title:           str
    organization:    str
    date:            str
    highlights:      List[str] = field(default_factory=list)
    publication_url: Optional[str] = None
    active:          bool = True


@dataclass
class CV:
    """Root data object passed to the Jinja2 template."""
    config:     SectionConfig
    header:     HeaderInfo
    position:   PositionInfo
    education:  List[EducationEntry]
    skills:     List[SkillCategory]
    experience: List[ExperienceEntry]
    projects:   List[ProjectEntry]
    research:   List[ResearchEntry]
    coursework: List[CourseworkEntry]
    output_file: str = ""
    summary:     Optional[str] = None


# ==============================================================================
# ENUM STRING BUILDER
# ==============================================================================

T = TypeVar('T', bound=Enum)


class EnumStringBuilder(Generic[T]):
    """Fluent builder for composing comma-separated skill strings from Enums.

    Usage:
        s = EnumStringBuilder(Languages).add(Languages.python).add(Languages.cpp).build
        # → "Python3, C++"
    """
    def __init__(self, enum_class: Type[T], separator: str = ", "):
        self._enum_class = enum_class
        self._separator = separator
        self._selections: List[T] = []

    def add(self, item: T) -> 'EnumStringBuilder[T]':
        if not isinstance(item, self._enum_class):
            raise TypeError(f"Expected {self._enum_class.__name__}, got {type(item).__name__}")
        self._selections.append(item)
        return self

    @property
    def build(self) -> str:
        return self._separator.join(str(item.value) for item in self._selections)


# ==============================================================================
# ENUMS — extend these as you gain new skills/tools
# ==============================================================================

def _enum_mixin():
    """Returns mixin methods for string-composable Enums."""
    def __add__(self, other):
        return str(self) + str(other)
    def __radd__(self, other):
        return str(other) + str(self)
    def __str__(self):
        return self.value
    return __add__, __radd__, __str__


class _StrEnum(Enum):
    """Base class that makes Enum values compose as strings."""
    def __add__(self, other):  return str(self) + str(other)
    def __radd__(self, other): return str(other) + str(self)
    def __str__(self):         return self.value


class Competencies(_StrEnum):
    ds           = "Data Structures"
    algo         = "Algorithms"
    dl           = "Deep Learning"
    ml           = "Machine Learning"
    rl           = "Reinforcement Learning"
    nlp          = "Natural Language Processing"
    mas          = "Multiagent Systems"
    cv           = "Computer Vision"
    genai        = "Generative AI"
    gd           = "Game Development"
    cam          = "Computer-Aided 3D Modeling"
    mlops        = "MLOps"
    distsys      = "Distributed Systems"
    parallelcomp = "Parallel Computing"
    gpuopti      = "GPU Optimization"


class Languages(_StrEnum):
    python = "Python3"
    csharp = "C\\#"
    cpp    = "C++"
    c      = "C"
    java   = "Java"
    js     = "JavaScript"


class Libraries(_StrEnum):
    ddp         = "PyTorch DDP"
    numpy       = "NumPy"
    pd          = "Pandas"
    matplotlib  = "Matplotlib"
    opencv      = "OpenCV"
    opengl      = "OpenGL"
    sklearn     = "Scikit-learn"
    skimage     = "Scikit-image"
    huggingface = "Hugging Face"
    jinja2      = "Jinja2"
    wandb       = "Weights \\& Biases"
    tb          = "TensorBoard"
    gym         = "Gymnasium"
    javafx      = "JavaFX"


class Frameworks(_StrEnum):
    pytorch   = "PyTorch"
    tf        = "TensorFlow"
    streamlit = "Streamlit"
    cuda      = "CUDA"
    nextjs    = "Next.js"
    twcss     = "Tailwind CSS"
    onnx      = "ONNX"
    fastapi   = "FastAPI"
    gym       = "OpenAI Gym"
    minigrid  = "MiniGrid"
    marllib   = "MARLlib"


class Tools(_StrEnum):
    github     = "GitHub"
    jupyterlab = "JupyterLab"
    vscode     = "VS Code"
    latex      = "LaTeX"
    anaconda   = "Anaconda"
    mssql      = "MS SQL"
    mysql      = "MySQL"
    unity      = "Unity 3D"
    docker     = "Docker"
    imageJ     = "ImageJ"
    ollama     = "Ollama"
    n8n        = "n8n"
    nsight     = "Nsight Compute"
    linux      = "Linux"
    matlab     = "MATLAB"
    unityprof  = "Unity Profiler"
