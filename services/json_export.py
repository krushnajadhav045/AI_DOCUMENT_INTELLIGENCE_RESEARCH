import json


def export_json(data, output_path):

    if hasattr(data, "model_dump"):
        data = data.model_dump()

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )