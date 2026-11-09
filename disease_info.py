"""Plain language information shown next to each prediction.

Each entry matches a class name the YOLO models were trained on. Matching ignores
case, spaces, underscores and the crop prefix (for example "Tomato___Early_blight").
The advice is general guidance, not a prescription. Edit the text freely.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Info:
    title: str
    status: str  # "healthy", "disease"
    about: str
    signs: str
    action: str
    keys: List[str] = field(default_factory=list)  # substrings of the normalised class name
    exact: Optional[str] = None  # normalised class name that must match exactly


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def _strip_crop(class_name: str) -> str:
    return class_name.split("___")[-1]


HEALTHY_ABOUT = "No sign of disease was found on this leaf."
HEALTHY_SIGNS = "Even green colour, no spots, no curling, no mould and no webbing."
HEALTHY_ACTION = (
    "Keep up good practice: water at the base of the plant, give plants space for airflow, "
    "and check the crop regularly so problems are caught early."
)

INFO = {
    "Potato": [
        Info(
            "Potato early blight", "disease",
            "A fungal disease (Alternaria solani) that mostly attacks older leaves and slowly weakens the plant.",
            "Dark brown spots with rings inside them, like a target. The leaf around a spot often turns yellow.",
            "Remove badly affected leaves, avoid watering over the leaves, rotate crops each season and keep plants well fed. "
            "Ask your local extension officer which fungicide is approved in your area.",
            keys=["earlyblight"],
        ),
        Info(
            "Potato late blight", "disease",
            "A fast spreading disease (Phytophthora infestans) that can destroy a field in days when the weather is cool and wet.",
            "Dark, wet looking blotches that spread quickly. A white fuzzy growth may appear under the leaf in humid weather.",
            "Act quickly. Remove and destroy infected plants (do not compost them), avoid wetting the leaves, "
            "and do not save tubers from infected plants. Contact your extension officer for approved sprays.",
            keys=["lateblight"],
        ),
        Info("Healthy potato leaf", "healthy", HEALTHY_ABOUT, HEALTHY_SIGNS, HEALTHY_ACTION, exact="healthy"),
    ],
    "Tomato": [
        Info(
            "Tomato bacterial spot", "disease",
            "A bacterial disease (Xanthomonas species) that spreads in splashing water and on wet leaves.",
            "Small, dark, greasy looking spots on the leaves, sometimes with a yellow edge. Fruit can also get rough spots.",
            "Use clean seed, avoid working among wet plants, remove plant debris and rotate crops. "
            "Copper based sprays can slow it down, so ask your extension officer.",
            keys=["bacterialspot"],
        ),
        Info(
            "Tomato early blight", "disease",
            "A fungal disease (Alternaria solani) that usually starts on the lowest, oldest leaves.",
            "Brown spots with rings inside them, like a target, and yellowing around the spots.",
            "Remove affected lower leaves, mulch to stop soil splashing, water at the base and rotate crops.",
            keys=["earlyblight"],
        ),
        Info(
            "Tomato late blight", "disease",
            "A fast spreading disease (Phytophthora infestans) that thrives in cool, wet weather.",
            "Large grey green or dark blotches that look soaked with water. White mould may show under the leaf.",
            "Act quickly. Remove and destroy affected plants, keep leaves dry and ask your extension officer about approved sprays.",
            keys=["lateblight"],
        ),
        Info(
            "Tomato leaf mould", "disease",
            "A fungal disease (Passalora fulva) that is common where the air is humid and the plants are crowded.",
            "Pale green or yellow patches on the top of the leaf, with a velvety olive or brown mould underneath.",
            "Improve airflow by spacing and pruning, reduce humidity, and avoid wetting the leaves.",
            keys=["leafmold", "leafmould"],
        ),
        Info(
            "Tomato Septoria leaf spot", "disease",
            "A fungal disease that starts on lower leaves and moves up the plant in wet weather.",
            "Many small round spots with dark edges and grey or tan centres, often with tiny black dots in the middle.",
            "Remove infected lower leaves, avoid overhead watering, clear plant debris and rotate crops.",
            keys=["septoria"],
        ),
        Info(
            "Tomato spider mites", "disease",
            "Tiny pests (two spotted spider mites) that feed on the underside of leaves, mostly in hot, dry weather.",
            "Fine yellow speckles on the leaf, thin webbing underneath, and leaves that turn bronze and dry out.",
            "Spray water on the underside of the leaves, remove heavily infested leaves and keep plants from drying out. "
            "Ask your extension officer about safe control options.",
            keys=["spidermite"],
        ),
        Info(
            "Tomato target spot", "disease",
            "A fungal disease (Corynespora cassiicola) that is favoured by warm, humid conditions.",
            "Brown spots with rings inside them and a yellow edge. Spots can also appear on the fruit.",
            "Remove affected leaves, improve airflow, avoid overhead watering and rotate crops.",
            keys=["targetspot"],
        ),
        Info(
            "Tomato yellow leaf curl virus", "disease",
            "A virus spread by whiteflies. There is no cure once a plant is infected.",
            "Leaves curl upward, edges turn yellow, new leaves stay small and the plant looks stunted.",
            "Remove infected plants, control whiteflies (for example with nets), and use resistant varieties next season.",
            keys=["yellowleafcurl"],
        ),
        Info(
            "Tomato mosaic virus", "disease",
            "A virus that spreads by touch, on tools and hands, and sometimes in seed. There is no cure.",
            "A patchy pattern of light and dark green on the leaves, and leaves that look twisted or narrow.",
            "Remove infected plants, wash hands and tools after handling plants, and use clean seed.",
            keys=["mosaicvirus"],
        ),
        Info("Healthy tomato leaf", "healthy", HEALTHY_ABOUT, HEALTHY_SIGNS, HEALTHY_ACTION, exact="healthy"),
    ],
    "Cassava": [
        Info(
            "Cassava bacterial blight", "disease",
            "A bacterial disease that spreads through infected cuttings and rain splash.",
            "Angular spots that look soaked with water, leaf blight and wilting, and sticky gum on the stems.",
            "Plant clean cuttings, use resistant varieties, remove and burn infected plants and rotate fields. "
            "Report outbreaks to your extension service.",
            keys=["bacterialblight"],
        ),
        Info(
            "Cassava brown streak disease", "disease",
            "A virus disease spread by whiteflies and by infected cuttings. It can damage the roots even when the leaves look mild.",
            "Yellow feathery patches along the leaf veins, brown marks on young stems, and brown corky patches inside the roots.",
            "Use clean cuttings and tolerant varieties, remove infected plants early and report to your extension service.",
            keys=["brownstreak"],
        ),
        Info(
            "Cassava green mottle", "disease",
            "A virus type disease that changes the colour pattern of the leaf and slows plant growth.",
            "Patches of pale and dark green on the leaf, sometimes with distortion and a stunted plant.",
            "Use clean cuttings, remove infected plants and ask your extension officer to confirm the disease, "
            "because several cassava diseases look alike.",
            keys=["greenmottle"],
        ),
        Info(
            "Cassava mosaic disease", "disease",
            "A virus disease spread by whiteflies and by infected cuttings. It is one of the most important cassava diseases.",
            "A yellow and green mosaic pattern, twisted or smaller leaves, and a stunted plant.",
            "Plant mosaic resistant varieties and clean cuttings, and remove infected plants early.",
            keys=["mosaicdisease"],
        ),
        Info("Healthy cassava leaf", "healthy", HEALTHY_ABOUT, HEALTHY_SIGNS, HEALTHY_ACTION, exact="healthy"),
    ],
    "Onion": [
        Info(
            "Unhealthy onion leaf", "disease",
            "The onion model only separates healthy leaves from unhealthy ones. It does not say which disease or problem is present.",
            "Spots, patches, tip dieback, unusual colour or other damage on the leaf.",
            "Look closely at the plant. Common causes include fungal leaf diseases such as purple blotch and Stemphylium leaf blight, "
            "downy mildew, pests and lack of nutrients. Ask your extension officer to identify the exact cause.",
            keys=["unhealthy"],
        ),
        Info("Healthy onion leaf", "healthy", HEALTHY_ABOUT, HEALTHY_SIGNS, HEALTHY_ACTION, exact="healthy"),
    ],
}

GENERIC = Info(
    "Result not recognised", "disease",
    "The model returned a class this app has no description for.",
    "",
    "Ask your extension officer to check the plant.",
)


def lookup(crop: str, class_name: str) -> Info:
    """Return the description for a class predicted by the model for the given crop."""
    norm = _norm(_strip_crop(class_name))
    entries = INFO.get(crop, [])
    for e in entries:
        if e.exact and norm == e.exact:
            return e
    for e in entries:
        if any(k in norm for k in e.keys):
            return e
    return GENERIC
