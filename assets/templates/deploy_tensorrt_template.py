#!/usr/bin/env python3
"""TensorRT deployment scaffold using an ONNX input model."""

from __future__ import annotations

import argparse
from pathlib import Path

import tensorrt as trt

QUANTIZE = {{QUANTIZE}}  # None | "fp16" | "int8"


def build_engine(onnx_path: Path, engine_path: Path, quantize: str | None) -> None:
    logger = trt.Logger(trt.Logger.INFO)
    builder = trt.Builder(logger)
    network = builder.create_network(
        1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)
    )
    parser = trt.OnnxParser(network, logger)

    with onnx_path.open("rb") as onnx_file:
        if not parser.parse(onnx_file.read()):
            raise RuntimeError("Failed to parse ONNX model")

    config = builder.create_builder_config()
    config.set_memory_pool_limit(trt.MemoryPoolType.WORKSPACE, 1 << 30)

    if quantize == "fp16":
        config.set_flag(trt.BuilderFlag.FP16)
    elif quantize == "int8":
        config.set_flag(trt.BuilderFlag.INT8)
        # TODO: provide an INT8 calibrator
        # config.int8_calibrator = MyCalibrator(...)

    serialized_engine = builder.build_serialized_network(network, config)
    if serialized_engine is None:
        raise RuntimeError("Engine build failed")

    engine_path.write_bytes(serialized_engine)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build TensorRT engine from ONNX")
    parser.add_argument("--onnx", type=Path, default=Path("model.onnx"))
    parser.add_argument("--engine", type=Path, default=Path("model.trt"))
    args = parser.parse_args()

    build_engine(args.onnx, args.engine, QUANTIZE)


if __name__ == "__main__":
    main()
