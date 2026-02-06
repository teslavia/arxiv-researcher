#!/usr/bin/env python3
"""FastAPI service wrapper for the Transformer model."""

import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
from typing import List
from inference_demo import Transformer

app = FastAPI(title="Transformer API", version="1.0.0")

# Model Configuration (Must match training in train_demo.py)
SRC_VOCAB = 100
TGT_VOCAB = 100
D_MODEL = 512
NUM_HEADS = 8
NUM_LAYERS = 2

# Load Model
model_path = Path(__file__).parent / "model.pt"
print(f"🔄 Initializing model...")
model = Transformer(SRC_VOCAB, TGT_VOCAB, D_MODEL, NUM_HEADS, NUM_LAYERS)

try:
    if model_path.exists():
        # Load to CPU for inference
        model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
        print(f"✅ Loaded weights from {model_path}")
    else:
        print(f"⚠️  Weights not found at {model_path}. Using random weights.")
except Exception as e:
    print(f"❌ Error loading weights: {e}")

model.eval()

class PredictRequest(BaseModel):
    """Request schema. Expects a list of token IDs."""
    input_ids: List[int]

class PredictResponse(BaseModel):
    """Response schema."""
    output_ids: List[int]

def greedy_decode(model, src, src_mask, max_len, start_symbol):
    """Simple greedy decoding for inference."""
    memory = model.encode(src, src_mask)
    # Initialize decoder input with start symbol
    ys = torch.ones(1, 1).fill_(start_symbol).type_as(src.data).long()

    for i in range(max_len-1):
        # Create target mask (triangular)
        sz = ys.size(1)
        tgt_mask = torch.tril(torch.ones(sz, sz)).type_as(src.data).unsqueeze(0).unsqueeze(0)

        out = model.decode(memory, src_mask, ys, tgt_mask)
        # Get last token output
        prob = model.generator(out[:, -1])
        _, next_word = torch.max(prob, dim=1)
        next_word = next_word.data[0]

        ys = torch.cat([ys, torch.ones(1, 1).type_as(src.data).long().fill_(next_word)], dim=1)

    return ys

@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    """Run inference using the Transformer."""
    try:
        # Prepare input
        src = torch.tensor([request.input_ids], dtype=torch.long)
        # Simple mask: all ones (allowing attention to all positions)
        src_mask = torch.ones(1, 1, 1, src.size(1))

        with torch.no_grad():
            # For this demo, we use the first token of input as the start symbol
            # In a real scenario, this would be a special <BOS> token
            start_symbol = request.input_ids[0] if request.input_ids else 1

            # Generate sequence
            output = greedy_decode(
                model,
                src,
                src_mask,
                max_len=len(request.input_ids),
                start_symbol=start_symbol
            )

        return PredictResponse(output_ids=output[0].tolist())

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    """Health check."""
    return {
        "status": "healthy",
        "model_path": str(model_path),
        "weights_loaded": model_path.exists()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
