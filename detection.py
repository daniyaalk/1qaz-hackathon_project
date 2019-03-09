import boto3, os, json, sys, math, cv2
from pathlib import Path

client = boto3.client('rekognition')

print("Choose Task: ")
print("1. Add to collection")
print("2. Search by image")

choice = input("Enter task: ")

input_option = 1

if input_option == 1:
    FILE_NAME = "/tmp/rekogwebcam.png"

    camera = cv2.VideoCapture(0)

    raw_input("Press Enter to capture picture...")

    # 30 frames are discarded to let the camera adjust brightness
    for i in xrange(30):
        temp = camera.read()

    print ("Processing...")
    cv2.imwrite("/tmp/rekogwebcam.png", camera.read()[1])
    del(camera)
    print ("Picture Taken")

elif input_option == 2:
    FILE_NAME = raw_input("Enter file name: ")

else:
    exit()

# check if file exists
if not Path(FILE_NAME).is_file():
    print("Could not find file.")
    exit()

## check file size
if os.path.getsize(FILE_NAME) > 5242880:
    print("File too large.")
    exit()

with open(FILE_NAME, "rb") as imageFile:
  f = imageFile.read()
  b = bytearray(f)

if choice == 1:
    response = client.search_faces_by_image(
        CollectionId='faces',
        Image={
            'Bytes': f
        }
    )

    matchedFaces = response["FaceMatches"]

    if(len(matchedFaces) != 0):
        print("That face already exists!")
        exit()

    name = str(raw_input("Enter name of subject: "))
    response = client.index_faces(
        CollectionId='faces',
        Image={
            'Bytes': f
        },
        ExternalImageId=name
    )
    if(response["ResponseMetadata"]["HTTPStatusCode"] == 200):
        print("Successfully added to database.")
    else:
        print("Something went wrong, please try again later.")

elif choice == 2:
    response = client.search_faces_by_image(
        CollectionId='faces',
        Image={
            'Bytes': f
        }
    )

    matchedFaces = response["FaceMatches"]

    if(len(matchedFaces) == 0):
        print("No match found.")
        exit()

    elif len(matchedFaces) >= 1:

        matchedFaces.sort(key=lambda match: match["Face"]["Confidence"], reverse=True)
        print("Matched with: " + matchedFaces[0]["Face"]["ExternalImageId"] + " with " + str(math.floor(matchedFaces[0]["Face"]["Confidence"])) + "% confidence.")

if('-v' in sys.argv):
    print json.dumps(response, indent=4, sort_keys=True)
