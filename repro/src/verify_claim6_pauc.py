#!/usr/bin/env python3
"""Claim 6: paper-faithful CPU reproduction of CIFAR partial-AUC training.

The profile configuration executes one epoch to measure the exact pipeline.
The full configuration executes both datasets, both temperatures, and three
paired seeds.  SCENT and SOX consume identical batches and frozen features.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import platform
import random
import subprocess
import sys
import time
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as functional
from PIL import Image
from sklearn.metrics import roc_auc_score
from torch.utils.data import DataLoader, Dataset, Sampler
from torchvision import datasets, models, transforms


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "repro" / "config" / "claim6_pauc.json"
CHECKER_PATH = ROOT / "repro" / "src" / "check_claim6_pauc.py"
ARTIFACT_DIR = ROOT / ".openresearch" / "artifacts" / "claim_6"
CACHE_DIR = Path.home() / ".cache" / "openresearch-scent-cifar"
METRICS_PATH = ARTIFACT_DIR / "raw_metrics.csv"

HYPERPARAMETERS = {
    ("cifar100", 0.1, "SCENT"): {"lr": 5e-3, "alpha_log": -6.0},
    ("cifar100", 0.1, "SOX"): {"lr": 5e-3, "gamma": 0.9},
    ("cifar100", 0.05, "SCENT"): {"lr": 5e-3, "alpha_log": -15.0},
    ("cifar100", 0.05, "SOX"): {"lr": 5e-3, "gamma": 0.7},
    ("cifar10", 0.1, "SCENT"): {"lr": 5e-3, "alpha_log": -7.0},
    ("cifar10", 0.1, "SOX"): {"lr": 5e-3, "gamma": 0.7},
    ("cifar10", 0.05, "SCENT"): {"lr": 1e-2, "alpha_log": -16.0},
    ("cifar10", 0.05, "SOX"): {"lr": 1e-2, "gamma": 0.9},
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)


class ImageArrayDataset(Dataset):
    """Released ImageDataset semantics, including crop-before-resize."""

    def __init__(
        self,
        images: np.ndarray,
        targets: np.ndarray,
        *,
        train: bool,
        return_position: bool = False,
    ) -> None:
        self.images = images.astype(np.uint8, copy=False)
        self.targets = targets.astype(np.int64, copy=False)
        self.return_position = return_position
        self.transform = (
            transforms.Compose(
                [
                    transforms.ToTensor(),
                    transforms.RandomCrop((30, 30), padding=None),
                    transforms.RandomHorizontalFlip(),
                    transforms.Resize((32, 32)),
                ]
            )
            if train
            else transforms.Compose(
                [transforms.ToTensor(), transforms.Resize((32, 32))]
            )
        )
        positive = np.flatnonzero(self.targets == 1)
        self.positive_position = np.full(len(self.targets), -1, dtype=np.int64)
        self.positive_position[positive] = np.arange(len(positive))

    def __len__(self) -> int:
        return len(self.targets)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, int, int]:
        image = self.transform(Image.fromarray(self.images[index]))
        position = int(self.positive_position[index]) if self.return_position else index
        return image, int(self.targets[index]), position


class BalancedBatchSampler(Sampler[int]):
    """Deterministic equivalent of the released LibAUC DualSampler."""

    def __init__(self, targets: np.ndarray, batch_size: int, *, seed: int) -> None:
        if batch_size % 2:
            raise ValueError("balanced batch size must be even")
        self.positive = np.flatnonzero(targets == 1)
        self.negative = np.flatnonzero(targets == 0)
        self.half = batch_size // 2
        self.num_batches = max(
            len(self.positive) // self.half, len(self.negative) // self.half
        )
        self.rng = np.random.default_rng(seed)
        self.positive = self.rng.permutation(self.positive)
        self.negative = self.rng.permutation(self.negative)
        self.positive_pointer = 0
        self.negative_pointer = 0

    def _next_chunk(self, which: str) -> np.ndarray:
        pool = getattr(self, which)
        pointer_name = f"{which}_pointer"
        pointer = getattr(self, pointer_name)
        if pointer + self.half > len(pool):
            tail = pool[pointer:]
            pool = self.rng.permutation(pool)
            pointer = (pointer + self.half) % len(pool)
            chunk = np.concatenate([tail, pool[:pointer]])
            setattr(self, which, pool)
        else:
            chunk = pool[pointer : pointer + self.half]
            pointer += self.half
        setattr(self, pointer_name, pointer)
        return chunk

    def __iter__(self):
        for _ in range(self.num_batches):
            for index in self._next_chunk("positive"):
                yield int(index)
            for index in self._next_chunk("negative"):
                yield int(index)

    def __len__(self) -> int:
        return self.num_batches * self.half * 2


def load_binary_dataset(name: str) -> tuple[np.ndarray, ...]:
    dataset_class = datasets.CIFAR10 if name == "cifar10" else datasets.CIFAR100
    train = dataset_class(root=CACHE_DIR, train=True, download=True)
    test = dataset_class(root=CACHE_DIR, train=False, download=True)
    train_images = np.asarray(train.data)
    train_classes = np.asarray(train.targets)
    test_images = np.asarray(test.data)
    test_classes = np.asarray(test.targets)
    split = 5 if name == "cifar10" else 50
    train_targets = (train_classes >= split).astype(np.int64)
    test_targets = (test_classes >= split).astype(np.int64)

    # The paper says to randomly remove 80% of positives.  This deliberately
    # differs from the released ImbalancedDataGenerator(imratio=.2), which
    # retains 6,250 positives and therefore removes only 75%.
    rng = np.random.default_rng(0)
    positive = rng.permutation(np.flatnonzero(train_targets == 1))
    negative = np.flatnonzero(train_targets == 0)
    retained = np.concatenate([negative, positive[: len(positive) // 5]])
    retained = rng.permutation(retained)
    return (
        train_images[retained],
        train_targets[retained],
        test_images,
        test_targets,
    )


def make_resnet18(seed: int) -> nn.Module:
    seed_everything(seed)
    model = models.resnet18(weights=None, num_classes=1)
    # Match the vendored LibAUC model used by the released pAUC entrypoint.
    for module in model.modules():
        if isinstance(module, nn.Conv2d):
            nn.init.xavier_normal_(module.weight)
        elif isinstance(module, (nn.BatchNorm2d, nn.GroupNorm)):
            nn.init.constant_(module.weight, 1)
            nn.init.constant_(module.bias, 0)
    return model


def pretrain_backbone(
    dataset_name: str,
    train_images: np.ndarray,
    train_targets: np.ndarray,
    config: dict,
) -> tuple[nn.Module, float, bool]:
    epochs = int(config["pretrain_epochs"])
    seed = int(config["pretrain_seed"])
    checkpoint = CACHE_DIR / f"{dataset_name}_paper_resnet18_seed{seed}_e{epochs}.pt"
    model = make_resnet18(seed)
    reused = checkpoint.exists()
    started = time.perf_counter()
    if reused:
        model.load_state_dict(torch.load(checkpoint, map_location="cpu", weights_only=True))
    else:
        dataset = ImageArrayDataset(train_images, train_targets, train=True)
        generator = torch.Generator().manual_seed(seed)
        loader = DataLoader(
            dataset,
            batch_size=int(config["batch_size"]),
            shuffle=True,
            generator=generator,
            num_workers=0,
        )
        optimizer = torch.optim.SGD(model.parameters(), lr=1e-3)
        criterion = nn.BCEWithLogitsLoss()
        model.train()
        for epoch in range(epochs):
            if epoch in (20, 40):
                for group in optimizer.param_groups:
                    group["lr"] /= 10
            for images, targets, _ in loader:
                optimizer.zero_grad(set_to_none=True)
                logits = model(images).squeeze(1)
                loss = criterion(logits, targets.float())
                loss.backward()
                optimizer.step()
            print(
                f"CLAIM6_PRETRAIN dataset={dataset_name} epoch={epoch + 1}/{epochs} "
                f"loss={float(loss):.8f}",
                flush=True,
            )
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        torch.save(model.state_dict(), checkpoint)

    model.fc = nn.Identity()
    model.eval()
    for parameter in model.parameters():
        parameter.requires_grad = False
    return model, time.perf_counter() - started, reused


def extract_features(
    backbone: nn.Module, images: np.ndarray, targets: np.ndarray
) -> torch.Tensor:
    dataset = ImageArrayDataset(images, targets, train=False)
    loader = DataLoader(dataset, batch_size=256, shuffle=False, num_workers=0)
    parts = []
    with torch.no_grad():
        for batch, _, _ in loader:
            parts.append(backbone(batch))
    return torch.cat(parts)


@dataclass
class MethodState:
    method: str
    head: nn.Linear
    optimizer: torch.optim.Optimizer
    scheduler: torch.optim.lr_scheduler.CosineAnnealingLR
    u: torch.Tensor
    alpha_log: float | None
    gamma: float | None


def make_method_state(
    dataset: str,
    tau: float,
    method: str,
    seed: int,
    positive_count: int,
    epochs: int,
    initial: dict[str, torch.Tensor],
) -> MethodState:
    head = nn.Linear(512, 1)
    head.load_state_dict(deepcopy(initial))
    params = HYPERPARAMETERS[(dataset, tau, method)]
    optimizer = torch.optim.SGD(head.parameters(), lr=float(params["lr"]), momentum=0)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=epochs, eta_min=0
    )
    return MethodState(
        method=method,
        head=head,
        optimizer=optimizer,
        scheduler=scheduler,
        u=torch.zeros(positive_count),
        alpha_log=params.get("alpha_log"),
        gamma=params.get("gamma"),
    )


def released_loss(
    state: MethodState,
    positive_features: torch.Tensor,
    negative_features: torch.Tensor,
    positive_positions: torch.Tensor,
    *,
    tau: float,
    margin: float,
) -> torch.Tensor:
    positive_scores = torch.sigmoid(state.head(positive_features)).view(-1, 1)
    negative_scores = torch.sigmoid(state.head(negative_features)).view(1, -1)
    surrogate = functional.relu(margin - (positive_scores - negative_scores)).square()
    exp_mean = torch.exp(surrogate / tau).mean(dim=1).detach()

    positions = positive_positions.long()
    uninitialized = state.u[positions] == 0
    state.u[positions[uninitialized]] = exp_mean[uninitialized]
    if state.method == "SCENT":
        gamma = torch.sigmoid(
            torch.tensor(float(state.alpha_log)) + torch.log(state.u[positions])
        )
    else:
        gamma = torch.full_like(exp_mean, float(state.gamma))
    state.u[positions] = (
        (1 - gamma) * state.u[positions] + gamma * exp_mean
    ).detach()

    weights = torch.exp(surrogate / tau - torch.log(state.u[positions])[:, None])
    return torch.mean(weights.detach() * surrogate)


def objective(
    head: nn.Linear,
    positive_features: torch.Tensor,
    negative_features: torch.Tensor,
    tau: float,
    margin: float,
) -> float:
    with torch.no_grad():
        positive = torch.sigmoid(head(positive_features)).view(-1)
        negative = torch.sigmoid(head(negative_features)).view(-1)
        parts = []
        log_count = math.log(len(negative))
        for start in range(0, len(positive), 256):
            difference = positive[start : start + 256, None] - negative[None, :]
            surrogate = functional.relu(margin - difference).square()
            parts.append(tau * (torch.logsumexp(surrogate / tau, dim=1) - log_count))
        return float(torch.cat(parts).mean())


def evaluate(
    state: MethodState,
    train_features: torch.Tensor,
    train_targets: np.ndarray,
    test_features: torch.Tensor,
    test_targets: np.ndarray,
    tau: float,
    margin: float,
) -> tuple[float, float]:
    train_positive = train_features[torch.from_numpy(train_targets == 1)]
    train_negative = train_features[torch.from_numpy(train_targets == 0)]
    train_objective = objective(
        state.head, train_positive, train_negative, tau, margin
    )
    with torch.no_grad():
        test_scores = torch.sigmoid(state.head(test_features)).view(-1).numpy()
    test_pauc = float(roc_auc_score(test_targets, test_scores, max_fpr=0.3))
    return train_objective, test_pauc


def run_dataset(
    dataset_name: str, config: dict
) -> tuple[list[dict[str, object]], dict[str, object]]:
    train_images, train_targets, test_images, test_targets = load_binary_dataset(
        dataset_name
    )
    counts = {
        "train_negative": int(np.sum(train_targets == 0)),
        "train_positive": int(np.sum(train_targets == 1)),
        "test_negative": int(np.sum(test_targets == 0)),
        "test_positive": int(np.sum(test_targets == 1)),
    }
    if counts != {
        "train_negative": 25_000,
        "train_positive": 5_000,
        "test_negative": 5_000,
        "test_positive": 5_000,
    }:
        raise RuntimeError(f"paper data contract violated: {counts}")

    backbone, pretrain_seconds, reused = pretrain_backbone(
        dataset_name, train_images, train_targets, config
    )
    feature_started = time.perf_counter()
    train_features = extract_features(backbone, train_images, train_targets)
    test_features = extract_features(backbone, test_images, test_targets)
    feature_seconds = time.perf_counter() - feature_started
    positive_count = counts["train_positive"]
    epochs = int(config["finetune_epochs"])
    rows: list[dict[str, object]] = []
    finetune_started = time.perf_counter()

    for seed in config["seeds"]:
        seed_everything(int(seed))
        initial_head = nn.Linear(512, 1).state_dict()
        states = {
            (float(tau), method): make_method_state(
                dataset_name,
                float(tau),
                method,
                int(seed),
                positive_count,
                epochs,
                initial_head,
            )
            for tau in config["taus"]
            for method in config["methods"]
        }
        for (tau, method), state in states.items():
            train_objective, test_pauc = evaluate(
                state,
                train_features,
                train_targets,
                test_features,
                test_targets,
                tau,
                float(config["margin"]),
            )
            rows.append(
                {
                    "dataset": dataset_name,
                    "tau": tau,
                    "method": method,
                    "seed": int(seed),
                    "epoch": 0,
                    "train_objective": train_objective,
                    "test_pauc": test_pauc,
                }
            )

        train_dataset = ImageArrayDataset(
            train_images, train_targets, train=True, return_position=True
        )
        sampler = BalancedBatchSampler(
            train_targets, int(config["batch_size"]), seed=int(seed)
        )
        for epoch in range(1, epochs + 1):
            loader = DataLoader(
                train_dataset,
                batch_size=int(config["batch_size"]),
                sampler=sampler,
                num_workers=0,
            )
            backbone.eval()
            for images, targets, positions in loader:
                # All methods and temperatures receive the exact same augmented
                # examples and frozen features.
                with torch.no_grad():
                    features = backbone(images)
                positive_mask = targets == 1
                positive_features = features[positive_mask]
                negative_features = features[~positive_mask]
                positive_positions = positions[positive_mask]
                for (tau, _), state in states.items():
                    state.optimizer.zero_grad(set_to_none=True)
                    loss = released_loss(
                        state,
                        positive_features,
                        negative_features,
                        positive_positions,
                        tau=tau,
                        margin=float(config["margin"]),
                    )
                    loss.backward()
                    for parameter in state.head.parameters():
                        parameter.grad.clamp_(-1, 1)
                    state.optimizer.step()
            for state in states.values():
                state.scheduler.step()

            if epoch % int(config["evaluation_every"]) == 0:
                for (tau, method), state in states.items():
                    train_objective, test_pauc = evaluate(
                        state,
                        train_features,
                        train_targets,
                        test_features,
                        test_targets,
                        tau,
                        float(config["margin"]),
                    )
                    rows.append(
                        {
                            "dataset": dataset_name,
                            "tau": tau,
                            "method": method,
                            "seed": int(seed),
                            "epoch": epoch,
                            "train_objective": train_objective,
                            "test_pauc": test_pauc,
                        }
                    )
                    print(
                        f"CLAIM6_EPOCH dataset={dataset_name} tau={tau} "
                        f"method={method} seed={seed} epoch={epoch}/{epochs} "
                        f"objective={train_objective:.8f} test_pauc={test_pauc:.8f}",
                        flush=True,
                    )

    timing = {
        "counts": counts,
        "pretrain_seconds": pretrain_seconds,
        "pretrain_checkpoint_reused": reused,
        "feature_extraction_seconds": feature_seconds,
        "finetune_seconds": time.perf_counter() - finetune_started,
        "balanced_batches_per_epoch": max(5_000 // 32, 25_000 // 32),
    }
    return rows, timing


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fields = [
        "dataset",
        "tau",
        "method",
        "seed",
        "epoch",
        "train_objective",
        "test_pauc",
    ]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def invoke_checker(metrics: Path, output_path: Path) -> tuple[int, dict]:
    process = subprocess.run(
        [sys.executable, str(CHECKER_PATH), str(CONFIG_PATH), str(metrics)],
        text=True,
        capture_output=True,
    )
    output_path.write_text(process.stdout + process.stderr)
    payload = json.loads(process.stdout.strip().splitlines()[-1]) if process.stdout else {}
    return process.returncode, payload


def main() -> int:
    started = time.perf_counter()
    config = json.loads(CONFIG_PATH.read_text())
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    threads = min(os.cpu_count() or 1, 8)
    torch.set_num_threads(threads)
    torch.set_num_interop_threads(1)
    seed_everything(0)

    all_rows: list[dict[str, object]] = []
    timings: dict[str, object] = {}
    for dataset_name in config["datasets"]:
        dataset_rows, timing = run_dataset(dataset_name, config)
        all_rows.extend(dataset_rows)
        timings[dataset_name] = timing
    write_csv(METRICS_PATH, all_rows)

    checker_code, checker = invoke_checker(
        METRICS_PATH, ARTIFACT_DIR / "independent_checker_output.json"
    )
    negative_path = ARTIFACT_DIR / "negative_control_metrics.csv"
    if config["mode"] == "profile":
        write_csv(negative_path, all_rows[:-1])
        negative_code, negative = invoke_checker(
            negative_path, ARTIFACT_DIR / "negative_control_output.json"
        )
        negative_rejected = negative_code != 0
    else:
        negative_rows = deepcopy(all_rows)
        final_epoch = int(config["finetune_epochs"])
        final_sox = {
            (row["dataset"], float(row["tau"]), int(row["seed"])): float(
                row["train_objective"]
            )
            for row in negative_rows
            if row["method"] == "SOX" and int(row["epoch"]) == final_epoch
        }
        for row in negative_rows:
            if row["method"] == "SCENT" and int(row["epoch"]) == final_epoch:
                key = (row["dataset"], float(row["tau"]), int(row["seed"]))
                row["train_objective"] = (
                    final_sox[key] + 5 * float(config["equivalence_margin"])
                )
        write_csv(negative_path, negative_rows)
        negative_code, negative = invoke_checker(
            negative_path, ARTIFACT_DIR / "negative_control_output.json"
        )
        negative_rejected = (
            negative_code == 0 and negative.get("verdict") != "VERIFIED"
        )

    runtime = time.perf_counter() - started
    git_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], text=True, capture_output=True, check=True
    ).stdout.strip()
    metadata = {
        "config": config,
        "config_sha256": sha256(CONFIG_PATH),
        "git_sha": git_sha,
        "fixed_command": "uv run --frozen python repro/src/verify_scent.py",
        "python": sys.version,
        "torch": torch.__version__,
        "torchvision": __import__("torchvision").__version__,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "logical_cpu_count": os.cpu_count(),
        "torch_threads": threads,
        "runtime_seconds": runtime,
        "timings": timings,
        "raw_metrics_sha256": sha256(METRICS_PATH),
        "checker": checker,
        "negative_control_rejected": negative_rejected,
    }
    (ARTIFACT_DIR / "metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True)
    )
    (ARTIFACT_DIR / "exact_command.txt").write_text(
        "uv run --frozen python repro/src/verify_scent.py\n"
    )
    (ARTIFACT_DIR / "environment.txt").write_text(
        f"python={platform.python_version()}\n"
        f"torch={torch.__version__}\n"
        f"torchvision={__import__('torchvision').__version__}\n"
        f"platform={platform.platform()}\n"
        f"logical_cpus={os.cpu_count()}\n"
        f"torch_threads={threads}\n"
    )
    verdict = checker.get("verdict", "BLOCKED")
    (ARTIFACT_DIR / "verdict.json").write_text(
        json.dumps(
            {
                "claim": 6,
                "mode": config["mode"],
                "verdict": verdict,
                "checker_passed": checker_code == 0,
                "negative_control_rejected": negative_rejected,
            },
            indent=2,
            sort_keys=True,
        )
    )
    (ARTIFACT_DIR / "EVAL.md").write_text(
        "# Claim 6 evaluation\n\n"
        f"- Mode: `{config['mode']}`\n"
        f"- Verdict: **{verdict}**\n"
        f"- Raw rows: {len(all_rows)}\n"
        f"- Runtime: {runtime:.3f} seconds of CPU-only wall clock\n"
        f"- Independent checker: {'PASS' if checker_code == 0 else 'FAIL'}\n"
        f"- Negative control rejected: {negative_rejected}\n"
        "- The profile mode is timing evidence only and cannot establish a claim verdict.\n"
    )

    print("\n" + "=" * 78)
    print("CLAIM 6 CIFAR PARTIAL-AUC CONTRACT")
    print("=" * 78)
    print(json.dumps(checker, sort_keys=True))
    print(f"NEGATIVE_CONTROL_REJECTED={negative_rejected}")
    print(f"RUNTIME_SECONDS={runtime:.3f}")
    print(f"CLAIM6_VERDICT={verdict}")
    if config["mode"] == "profile":
        print(
            f"CLAIM6_PROFILE_FULL_SCALE_FACTOR="
            f"{(2 * 2 * 3 * 60) / max(1, len(config['datasets']) * len(config['taus']) * len(config['seeds']) * config['finetune_epochs']):.1f}"
        )
        print("CLAIM6_PROFILE_SUITE=PASS" if checker_code == 0 and negative_rejected else "CLAIM6_PROFILE_SUITE=FAIL")
    else:
        print("CLAIM6_FULL_SUITE=PASS" if checker_code == 0 and negative_rejected else "CLAIM6_FULL_SUITE=FAIL")
    return 0 if checker_code == 0 and negative_rejected else 1


if __name__ == "__main__":
    raise SystemExit(main())
