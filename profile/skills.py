"""
profile/skills.py
-----------------
Skill category presets. These are pre-built lists of SkillCategory objects
ready to drop into a CV tailoring file.

Agent instructions:
  - To add a new skill to an existing category: add the enum value to the builder chain.
  - To add a brand-new skill/tool that doesn't exist yet: add it to the relevant
    Enum class in resume/cv_utils.py first, then reference it here.
  - To create a new preset (e.g. SKILLS_GAMEDEV): copy the SKILLS_SWE_FOCUSED block.
  - After editing, append a line to profile/CHANGELOG.md.

Available Enum classes (in resume/cv_utils.py):
  Languages, Frameworks, Libraries, Tools, Competencies
"""

from resume.cv_utils import (
    SkillCategory, EnumStringBuilder,
    Competencies, Languages, Frameworks, Libraries, Tools
)

# ── Full skill set ────────────────────────────────────────────────────────────
# Use for: senior roles, academic positions, anything where breadth matters.

SKILLS_FULL = [
    SkillCategory("Core Competencies",
        EnumStringBuilder(Competencies)
        .add(Competencies.dl).add(Competencies.cv).add(Competencies.ml)
        .add(Competencies.nlp).add(Competencies.rl).add(Competencies.mas)
        .add(Competencies.genai).add(Competencies.mlops)
        .add(Competencies.parallelcomp).add(Competencies.gpuopti)
        .add(Competencies.distsys).add(Competencies.algo).add(Competencies.ds)
        .build
    ),
    SkillCategory("Languages",
        EnumStringBuilder(Languages)
        .add(Languages.python).add(Languages.csharp).add(Languages.cpp)
        .add(Languages.c).add(Languages.java).add(Languages.js)
        .build
    ),
    SkillCategory("Frameworks",
        EnumStringBuilder(Frameworks)
        .add(Frameworks.pytorch).add(Frameworks.fastapi).add(Frameworks.tf)
        .add(Frameworks.onnx).add(Frameworks.streamlit)
        .add(Frameworks.nextjs).add(Frameworks.twcss).add(Frameworks.cuda)
        .build
    ),
    SkillCategory("Libraries",
        EnumStringBuilder(Libraries)
        .add(Libraries.huggingface).add(Libraries.wandb).add(Libraries.tb)
        .add(Libraries.ddp).add(Libraries.numpy).add(Libraries.pd)
        .add(Libraries.matplotlib).add(Libraries.opencv)
        .add(Libraries.sklearn).add(Libraries.gym).add(Libraries.jinja2)
        .build
    ),
    SkillCategory("Tools",
        EnumStringBuilder(Tools)
        .add(Tools.docker).add(Tools.github).add(Tools.linux)
        .add(Tools.nsight).add(Tools.matlab).add(Tools.unity)
        .add(Tools.unityprof).add(Tools.ollama).add(Tools.n8n)
        .build
    ),
]

# ── ML / AI engineering focused ───────────────────────────────────────────────
# Use for: ML Engineer, AI Engineer, DL Engineer, Research Engineer roles.

SKILLS_ML_FOCUSED = [
    SkillCategory("Core Competencies",
        EnumStringBuilder(Competencies)
        .add(Competencies.dl).add(Competencies.ml).add(Competencies.cv)
        .add(Competencies.nlp).add(Competencies.genai).add(Competencies.mlops)
        .add(Competencies.gpuopti).add(Competencies.parallelcomp)
        .build
    ),
    SkillCategory("Languages",
        EnumStringBuilder(Languages)
        .add(Languages.python).add(Languages.cpp).add(Languages.c)
        .add(Languages.java).add(Languages.js)
        .build
    ),
    SkillCategory("Frameworks",
        EnumStringBuilder(Frameworks)
        .add(Frameworks.pytorch).add(Frameworks.tf).add(Frameworks.onnx)
        .add(Frameworks.cuda).add(Frameworks.fastapi)
        .build
    ),
    SkillCategory("Libraries",
        EnumStringBuilder(Libraries)
        .add(Libraries.huggingface).add(Libraries.wandb).add(Libraries.ddp)
        .add(Libraries.numpy).add(Libraries.pd).add(Libraries.opencv)
        .add(Libraries.sklearn)
        .build
    ),
    SkillCategory("Tools",
        EnumStringBuilder(Tools)
        .add(Tools.docker).add(Tools.github).add(Tools.linux)
        .add(Tools.nsight).add(Tools.matlab)
        .build
    ),
]

# ── Software engineering focused ──────────────────────────────────────────────
# Use for: SWE, Backend Engineer, Systems Engineer roles.

SKILLS_SWE_FOCUSED = [
    SkillCategory("Core Competencies",
        EnumStringBuilder(Competencies)
        .add(Competencies.ds).add(Competencies.algo).add(Competencies.distsys)
        .add(Competencies.parallelcomp).add(Competencies.gpuopti)
        .build
    ),
    SkillCategory("Languages",
        EnumStringBuilder(Languages)
        .add(Languages.python).add(Languages.cpp).add(Languages.c)
        .add(Languages.java).add(Languages.js).add(Languages.csharp)
        .build
    ),
    SkillCategory("Frameworks",
        EnumStringBuilder(Frameworks)
        .add(Frameworks.pytorch).add(Frameworks.fastapi).add(Frameworks.cuda)
        .add(Frameworks.nextjs).add(Frameworks.twcss)
        .build
    ),
    SkillCategory("Libraries",
        EnumStringBuilder(Libraries)
        .add(Libraries.numpy).add(Libraries.pd).add(Libraries.opencv)
        .add(Libraries.ddp).add(Libraries.jinja2)
        .build
    ),
    SkillCategory("Tools",
        EnumStringBuilder(Tools)
        .add(Tools.docker).add(Tools.github).add(Tools.linux)
        .add(Tools.nsight).add(Tools.matlab)
        .build
    ),
]

# ── Research scientist focused ────────────────────────────────────────────────
# Use for: Research Scientist, Research Engineer, PhD applications.

SKILLS_RESEARCH_FOCUSED = [
    SkillCategory("Core Competencies",
        EnumStringBuilder(Competencies)
        .add(Competencies.dl).add(Competencies.rl).add(Competencies.mas)
        .add(Competencies.ml).add(Competencies.nlp).add(Competencies.cv)
        .add(Competencies.genai)
        .build
    ),
    SkillCategory("Languages",
        EnumStringBuilder(Languages)
        .add(Languages.python).add(Languages.cpp).add(Languages.java)
        .build
    ),
    SkillCategory("Frameworks",
        EnumStringBuilder(Frameworks)
        .add(Frameworks.pytorch).add(Frameworks.tf).add(Frameworks.cuda)
        .add(Frameworks.marllib).add(Frameworks.minigrid).add(Frameworks.gym)
        .build
    ),
    SkillCategory("Libraries",
        EnumStringBuilder(Libraries)
        .add(Libraries.huggingface).add(Libraries.wandb).add(Libraries.tb)
        .add(Libraries.gym).add(Libraries.numpy).add(Libraries.pd)
        .build
    ),
    SkillCategory("Tools",
        EnumStringBuilder(Tools)
        .add(Tools.docker).add(Tools.github).add(Tools.linux).add(Tools.matlab)
        .build
    ),
]
