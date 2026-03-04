# LogPlotter tool

Create a python tool that plots cfclient log files.

See examples of log data in ./example-logdata/

## Subframes

The tools should contain a number of subframes, all visible in the main window.

It should be possible to resize the frames.

Following subchapters describe the subframes.

### File picker

Choose file in a file picker. Multiple choice, across folders.
File types: .csv

When a file is chosen, it should be dynamically added to other frames.

There should be a button to clear all picked files.

When a file is chosen, it should be visible in the file picker.

### Signal picker

For each file, pick which signals should be plotted

### Plot configuration

Available configurations:
Start time from zero: Boolean. If true, start time at 0, where time 0 is the lowest time in any of the chosen log files. All plots should have the same time reference.
Link x axis: Boolean. If true, x axes should be linked (for example when zooming).

### Plots

Each signal should have its own subplot.

Every plot should contain:
X label
Y label
Title: filename:signal_name
