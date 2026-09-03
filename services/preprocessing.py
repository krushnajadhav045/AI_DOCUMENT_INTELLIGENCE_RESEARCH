from pathlib import Path

import cv2


def preprocess_image(
    input_path: str,
    output_path: str
) -> str:

    image = cv2.imread(
        input_path
    )

    if image is None:

        raise ValueError(
            f"Unable to read image: {input_path}"
        )

    # -----------------------------------------
    # Grayscale
    # -----------------------------------------

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # -----------------------------------------
    # Noise removal
    # -----------------------------------------

    denoised = cv2.fastNlMeansDenoising(
        gray,
        None,
        10,
        7,
        21
    )

    # -----------------------------------------
    # Contrast enhancement
    # -----------------------------------------

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(
        denoised
    )

    # -----------------------------------------
    # Adaptive threshold
    # -----------------------------------------

    processed = cv2.adaptiveThreshold(
        enhanced,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11
    )

    output_path = Path(
        output_path
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    cv2.imwrite(
        str(output_path),
        processed
    )

    return str(output_path)