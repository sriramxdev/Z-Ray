import json

with open("1_Xray.ipynb", "r") as f:
    nb = json.load(f)

for cell in nb["cells"]:
    if cell["cell_type"] == "code":
        source = cell["source"]
        for i, line in enumerate(source):
            if "return cv2.cvtColor(img_clahe, cv2.COLOR_GRAY2RGB)" in line:
                source[i] = "            img_rgb = cv2.cvtColor(img_clahe, cv2.COLOR_GRAY2RGB)\n            return np.transpose(img_rgb, (2, 0, 1)).astype(np.float32) / 255.0\n"
            elif "return np.zeros((self.image_size, self.image_size, 3), dtype=np.uint8)" in line:
                source[i] = "            img_rgb = np.zeros((self.image_size, self.image_size, 3), dtype=np.uint8)\n            return np.transpose(img_rgb, (2, 0, 1)).astype(np.float32) / 255.0\n"

        cell["source"] = source

with open("1_Xray.ipynb", "w") as f:
    json.dump(nb, f, indent=1)
