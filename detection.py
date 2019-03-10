import boto3, os, json, sys, math, cv2, pprint
from pathlib import Path

client = boto3.client('rekognition')

FILE_NAME = "/tmp/rekogwebcam.png"

def get_image():

    camera = cv2.VideoCapture(0)

    raw_input("Press Enter to capture picture...")

    # 30 frames are discarded to let the camera adjust brightness
    for i in xrange(30):
        temp = camera.read()

    print ("Processing...")
    cv2.imwrite(FILE_NAME, camera.read()[1])
    del(camera)
    print ("Picture Taken")
    with open(FILE_NAME, "rb") as imageFile:
        f = imageFile.read()
    os.remove(FILE_NAME)
    return f

def remove_user():

    response = client.list_faces(
        CollectionId='faces'
    )

    i = 1
    for face in response["Faces"]:
        print(str(i)+". "+face["ExternalImageId"][1:])
        i+=1

    while True:
        delete_face = int(raw_input("Which user do you wish to delete? "))

        if delete_face < i and delete_face > 0:
            break
        else:
            continue

    delete_face -= 1
    delete_face_id = response["Faces"][delete_face]["FaceId"]
    response = client.delete_faces(
        CollectionId='faces',
        FaceIds=[
            delete_face_id
        ]
    )
    if(response["ResponseMetadata"]["HTTPStatusCode"] == 200):
        print("Successfully deleted the user.")
    else:
        print("Something went wrong, please try again later.")
    exit()

f = get_image()

def add_user():
    f = get_image()

    name = str(raw_input("Enter name of subject: "))

    while True:
        authority = str(raw_input("Is the user an admin? (Y/n): "))

        if authority != 'Y' and authority != 'N':
            continue
        else:
            break

    response = client.index_faces(
        CollectionId='faces',
        Image={
            'Bytes': f
        },
        ExternalImageId=authority+name,
        MaxFaces=1
    )
    if(response["ResponseMetadata"]["HTTPStatusCode"] == 200):
        print("Successfully added to database.")
    else:
        print("Something went wrong, please try again later.")

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
    print("Matched with: " + matchedFaces[0]["Face"]["ExternalImageId"][1:] + " with " + str(math.floor(matchedFaces[0]["Face"]["Confidence"])) + "% confidence.")
    if(matchedFaces[0]["Face"]["ExternalImageId"][0] == "Y"):
        while True:

            print("You are an admin, what do you wish to do?")
            print("1. Add new User")
            print("2. Remove User")
            print("3. Exit")

            choice = str(raw_input())

            if choice == "1":
                add_user()
            elif choice == "2":
                remove_user()
            elif choice == "3":
                exit()
            else:
                continue


if('-v' in sys.argv):
    print json.dumps(response, indent=4, sort_keys=True)
