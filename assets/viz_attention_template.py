#!/usr/bin/env python3
"""
Attention Visualization Script.
Features:
- Loads trained model from 'model.pt'
- Uses PyTorch Forward Hooks to capture attention weights
- Plots heatmaps using Seaborn/Matplotlib
"""

import torch
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from inference_demo import Transformer

# Global storage for attention weights
attention_weights = {}

def get_attention_hook(name):
    """Create a hook to capture attention weights."""
    def hook(module, input, output):
        # Assuming the module stores weights in 'attn_weights' attribute
        # (Standard in our inference_demo.py implementation)
        if hasattr(module, 'attn_weights'):
            attention_weights[name] = module.attn_weights.detach()
    return hook

def plot_attention(data, title="Attention Map"):
    """Plot heatmap of attention weights."""
    plt.figure(figsize=(10, 8))
    sns.heatmap(data, cmap='viridis', square=True, vmin=0.0, vmax=1.0)
    plt.title(title)
    plt.xlabel("Key Position")
    plt.ylabel("Query Position")

    # Save to file
    filename = f"attn_{title.lower().replace(' ', '_')}.png"
    output_path = Path(__file__).parent / filename
    plt.savefig(output_path)
    print(f"   Saved plot to {output_path}")
    plt.close()

def main():
    print("🎨 Transformer Attention Visualization")
    print("-" * 40)

    # 1. Initialize Model structure
    # Must match training config
    model = Transformer(src_vocab_size=100, tgt_vocab_size=100, num_layers=2)

    # 2. Load Weights
    model_path = Path(__file__).parent / "model.pt"
    try:
        model.load_state_dict(torch.load(model_path))
        print(f"💾 Loaded trained model from {model_path}")
    except FileNotFoundError:
        print("⚠️  No trained model found at {model_path}")
        print("   Using random initialization (Expect random patterns)")

    model.eval()

    # 3. Register Hooks
    # Target: First Encoder Layer's Self-Attention
    # Adjust path if your model structure differs
    try:
        layer = model.encoder.layers[0].self_attn
        layer.register_forward_hook(get_attention_hook("encoder_layer0_head0"))
        print("1️⃣ Hook registered on Encoder Layer 0")
    except AttributeError:
        print("❌ Could not find target layer to hook. Check model structure.")
        return

    # 4. Run Inference
    print("2️⃣ Running Inference...")
    batch_size = 1
    seq_len = 10
    src = torch.randint(1, 100, (batch_size, seq_len))
    tgt = torch.randint(1, 100, (batch_size, seq_len))

    # Masks
    src_mask = torch.ones(batch_size, 1, 1, seq_len)
    tgt_mask = torch.tril(torch.ones(seq_len, seq_len)).unsqueeze(0).unsqueeze(0)

    with torch.no_grad():
        _ = model(src, tgt, src_mask, tgt_mask)

    # 5. Plot
    print("3️⃣ Plotting Attention...")
    if "encoder_layer0_head0" in attention_weights:
        attn = attention_weights["encoder_layer0_head0"]
        # Shape: [Batch, Heads, Seq_Q, Seq_K]
        print(f"   Captured Attention Shape: {attn.shape}")

        # Plot Head 0 of Batch 0
        head0_attn = attn[0, 0, :, :].numpy()

        try:
            plot_attention(head0_attn, title="Encoder Layer 0 - Head 0")
            print("✅ Visualization complete.")
        except Exception as e:
            print(f"⚠️  Plotting failed: {e}")
            print("   (Ensure matplotlib and seaborn are installed)")
    else:
        print("❌ Failed to capture attention weights. Did the hook fire?")

if __name__ == "__main__":
    main()
