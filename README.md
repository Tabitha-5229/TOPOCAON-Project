---
title: TOPOCAON Leaf Check
emoji: 🌿
colorFrom: green
colorTo: green
sdk: streamlit
app_file: app.py
pinned: false
---

# TOPOCAON Leaf Check

A small website where you add a photo of one leaf (potato, tomato, cassava or onion) and get the most likely
health problem, a plain description and what to do next. It uses the YOLO11n models from the project.

## What is in this folder

| File | What it does |
|---|---|
| app.py | The web page (layout, tabs, result card). Edit TEAM and INSTITUTION at the top. |
| engine.py | Loads the models and turns a photo into a ranked result. |
| disease_info.py | The descriptions and advice shown for each disease. Edit the wording here. |
| models/ | Put the four trained model files here. |
| requirements.txt, packages.txt | What the server must install. |

## Step 1: add the model files

Open Google Drive, go to `runs`, and for each crop download this file:

`runs/<crop>_health_yolo/weights/best.pt`

Rename and place them like this:

```
models/potato.pt
models/tomato.pt
models/cassava.pt
models/onion.pt
```

## Step 2: try it on your own computer

Open a terminal in this folder (in PyCharm: View, Tool Windows, Terminal) and run:

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

A browser tab opens at http://localhost:8501. Choose a crop, upload a leaf photo and check the result.

## Step 3: put it online for free (Hugging Face Spaces)

1. Create a free account at huggingface.co.
2. Click New, then Space. Give it a name, choose **Streamlit** as the SDK, keep the free CPU hardware, and make it Public.
3. Open the Space, go to Files, then Add file, then Upload files. Upload everything in this folder, including
   packages.txt, the `.streamlit` folder and the four model files inside a `models` folder.
4. Wait a few minutes for the build. Your site appears at the Space link, which you can share.

If the build fails with an error about libGL, check that packages.txt was uploaded. A free Space goes to sleep when
nobody uses it, so the first visit after a break takes longer to load.

## Notes

* The models were trained on clear single leaf photos, so photos taken in the field can be less accurate.
* The onion model only says healthy or unhealthy.
* The text in the Accuracy tab comes from the dissertation tables. Update it if your final numbers change.
