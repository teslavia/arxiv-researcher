#!/usr/bin/env python3
"""Core ML deployment scaffold using coremltools."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import coremltools as ct
import torch
from coremltools.optimize.coreml import quantization_utils

QUANTIZE = {{QUANTIZE}}  # None | "fp16" | "int8"


def build_model() -> torch.nn.Module:
    """Build and load your PyTorch model here."""
    # TODO: construct model and load weights
    raise NotImplementedError


def example_input() -> torch.Tensor:
    """Return a representative example input for tracing."""
    # TODO: return real input shape
    return torch.randn(1, 3, 224, 224)


def export_coreml(
    model: torch.nn.Module,
    example: torch.Tensor,
    output_path: Path,
    quantize: str | None,
) -> None:
    model.eval()
    traced = torch.jit.trace(model, example)

    convert_args: dict[str, Any] = {
        "convert_to": "mlprogram",
        "inputs": [ct.TensorType(shape=example.shape)],
    }
    if quantize == "fp16":
        convert_args["compute_precision"] = ct.precision.FLOAT16

    mlmodel = ct.convert(traced, **convert_args)

    if quantize == "int8":
        # TODO: supply calibration data if needed
        mlmodel = quantization_utils.quantize_weights(mlmodel, nbits=8)

    mlmodel.save(str(output_path))


def main() -> None:
    parser = argparse.ArgumentParser(description="Export PyTorch model to Core ML")
    parser.add_argument("--output", type=Path, default=Path("model.mlpackage"))
    args = parser.parse_args()

    model = build_model()
    sample = example_input()
    export_coreml(model, sample, args.output, QUANTIZE)


if __name__ == "__main__":
    main()
