import datetime
import csv
import os


def create_output_csv(base_dir: str = ".", prefix: str = "processing_results") -> str:
    """
    Creates a CSV file with a timestamped filename and writes the header row.
    
    Args:
        base_dir (str): Directory where the CSV file will be created.
        prefix (str): Prefix for the filename.

    Returns:
        str: Full path to the created CSV file.
    """
    # Generate timestamped filename
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{prefix}_{timestamp}.csv"
    filepath = os.path.join(base_dir, filename)

    # Prepare CSV header
    header = ['image_index']
    header += ['has_marker']
    header += [f'gt_point_{k}_{coord}' for k in range(4) for coord in ['x', 'y']]

    header += ['sw_success']
    header += [f'sw_R_{i}{j}' for i in range(3) for j in range(3)]
    header += [f'sw_t_{j}' for j in range(3)]
    header += [f'sw_point_{k}_{coord}' for k in range(4) for coord in ['x', 'y']]

    header += ['hw_success']
    header += [f'hw_R_{i}{j}' for i in range(3) for j in range(3)]
    header += [f'hw_t_{j}' for j in range(3)]
    header += [f'hw_point_{k}_{coord}' for k in range(4) for coord in ['x', 'y']]
    header += ['hw_time', 'hw_current', 'hw_temp']

    # Write header to CSV
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)

    return filepath