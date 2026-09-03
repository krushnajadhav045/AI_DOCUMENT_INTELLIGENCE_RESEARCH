async def process_document(document_id: str):

    print("=" * 60)
    print("DOCUMENT ID:", document_id)
    print("UPLOAD DIRECTORY:", UPLOAD_DIR)
    print("=" * 60)

    print("FILES IN UPLOAD DIRECTORY:")

    for file in UPLOAD_DIR.rglob("*"):
        print(file)

    # continue your existing code...