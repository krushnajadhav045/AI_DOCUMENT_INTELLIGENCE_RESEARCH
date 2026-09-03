from pathlib import Path

import pymupdf


def pdf_to_images(
    pdf_path: str,
    output_dir: str
) -> list[str]:

    pdf_path = Path(pdf_path)

    output_dir = Path(
        output_dir
    )

    # ---------------------------------------------
    # Create output directory
    # ---------------------------------------------

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # ---------------------------------------------
    # Open PDF
    # ---------------------------------------------

    document = pymupdf.open(
        str(pdf_path)
    )

    image_paths = []

    # ---------------------------------------------
    # Convert each page
    # ---------------------------------------------

    for page_number, page in enumerate(
        document,
        start=1
    ):

        print(
            f"Converting PDF page {page_number}..."
        )

        # 2x resolution
        matrix = pymupdf.Matrix(
            2.0,
            2.0
        )

        pixmap = page.get_pixmap(
            matrix=matrix,
            alpha=False
        )

        image_path = (
            output_dir /
            f"page_{page_number}.png"
        )

        pixmap.save(
            str(image_path)
        )

        image_paths.append(
            str(image_path)
        )

    # ---------------------------------------------
    # Close PDF
    # ---------------------------------------------

    document.close()

    print(
        f"PDF converted successfully: "
        f"{len(image_paths)} page(s)"
    )

    return image_paths