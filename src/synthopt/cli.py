# src/synthopt/cli.py
import argparse
from .device import DeviceOptimizer  # your class

def main():
    ap = argparse.ArgumentParser(prog="synth-opt", description="Optimize Live device params")
    ap.add_argument("--device", required=True, help="Device name (substring match)")
    ap.add_argument("--track", help="Track name (exact match)")
    ap.add_argument("--apply", action="store_true", help="Apply proposed params to Live")
    ap.add_argument("--score", type=float, help="Score for the *previous* proposal")
    ap.add_argument("--state-file", help="Path to optimizer state file (pickle)")
    args = ap.parse_args()

    opt = DeviceOptimizer(
        device_name=args.device,
        track_name=args.track,
        state_file=args.state_file
    )

    # If user passed a score, record it for the *last* ask()
    if args.score is not None:
        opt.tell(args.score)
        print(f"Recorded score: {args.score}")

    # Always propose the next set
    proposal = opt.ask()
    print("Next proposal:", proposal)

    if args.apply:
        opt.set_params(proposal)
        opt.push_params()
        print("Applied proposal to Live.")
