import insightface
import cv2
import os
import pickle

def get_embedding(image):
    """
    Accepts either:
    - a cv2/numpy image (np.ndarray)

    Returns a 512-dim embedding list
    """
    model = insightface.app.FaceAnalysis()
    model.prepare(ctx_id=0)

    faces = model.get(image)
    if not faces:
        raise ValueError("No face detected in image")

    embedding = faces[0]['embedding'].tolist()

    return embedding


# TODO Take all images from the directory called example_images, load them with cv2 generate embeddings and append them to the list, then print the embeddings

IMAGE_DIR = "example_images"
embeddings = []
# Loop through all files in the directory
for filename in os.listdir(IMAGE_DIR):
    # Only process image files (common extensions)
    if filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
        image_path = os.path.join(IMAGE_DIR, filename)
        image = cv2.imread(image_path)

        if image is None:
            print(f"Failed to load {filename}, skipping.")
            continue

        try:
            emb = get_embedding(image)
            embeddings.append(emb)
            print(f"Processed {filename}: embedding length = {len(emb)}")
        except ValueError as e:
            print(f"{filename}: {e}")

with open("embeddings.pkl", "wb") as f:
    pickle.dump(embeddings, f)


