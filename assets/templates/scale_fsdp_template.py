#!/usr/bin/env python3
"""PyTorch FSDP training scaffold with AMP and checkpointing."""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from typing import Any, cast

import torch
import torch.distributed as dist
from torch.distributed.fsdp import FullyShardedDataParallel as FSDP
from torch.distributed.fsdp.wrap import size_based_auto_wrap_policy
from torch.utils.checkpoint import checkpoint
from torch.utils.data.distributed import DistributedSampler


@dataclass
class TrainConfig:
    epochs: int = 1
    lr: float = 1e-4
    batch_size: int = 4
    use_amp: bool = True
    use_checkpoint: bool = True


def build_model() -> torch.nn.Module:
    """Build and load your model here."""
    # TODO: construct model and load weights
    raise NotImplementedError


def build_dataloader(batch_size: int) -> torch.utils.data.DataLoader:
    """Return a distributed dataloader."""
    # TODO: implement dataset and sampler
    dataset = torch.utils.data.TensorDataset(torch.randn(8, 3, 224, 224))
    sampler = DistributedSampler(dataset)
    return torch.utils.data.DataLoader(dataset, batch_size=batch_size, sampler=sampler)


def forward_step(
    model: torch.nn.Module, batch: torch.Tensor, use_checkpointing: bool
) -> torch.Tensor:
    def run(inputs: torch.Tensor) -> torch.Tensor:
        return model(inputs)

    if use_checkpointing:
        output = checkpoint(run, batch)
        if not isinstance(output, torch.Tensor):
            raise RuntimeError("Checkpoint returned non-tensor output")
        return output
    return model(batch)


def train(rank: int, world_size: int, config: TrainConfig) -> None:
    if not torch.cuda.is_available():
        print("CUDA not available; FSDP requires GPUs.")
        return
    dist.init_process_group(backend="nccl", rank=rank, world_size=world_size)
    torch.cuda.set_device(rank)

    model = build_model().cuda()

    def auto_wrap_policy(
        module: torch.nn.Module, recurse: bool, nonwrapped_numel: int
    ) -> bool:
        return size_based_auto_wrap_policy(
            module=module,
            recurse=recurse,
            nonwrapped_numel=nonwrapped_numel,
            min_num_params=100_000_000,
        )

    model = FSDP(model, auto_wrap_policy=auto_wrap_policy)

    optimizer = torch.optim.AdamW(model.parameters(), lr=config.lr)
    scaler = torch.cuda.amp.GradScaler(enabled=config.use_amp)

    dataloader = build_dataloader(config.batch_size)

    model.train()
    for _ in range(config.epochs):
        sampler = dataloader.sampler
        if isinstance(sampler, DistributedSampler):
            cast(DistributedSampler[Any], sampler).set_epoch(0)
        for batch in dataloader:
            if isinstance(batch, (list, tuple)):
                batch = batch[0]
            batch = batch.cuda(non_blocking=True)

            optimizer.zero_grad(set_to_none=True)
            with torch.cuda.amp.autocast(enabled=config.use_amp):
                outputs = forward_step(model, batch, config.use_checkpoint)
                loss = outputs.mean()

            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()

    dist.destroy_process_group()


def main() -> None:
    parser = argparse.ArgumentParser(description="FSDP training scaffold")
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--batch", type=int, default=4)
    parser.add_argument("--no-amp", action="store_true")
    parser.add_argument("--no-checkpoint", action="store_true")
    args = parser.parse_args()

    config = TrainConfig(
        epochs=args.epochs,
        lr=args.lr,
        batch_size=args.batch,
        use_amp=not args.no_amp,
        use_checkpoint=not args.no_checkpoint,
    )

    # TODO: use torchrun to launch distributed training
    # torchrun --nproc_per_node=NUM_GPUS scale_fsdp.py
    rank = int(os.environ.get("LOCAL_RANK", "0"))
    world_size = int(os.environ.get("WORLD_SIZE", "1"))
    train(rank, world_size, config)


if __name__ == "__main__":
    main()
