#!/usr/bin/env python3
"""Benchmark model performance."""

import argparse
import time
import torch
from pathlib import Path
from inference_demo import Transformer

# Model Configuration (Must match training)
SRC_VOCAB = 100
TGT_VOCAB = 100
D_MODEL = 512
NUM_HEADS = 8
NUM_LAYERS = 2

def measure_latency(model, src, tgt, src_mask, tgt_mask, num_warmup=5, num_runs=20):
    """Measure inference latency."""
    print(f"   Warmup ({num_warmup} runs)...")
    with torch.no_grad():
        for _ in range(num_warmup):
            _ = model(src, tgt, src_mask, tgt_mask)

    print(f"   Measuring ({num_runs} runs)...")
    latencies = []
    with torch.no_grad():
        for _ in range(num_runs):
            start = time.perf_counter()
            _ = model(src, tgt, src_mask, tgt_mask)
            end = time.perf_counter()
            latencies.append((end - start) * 1000)  # ms

    return {
        "mean_ms": sum(latencies) / len(latencies),
        "min_ms": min(latencies),
        "max_ms": max(latencies),
        "p95_ms": sorted(latencies)[int(len(latencies) * 0.95)]
    }

def measure_memory():
    """Measure GPU memory usage."""
    if torch.cuda.is_available():
        return {
            "allocated_mb": torch.cuda.memory_allocated() / 1024 / 1024,
            "max_allocated_mb": torch.cuda.max_memory_allocated() / 1024 / 1024,
        }
    return {"allocated_mb": 0.0, "max_allocated_mb": 0.0}

def main():
    parser = argparse.ArgumentParser(description="Benchmark Transformer model")
    default_model_path = Path(__file__).parent / "model.pt"
    parser.add_argument("--model", "-m", type=Path, default=default_model_path,
                        help="Path to model weights")
    parser.add_argument("--batch-size", "-b", type=int, default=1, help="Batch size")
    parser.add_argument("--seq-len", "-s", type=int, default=10, help="Sequence length")
    parser.add_argument("--runs", "-r", type=int, default=100, help="Number of runs")
    parser.add_argument("--device", "-d", type=str, default="cpu", help="Device (cpu/cuda)")
    args = parser.parse_args()

    device = torch.device(args.device if torch.cuda.is_available() else "cpu")
    print(f"🚀 Benchmarking on {device}")
    print(f"   Config: Batch={args.batch_size}, Seq={args.seq_len}, Runs={args.runs}")

    # Initialize Model
    print(f"🔄 Initializing model...")
    model = Transformer(SRC_VOCAB, TGT_VOCAB, D_MODEL, NUM_HEADS, NUM_LAYERS)
    model.to(device)
    model.eval()

    if args.model.exists():
        print(f"   Loading weights from {args.model}")
        try:
            model.load_state_dict(torch.load(args.model, map_location=device))
        except Exception as e:
            print(f"⚠️  Could not load weights: {e}")
            print("   Continuing with random weights...")
    else:
        print("   Using random weights (file not found)")

    # Prepare Input
    src = torch.randint(1, SRC_VOCAB, (args.batch_size, args.seq_len)).to(device)
    tgt = torch.randint(1, TGT_VOCAB, (args.batch_size, args.seq_len)).to(device)
    src_mask = torch.ones(args.batch_size, 1, 1, args.seq_len).to(device)
    tgt_mask = torch.tril(torch.ones(args.seq_len, args.seq_len)).unsqueeze(0).unsqueeze(0).to(device)

    # Run Benchmark
    print("📊 Running latency benchmark...")
    latency = measure_latency(model, src, tgt, src_mask, tgt_mask, num_runs=args.runs)

    print("\n📈 Results:")
    print(f"   Mean Latency: {latency['mean_ms']:.4f} ms")
    print(f"   Min  Latency: {latency['min_ms']:.4f} ms")
    print(f"   Max  Latency: {latency['max_ms']:.4f} ms")
    print(f"   P95  Latency: {latency['p95_ms']:.4f} ms")
    print(f"   Throughput:   {1000 / latency['mean_ms'] * args.batch_size:.2f} samples/sec")

    if device.type == 'cuda':
        mem = measure_memory()
        print(f"\n💾 Memory:")
        print(f"   Allocated: {mem['allocated_mb']:.2f} MB")
        print(f"   Max Alloc: {mem['max_allocated_mb']:.2f} MB")

if __name__ == "__main__":
    main()
