

from app.schemas import StudentIn
import uuid
import base64
import os
import insightface
import cv2
import numpy as np

FACE_IMAGE_DIR = os.path.join(os.path.dirname(__file__), "../images/faces")
FACE_EMBEDDING_SIZE = 512

def store_face(student: StudentIn) -> str:
    """
    stores student face image and returns the storage URI
    """
    header, encoded = student.photo.split(",", 1)
    file_ext = header.split(";")[0].split("/")[1]
    file_name = f"{student.PID}_{uuid.uuid4()}.{file_ext}"
    storage_path = os.path.join(FACE_IMAGE_DIR, file_name)
    image_bytes = base64.b64decode(encoded)
    
    with open(storage_path, "wb") as f:
        f.write(image_bytes)

    return file_name

def get_embedding(image_input):
    """
    Accepts either:
    - a filename (str) relative to FACE_IMAGE_DIR
    - a cv2/numpy image (np.ndarray)

    Returns a 512-dim embedding list
    """

    model = insightface.app.FaceAnalysis()
    model.prepare(ctx_id=0)

    # If it's a string, treat as a filename
    if isinstance(image_input, str):
        storage_path = os.path.join(FACE_IMAGE_DIR, image_input)
        image = cv2.imread(storage_path)

        if image is None:
            raise ValueError(f"Image could not be loaded from {storage_path}")

    # If it's already an image (np array)
    elif isinstance(image_input, np.ndarray):
        image = image_input

    else:
        raise TypeError("Input must be a filename (str) or a cv2 image (np.ndarray)")

    faces = model.get(image)
    if not faces:
        raise ValueError("No face detected in image")

    embedding = faces[0]['embedding'].tolist()

    if len(embedding) != FACE_EMBEDDING_SIZE:
        raise ValueError(f"Embedding size mismatch: expected {FACE_EMBEDDING_SIZE}, got {len(embedding)}")

    return embedding

def base64_to_cv2(base64_str: str):
    # Remove data:image/...;base64, header if present
    if "," in base64_str:
        base64_str = base64_str.split(",", 1)[1]

    # Decode base64 to bytes
    image_bytes = base64.b64decode(base64_str)

    # Convert bytes to numpy array
    np_arr = np.frombuffer(image_bytes, np.uint8)

    # Decode to OpenCV image
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("Could not decode image")

    return image

    
