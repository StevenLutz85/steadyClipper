#!/usr/bin/python3

import cv2
import os
import argparse

#!/usr/bin/python3
import cv2

def calculate_steady_threshold(frame_diffs):
    # Calculate the average frame difference
    average_diff = sum(frame_diffs) / len(frame_diffs)
    # Set the threshold as a multiple of the average difference
    return average_diff

def extract_steady_sections(input_file, output_folder, min_duration_seconds=1):
    cap = cv2.VideoCapture(input_file)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    frame_diffs = []  # Store frame differences for threshold calculation
    prev_frame = None
    frame_index = 0

    # First Pass: Calculate the steady threshold
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if prev_frame is not None:
            frame_diff = cv2.absdiff(prev_frame, frame).mean()
            frame_diffs.append(frame_diff)

        prev_frame = frame

    frame_index += 1

    cap.release()

    # Calculate the steady threshold based on the first pass
    steady_threshold = calculate_steady_threshold(frame_diffs)

    print(f"Steady Threshold: {steady_threshold}")

    # Second Pass: Extract steady sections using the calculated threshold
    cap = cv2.VideoCapture(input_file)
    steady_frames = []
    prev_frame = None
    frame_index = 0

    output_folder = os.path.splitext(input_file)[0] + "_output"
    os.makedirs(output_folder, exist_ok=True)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if prev_frame is not None:
            frame_diff = cv2.absdiff(prev_frame, frame).mean()
            if frame_diff < steady_threshold:
                steady_frames.append(frame)
            else:
                if steady_frames:
                    # Calculate the duration of the steady section in seconds
                    duration_seconds = len(steady_frames) / fps
                    # Export steady section as separate video file if duration is >= min_duration_seconds
                    if duration_seconds >= min_duration_seconds:
                        output_file = f"{output_folder}/steady_section_{frame_index}.mp4"
                        out = cv2.VideoWriter(output_file,
                                              cv2.VideoWriter_fourcc(*'mp4v'),
                                              fps, (frame_width, frame_height))
                        for steady_frame in steady_frames:
                            out.write(steady_frame)
                        out.release()

                steady_frames.clear()

        prev_frame = frame

        frame_index += 1

    cap.release()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract steady sections from a video file.")
    parser.add_argument("video_file", type=str, help="Input video file (MP4 format)")
    parser.add_argument("--min_duration_seconds", type=float, default=1, help="Minimum duration for exported sections")
    args = parser.parse_args()

    extract_steady_sections(args.video_file, args.min_duration_seconds)
