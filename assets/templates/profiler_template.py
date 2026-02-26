#!/usr/bin/env python3
"""PyTorch profiling scaffold with memory and FLOPs tracing."""

from __future__ import annotations

import argparse
import contextlib
from pathlib import Path

import torch

try:
    from torch.profiler import ProfilerActivity, profile, record_function
except (ImportError, OSError):
    ProfilerActivity = None
    profile = None
    record_function = None

try:
    import torch_tie  # type: ignore
except (ImportError, OSError):
    torch_tie = None


def build_model() -> torch.nn.Module:
    """Build and load your model here."""
    # TODO: construct model and load weights
    raise NotImplementedError


def example_input() -> torch.Tensor:
    """Return a representative example input."""
    # TODO: return real input shape
    return torch.randn(1, 3, 224, 224)


@contextlib.contextmanager
def record_scope(name: str):
    if record_function is None:
        yield
        return
    with record_function(name):
        yield


def run_step(model: torch.nn.Module, inputs: torch.Tensor) -> torch.Tensor:
    outputs = model(inputs)
    loss = outputs.mean()
    loss.backward()
    return loss


def run_profiler(
    model: torch.nn.Module, inputs: torch.Tensor, output_dir: Path
) -> None:
    if profile is None or ProfilerActivity is None:
        print("torch.profiler is unavailable. Install a newer PyTorch build.")
        return

    activities = [ProfilerActivity.CPU]
    if torch.cuda.is_available():
        activities.append(ProfilerActivity.CUDA)
        model = model.cuda()
        inputs = inputs.cuda()
    else:
        print("CUDA not available; profiling on CPU only.")

    output_dir.mkdir(parents=True, exist_ok=True)
    trace_path = output_dir / "trace.json"

    with profile(
        activities=activities,
        record_shapes=True,
        profile_memory=True,
        with_flops=True,
    ) as prof:
        with record_scope("forward_backward"):
            run_step(model, inputs)
        prof.step()

    prof.export_chrome_trace(str(trace_path))
    print(f"Saved trace: {trace_path}")
    print(prof.key_averages().table(sort_by="self_cuda_memory_usage", row_limit=10))


def run_tie_analysis(model: torch.nn.Module, inputs: torch.Tensor) -> None:
    if torch_tie is None:
        print("TorchTIE not installed; skipping TorchTIE analysis.")
        return
    # TODO: integrate TorchTIE once available in your environment
    _ = model, inputs
    print("TorchTIE hook placeholder")


def main() -> None:
    parser = argparse.ArgumentParser(description="Profile model memory and FLOPs")
    parser.add_argument("--output", type=Path, default=Path("profile"))
    args = parser.parse_args()

    model = build_model()
    inputs = example_input()

    run_profiler(model, inputs, args.output)
    run_tie_analysis(model, inputs)


if __name__ == "__main__":
    main()
