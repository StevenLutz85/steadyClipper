#!/usr/bin/python3

import cv2
import os
import argparse

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
    prev_frame = None
    frame_index = 0

    os.makedirs(output_folder, exist_ok=True)

    # Create VideoWriter with the correct frame rate
    output_fps = fps

    out = None
    steady_frames_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if prev_frame is not None:
            frame_diff = cv2.absdiff(prev_frame, frame).mean()
            if frame_diff < steady_threshold:
                if out is None:
                    output_file = f"{output_folder}/steady_section_{frame_index}.mp4"
                    out = cv2.VideoWriter(output_file,
                                          cv2.VideoWriter_fourcc(*'mp4v'),
                                          output_fps, (frame_width, frame_height))
                out.write(frame)
                steady_frames_count += 1
            else:
                if out is not None:
                    duration_seconds = steady_frames_count / fps
                    if duration_seconds >= min_duration_seconds:
                        out.release()

                out = None
                steady_frames_count = 0

        prev_frame = frame

        frame_index += 1

    if out is not None:
        duration_seconds = steady_frames_count / fps
        if duration_seconds >= min_duration_seconds:
            out.release()

    cap.release()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract steady sections from a video file.")
    parser.add_argument("video_file", type=str, help="Input video file (MP4 format)")
    parser.add_argument("--min_duration_seconds", type=float, default=1, help="Minimum duration for exported sections")
    args = parser.parse_args()

    output_folder = os.path.splitext(args.video_file)[0] + "_output"
    extract_steady_sections(args.video_file, output_folder, args.min_duration_seconds)
