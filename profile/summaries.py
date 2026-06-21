"""
profile/summaries.py
--------------------
Professional summary strings, keyed by role type.
"""

SUMMARIES: dict[str, str] = {

    "ml_engineer": (
        "ML Engineer with an M.S. in AI and hands-on experience building "
        "production-grade \\textbf{deep learning} systems, \\textbf{GPU-optimized} inference "
        "pipelines, and LLM-powered agents. Proficient in PyTorch, CUDA, and MLOps tooling. "
        "Seeking roles at the intersection of model development and systems performance."
    ),

    "swe": (
        "Software engineer with an M.S. in AI and a strong foundation in \\textbf{algorithms}, "
        "\\textbf{distributed systems}, and parallel computing. Experienced building full-stack "
        "applications and GPU-accelerated ML pipelines."
    ),

    "research_scientist": (
        "AI researcher specializing in \\textbf{reinforcement learning} and deep learning. "
        "Strong background in Python, PyTorch, and experimental design."
    ),

    "research_engineer": (
        "Research engineer bridging ML research and production systems. "
        "Experience in \\textbf{CUDA kernel development}, distributed training, and deploying "
        "research prototypes to production APIs."
    ),

    "cv_engineer": (
        "Computer vision engineer with experience building \\textbf{real-time detection} "
        "and \\textbf{anomaly detection} pipelines. Proficient in PyTorch, OpenCV, and ONNX Runtime."
    ),

    "generic": (
        "M.S. in Artificial Intelligence with experience spanning \\textbf{deep learning}, "
        "\\textbf{computer vision}, NLP, reinforcement learning, and GPU optimization."
    ),
}
