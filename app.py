"""TOPOCAON Leaf Check: upload a leaf photo and get a likely diagnosis.

Run locally:   streamlit run app.py
"""
from __future__ import annotations

import datetime

import streamlit as st
from PIL import Image

import engine
from disease_info import lookup

# ---- Edit these two lines for your own project details ----------------------
TEAM = "Add your names here"
INSTITUTION = "Add your school and department here"
# -----------------------------------------------------------------------------

st.set_page_config(page_title="TOPOCAON Leaf Check", page_icon="🌿", layout="centered")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Literata:wght@500;700&family=Public+Sans:wght@400;600&display=swap');
.stApp, .stApp p, .stApp li, .stApp label, .stApp span { font-family: 'Public Sans', sans-serif; }
.stApp h1, .stApp h2, .stApp h3 { font-family: 'Literata', serif; color: #16231C; }
.hero { padding: 0.5rem 0 1.25rem 0; }
.hero h1 { font-size: 2.2rem; margin: 0 0 0.4rem 0; line-height: 1.15; }
.hero p { font-size: 1.05rem; color: #3d4f44; max-width: 34rem; margin: 0; }
.result { background: #ffffff; border-left: 6px solid var(--c); border-radius: 6px; padding: 1rem 1.25rem; margin: 1rem 0 0.75rem 0; }
.result.healthy { --c: #2E7D4F; }
.result.disease { --c: #A63D2F; }
.result.unsure  { --c: #B7791F; }
.result .small { color: #4a5a50; font-size: 0.95rem; margin: 0; }
.result h2 { margin: 0.15rem 0 0.3rem 0; font-size: 1.6rem; }
.note { color: #4a5a50; font-size: 0.9rem; }
</style>
""",
    unsafe_allow_html=True,
)

DISCLAIMER = (
    "This is a student research prototype. It can be wrong, so treat the result as a first guide and "
    "confirm with an agricultural extension officer before you treat a crop."
)


def show_hero() -> None:
    st.markdown(
        """
<div class="hero">
<h1>TOPOCAON Leaf Check</h1>
<p>Add a photo of one leaf from a potato, tomato, cassava or onion plant. You get the most likely
health problem and what to do next.</p>
</div>
""",
        unsafe_allow_html=True,
    )


def build_report(crop: str, result: engine.Result) -> str:
    lines = [
        "TOPOCAON Leaf Check report",
        f"Date: {datetime.datetime.now():%Y-%m-%d %H:%M}",
        f"Crop: {crop}",
    ]
    if result.verdict == "none":
        lines.append("Result: no clear result")
    else:
        top = result.ranked[0]
        info = lookup(crop, top.class_name)
        lines += [
            f"Result: {info.title} ({round(top.score * 100)}% confidence)",
            f"What it is: {info.about}",
            f"What to look for: {info.signs}",
            f"What to do next: {info.action}",
            "Other possibilities:",
        ]
        for p in result.ranked[1:3]:
            lines.append(f"  {lookup(crop, p.class_name).title}: {round(p.score * 100)}%")
    lines += ["", DISCLAIMER]
    return "\n".join(lines)


def render_result(crop: str, result: engine.Result) -> None:
    if result.verdict == "none":
        st.markdown(
            """
<div class="result unsure">
<p class="small">Result</p>
<h2>No clear result</h2>
<p class="small">The model could not find a leaf it recognises. Retake the photo with one leaf filling the
frame, on a plain background, in good light.</p>
</div>
""",
            unsafe_allow_html=True,
        )
        return

    top = result.ranked[0]
    info = lookup(crop, top.class_name)
    css = "unsure" if result.verdict == "uncertain" else info.status
    pct = round(top.score * 100)
    st.markdown(
        f"""
<div class="result {css}">
<p class="small">Most likely for {crop.lower()}</p>
<h2>{info.title}</h2>
<p class="small">{pct}% confidence</p>
</div>
""",
        unsafe_allow_html=True,
    )
    if result.verdict == "uncertain":
        st.warning("The model is not sure about this one. Retake the photo, or treat the result as a guess.")

    st.markdown("**What it is**")
    st.write(info.about)
    if info.signs:
        st.markdown("**What to look for**")
        st.write(info.signs)
    st.markdown("**What to do next**")
    st.write(info.action)

    others = result.ranked[1:3]
    if others:
        st.markdown("**Other possibilities**")
        for p in others:
            st.progress(min(max(p.score, 0.0), 1.0), text=f"{lookup(crop, p.class_name).title}: {round(p.score * 100)}%")

    st.download_button(
        "Save this result as a text file",
        data=build_report(crop, result),
        file_name=f"leaf_check_{crop.lower()}.txt",
        mime="text/plain",
    )
    st.caption(DISCLAIMER)


def tab_check() -> None:
    crop = st.radio("Which crop is the leaf from?", engine.CROPS, horizontal=True)

    if not engine.model_available(crop):
        st.error(
            f"The {crop.lower()} model file is missing. Copy it to models/{crop.lower()}.pt and restart the app "
            "(see the README for where to find it)."
        )
        return

    with st.expander("Tips for a good photo"):
        st.write(
            "Use one leaf and let it fill most of the frame. Put it on a plain background, such as a sheet of paper "
            "or your hand, in daylight. Keep the photo sharp and avoid shadows across the leaf. "
            "The models learned from clear single leaf photos, so photos of a whole field or many leaves "
            "at once will be less reliable."
        )

    source = st.radio("How do you want to add the photo?", ["Upload a photo", "Take a photo"], horizontal=True)
    if source == "Upload a photo":
        file = st.file_uploader("Choose a photo of a leaf", type=["jpg", "jpeg", "png"], key="upload")
    else:
        file = st.camera_input("Take a photo of the leaf", key="camera")

    if file is None:
        st.info("Add a photo to see the result.")
        return

    try:
        image = Image.open(file)
        image.load()
    except Exception:
        st.error("That file could not be read as an image. Try a JPG or PNG photo.")
        return

    show_box = st.checkbox("Show the detection box on the photo", value=False)

    try:
        with st.spinner("Checking the leaf"):
            result = engine.predict(crop, image, draw_box=True)
    except Exception as exc:  # keep the page alive and say what happened
        st.error(f"The model could not run: {exc}")
        return

    shown = engine.prepare_image(image)
    if show_box and result.annotated is not None:
        shown = Image.fromarray(result.annotated)
    shown.thumbnail((900, 900))
    st.image(shown, caption="Your photo")

    render_result(crop, result)
    st.caption(f"Checked in {result.inference_ms:.0f} ms")


def tab_how() -> None:
    st.subheader("How it works")
    st.markdown(
        """
1. You choose the crop and add a photo of one leaf.
2. The app sends the photo to a small YOLO11n model that was trained for that crop on thousands of labelled leaf photos.
3. The model gives each possible condition a score. The highest score is shown as the result, and the next two are listed as other possibilities.
4. The page adds a plain description of the condition and what to do next.
"""
    )
    st.markdown("**What the score means**")
    st.write(
        "The score is the model's own confidence, not a guarantee. When two diseases look alike, both can score high. "
        "Below 35% the app says there is no clear result, and between 35% and 60% it asks you to retake the photo."
    )
    st.markdown("**What the app cannot do**")
    st.write(
        "It was trained mostly on single leaves photographed against plain backgrounds, so photos taken in the field, "
        "with soil, hands or many leaves in view, can give worse results. It cannot see roots, stems or fruit. "
        "Cassava is the hardest crop for the models and has the lowest accuracy. "
        "The onion model only separates healthy from unhealthy leaves."
    )


def tab_accuracy() -> None:
    st.subheader("How accurate is it?")
    st.write(
        "These figures come from the project dissertation. Accuracy is the share of leaves given the right label. "
        "For YOLO the figure is the mean recall across classes."
    )
    st.markdown(
        """
| Crop | Classes | Random Forest | VGG16 CNN | YOLO11n (used here) |
|---|---|---|---|---|
| Potato | 3 | 94.84% | 92.33% | 100.0% |
| Tomato | 10 (7 for Random Forest) | 87.34% | 88.80% | 98.8% |
| Cassava | 5 | 61.43% | 65.32% | 80.4% |
| Onion | 2 | 95.87% | 87.25% | 94.1% |
"""
    )
    st.markdown(
        '<p class="note">The models were tested on different splits of the data, so compare the columns with care. '
        "The tomato Random Forest used 7 classes instead of 10. YOLO onion and cassava figures use the validation "
        "split.</p>",
        unsafe_allow_html=True,
    )


def tab_about() -> None:
    st.subheader("About TOPOCAON")
    st.write(
        "TOPOCAON stands for the four crops in this study: tomato, potato, cassava and onion. "
        "The project compares three ways of recognising leaf diseases from photos: a Random Forest on hand made "
        "image features, a VGG16 convolutional neural network, and a YOLO11n object detector. "
        "This app uses YOLO11n, which scored highest for potato, tomato and cassava."
    )
    st.markdown(f"**Team:** {TEAM}")
    st.markdown(f"**Institution:** {INSTITUTION}")
    st.caption(DISCLAIMER)


def main() -> None:
    show_hero()
    t1, t2, t3, t4 = st.tabs(["Check a leaf", "How it works", "Accuracy", "About"])
    with t1:
        tab_check()
    with t2:
        tab_how()
    with t3:
        tab_accuracy()
    with t4:
        tab_about()


main()
