# note2srt

A simple Python script to convert timestamped plain text files into standard .srt subtitle files.

## Features

- **Timestamp Conversion**: Converts various timestamp formats into the standard SRT format (`HH:MM:SS,mmm`).
- **FPS Support**: Allows you to specify the video's FPS (`--fps`) to accurately convert frame counts into milliseconds.
- **Automatic Duration Calculation**:
  - By default, a subtitle's duration is the interval between its start time and the next subtitle's start time.
  - **Key Rule**: If the interval exceeds 3 seconds, the duration will be **capped at 3 seconds**.
- **Hour Correction**:
  - `--subtract_one_hour`: Use this if your input file's timestamps start from `01:00:00`.
  - `--hour_offset`: Adds a specified number of hours to all _output_ timestamps.
- **Paragraph Handling**: Multiple text paragraphs under a single timestamp (separated by blank lines) will be converted into multiple, separate subtitle entries.

## Input File Format

The script expects a plain text (`.txt`) file formatted as follows:

- Each subtitle block begins with a timestamp.
- The timestamp **must be on its own line**.
- All non-empty lines following the timestamp are treated as the content.
- Blank lines between text (under the same timestamp) are used to separate paragraphs.

### Supported Timestamp Formats

The script is flexible and supports three different timestamp formats. **You can freely mix all three formats in the same file.**

1.  `mm:ss` (e.g., `25:30`)
    - Interpreted as **Minutes:Seconds**.
2.  `hh:mm:ss` (e.g., `01:10:45`)
    - Interpreted as **Hours:Minutes:Seconds**.
3.  `hh:mm:ss:ff` (e.g., `01:10:45:12`)
    - Interpreted as **Hours:Minutes:Seconds:Frames**.
    - When using this format, the script uses the `--fps` argument to calculate the precise millisecond.
    - If you use this format but do not provide an `--fps` argument, the script will **default to 24.0 FPS** for the calculation.

### Example Input (`my_notes.txt`)

This example shows how all three formats can be mixed.

```

00:05
This is the first subtitle. (Uses mm:ss format - 5 seconds)

01:08:12
This is the second subtitle. (Uses hh:mm:ss format)

01:10:00
This is the first paragraph for the third subtitle.

This is the second paragraph.
It will become a separate SRT entry.

01:15:20:12
This is the fourth subtitle. (Uses hh:mm:ss:ff format with 12 frames)

18:30
This is the fifth subtitle. (Uses mm:ss format - 18 minutes, 30 seconds)

```

## How to Use

1.  Copy the transcript from your notes and paste it into a plain text file (e.g., `my_notes.txt`).
2.  Open your terminal and run the script (`make_srt.py` being your script's filename):

```bash
python make_srt.py [input_file] [output_file] [options]
```

### Basic Example

```bash
python make_srt.py my_notes.txt subtitles.srt
```

### Advanced Example

This example processes an input file that starts at `01:00:00` and has a framerate of 24 FPS:

```bash
python make_srt.py "video_transcript.txt" "output.srt" --subtract_one_hour --fps 24
```

## Command-Line Arguments

- `input_file`: (Required) Path to your plain text notes file.
- `output_file`: (Required) Path for the output `.srt` file.
- `--hour_offset INT`: (Optional) Hour offset to add to the output SRT timestamps. (Default: 0)
- `--subtract_one_hour`: (Optional) Use this flag if your input file's timeline starts at `01:00:00` instead of `00:00:00`.
- `--fps FLOAT`: (Optional) The frame rate (FPS) of the source video for accurate frame-to-ms conversion from `hh:mm:ss:ff` format. (Default: 24.0)

## Why Does This Exist?

I originally built this script because I write all my vlog subtitles in the Notes app first. Manually copying and pasting every single line into my video editor (like Final Cut Pro or Premiere Pro) was tedious, time-consuming, and just plain boring.

note2srt was born from that frustration. It automates the entire process.

It lets you focus on writing in a simple text environment. When you're done, just run the script once to get a universal .srt file that's ready for any video editing software.

I'm sharing this in the hope it can help someone else with the same problem. If it helps you, that makes me happy. :)
