# synth-opt
Bayesian optimization for sound design in Ableton Live. 

This package lets you run optimization on any number of device parameters, and updates the device with interesting parameters automatically based on a score you provide for each set of parameters. 

User preference is obviously a highly subjective scoring metric. This is a bit of an experiment to understand whether an approach like this even works, and if it could augment the sound design workflow.

**Current only validated with Serum/Serum 2!** 

Installation:
1. Follow the installation instructions for [AbletonOSC](https://github.com/ideoforms/AbletonOSC). This is required to allow synth-opt to talk to Ableton Live.
2. Clone the synth-opt repo: `git clone https://github.com/helloimfrei/synth-opt.git`
3. Enter the directory: `cd synth-opt`
4. Install package: `pip install .`

Usage:
1. Open an Ableton Live set, and make sure you configure the parameters you're interested in (in Serum: Click "Configure", then select each parameter you want to include in optimization).
2. Run `synth-opt --device <the device you want to optimize: e.g. serum>` in your terminal to launch the optimization session.
That's it! Provide a score from 0-100 for each suggested parameter set, and synth-opt will update the device automatically.

Some notes:
- Use --track to optionally specify a track name (exact match) containg your device if you have multiple device instances 
- Adding devices or effects *before* the device you're optimizing breaks things. synth-opt locates the device by name initially, but then pushes parameters to the device's **position** in track's chain. 
- For devices with a Configure button (stock plugins), you'll need to group the device into an Instrument Rack and assign macros for each parameter of interest. Otherwise, every parameter of the device will be included.
- Scoring is up to you. I specified 0-10 for simplicity, but if you hate or love a certain parameter set, you can go negative or way higher than 10 to tip the algorithm in the right direction.

This is a work in progress. If you have any feedback or suggestions, please let me know.

Happy sound designing!