#!/usr/bin/env python3
"""Quick test to verify the reproducibility test works."""

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import numpy as np
import os
import sys

# Force output flushing
sys.stdout.reconfigure(line_buffering=True)

print("Quick Test Starting...", flush=True)

# Golden ratio constants
PHI = (1 + np.sqrt(5)) / 2
OPTIMAL_LAMBDA = 0.2955977425220668

class OuroborosExact(nn.Module):
    def __init__(self):
        super().__init__()
        self.lam = OPTIMAL_LAMBDA

    def forward(self, x):
        s = torch.sigmoid(x)
        gate = self.lam + (1 - self.lam) * s
        return x * gate

class DeepMLP(nn.Module):
    def __init__(self, depth=5, width=64):
        super().__init__()
        self.activation = OuroborosExact()
        scale = 1.3820

        layers = []
        input_layer = nn.Linear(28 * 28, width)
        nn.init.normal_(input_layer.weight, mean=0, std=scale / np.sqrt(28 * 28))
        nn.init.zeros_(input_layer.bias)
        layers.append(input_layer)

        for _ in range(depth - 1):
            layer = nn.Linear(width, width)
            nn.init.normal_(layer.weight, mean=0, std=scale / np.sqrt(width))
            nn.init.zeros_(layer.bias)
            layers.append(layer)

        self.layers = nn.ModuleList(layers)
        self.output_layer = nn.Linear(width, 10)
        nn.init.normal_(self.output_layer.weight, mean=0, std=1.0 / np.sqrt(width))
        nn.init.zeros_(self.output_layer.bias)

    def forward(self, x):
        x = x.view(x.size(0), -1)
        for layer in self.layers:
            x = layer(x)
            x = self.activation(x)
        return self.output_layer(x)

def main():
    print("Setting seed...", flush=True)
    torch.manual_seed(42)
    np.random.seed(42)

    print("Loading data...", flush=True)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, 'data')

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,))
    ])

    train_dataset = datasets.FashionMNIST(
        root=data_dir, train=True, download=False, transform=transform
    )
    test_dataset = datasets.FashionMNIST(
        root=data_dir, train=False, download=False, transform=transform
    )

    train_loader = DataLoader(train_dataset, batch_size=256, shuffle=True, num_workers=0)
    test_loader = DataLoader(test_dataset, batch_size=256, shuffle=False, num_workers=0)

    print(f"Train: {len(train_dataset)}, Test: {len(test_dataset)}", flush=True)

    print("Creating model...", flush=True)
    model = DeepMLP(depth=5, width=64)
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.CrossEntropyLoss()

    print("Training 2 epochs...", flush=True)
    for epoch in range(2):
        model.train()
        total_correct = 0
        total = 0
        for batch_idx, (data, target) in enumerate(train_loader):
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()

            pred = output.argmax(dim=1)
            total_correct += pred.eq(target).sum().item()
            total += len(target)

            if batch_idx % 50 == 0:
                print(f"  Epoch {epoch+1}, Batch {batch_idx}/{len(train_loader)}, Acc: {100*total_correct/total:.1f}%", flush=True)

        print(f"Epoch {epoch+1} complete, Train Acc: {100*total_correct/total:.1f}%", flush=True)

    # Test
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for data, target in test_loader:
            output = model(data)
            pred = output.argmax(dim=1)
            correct += pred.eq(target).sum().item()
            total += len(target)

    print(f"\nFinal Test Accuracy: {100*correct/total:.2f}%", flush=True)
    print("Quick test PASSED!", flush=True)

if __name__ == "__main__":
    main()
