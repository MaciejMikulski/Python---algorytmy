import cv2
import matplotlib.pyplot as plt
import numpy as np

# Load both images in grayscale
image1 = cv2.imread('ccl_in.bmp', cv2.IMREAD_GRAYSCALE)
image2 = cv2.imread('1-45-86.png', cv2.IMREAD_GRAYSCALE)

# Check if images loaded properly
if image1 is None:
    raise FileNotFoundError("Image 'ccl_in.bmp' not found.")
if image2 is None:
    raise FileNotFoundError("Image '1-45-86.bmp' not found.")

# Compute histograms with 64 bins (4 intensity values per bin)
bins = 128
hist1 = cv2.calcHist([image1], [0], None, [bins], [0, 256]).flatten()
hist2 = cv2.calcHist([image2], [0], None, [bins], [0, 256]).flatten()

# X-axis positions (center of each bin)
bin_centers = np.arange(0, 256, 2) + 2  # midpoints: 2, 6, ..., 254

# Plot both histograms as line plots
plt.figure(figsize=(7, 4.5))
plt.plot(bin_centers, hist1, color='black', alpha=1.0, label='With marker')
plt.plot(bin_centers, hist2, color='red', alpha=1.0, label='Without marker')
plt.title('Histogram of an IR image')
plt.xlabel('Intensity')
plt.ylabel('Count')
plt.grid(True, which='both', axis='both')
plt.xlim([0, 255])
plt.legend()
plt.tight_layout()
plt.show()

#from threshold import *
#from helperFunctions import *
#from visualAlgorithm import *
#from output_csv import *
#
#from skimage.filters import threshold_otsu  
#
#from torch.utils.data import DataLoader
#from ImageRecognitionDataset import *
#
#csv_file = r"H:\SR\fok-visual-data\Labeling\labeling_marker_B\exported_label_data.csv"
#image_base_dir = r"H:\SR\fok-visual-data\IR_images\Marker_B"
#csv_file = os.path.normpath(csv_file)
#image_base_dir = os.path.normpath(image_base_dir)
#
#dataset = ImageRecognitionDataset(csv_file, image_base_dir)                  # Create dataset
#dataloader = DataLoader(dataset, batch_size=16, shuffle=True, num_workers=4) # Create DataLoader
#
#visualAlg = visualAlgorithm(algType=AlgorithmType.ALGORITHM_PEAK, implType=ImplementationType.IMPL_HARDWARE) # Configure algorithm
#
#img_num = len(dataset)
#################################################### Average intensity of background ####################################################
#avg_peak_intens = 0.0
#avg_background_intens_no_marker = 0.0
#avg_background_intens_marker = 0.0
#
## Counters of images with and without marker
#no_marker_cnt = 0
#marker_cnt = 0
#
#
#for i in range(0, img_num):
#    if (i% 25 == 0):
#        print(f"{i}/{img_num}")
#
#    img, has_marker, img_points = dataset[i]
#    img = img.astype(np.uint16)
#    if has_marker:
#        marker_cnt += 1
#        
#        # Calculate average background value
#        thresh = threshold_otsu(img)
#        background_mask = img < thresh
#        background_mask_bool = background_mask.astype(bool)
#
#        avg_background_intens_marker += img[background_mask_bool].mean()
#    
#        blob_mask = img >= thresh
#        blob_mask_bool = blob_mask.astype(bool)
#         
#        # Calculate average intensity of top 10% of brightest pixels that make up blobs
#        masked_pixels = img[blob_mask_bool]
#        sorted_pixels = np.sort(masked_pixels)[::-1] # Sort pixel values in descending order
#        top_10_count = max(1, int(0.10 * len(sorted_pixels)))  # prevent zero division
#        top_10_pixels = sorted_pixels[:top_10_count] # Get top 10% brightest pixel values
#        avg_peak_intens += top_10_pixels.mean() # Compute the average
#
#    else:
#        no_marker_cnt += 1
#        avg_background_intens_no_marker += img.mean()
#
## Compute final averages
#avg_peak_intens = avg_peak_intens / marker_cnt
#avg_background_intens_no_marker = avg_background_intens_no_marker / no_marker_cnt
#avg_background_intens_marker = avg_background_intens_marker / marker_cnt
#
#print(f"Average peak intensity from top 10% brightest pixels: {avg_peak_intens:.2f}")
#print(f"Average background with peaks intensity: {avg_background_intens_marker:.2f}")
#print(f"Average background without peaks intensity: {avg_background_intens_no_marker:.2f}")