from typing import List, Dict, Any
import torch
import json
import imageio

def climb_to_img(climb: Dict[str, Any]):
    assert "start_holds" in climb
    assert "middle_holds" in climb
    assert "finish_holds" in climb

    img = torch.zeros((18, 11, 3)) # channels ordered: start holds, middle holds, finish holds
    for i, hold_name in enumerate(["start_holds", "middle_holds", "finish_holds"]):
        for hold in climb[hold_name]:
            col = ord(hold[0]) - 65
            row = hold[1] - 1
            img[row, col, i] = 1

    return img

class ImageDataset(torch.utils.data.Dataset):
    def __init__(self, path: str):
        with open(path, "r") as f:
            self.data: List[Dict[str, Any]] = json.load(f)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx: int):
        climb = self.data[idx]
        return climb_to_img(climb)


if __name__ == "__main__":
    dataset = ImageDataset("data/2016_data_clean.json")
    for i in range(10):
        img = dataset[i]
        imageio.imsave(f"climb_{i}.png", img)



