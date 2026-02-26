#!/usr/bin/env python3
"""Triton kernel scaffold with benchmarking against PyTorch."""

from __future__ import annotations

import argparse
import time
from typing import Any, cast

import torch

try:
    import triton  # type: ignore
    import triton.language as tl  # type: ignore
except (ImportError, OSError):
    triton = None
    tl = None

TRITON_AVAILABLE = triton is not None and tl is not None


def torch_reference(x: torch.Tensor, w: torch.Tensor) -> torch.Tensor:
    """Baseline implementation (replace with your PyTorch logic)."""
    return x @ w


def _ensure_triton() -> bool:
    if triton is None or tl is None:
        print("Triton not installed. Install with: pip install triton")
        return False
    if not torch.cuda.is_available():
        print("CUDA not available; Triton kernels require GPU.")
        return False
    return True


if TRITON_AVAILABLE:
    _triton = cast(Any, triton)
    _tl = cast(Any, tl)

    class _KernelNamespace:
        @staticmethod
        @_triton.jit
        def matmul_kernel(
            x_ptr,
            w_ptr,
            y_ptr,
            m,
            n,
            k,
            stride_xm,
            stride_xk,
            stride_wk,
            stride_wn,
            stride_ym,
            stride_yn,
            BLOCK_M,
            BLOCK_N,
            BLOCK_K,
        ):
            """
            Tiled matrix multiplication kernel.

            Heuristics:
            - BLOCK_M/BLOCK_N aligned to 128 bytes for coalesced loads.
            - BLOCK_K chosen to balance L2 reuse vs. register pressure.
            """
            pid_m = _tl.program_id(0)
            pid_n = _tl.program_id(1)

            offs_m = pid_m * BLOCK_M + _tl.arange(0, BLOCK_M)
            offs_n = pid_n * BLOCK_N + _tl.arange(0, BLOCK_N)
            offs_k = _tl.arange(0, BLOCK_K)

            acc = _tl.zeros((BLOCK_M, BLOCK_N), dtype=_tl.float32)
            k_iter = _tl.cdiv(k, BLOCK_K)
            for k_block in range(0, k_iter):
                k_start = k_block * BLOCK_K
                k_offsets = k_start + offs_k
                x_ptrs = (
                    x_ptr + offs_m[:, None] * stride_xm + k_offsets[None, :] * stride_xk
                )
                w_ptrs = (
                    w_ptr + k_offsets[:, None] * stride_wk + offs_n[None, :] * stride_wn
                )

                mask_x = (offs_m[:, None] < m) & (k_offsets[None, :] < k)
                mask_w = (k_offsets[:, None] < k) & (offs_n[None, :] < n)

                x = _tl.load(x_ptrs, mask=mask_x, other=0.0)
                w = _tl.load(w_ptrs, mask=mask_w, other=0.0)
                acc += _tl.dot(x, w)

            y = acc.to(_tl.float16)
            y_ptrs = y_ptr + offs_m[:, None] * stride_ym + offs_n[None, :] * stride_yn
            mask_y = (offs_m[:, None] < m) & (offs_n[None, :] < n)
            _tl.store(y_ptrs, y, mask=mask_y)


def triton_matmul(x: torch.Tensor, w: torch.Tensor) -> torch.Tensor:
    if not _ensure_triton():
        return torch_reference(x, w)

    if triton is None or tl is None or "matmul_kernel" not in globals():
        print("Triton kernel unavailable; falling back to PyTorch.")
        return torch_reference(x, w)

    m, k = x.shape
    _, n = w.shape
    y = torch.empty((m, n), device=x.device, dtype=torch.float16)

    # Block sizes tuned for coalesced memory access and occupancy.
    # Adjust BLOCK_K for better L2 reuse on your GPU.
    BLOCK_M = 128
    BLOCK_N = 128
    BLOCK_K = 32

    grid = (_triton.cdiv(m, BLOCK_M), _triton.cdiv(n, BLOCK_N))
    _KernelNamespace.matmul_kernel[grid](
        x,
        w,
        y,
        m,
        n,
        k,
        x.stride(0),
        x.stride(1),
        w.stride(0),
        w.stride(1),
        y.stride(0),
        y.stride(1),
        BLOCK_M=BLOCK_M,
        BLOCK_N=BLOCK_N,
        BLOCK_K=BLOCK_K,
    )
    return y


def benchmark(fn, x: torch.Tensor, w: torch.Tensor, iters: int = 50) -> float:
    torch.cuda.synchronize()
    start = time.perf_counter()
    for _ in range(iters):
        _ = fn(x, w)
    torch.cuda.synchronize()
    elapsed = time.perf_counter() - start
    return elapsed / iters


def tflops(m: int, n: int, k: int, seconds: float) -> float:
    flops = 2.0 * m * n * k
    return flops / seconds / 1e12


def bandwidth_gbps(
    m: int, n: int, k: int, seconds: float, bytes_per_el: int = 2
) -> float:
    bytes_moved = bytes_per_el * (m * k + k * n + m * n)
    return bytes_moved / seconds / 1e9


def main() -> None:
    parser = argparse.ArgumentParser(description="Triton kernel scaffold")
    parser.add_argument("--m", type=int, default=2048)
    parser.add_argument("--n", type=int, default=2048)
    parser.add_argument("--k", type=int, default=2048)
    parser.add_argument("--iters", type=int, default=50)
    args = parser.parse_args()

    if not torch.cuda.is_available():
        print("CUDA not available; skipping Triton benchmark.")
        return

    x = torch.randn(args.m, args.k, device="cuda", dtype=torch.float16)
    w = torch.randn(args.k, args.n, device="cuda", dtype=torch.float16)

    # Warmup
    _ = torch_reference(x, w)
    _ = triton_matmul(x, w)

    torch_time = benchmark(torch_reference, x, w, args.iters)
    triton_time = benchmark(triton_matmul, x, w, args.iters)

    torch_bw = bandwidth_gbps(args.m, args.n, args.k, torch_time)
    triton_bw = bandwidth_gbps(args.m, args.n, args.k, triton_time)

    print(
        "PyTorch: "
        f"{torch_time * 1e3:.3f} ms, "
        f"{tflops(args.m, args.n, args.k, torch_time):.2f} TFLOPS, "
        f"{torch_bw:.2f} GB/s"
    )
    print(
        "Triton : "
        f"{triton_time * 1e3:.3f} ms, "
        f"{tflops(args.m, args.n, args.k, triton_time):.2f} TFLOPS, "
        f"{triton_bw:.2f} GB/s"
    )


if __name__ == "__main__":
    main()
