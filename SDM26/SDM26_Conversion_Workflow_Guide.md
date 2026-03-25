# SDM26 Conversion Workflow Guide

This guide explains how to convert raw `.benji2` logger files into both:

- `.csv` files
- MoTeC `.ld` files

You now only need to run one GUI. The GUI does both conversions for you.

## What You Will Do

1. Put your `.benji2` file or files in one place.
2. Open PowerShell in the project folder.
3. Launch the SDM26 conversion GUI.
4. Select one `.benji2` file or one folder that contains `.benji2` files.
5. Select an output folder.
6. Click `Start Conversion`.
7. Open the finished `.ld` files in MoTeC i2.

## One-Time Setup

If Python is not installed yet:

1. Install Python from `python.org`.
2. During installation, make sure `Add Python to PATH` is enabled.

Install the required packages one time:

```powershell
py -m pip install numpy pandas
```

## Before You Start

Put your logger files in a clearly named folder.

Example:

`c:\Users\Example\Documents\GitHub\processing\SDM26\data\2026_03_11_Autocross`

You can use:

- one single `.benji2` file, or
- one folder that contains multiple `.benji2` files

## Step 1: Open PowerShell In The Project Folder

Copy and paste:

```powershell
cd c:\Users\Example\Documents\GitHub\processing
```

Replace the path above if your project folder is stored somewhere else.

## Step 2: Launch The Conversion GUI

Copy and paste:

```powershell
py SDM26\SDM26_gui_benji2_to_csv.py
```

If you prefer, this command also opens the same GUI:

```powershell
py SDM26\SDM26_gui_converter.py
```

## Step 3: Use The GUI

Inside the GUI:

1. Click `Select File` if you want to convert one `.benji2` file.
2. Click `Select Folder` if you want to convert every `.benji2` file in a folder.
3. Click `Select Output` and choose where you want the converted files saved.
4. Click `Start Conversion`.

The GUI will:

- convert `.benji2` to `.csv`
- convert `.csv` to `.ld`
- show a progress bar while processing
- show live status and debug output in the log window

## Step 4: Find The Output Files

The GUI creates one output session folder inside the output directory you selected.

That folder is named:

`converted_<input_name>`

Inside that folder you will find:

- `csv`
- `ld`

Example:

If your input folder is named:

`2026_03_11_Autocross`

and you select this output directory:

`c:\Users\Example\Documents\Converted_Data`

then the GUI will create:

`c:\Users\Example\Documents\Converted_Data\converted_2026_03_11_Autocross`

and inside it:

- `c:\Users\Example\Documents\Converted_Data\converted_2026_03_11_Autocross\csv`
- `c:\Users\Example\Documents\Converted_Data\converted_2026_03_11_Autocross\ld`

If you select one file instead of one folder, the output folder uses that file name.

Example:

- input file: `skidpad_run_01.benji2`
- output root: `converted_skidpad_run_01`

## Step 5: Open In MoTeC i2

1. Open MoTeC i2.
2. Open the `.ld` file or files from the `ld` folder created by the GUI.

## Full Example For Copy And Paste

Use these commands in order:

```powershell
cd c:\Users\Example\Documents\GitHub\processing
py -m pip install numpy pandas
py SDM26\SDM26_gui_benji2_to_csv.py
```

Then in the GUI:

1. Select your `.benji2` file or folder.
2. Select your output directory.
3. Click `Start Conversion`.

## Example Workflow

Example input folder:

`c:\Users\Example\Documents\GitHub\processing\SDM26\data\2026_03_11_Autocross`

Example output directory selected in the GUI:

`c:\Users\Example\Documents\Converted_Data`

Expected results:

- CSV files: `c:\Users\Example\Documents\Converted_Data\converted_2026_03_11_Autocross\csv`
- MoTeC files: `c:\Users\Example\Documents\Converted_Data\converted_2026_03_11_Autocross\ld`

## Troubleshooting

- `Missing Input`: In the GUI, select a `.benji2` file or a folder that contains `.benji2` files.
- `Missing Output`: In the GUI, select an output directory before clicking `Start Conversion`.
- `No .benji2 files found`: Make sure the selected folder actually contains `.benji2` files.
- `Error importing ...`: Make sure you are running PowerShell from the project folder and that the files in `SDM26` are still present.
- `No module named numpy` or `No module named pandas`: Run:

```powershell
py -m pip install numpy pandas
```

## Recommended Naming

Use clear names that include the date and event.

Examples:

- `2026_03_11_Autocross`
- `2026_03_11_Track_Test_A`
- `2026_03_11_Skidpad_PM`

This makes it much easier to find the correct CSV and MoTeC files later.
