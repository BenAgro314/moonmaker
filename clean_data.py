import json

if __name__ == "__main__":
    with open("data/2016_data.json", "r") as f:
        dirty_data = json.load(f)
    print(f"Number of dirty climbs: {len(dirty_data)}")
    clean_data = []
    for climb in dirty_data:
        if "raw_text" in climb:
            continue
        clean_data.append(climb)
    print(f"Number of clean climbs: {len(clean_data)}")
    with open("data/2016_data_clean.json", "w") as f:
        json.dump(clean_data, f, indent = 4)