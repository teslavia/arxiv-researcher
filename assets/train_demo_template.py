#!/usr/bin/env python3
"""
Training Demo Template.
Features:
- Teacher Forcing training loop
- LR Scheduler (ReduceLROnPlateau)
- CrossEntropyLoss with masking
- Automatic model saving (relative path)
"""

import torch
import torch.nn as nn
import torch.optim as optim
from pathlib import Path
from inference_demo import Transformer

def train_step(model, src, tgt, src_mask, tgt_mask, criterion, optimizer):
    model.train()

    # Forward
    # tgt_input: input to decoder (shifted right)
    tgt_input = tgt[:, :-1]
    # tgt_y: target output (next token)
    tgt_y = tgt[:, 1:]

    # Adjust masks for shifted input
    tgt_mask = tgt_mask[:, :, :-1, :-1]

    output = model(src, tgt_input, src_mask, tgt_mask)

    # Reshape for loss: (Batch * Seq, Vocab)
    output_flat = output.contiguous().view(-1, output.size(-1))
    tgt_y_flat = tgt_y.contiguous().view(-1)

    loss = criterion(output_flat, tgt_y_flat)

    # Backward
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    return loss.item()

def main():
    print("🚂 Transformer Training Demo")
    print("-" * 40)

    # Settings (Robust defaults)
    d_model = 512
    num_layers = 2
    num_heads = 8
    src_vocab = 100
    tgt_vocab = 100
    batch_size = 64        # Larger batch size for stability
    seq_len = 10
    num_epochs = 1000      # Sufficient for convergence on toy tasks

    # 1. Initialize Model
    print("1️⃣ Initializing Model...")
    model = Transformer(src_vocab, tgt_vocab, d_model, num_heads, num_layers)

    # 2. Setup Optimizer & Loss
    print("2️⃣ Setup Optimizer & Loss...")
    # LR=0.0001 is stable for Transformers
    optimizer = optim.Adam(model.parameters(), lr=0.0001, betas=(0.9, 0.98), eps=1e-9)
    criterion = nn.CrossEntropyLoss(ignore_index=0) # Assume 0 is padding

    # Scheduler: Reduce LR if loss stagnates
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=100
    )

    # 3. Training Loop
    print(f"3️⃣ Starting Training ({num_epochs} epochs)...")

    # Pre-compute masks (if batch/seq_len are constant)
    src_mask = torch.ones(batch_size, 1, 1, seq_len)
    tgt_mask = torch.tril(torch.ones(seq_len, seq_len)).unsqueeze(0).unsqueeze(0)

    for epoch in range(num_epochs):
        # Generate NEW random data every epoch to force learning the RULE
        src = torch.randint(1, src_vocab, (batch_size, seq_len))
        tgt = src.clone() # Copy task

        loss = train_step(model, src, tgt, src_mask, tgt_mask, criterion, optimizer)

        # Step scheduler
        scheduler.step(loss)

        if (epoch + 1) % 50 == 0:
            print(f"   Epoch {epoch+1}/{num_epochs} | Loss: {loss:.4f}")

    print("-" * 40)
    print("✅ Training loop finished.")

    # 4. Save Model
    # Use absolute path relative to this script
    save_path = Path(__file__).parent / "model.pt"
    torch.save(model.state_dict(), save_path)
    print(f"💾 Model saved to {save_path}")

if __name__ == "__main__":
    main()
