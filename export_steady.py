#!/usr/bin/python3

import cv2
import os
import argparse
import numpy as np

def calculate_steady_threshold(frame_diffs, std_multiplier=1):
    # Calculate the standard deviation of frame differences
    std_deviation = np.std(frame_diffs)

    # Calculate the average frame difference
    average_diff = sum(frame_diffs) / len(frame_diffs)

    # Set the threshold as a multiple of the standard deviation plus the average difference
    threshold = (std_deviation * std_multiplier) + average_diff

    return threshold

def extract_steady_sections(input_file, output_folder, min_duration_seconds=1, buffer_size=100):
    # First Pass: Calculate the steady threshold
    cap = cv2.VideoCapture(input_file)
    frame_diffs = []  # Store frame differences for threshold calculation
    prev_frame = None
    frame_index = 0
    goodClip = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if prev_frame is not None:
            # Calculate the absolute difference between consecutive frames and find the mean
            frame_diff = cv2.absdiff(prev_frame, frame).mean()
            frame_diffs.append(frame_diff)

        prev_frame = frame
        frame_index += 1

    cap.release()

    # Calculate the steady threshold based on the first pass
    steady_threshold = calculate_steady_threshold(frame_diffs)
    print(f"Steady Threshold: {steady_threshold}")

    #Find max frame diffs
    print(f"Max Diffs: {max(frame_diffs)}")

    #Find min frame diffs
    print(f"Min Diffs: {min(frame_diffs)}")

    #Find average frame differences
    print(f"Avg Diffs: {sum(frame_diffs) / len(frame_diffs)}")

    #Find frames Std Deviation
    print(f"Standard Deviation: {np.std(frame_diffs)}")

    # Second Pass: Extract steady sections using the calculated threshold
    cap = cv2.VideoCapture(input_file)
    frame_index = 0

    os.makedirs(output_folder, exist_ok=True)

    # Get video properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    output_fps = fps

    # Initialize variables for steady section detection
    steady_frames = []
    steady_section_start_frame = None

    # Calculate the minimum number of frames required for exported clips
    min_frames_required = int(fps * min_duration_seconds)

    out = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if prev_frame is not None:
            # Calculate the absolute difference between consecutive frames and find the mean
            frame_diff = cv2.absdiff(prev_frame, frame).mean()

            # Check if the frame is steady (frame difference below the threshold)
            if frame_diff < steady_threshold:
                if steady_section_start_frame is None:
                    steady_section_start_frame = frame_index

                steady_frames.append(frame)

                # If the collected steady frames meet the minimum requirement, start exporting frames to the video file starting with the frames in the buffer.
                if len(steady_frames) >= min_frames_required or goodClip == 1:
                    if goodClip == 0:
                        output_file = f"{output_folder}/steady_section_{frame_index}.mp4"
                        out = cv2.VideoWriter(output_file,
                                              cv2.VideoWriter_fourcc(*'hvcl'),
                                              output_fps, (frame_width, frame_height))

                        for steady_frame in steady_frames:
                            out.write(steady_frame)
                        goodClip = 1

                    else:
                        out.write(frame)

            else:
                if out is not None:
                    out.release()
                    steady_frames.clear()
                    steady_section_start_frame = None
                    goodClip = 0

        prev_frame = frame
        frame_index += 1

    cap.release()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract steady sections from a video file.")
    parser.add_argument("video_file", type=str, help="Input video file (MP4 format)")
    parser.add_argument("--min_duration_seconds", type=float, default=1, help="Minimum duration in seconds for exported sections, Default 1")
    parser.add_argument("--deviation-mult", type=float, default=1, help="Multiplier of Standard Deviation which is added to the frames average difference value for Clipping Threshold, Default 2")
    args = parser.parse_args()

    output_folder = os.path.splitext(args.video_file)[0] + "_output"
    extract_steady_sections(args.video_file, output_folder, args.min_duration_seconds)
