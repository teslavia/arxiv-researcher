#!/usr/bin/env python3
"""RKNN deployment scaffold using an ONNX input model."""

from __future__ import annotations

import argparse
from pathlib import Path

from rknn.api import RKNN

QUANTIZE = {{QUANTIZE}}  # None | "fp16" | "int8"


def build_rknn(onnx_path: Path, output_path: Path, quantize: str | None) -> None:
    rknn = RKNN()

    # TODO: set the correct target platform (e.g., rk3588, rk3566, rv1106)
    rknn.config(target_platform="rk3588")

    ret = rknn.load_onnx(model=str(onnx_path))
    if ret != 0:
        raise RuntimeError("Failed to load ONNX model")

    do_quantization = quantize == "int8"
    dataset_path = "dataset.txt" if do_quantization else None
    # TODO: provide a real dataset file for quantization

    ret = rknn.build(do_quantization=do_quantization, dataset=dataset_path)
    if ret != 0:
        raise RuntimeError("RKNN build failed")

    ret = rknn.export_rknn(str(output_path))
    if ret != 0:
        raise RuntimeError("RKNN export failed")

    rknn.release()


def main() -> None:
    parser = argparse.ArgumentParser(description="Build RKNN model from ONNX")
    parser.add_argument("--onnx", type=Path, default=Path("model.onnx"))
    parser.add_argument("--output", type=Path, default=Path("model.rknn"))
    args = parser.parse_args()

    build_rknn(args.onnx, args.output, QUANTIZE)


if __name__ == "__main__":
    main()
