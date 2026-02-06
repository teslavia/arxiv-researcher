#!/usr/bin/env python3
"""
Export Transformer model to ONNX format.
Exports the 'forward' method (Teacher Forcing mode).
"""

import argparse
import torch
import torch.onnx
from pathlib import Path
from inference_demo import Transformer

# Model Configuration (Must match training)
SRC_VOCAB = 100
TGT_VOCAB = 100
D_MODEL = 512
NUM_HEADS = 8
NUM_LAYERS = 2

def export_to_onnx(model_path: Path, output_path: Path, opset_version: int = 14):
    print(f"🔄 Initializing model structure...")
    model = Transformer(SRC_VOCAB, TGT_VOCAB, D_MODEL, NUM_HEADS, NUM_LAYERS)

    if model_path.exists():
        print(f"💾 Loading weights from {model_path}")
        model.load_state_dict(torch.load(model_path, map_location="cpu"))
    else:
        print("⚠️  No weights found, using random initialization for demo export.")

    model.eval()

    # Create dummy inputs
    # Batch size 1, Sequence length 10
    batch_size = 1
    seq_len = 10

    src = torch.randint(1, SRC_VOCAB, (batch_size, seq_len))
    tgt = torch.randint(1, TGT_VOCAB, (batch_size, seq_len))

    # Create masks
    src_mask = torch.ones(batch_size, 1, 1, seq_len)
    tgt_mask = torch.tril(torch.ones(seq_len, seq_len)).unsqueeze(0).unsqueeze(0)

    print(f"📦 Exporting to {output_path}...")

    input_names = ["src", "tgt", "src_mask", "tgt_mask"]
    output_names = ["output_logits"]

    # Dynamic axes allow variable sequence lengths at runtime
    dynamic_axes = {
        "src": {0: "batch_size", 1: "seq_len"},
        "tgt": {0: "batch_size", 1: "seq_len"},
        "src_mask": {0: "batch_size", 3: "seq_len"},
        "tgt_mask": {0: "batch_size", 2: "seq_len", 3: "seq_len"},
        "output_logits": {0: "batch_size", 1: "seq_len"}
    }

    try:
        torch.onnx.export(
            model,
            (src, tgt, src_mask, tgt_mask),
            output_path,
            export_params=True,
            opset_version=opset_version,
            do_constant_folding=True,
            input_names=input_names,
            output_names=output_names,
            dynamic_axes=dynamic_axes
        )

        print(f"✅ ONNX model saved to {output_path}")
        print("\n💡 Usage with ONNX Runtime:")
        print("   import onnxruntime as ort")
        print(f"   session = ort.InferenceSession('{output_path}')")
        print("   outputs = session.run(None, {'src': ..., 'tgt': ..., ...})")
    except Exception as e:
        print(f"❌ Export failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="Export model to ONNX")
    # Default look for model.pt in the same directory
    default_model_path = Path(__file__).parent / "model.pt"
    default_output_path = Path(__file__).parent / "transformer.onnx"

    parser.add_argument("--model", "-m", type=Path, default=default_model_path,
                        help="Path to pytorch model checkpoint")
    parser.add_argument("--output", "-o", type=Path, default=default_output_path,
                        help="Output ONNX path")
    parser.add_argument("--opset", type=int, default=14, help="ONNX opset version")

    args = parser.parse_args()
    export_to_onnx(args.model, args.output, args.opset)

if __name__ == "__main__":
    main()
