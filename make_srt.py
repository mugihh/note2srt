import sys
import re
from datetime import timedelta
import argparse


def parse_time(timestr, subtract_one_hour=False, fps=24.0):
    """
    Parse timestamp and convert frames to milliseconds based on FPS.
    """
    if fps <= 0:
        raise ValueError("FPS must be greater than 0")

    parts = [int(p) for p in timestr.strip().split(":")]
    h, m, s, ms = 0, 0, 0, 0

    if len(parts) == 2:  # mm:ss
        m, s = parts
    elif len(parts) == 3:  # hh:mm:ss
        h, m, s = parts
    elif len(parts) == 4:  # hh:mm:ss:ff (frames)
        h, m, s, frames = parts
        # This is the correct formula for frame-to-ms conversion
        ms = int((frames / fps) * 1000)
    else:
        raise ValueError(f"Invalid time format: {timestr}")

    if subtract_one_hour and h > 0:
        h -= 1

    return timedelta(hours=h, minutes=m, seconds=s, milliseconds=ms)


def parse_blocks(lines, subtract_one_hour_if_needed=False, fps=24.0):
    """
    Parse input lines into (time, text_lines) blocks.
    Consecutive non-empty lines form a single block.
    Blank lines act as separators between blocks.
    """
    blocks = []
    current_time = None
    current_raw_lines = []

    time_pattern = re.compile(r"^\d{1,2}(:\d{2}){1,3}$")

    def process_collected_lines():
        if not current_raw_lines:
            return []
        final_text_blocks, current_paragraph = [], []
        for line in current_raw_lines:
            stripped = line.strip()
            if stripped:
                current_paragraph.append(stripped)
            else:
                if current_paragraph:
                    final_text_blocks.append("\n".join(current_paragraph))
                    current_paragraph = []
        if current_paragraph:
            final_text_blocks.append("\n".join(current_paragraph))
        return final_text_blocks

    for line in lines:
        stripped_line = line.strip()
        is_timestamp = time_pattern.match(stripped_line)
        if is_timestamp:
            if current_time is not None:
                processed_text = process_collected_lines()
                blocks.append((current_time, processed_text))
            current_time = parse_time(
                stripped_line,
                subtract_one_hour=subtract_one_hour_if_needed,
                fps=fps,
            )
            current_raw_lines = []
        else:
            if current_time is not None:
                current_raw_lines.append(line)

    if current_time is not None:
        processed_text = process_collected_lines()
        blocks.append((current_time, processed_text))
    return blocks


def format_srt_time(td, hour_offset=0):
    """Format timedelta into SRT time with optional hour offset, in milliseconds."""
    total_ms = int(td.total_seconds() * 1000)
    h = total_ms // 3600000
    m = (total_ms % 3600000) // 60000
    s = (total_ms % 60000) // 1000
    ms = total_ms % 1000
    h += hour_offset
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def generate_srt(blocks, hour_offset=0, max_duration=3.0):
    """
    Generates SRT content based on the rule:
    Each text cue lasts up to max_duration and consecutive cues under the same
    timestamp are placed one after another.
    """
    if max_duration <= 0:
        raise ValueError("Maximum duration must be greater than 0")

    srt_lines, index = [], 1
    blocks = [(start_time, text_lines) for start_time, text_lines in blocks if text_lines]

    for i, (current_start_time, text_lines) in enumerate(blocks):
        for text_index, line in enumerate(text_lines):
            start_time = current_start_time + timedelta(seconds=max_duration * text_index)

            if text_index < len(text_lines) - 1:
                duration = timedelta(seconds=max_duration)
            elif i == len(blocks) - 1:
                duration = timedelta(seconds=max_duration)
            else:
                next_start_time, _ = blocks[i + 1]
                interval_seconds = (next_start_time - start_time).total_seconds()

                if interval_seconds <= 0 or interval_seconds > max_duration:
                    duration = timedelta(seconds=max_duration)
                else:
                    duration = next_start_time - start_time

            end_time = start_time + duration
            srt_lines.append(str(index))
            srt_lines.append(
                f"{format_srt_time(start_time, hour_offset)} --> {format_srt_time(end_time, hour_offset)}"
            )
            srt_lines.append(line)
            srt_lines.append("")
            index += 1

    return "\n".join(srt_lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate SRT subtitle files from a timestamped text file.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("input_file", help="Path to the input text file.")
    parser.add_argument("output_file", help="Path for the output .srt file.")
    parser.add_argument(
        "--hour_offset",
        type=int,
        default=0,
        help="Hour offset for the output SRT. E.g., 1 to start timestamps at 01:xx:xx.",
    )
    parser.add_argument(
        "--subtract_one_hour",
        action="store_true",
        help="Use this if your input file's timeline starts at 01:00:00 instead of 00:00:00.",
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=24.0,
        help="Frame rate (FPS) of the source video for accurate timestamp conversion (e.g., 24, 29.97, 30). Default: 24.0",
    )
    parser.add_argument(
        "--max_duration",
        type=float,
        default=3.0,
        help="Maximum duration in seconds for each timestamp block. Default: 3.0",
    )
    args = parser.parse_args()

    try:
        with open(args.input_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Input file not found at '{args.input_file}'")
        sys.exit(1)

    try:
        blocks = parse_blocks(
            lines, subtract_one_hour_if_needed=args.subtract_one_hour, fps=args.fps
        )
        srt_content = generate_srt(
            blocks, hour_offset=args.hour_offset, max_duration=args.max_duration
        )
    except ValueError as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    with open(args.output_file, "w", encoding="utf-8") as f:
        f.write(srt_content)

    print(f"Successfully generated SRT file: {args.output_file}")


if __name__ == "__main__":
    main()
