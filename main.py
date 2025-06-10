from threshold import *
from helperFunctions import *
from visualAlgorithm import *
from hardwarePeakMax import *
from uart import send_to_hardware
from uart import default_response
from output_csv import *

import os
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from torch.utils.data import DataLoader
from ImageRecognitionDataset import *

# UART Config
COM_PORT = 'COM8'
BAUD_RATE = 230400

# Set up logging
log_filename = datetime.now().strftime("logs/log_%Y%m%d_%H%M%S.txt")
logging.basicConfig(filename=log_filename, level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Set paths to marker dataset and image data
csv_file = r"H:\SR\fok-visual-data\Labeling\labeling_marker_B\exported_label_data.csv"
image_base_dir = r"H:\SR\fok-visual-data\IR_images\Marker_B"
csv_file = os.path.normpath(csv_file)
image_base_dir = os.path.normpath(image_base_dir)

dataset = ImageRecognitionDataset(csv_file, image_base_dir)                  # Create dataset
dataloader = DataLoader(dataset, batch_size=16, shuffle=True, num_workers=4) # Create DataLoader

visualAlg = visualAlgorithm(algType=AlgorithmType.ALGORITHM_PEAK, implType=ImplementationType.IMPL_HARDWARE) # Configure algorithm

output_csv_filename = create_output_csv(base_dir=r".\test_output")

true_positive = 0
true_negative = 0
false_positive = 0
false_negative = 0
total = int(len(dataset))

# Main testing loop
with open(output_csv_filename, 'a', newline='') as csvfile:
    writer = csv.writer(csvfile)

        # Optional: limit max threads if needed
    with ThreadPoolExecutor(max_workers=2) as executor:
        for i in range(0, len(dataset)):
            print(i)
            if (i% 25 == 0):
                print(f"{i}/{total}")

            img, has_marker, img_points = dataset[i]
            img = img.astype(np.uint16)
            showImages([img])
            # Submit both functions to the thread pool
            future_sw = executor.submit(visualAlg.execute, img)
            #future_hw = executor.submit(send_to_hardware, img, COM_PORT, BAUD_RATE)

            # Wait for results (these run in parallel)
            sw_R, sw_t, sw_success, sw_points = future_sw.result()
            hw_R, hw_t, hw_success, hw_points, hw_time, hw_current, hw_temp = default_response()#future_hw.result()

            row = [i]
            row += [has_marker]
            row += img_points.flatten().tolist()

            row += [sw_success]
            row += sw_R.flatten().tolist()
            row += sw_t.flatten().tolist()
            row += sw_points.flatten().tolist()

            row += [hw_success]
            row += hw_R.flatten().tolist()
            row += hw_t.flatten().tolist()
            row += hw_points.flatten().tolist()
            row += [hw_time, hw_current, hw_temp]

            if (has_marker == 1 and sw_success == 1): 
                true_positive += 1
            elif (has_marker == 1 and sw_success == 0):
                false_negative += 1
            elif (has_marker == 0 and sw_success == 1):
                false_positive += 1
            elif (has_marker == 0 and sw_success == 0):
                true_negative += 1

            writer.writerow(row)


print(f"Processing completed. Results saved in: {output_csv_filename}")
print(f"True positive:  {true_positive/total}")
print(f"True negative:  {true_negative/total}")
print(f"False positive: {false_positive/total}")
print(f"Fakse negative: {false_negative/total}")












# peakCoordinates = np.array(((117, 58),
#                                     (118, 58),
#                                     (71, 61),
#                                     (110, 78),
#                                     (82, 88),
#                                     (83, 88)))
# 
# marker2Dpoints, noisePointsIm, markerFindSuccess = visualAlg._findMarkerPoints(peakCoordinates)

########################## OLD IMAGE LOADING ##########################
# #usedMarkerType = "A"
# usedMarkerType = "B"
# #usedMarkerType = "Bcorrect"
# 
# # Path to images folder
# pathA = os.path.join(os.path.dirname(__file__), 'Zdjecia', 'zdjecia_FOK2', 'Znacznik_A')
# pathB = os.path.join(os.path.dirname(__file__), 'Zdjecia', 'zdjecia_FOK2', 'Znacznik_B')
# pathBCorrect = os.path.join(os.path.dirname(__file__), 'Zdjecia', 'zdjecia_FOK2', 'Znacznik_B_poprawne')
# 
# # Path to data folder
# testDataPath = os.path.join(os.path.dirname(__file__), 'CumulativeTHresholdingAreaTests', 'Marker_B')
# 
# 
# # Get images and parsed data
# if usedMarkerType == "A":
#     images, markerTypes, distances, imageIndexes, filenames = getImages(pathA)
# elif usedMarkerType == "B":
#     images, markerTypes, distances, imageIndexes, filenames = getImages(pathB)
# elif usedMarkerType == "Bcorrect":
#     images, markerTypes, distances, imageIndexes, filenames = getImages(pathBCorrect)
# else:
#     raise Exception("Wrong marker type.")
# 
# # maximum image IDs that contain valid markers
# #          Distances: 2        25        3        35        4        45        5        55
# #markerPresentIndex = (2.0: 40, 25.0: 80, 3.0: 79, 35.0: 80, 4.0: 80, 45.0: 80, 5.0: 80, 55.0: 80)





























# angles = []
# blobNum = []
######## GET BLOB ANGLES #########
# for i in range(len(images)):
#     x, y, rot, num, blobAngles = blobAlg.blobAlgorithm(images[i], distances[i])
#     #blobNum.append(num)
#     angles.append(blobAngles)
# #print(blobNum)
# 
# angles = np.array(angles)
# angles.sort(axis=1)
# angles = np.around(angles/5.0, decimals=0)*5
# print(angles)

############### DETERMINE OPTIMAL NUMBER OF CLUSTERS ###############
#kmeans = KMeans(n_clusters=2, random_state=0, n_init="auto").fit(angles)
#labels = kmeans.labels_

#angles0 = angles[labels == 0,:]
#angles1 = angles[labels == 1,:]
#print(angles0.shape)
#print(angles1.shape)
#print(angles.shape)
#print(angles0)
#print(angles1)

#index = []
#N = 20
#print("Davies-Bouldin scores:")
#for i in range(2,N+1,1):
#    kmeans = KMeans(n_clusters=i, random_state=0, n_init="auto").fit(angles)
#    labels = kmeans.labels_
#    score = silhouette_score(angles, labels)
#    index.append(score)
#    print("i: ", i, "score: ", score)

#for i in range(len(images)):
#    title = str(round(angles[i, 0], 3)) + " " + str(round(angles[i, 1], 3)) + " " + str(round(angles[i, 2], 3)) + " " + str(round(angles[i, 3], 3))
#    showImages([images[i,:,:]], 1, 1, title)

