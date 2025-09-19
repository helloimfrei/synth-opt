import argparse
from .device import DeviceOptimizer
import os
import pyfiglet

def main():
    ap = argparse.ArgumentParser(
        prog="synth-opt",
        description="Interactive Bayesian optimization session for Live device params",
    )
    ap.add_argument("--device", required=True, help="Device name (substring match)")
    ap.add_argument("--track", help="Track name (exact match)")
    ap.add_argument(
        "--state-file",
        help="Path to optimizer state file (pickle)",
        default="saved_state/optimizer_state.pkl",
    )
    args = ap.parse_args()

    opt = DeviceOptimizer(
        device_name=args.device,
        track_name=args.track,
        state_file=args.state_file,
    )

    print(f"Starting optimization session for device: {args.device}")
    print("Press Ctrl+C to quit.\n")

    try:
        while True:
            os.system('clear')
            print(pyfiglet.figlet_format("SYNTH OPT"))
            # Ask the optimizer for the next parameters
            proposal = opt.ask()
            print("Proposed parameters:")
            for k, v in proposal.items():
                print(f"{k}: {v}")

            # Apply them to Live
            opt.set_params(proposal)
            opt.push_params()
            print("Parameters pushed to Live.\n")

            # Ask the user for feedback
            score = input("How do you like the sound? (0-10, or 'q' to quit): ")
            if score.lower().startswith("q"):
                print("Exiting session.")
                break
            if score == "":
                score = 0

            try:
                score_val = float(score)
            except ValueError:
                print("Invalid score. Please enter a number or 'q' to quit.")
                continue

            # Tell optimizer the result
            opt.tell(score_val)
            print(f"Recorded score: {score_val}\n")

    except KeyboardInterrupt:
        print("\nSession interrupted. Goodbye!")
