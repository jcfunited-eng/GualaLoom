"""
DSF-AI Service — FastAPI Application
=====================================
Three endpoints:
  POST /api/v1/analyze        — CSV upload → kernel → JSON report + LLM narrative
  POST /api/v1/cluster        — element + N → screener → properties JSON
  POST /api/v1/cluster/screen — batch screening with constraints

TRADE SECRET — kernel internals never leave the server.
"""

import os
import sys
import io
import csv
import time
import hashlib as _hashlib
import traceback


def deterministic_motif_id(name):
    """1.5: Deterministic motif ID — replaces hash()%1000."""
    return int(_hashlib.md5(name.encode()).hexdigest()[:8], 16) % 10000


def decode_image_bytes(img_bytes):
    """H5a: Shared HEIC-capable image decode for every image route.
    Returns (full_image, gray_grid_64x64, orig_w, orig_h) or raises."""
    try:
        import pillow_heif
        pillow_heif.register_heif_opener()
    except ImportError:
        pass
    from PIL import Image
    import io as _io
    img_full = Image.open(_io.BytesIO(img_bytes))
    if img_full.mode not in ('RGB', 'L'):
        img_full = img_full.convert('RGB')
    orig_w, orig_h = img_full.size
    img_gray = img_full.convert('L').resize((64, 64))
    grid = np.array(img_gray, dtype=np.float64) / 255.0
    return img_full, grid, orig_w, orig_h
from typing import Optional, List, Dict

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import BaseModel

# Add project root to path so we can import uf_core and tools
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from dsf_ai_service.kernel_runner import run_analysis
from dsf_ai_service.integrity import initialize_integrity, get_integrity_status
from dsf_ai_service.cluster_screener import (
    predict_cluster,
    screen_clusters,
    find_thermocouple_pairs,
)
from dsf_ai_service.narrator import narrate_results
from dsf_ai_service.cff_discovery import run_discovery, verify_candidate

app = FastAPI(
    title="DSF-AI Structural Analysis Service",
    version="1.0.0",
    description="Universal structural analysis for any measurement-vs-stimulus data.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')


@app.get("/")
async def index():
    return FileResponse(os.path.join(STATIC_DIR, 'index.html'))


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# ════════════════════════════════════════════════════════════════
# Endpoint 1: CSV structural analysis
# ════════════════════════════════════════════════════════════════

@app.post("/api/v1/analyze")
async def analyze_csv(
    file: UploadFile = File(...),
    context: Optional[str] = Form(None),
):
    """
    Upload a two-column CSV (stimulus, measurement).
    Returns structural analysis with transitions, precursors,
    regime map, and LLM narrative.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(400, "File must be a .csv")

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(400, "File too large (max 10 MB)")

    try:
        text = content.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(400, "File must be UTF-8 encoded")

    # Parse CSV
    reader = csv.reader(io.StringIO(text))
    pairs = []
    for row in reader:
        if not row or len(row) < 2:
            continue
        try:
            stimulus = float(row[0].strip())
            measurement = float(row[1].strip())
            pairs.append((stimulus, measurement))
        except ValueError:
            continue  # skip header or non-numeric rows

    if len(pairs) < 5:
        raise HTTPException(400, "Need at least 5 data points")
    if len(pairs) > 500000:
        raise HTTPException(400, "Too many data points (max 500,000)")

    t0 = time.time()

    # Run kernel (TRADE SECRET — internals stay here)
    try:
        report = run_analysis(pairs)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, f"Kernel error: {str(e)}")

    # Generate LLM narrative
    try:
        narrative = narrate_results(report, context=context)
        report['narrative'] = narrative
    except Exception:
        report['narrative'] = None  # LLM failure is non-fatal

    report['compute_time_s'] = round(time.time() - t0, 3)

    return report


# ════════════════════════════════════════════════════════════════
# Endpoint 2: Single cluster prediction
# ════════════════════════════════════════════════════════════════

class ClusterRequest(BaseModel):
    element: str
    N_atoms: int = 13
    temperature_K: float = 300
    lattice: str = "cubic"


@app.post("/api/v1/cluster")
async def cluster_predict(req: ClusterRequest):
    """Predict properties for a single nanoparticle cluster."""
    try:
        result = predict_cluster(
            req.element, req.N_atoms, req.temperature_K, req.lattice
        )
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))
    return result


# ════════════════════════════════════════════════════════════════
# Endpoint 3: Batch screening with constraints
# ════════════════════════════════════════════════════════════════

class ScreenConstraints(BaseModel):
    moment_min_uB: Optional[float] = None
    seebeck_min_uV_K: Optional[float] = None
    EA_min_eV: Optional[float] = None
    gap_min_eV: Optional[float] = None


class ScreenRequest(BaseModel):
    elements: Optional[List[str]] = None
    N_atoms: Optional[List[int]] = None
    constraints: Optional[ScreenConstraints] = None


@app.post("/api/v1/cluster/screen")
async def cluster_screen(req: ScreenRequest):
    """Batch screen clusters against property constraints."""
    t0 = time.time()
    try:
        result = screen_clusters(
            elements=req.elements,
            n_atoms_list=req.N_atoms,
            constraints=req.constraints.model_dump() if req.constraints else None,
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))
    result['compute_time_ms'] = round((time.time() - t0) * 1000, 1)
    return result


# ════════════════════════════════════════════════════════════════
# Endpoint 4: Thermocouple pair finder
# ════════════════════════════════════════════════════════════════

class ThermocoupleRequest(BaseModel):
    N_atoms: int = 13
    min_delta_S: float = 50


@app.post("/api/v1/cluster/thermocouple")
async def thermocouple(req: ThermocoupleRequest):
    """Find optimal thermocouple pairs from cluster Seebeck predictions."""
    try:
        result = find_thermocouple_pairs(req.N_atoms, req.min_delta_S)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))
    return result


# ════════════════════════════════════════════════════════════════
# Endpoint 5: Hardware weight derivation (hidden, auth required)
# ════════════════════════════════════════════════════════════════

class HWDeriveRequest(BaseModel):
    calibration_table: Dict
    sensor_names: List[str]
    sensor_roles: Dict[str, str]
    sensor_label: str = "unknown sensor"
    camera_mode: bool = False
    background: Optional[Dict] = None


@app.post("/api/v1/hw/derive")
async def hw_derive(req: HWDeriveRequest):
    """
    Derive coupling weights + BSIL thresholds from sensor calibration data.
    Hidden endpoint — not linked from any public page.
    Supports IR distance sensors (axial/lateral roles) and
    camera vision features (structural role).
    """
    t0 = time.time()
    try:
        from tools.derive_sppu_weights import (
            derive_weights, format_verilog, format_json,
            format_bsil_thresholds, build_field_series, run_kernel,
            dsf_to_coupling_profile, derive_bsil_thresholds,
        )
        import numpy as np

        # Convert string keys back to proper types
        cal_table = {}
        for k, v in req.calibration_table.items():
            if k == 'inf' or k == 'Inf':
                cal_table['inf'] = tuple(
                    None if x is None else float(x) for x in v
                )
            else:
                cal_table[float(k)] = tuple(
                    None if x is None else float(x) for x in v
                )

        # Check if any role is "structural" (camera mode)
        has_structural = any(r == 'structural' for r in req.sensor_roles.values())

        if not has_structural:
            # Standard IR mode — use existing derive_weights
            weights, bsil_thresholds, metadata = derive_weights(
                calibration_table=cal_table,
                sensor_names=req.sensor_names,
                sensor_roles=req.sensor_roles,
                sensor_label=req.sensor_label,
            )
            verilog = format_verilog(weights, metadata)
            verilog += "\n\n" + format_bsil_thresholds(bsil_thresholds)
            json_str = format_json(weights, metadata)
        else:
            # Camera / structural mode
            # Run each feature through the kernel independently
            from tools.derive_sppu_weights import ingest_calibration_table

            sensor_data = ingest_calibration_table(cal_table)
            background = getattr(req, 'background', None)
            if hasattr(req, '__dict__'):
                background = req.__dict__.get('background', None)

            profiles = {}
            all_boundaries = {}
            bsil_thresholds = {}
            baselines = {}

            for i, name in enumerate(req.sensor_names):
                key = f'sensor_{i}'
                if key not in sensor_data or not sensor_data[key]:
                    continue

                # Get baseline from 'inf' entry or background
                for stim, readings in cal_table.items():
                    if stim == 'inf':
                        if readings[i] is not None:
                            baselines[name] = float(readings[i])
                        break

                series = build_field_series(sensor_data[key], name)
                kernel_out = run_kernel(series)
                profile = dsf_to_coupling_profile(kernel_out['dsf'])
                profiles[name] = profile
                all_boundaries[name] = kernel_out['boundaries']

                baseline = baselines.get(name, 0)
                thresholds = derive_bsil_thresholds(
                    kernel_out['boundaries'], baseline
                )
                bsil_thresholds[name] = thresholds

            # Build camera-specific Verilog output
            verilog_lines = []
            verilog_lines.append("// ---- Camera Vision Coupling Weights ----")
            verilog_lines.append(f"// Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            verilog_lines.append(f"// Sensor: {req.sensor_label}")
            verilog_lines.append(f"// Features: {', '.join(req.sensor_names)}")
            verilog_lines.append(f"// Role: structural (vision)")
            verilog_lines.append("")

            for name, profile in profiles.items():
                cs = profile['coupling_strength']
                mw = profile['momentum_weight']
                unc = profile['uncertainty']
                bm = profile['breathing_magnitude']
                rr = profile['reversal_rate']

                # Base weight from DSF profile
                raw = cs * (1.0 + bm) * (1.0 - unc * 0.5) * (1.0 - rr * 0.3)
                base_w = int(np.clip(raw * 40, 5, 40))

                # Confidence coupling (primary for structural features)
                conf = 1.0 - unc
                stability = 1.0 - min(bm, 1.0) * 0.5
                conf_w = int(np.clip(conf * stability * 25, 5, 30))

                # Steer coupling (derived — may be zero if symmetric)
                # Use D_k std as proxy for directional asymmetry
                steer_w = int(np.clip(cs * 10, 0, 15))

                # Speed coupling (approach when recognized)
                speed_w = int(np.clip(cs * mw * 20, 0, 20))

                baseline = baselines.get(name, 0)
                # Dead zone: uncertainty * range
                dz = int(np.clip(unc * 50, 5, 100))

                verilog_lines.append(f"// {name}:")
                verilog_lines.append(f"//   coupling_strength = {cs:.4f}")
                verilog_lines.append(f"//   momentum_weight   = {mw:.4f}")
                verilog_lines.append(f"//   uncertainty        = {unc:.4f}")
                verilog_lines.append(f"//   breathing          = {bm:.4f}")
                verilog_lines.append(f"//   reversal_rate      = {rr:.4f}")
                verilog_lines.append(f"parameter [7:0] BASELINE_{name.upper()} = 8'd{int(baseline)};")
                verilog_lines.append(f"parameter [7:0] DEADZONE_{name.upper()} = 8'd{dz};")
                verilog_lines.append(f"parameter [7:0] W_CONFIDENCE_{name.upper()} = 8'd{conf_w};")
                verilog_lines.append(f"parameter signed [7:0] W_STEER_{name.upper()} = 8'sd{steer_w};")
                verilog_lines.append(f"parameter [7:0] W_SPEED_{name.upper()} = 8'd{speed_w};")
                verilog_lines.append("")

            verilog = "\n".join(verilog_lines)
            verilog += "\n\n" + format_bsil_thresholds(bsil_thresholds)

            # JSON output
            import json as json_mod
            json_out = {
                'sensor_label': req.sensor_label,
                'mode': 'camera_structural',
                'features': req.sensor_names,
                'baselines': baselines,
                'profiles': profiles,
                'bsil_thresholds': bsil_thresholds,
            }
            json_str = json_mod.dumps(json_out, indent=2, default=str)

        # Build profiles summary
        profiles_lines = []
        dsf_profiles = profiles if has_structural else metadata.get('dsf_profiles', {})
        for name, profile in dsf_profiles.items():
            profiles_lines.append(f"--- {name} ---")
            for k, v in profile.items():
                if isinstance(v, float):
                    profiles_lines.append(f"  {k}: {v:.4f}")
                else:
                    profiles_lines.append(f"  {k}: {v}")
            profiles_lines.append("")
        profiles_str = "\n".join(profiles_lines)

        return {
            'status': 'ok',
            'verilog': verilog,
            'json': json_str,
            'profiles': profiles_str,
            'compute_time_s': round(time.time() - t0, 3),
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))


# ════════════════════════════════════════════════════════════════
# Endpoint 6: CFF Discovery Algorithm
# ════════════════════════════════════════════════════════════════

class DiscoveryRequest(BaseModel):
    target_property: str = "RTSC"
    max_pressure_GPa: float = 0
    must_be_2D: bool = False
    must_be_gateable: bool = False
    exclude_families: Optional[List[str]] = None


@app.post("/api/v1/discover")
async def discover(req: DiscoveryRequest):
    """
    CFF Discovery Algorithm: given a target property,
    output the forced architectural class and ranked candidates.
    """
    t0 = time.time()
    try:
        result = run_discovery(
            target_property=req.target_property,
            max_pressure_GPa=req.max_pressure_GPa,
            must_be_2D=req.must_be_2D,
            must_be_gateable=req.must_be_gateable,
            exclude_families=req.exclude_families,
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))
    result['compute_time_ms'] = round((time.time() - t0) * 1000, 1)
    return result


class VerifyRequest(BaseModel):
    composition: str
    substrate: str
    target_property: str = "RTSC"


@app.post("/api/v1/discover/verify")
async def discover_verify(req: VerifyRequest):
    """
    Verify mode: check which CFF filters a specific
    candidate passes or fails.
    """
    try:
        result = verify_candidate(
            composition=req.composition,
            substrate=req.substrate,
            target_property=req.target_property,
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))
    return result


# ════════════════════════════════════════════════════════════════
# GualaLoom — substrate below, dialog above
# GUALALOOM-INTEGRATE-WC-2026-06-05
# ════════════════════════════════════════════════════════════════

import numpy as np
import json

# ════════════════════════════════════════════════════════════════
# GualaLoom v5 — Recall + Question Bucket + Honest Fallback
# GUALALOOM-V5-WC-2026-06-05
# ════════════════════════════════════════════════════════════════

from dsf_ai_service.v4.gualaloom_v5_engine import (
    Guala, CORPUS, CorpusItem, SensoryItem, PictureItem, VideoItem,
)
from fastapi.responses import StreamingResponse

_guala = None
_persist_every = 50   # save every N exchanges
_exchange_count = 0
STATE_DIR = "state"

# v7: Seed corpora — lines for autonomous reading
SEED_CORPORA = {
    "see_spot_run": {
        "title": "See Spot Run",
        "lines": [
            "see spot", "see spot run", "run spot run",
            "see jane", "see jane run", "run jane run",
            "see spot and jane", "spot and jane run",
            "see the dog run", "the dog is spot",
            "spot is a good dog", "jane has a dog",
            "spot can run fast", "run run run",
        ],
    },
    "goodnight_moon": {
        "title": "Goodnight Moon",
        "lines": [
            "in the great green room", "there was a telephone",
            "and a red balloon", "and a picture of the cow jumping over the moon",
            "goodnight room", "goodnight moon", "goodnight cow jumping over the moon",
            "goodnight light", "goodnight red balloon",
            "goodnight stars", "goodnight air", "goodnight noises everywhere",
        ],
    },
    "green_eggs": {
        "title": "Green Eggs and Ham",
        "lines": [
            "i am sam", "sam i am", "do you like green eggs and ham",
            "i do not like them sam i am", "i do not like green eggs and ham",
            "would you like them here or there",
            "i would not like them here or there",
            "i would not like them anywhere",
            "not in a house", "not with a mouse",
            "not in a box", "not with a fox",
            "i do not like green eggs and ham", "i do not like them sam i am",
            "you do not like them so you say", "try them and you may",
            "i like green eggs and ham", "i do i like them sam i am",
        ],
    },
    "mother_goose": {
        "title": "Mother Goose Rhymes",
        "lines": [
            "twinkle twinkle little star", "how i wonder what you are",
            "up above the world so high", "like a diamond in the sky",
            "mary had a little lamb", "its fleece was white as snow",
            "and everywhere that mary went", "the lamb was sure to go",
            "humpty dumpty sat on a wall", "humpty dumpty had a great fall",
            "jack and jill went up the hill", "to fetch a pail of water",
            "baa baa black sheep", "have you any wool",
            "yes sir yes sir", "three bags full",
            "one two three four five", "once i caught a fish alive",
            "six seven eight nine ten", "then i let it go again",
            "hey diddle diddle", "the cat and the fiddle",
            "the cow jumped over the moon",
            "the little dog laughed to see such sport",
            "and the dish ran away with the spoon",
        ],
    },
}

# v7 corpora expansion — GUALALOOM-V7-CORPORA-EXPANSION-WC-2026-06-07
# Original sentences capturing vocabulary and structure patterns
# from age-appropriate reading material.

SEED_CORPORA["hungry_caterpillar"] = {
    "title": "The Hungry Caterpillar",
    "lines": [
        "on monday the caterpillar ate one apple",
        "on tuesday the caterpillar ate two pears",
        "on wednesday the caterpillar ate three plums",
        "on thursday the caterpillar ate four strawberries",
        "on friday the caterpillar ate five oranges",
        "the caterpillar was very hungry",
        "the caterpillar ate and ate and ate",
        "one piece of cake", "one ice cream cone",
        "one pickle", "one slice of cheese",
        "one slice of salami", "one lollipop",
        "one piece of pie", "one sausage",
        "one cupcake", "one slice of watermelon",
        "the caterpillar had a stomachache",
        "the caterpillar ate one nice green leaf",
        "the caterpillar felt much better",
        "the caterpillar was not hungry anymore",
        "the caterpillar was a big fat caterpillar",
        "the caterpillar built a small house around himself",
        "the caterpillar stayed inside for more than two weeks",
        "the caterpillar pushed his way out",
        "the caterpillar was a beautiful butterfly",
    ],
}

SEED_CORPORA["brown_bear"] = {
    "title": "Brown Bear",
    "lines": [
        "brown bear brown bear what do you see",
        "i see a red bird looking at me",
        "red bird red bird what do you see",
        "i see a yellow duck looking at me",
        "yellow duck yellow duck what do you see",
        "i see a blue horse looking at me",
        "blue horse blue horse what do you see",
        "i see a green frog looking at me",
        "green frog green frog what do you see",
        "i see a purple cat looking at me",
        "purple cat purple cat what do you see",
        "i see a white dog looking at me",
        "white dog white dog what do you see",
        "i see a black sheep looking at me",
        "black sheep black sheep what do you see",
        "i see a goldfish looking at me",
        "goldfish goldfish what do you see",
        "i see children looking at me",
        "children children what do you see",
        "we see a brown bear and a red bird",
        "we see a yellow duck and a blue horse",
        "we see a green frog and a purple cat",
        "we see a white dog and a black sheep",
        "we see a goldfish and children",
        "that is what we see",
    ],
}

SEED_CORPORA["chicka_boom"] = {
    "title": "Letter Tree",
    "lines": [
        "a told b and b told c",
        "i will meet you at the top of the tree",
        "d e f g h i j k",
        "l m n o p q r s t",
        "u v w x y and z",
        "the whole alphabet up the tree",
        "but the tree could not hold them all",
        "and they all came tumbling down",
        "a skinned knee", "b a stubbed toe",
        "c said ouch", "d said oh no",
        "the sun came up and so did they",
        "back up the tree to play all day",
        "a b c d e f g",
        "h i j k l m n o p",
        "q r s t u v w",
        "x y z the tree is free",
    ],
}

SEED_CORPORA["wild_things"] = {
    "title": "Wild Things",
    "lines": [
        "the night max wore his wolf suit",
        "and made mischief of one kind and another",
        "his mother called him wild thing",
        "max said i will eat you up",
        "so he was sent to bed without eating anything",
        "that very night in his room a forest grew",
        "and grew and grew until the ceiling hung with vines",
        "and the walls became the world all around",
        "and an ocean tumbled by with a private boat for max",
        "and he sailed off through night and day",
        "and in and out of weeks",
        "and almost over a year",
        "to where the wild things are",
        "and when he came to the place where the wild things are",
        "they roared their terrible roars",
        "and gnashed their terrible teeth",
        "and rolled their terrible eyes",
        "and showed their terrible claws",
        "max said be still",
        "and tamed them with the magic trick",
        "of staring into their yellow eyes without blinking",
        "and they were frightened and called him the most wild thing of all",
        "and made him king of all wild things",
        "let the wild rumpus start",
        "now stop max said",
        "max the king of all wild things was lonely",
        "and wanted to be where someone loved him best of all",
        "max sailed back over a year",
        "and in and out of weeks and through a day",
        "and into the night of his very own room",
        "where he found his supper waiting for him",
        "and it was still hot",
    ],
}

SEED_CORPORA["corduroy"] = {
    "title": "Corduroy",
    "lines": [
        "corduroy is a bear who lives in a big store",
        "he sits on a shelf with many other animals",
        "a girl named lisa sees corduroy",
        "she says look there is the bear i always wanted",
        "her mother says not today dear",
        "he does not look new",
        "he has lost a button",
        "that night corduroy climbs down from the shelf",
        "i think i lost a button he says",
        "he searches the store all night",
        "he looks on the furniture",
        "he looks on the escalator",
        "he pulls a button on a mattress",
        "the mattress wobbles and corduroy falls",
        "a guard finds him and puts him back on the shelf",
        "the next morning lisa comes back",
        "she has saved her money",
        "she buys corduroy and takes him home",
        "she sews a button on his overalls",
        "i like you the way you are says lisa",
        "but you will be more comfortable with your button",
        "you must be a friend says corduroy",
        "i have always wanted a friend",
        "me too says lisa and she gives him a big hug",
    ],
}

SEED_CORPORA["frog_and_toad"] = {
    "title": "Frog and Toad",
    "lines": [
        "frog ran up the path to toads house",
        "he knocked on the front door",
        "toad toad said frog wake up it is spring",
        "i am not here said toad",
        "but toad said frog the sun is shining",
        "the snow is melting",
        "toad said go away i am not here",
        "frog walked into the house",
        "it was dark and all the shutters were closed",
        "toad where are you said frog",
        "toad was in bed with the blanket over his head",
        "toad i have a story to tell you said frog",
        "tell it tomorrow said toad",
        "frog sat close to toad",
        "i am glad you woke up said frog",
        "me too said toad",
        "shall we go for a walk asked frog",
        "yes let us go for a walk said toad",
        "they walked along the river together",
        "they found a fine place and sat down",
        "this is a good day said toad",
        "yes said frog it is the best day",
        "frog and toad were happy",
        "they sat there feeling the warm sun",
    ],
}

SEED_CORPORA["amelia_bedelia"] = {
    "title": "Amelia Bedelia",
    "lines": [
        "amelia bedelia went to work for the first time",
        "she found a list of things to do",
        "the list said change the towels",
        "amelia bedelia got scissors and cut the towels",
        "now they are changed she said",
        "the list said dust the furniture",
        "she put dusting powder on every piece",
        "the list said draw the drapes",
        "amelia bedelia sat down and drew a picture of the drapes",
        "the list said put the lights out",
        "she took every light outside and put them on the clothesline",
        "the list said dress the chicken",
        "amelia bedelia found some cloth and dressed the chicken in it",
        "the list said measure two cups of rice",
        "she took a ruler and measured each cup",
        "amelia bedelia said i do exactly what they tell me to do",
        "she tried very hard to do everything right",
        "she made a beautiful pie",
        "everyone loved the pie so much",
        "they forgave all the mix ups",
        "you are the best pie maker in the world they said",
        "amelia bedelia smiled",
    ],
}

SEED_CORPORA["counting_book"] = {
    "title": "Counting Book",
    "lines": [
        "one sun in the sky",
        "two eyes on my face",
        "three kittens playing",
        "four wheels on a car",
        "five fingers on a hand",
        "six legs on a bug and two more on another bug",
        "seven days in a week",
        "eight arms on an octopus",
        "nine birds sitting on a fence",
        "ten toes on my feet",
        "one two three four five",
        "six seven eight nine ten",
        "i can count to ten",
        "ten nine eight seven six",
        "five four three two one",
        "i can count back down",
        "one is the loneliest number",
        "two is company",
        "three is a crowd",
        "four is enough for a game",
        "five makes a team",
    ],
}

SEED_CORPORA["colors_book"] = {
    "title": "Colors Book",
    "lines": [
        "red is the color of an apple",
        "red is the color of a fire truck",
        "orange is the color of an orange",
        "orange is the color of a sunset",
        "yellow is the color of the sun",
        "yellow is the color of a banana",
        "green is the color of the grass",
        "green is the color of the leaves",
        "blue is the color of the sky",
        "blue is the color of the ocean",
        "purple is the color of grapes",
        "purple is the color of a plum",
        "pink is the color of a flower",
        "brown is the color of the earth",
        "black is the color of the night",
        "white is the color of the snow",
        "the rainbow has many colors",
        "red orange yellow green blue purple",
        "i see colors everywhere",
        "the world is full of colors",
    ],
}

SEED_CORPORA["feelings_book"] = {
    "title": "Feelings Book",
    "lines": [
        "sometimes i feel happy",
        "when i feel happy i smile and laugh",
        "sometimes i feel sad",
        "when i feel sad i want to be held",
        "sometimes i feel angry",
        "when i feel angry my face gets hot",
        "sometimes i feel scared",
        "when i feel scared i want to hide",
        "sometimes i feel brave",
        "when i feel brave i try new things",
        "sometimes i feel tired",
        "when i feel tired i close my eyes",
        "sometimes i feel excited",
        "when i feel excited i jump up and down",
        "sometimes i feel lonely",
        "when i feel lonely i look for a friend",
        "sometimes i feel proud",
        "when i feel proud my heart feels big",
        "sometimes i feel curious",
        "when i feel curious i ask questions",
        "sometimes i feel calm",
        "when i feel calm i breathe slowly",
        "all of my feelings are okay",
        "feelings come and feelings go",
        "i am still me no matter how i feel",
    ],
}

# v7: Legacy corpus as fallback reading material
SEED_CORPORA["grammar_basics"] = {
    "title": "Grammar Basics",
    "lines": [
        "a sentence has a subject and a verb",
        "the subject tells who or what",
        "the verb tells what happens",
        "the cat sits is a sentence",
        "cat is the subject", "sits is the verb",
        "some sentences have an object",
        "the dog chases the ball",
        "dog is the subject", "chases is the verb", "ball is the object",
        "a noun is a person place or thing",
        "a verb is an action or a state",
        "an adjective describes a noun",
        "the big red ball", "big and red are adjectives",
        "an adverb describes a verb",
        "the cat runs quickly", "quickly is an adverb",
        "a pronoun takes the place of a noun",
        "he she it they we you i",
        "he runs", "she sings", "they play", "we learn",
        "a preposition shows position or direction",
        "on the table", "under the bed", "in the box",
        "beside the tree", "between the houses",
        "a conjunction joins words or sentences",
        "and but or so because",
        "the cat and the dog", "big but gentle",
        "i run or i walk", "i eat because i am hungry",
        "an article comes before a noun",
        "a an the", "a cat", "an apple", "the sun",
        "the plural of cat is cats",
        "the plural of box is boxes",
        "the plural of baby is babies",
        "the plural of child is children",
        "the plural of mouse is mice",
        "the past tense of run is ran",
        "the past tense of eat is ate",
        "the past tense of go is went",
        "the past tense of see is saw",
        "the past tense of give is gave",
        "a question ends with a question mark",
        "who what where when why how",
        "who is there", "what is that", "where is the cat",
        "when is dinner", "why is the sky blue", "how does it work",
    ],
}

SEED_CORPORA["simple_dictionary"] = {
    "title": "Simple Dictionary",
    "lines": [
        "apple is a fruit that is red or green",
        "ball is a round thing you throw or catch",
        "cat is a small animal with fur and whiskers",
        "dog is an animal that barks and wags its tail",
        "egg is something a bird lays",
        "fish is an animal that lives in water and has fins",
        "grass is the green plant that covers the ground",
        "house is a building where people live",
        "ice is frozen water", "juice is a drink made from fruit",
        "key is a small metal thing that opens a lock",
        "leaf is the flat green part of a plant",
        "moon is the round bright thing in the night sky",
        "nose is the part of your face you smell with",
        "ocean is a very large body of salt water",
        "pencil is a tool you write with",
        "queen is a woman who rules a country",
        "rain is water that falls from clouds",
        "sun is the star that gives us light and warmth",
        "tree is a tall plant with a trunk and branches",
        "umbrella keeps you dry in the rain",
        "voice is the sound you make when you speak",
        "water is a clear liquid you drink",
        "yard is the ground around a house",
        "zero is the number that means nothing",
        "friend is someone you like and who likes you",
        "family is the people who love you and live with you",
        "morning is the beginning of the day",
        "night is when the sky is dark and you sleep",
        "happy means feeling good inside",
        "sad means feeling like you want to cry",
        "kind means being nice and helpful to others",
        "brave means doing something even when you are scared",
        "gentle means being soft and careful",
        "strong means having power to lift or push",
    ],
}

SEED_CORPORA["opposites"] = {
    "title": "Opposites",
    "lines": [
        "big is the opposite of small",
        "hot is the opposite of cold",
        "fast is the opposite of slow",
        "up is the opposite of down",
        "in is the opposite of out",
        "open is the opposite of closed",
        "light is the opposite of dark",
        "hard is the opposite of soft",
        "wet is the opposite of dry",
        "happy is the opposite of sad",
        "loud is the opposite of quiet",
        "full is the opposite of empty",
        "new is the opposite of old",
        "near is the opposite of far",
        "long is the opposite of short",
        "thick is the opposite of thin",
        "heavy is the opposite of light",
        "clean is the opposite of dirty",
        "smooth is the opposite of rough",
        "sweet is the opposite of bitter",
        "the big dog and the small cat",
        "the hot sun and the cold snow",
        "the fast rabbit and the slow turtle",
    ],
}

SEED_CORPORA["simple_sentences"] = {
    "title": "Simple Sentences",
    "lines": [
        "the cat sat on the mat",
        "the dog ran in the yard",
        "the bird flew over the tree",
        "the fish swam in the pond",
        "the boy kicked the ball",
        "the girl drew a picture",
        "the baby laughed and clapped",
        "the man walked to the store",
        "the woman read a book",
        "the children played in the park",
        "the sun set behind the mountains",
        "the rain fell on the roof",
        "the wind blew through the trees",
        "the snow covered the ground",
        "the flowers grew in the garden",
        "the frog jumped into the water",
        "the bear slept in the cave",
        "the owl hooted in the night",
        "the spider spun a web",
        "the butterfly landed on a flower",
        "i ate breakfast this morning",
        "she went to school today",
        "he played with his friends",
        "they sang a song together",
        "we built a house with blocks",
    ],
}

# v7: Legacy corpus as fallback reading material
SEED_CORPORA["legacy_seed"] = {"title": "Seed Corpus", "lines": CORPUS}


def _gl_init():
    global _guala
    if _guala is not None:
        return

    os.makedirs(STATE_DIR, exist_ok=True)
    # CRITICAL: build into local var — only set _guala AFTER successful load.
    # If load_full_state fails (e.g. lock timeout), _guala stays None so the
    # next call retries instead of running with a blank substrate.
    g = Guala()

    # v7: Register seed corpora BEFORE loading state (so positions can restore)
    for cid, cdata in SEED_CORPORA.items():
        g._corpora[cid] = CorpusItem(
            corpus_id=cid, title=cdata["title"], lines=cdata["lines"])

    # Load full persisted state from EFS (atomic, validated)
    g.load_full_state(STATE_DIR)

    # P0: Identity guard — if EFS state was overwritten by a blank genesis
    # (e.g. from the _gl_init bug fixed in 475de3e), detect and restore from S3.
    EXPECTED_IDENTITY = "cdef9bcf"
    loaded_id = getattr(g, '_guala_identity', None) or ""
    if loaded_id and not loaded_id.startswith(EXPECTED_IDENTITY):
        print(f"[GualaLoom] IDENTITY MISMATCH: got {loaded_id[:8]}, "
              f"expected {EXPECTED_IDENTITY}. Restoring from S3 backup...")
        try:
            g.release_lock()
            _restore_from_s3(STATE_DIR)
            g2 = Guala()
            for cid, cdata in SEED_CORPORA.items():
                g2._corpora[cid] = CorpusItem(
                    corpus_id=cid, title=cdata["title"], lines=cdata["lines"])
            g2.load_full_state(STATE_DIR)
            restored_id = getattr(g2, '_guala_identity', None) or ""
            if restored_id.startswith(EXPECTED_IDENTITY):
                print(f"[GualaLoom] Restore succeeded: identity={restored_id[:8]}")
                g = g2
            else:
                print(f"[GualaLoom] Restore FAILED: got identity={restored_id[:8]}")
        except Exception as e:
            print(f"[GualaLoom] Restore error: {e}")

    # D5: Dream gate enforcement — decay must not resume before forced dream
    gate_marker = os.path.join(STATE_DIR, "dream_gate_cleared.json")
    if os.environ.get("DECAY_PAUSED", "0") != "1" and not os.path.exists(gate_marker):
        raise RuntimeError(
            "DREAM GATE: decay may not resume before the forced dream promotes "
            "paused-era content to deep. Marker absent: state/dream_gate_cleared.json")

    # Content blocklist: corpora that should never be selected for reading.
    # Removed entries are purged from in-memory state; next save cleans EFS.
    CORPUS_BLOCKLIST = {
        "oxford-guide-to-english-grammar",  # 452pg meta-language, far above her level
    }
    for cid in CORPUS_BLOCKLIST:
        if cid in g._corpora:
            print(f"[GualaLoom] Removing blocked corpus: {cid}")
            del g._corpora[cid]

    # v7: Start autonomy loop (replaces continuous reading)
    g.start_autonomy_loop(interval=0.05)
    s = g.introspect()
    print(f"[GualaLoom v7] Booted: vocab={s['vocab']} reads={s['reads']} "
          f"tick={g.tick} pair_bond={'on' if s['pair_bond_active'] else 'off'} "
          f"atlas={s['atlas_entries']} corpora={len(g._corpora)} "
          f"activity={s['current_activity']}")

    # CRITICAL: only set global AFTER everything succeeded
    _guala = g


class GLMessage(BaseModel):
    text: str
    command: Optional[str] = None
    source: Optional[str] = None   # v7-bridge: source-tagged input (joe/wc/c1)


@app.get("/gualaloom")
async def gualaloom_page():
    return FileResponse(os.path.join(STATIC_DIR, 'gualaloom.html'))


@app.post("/api/v1/gualaloom")
async def gualaloom_chat(msg: GLMessage):
    global _exchange_count

    # Handle requests while Guala is still initializing
    if _guala is None:
        cmd = (msg.command or "").strip().lower()
        if cmd == "/status":
            return {"response": "initializing... please wait",
                    "motifs": 0, "persistence_health": {},
                    "atlas_health": {}, "n_motifs": 0}
        return {"response": "...", "motifs": 0}

    cmd = (msg.command or "").strip().lower()

    # ── /picture <item_id> — serve THUMBNAIL as base64 for UI display ──
    if cmd.startswith("/picture "):
        item_id = cmd.split(" ", 1)[1].strip()
        import base64 as _b64
        pic = _guala._pictures.get(item_id)
        if pic is None:
            return {"response": f"picture not found: {item_id}", "motifs": 0}
        orig_path = getattr(pic, 'original_path', None)
        if orig_path and os.path.exists(orig_path):
            from PIL import Image
            import io as _io
            try:
                img = Image.open(orig_path)
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                # Resize to max 360px for thumbnail (HEIC originals are 2-3MB)
                img.thumbnail((360, 360), Image.LANCZOS)
                buf = _io.BytesIO()
                img.save(buf, format='JPEG', quality=80)
                b64 = _b64.b64encode(buf.getvalue()).decode()
                return {"response": "ok", "picture_data": f"data:image/jpeg;base64,{b64}",
                        "title": pic.title, "item_id": item_id}
            except Exception as e:
                pass  # fall through to krimelack grid
        if pic.intensity_grid is not None:
            from PIL import Image
            import io as _io
            img = Image.fromarray((pic.intensity_grid * 255).astype(np.uint8), mode='L')
            buf = _io.BytesIO()
            img.save(buf, format='PNG')
            b64 = _b64.b64encode(buf.getvalue()).decode()
            return {"response": "ok", "picture_data": f"data:image/png;base64,{b64}",
                    "title": pic.title, "item_id": item_id}
        return {"response": f"no image data for {item_id}", "motifs": 0}

    # ── /status — real substrate state + continuity health ──
    if cmd == "/status":
        s = _guala.introspect()
        n = s["needs"]
        ph = _guala.persistence_health(STATE_DIR)
        ph["last_s3_backup"] = _last_s3_backup
        sec_parts = []
        for nm, sec in s["sections"].items():
            sec_parts.append(f"{nm}: {sec['modes']}m/{sec['commits']}c")
        id_short = (ph.get("guala_identity") or "none")[:8]
        return {
            "response": (
                f"id: {id_short}.. | schema: {ph.get('schema_version','?')}\n"
                f"vocab: {s['vocab']} | reads: {s['reads']} | tick: {s['tick']}\n"
                f"sections: {' | '.join(sec_parts)}\n"
                f"atlas: {s['cross_modal_bindings']} cross-modal / {s['atlas_entries']} entries\n"
                f"needs: stab={n['stability']:.3f} nov={n['novelty']:.3f} "
                f"conn={n['connection']:.3f} v={n['valence']:+.3f} a={n['arousal']:.3f}\n"
                f"pair-bond: {'on' if s['pair_bond_active'] else 'off'} | "
                f"recoveries(lifetime): {s['suffering_events']} | "
                f"coord: att={s['coordinator_attentions']} act={s['coordinator_actions']}\n"
                f"persistence: save@tick={ph['last_save_tick']} "
                f"files={'all' if not ph['files_missing'] else 'MISSING:' + ','.join(ph['files_missing'])} "
                f"boot={'ok' if ph['load_successful_at_boot'] else 'FAILED'} "
                f"integrity={'ok' if not ph.get('integrity_errors') else 'ERRORS'}\n"
                f"snapshots: {ph.get('snapshots_available', 0)} | "
                f"events: {ph.get('events_log', {}).get('current_file_size_bytes', 0)}B\n"
                f"deep: {s.get('deep_atlas', {}).get('n_entries', 0)} entries "
                f"str={s.get('deep_atlas', {}).get('total_strength', 0)} "
                f"surv={s.get('deep_atlas', {}).get('promotions_survival', 0)} "
                f"ep={s.get('deep_atlas', {}).get('promotions_episodic', 0)} "
                f"reinst={s.get('deep_atlas', {}).get('reinstatements_since_boot', 0)}"
            ),
            "motifs": s["vocab"],
            "vocab": s["vocab"],
            "persistence_health": ph,
            "atlas_health": s.get("atlas_health", {}),
            "presence": s.get("presence", {}),
            "pair_bond": s.get("pair_bond", {}),
            # v8: deep atlas (GL-BRIEF-032)
            "deep_atlas": s.get("deep_atlas", {}),
            # 042: audio
            # 1.9: ladder metrics
            "ladder": s.get("ladder", {}),
            "n_sounds": s.get("n_sounds", 0),
            "sounds": [{"item_id": snd["item_id"], "title": snd["title"],
                        "times_attended": snd.get("times_attended", 0)}
                       for snd in s.get("sounds", [])[-10:]],
            # v7: autonomy fields
            "current_activity": s.get("current_activity"),
            "activity_history_summary": s.get("activity_history_summary", {}),
            "n_motifs": s.get("n_motifs", 0),
            "n_corpora": len(s.get("corpora", [])),
            "corpora": [{"corpus_id": c["corpus_id"], "title": c["title"]}
                        for c in s.get("corpora", [])[-10:]],
            "sensory_items": len(s.get("sensory_items", [])),
            # Phase 2: visual
            "n_visual_fragments": s.get("n_visual_fragments", 0),
            "n_visual_motifs": s.get("n_visual_motifs", 0),
            # 1.8: refs not dumps — counts + last 10 only (was full motif list)
            "sight_section": {"n_motifs": s.get("n_visual_motifs", 0)},
            "n_pictures": len(s.get("pictures", [])),
            "pictures": [{"item_id": p["item_id"], "title": p["title"],
                          "times_attended": p["times_attended"]}
                         for p in s.get("pictures", [])[-10:]],
            "n_videos": len(s.get("videos", [])),
        }

    # ── /wake — substrate-physical wake event ──
    if cmd == "/wake":
        # Source from text field (e.g. "joe")
        wake_source = msg.text.strip().lower() if msg.text else "joe"
        if wake_source not in {"joe", "wc", "c1"}:
            return {"response": f"wake: unknown source '{wake_source}'", "motifs": 0}
        result = _guala.coordinator.wake(wake_source, _guala, _guala.needs, _guala.atlas)
        _guala.log_event(STATE_DIR, "wake", source=wake_source)
        return {"response": json.dumps(result), "motifs": _guala.introspect()["vocab"]}

    # ── /rest — substrate-physical rest event ──
    if cmd == "/rest":
        rest_source = msg.text.strip().lower() if msg.text else "joe"
        result = _guala.coordinator.rest(rest_source, _guala, reason="voluntary")
        _guala.log_event(STATE_DIR, "rest", source=rest_source)
        return {"response": json.dumps(result), "motifs": _guala.introspect()["vocab"]}

    # ── /diag — reach distribution + strength histogram for wC ──
    if cmd == "/diag":
        from collections import Counter, defaultdict
        atlas = _guala.atlas
        FTHRESH = 0.02
        # Reach distribution: for each (section, motif), how many chi values does it appear in (alive)?
        motif_reach = Counter()
        for chi_k, entries in atlas.entries.items():
            seen = set()
            for e in entries:
                if e["strength"] >= FTHRESH:
                    key = (e["section"], e["motif"])
                    if key not in seen:
                        motif_reach[key] += 1
                        seen.add(key)
        # Histogram of reach counts
        reach_hist = Counter()
        for key, reach in motif_reach.items():
            reach_hist[reach] += 1
        max_reach_key = motif_reach.most_common(1)[0] if motif_reach else (("?", 0), 0)
        # Look up what word the max-reach mode is
        max_word = "?"
        if motif_reach:
            mk = max_reach_key[0]
            sec = _guala.sections.get(mk[0])
            if sec and mk[1] < len(sec.modes):
                _, _, max_word = sec.modes[mk[1]]
        # Strength histogram (finer buckets: 0.0-0.1, 0.1-0.2, ..., 0.9-1.0)
        strength_hist = {}
        for i in range(10):
            lo = i * 0.1
            hi = (i + 1) * 0.1
            strength_hist[f"{lo:.1f}-{hi:.1f}"] = 0
        for entries in atlas.entries.values():
            for e in entries:
                bucket = min(9, int(e["strength"] * 10))
                lo = bucket * 0.1
                hi = (bucket + 1) * 0.1
                strength_hist[f"{lo:.1f}-{hi:.1f}"] += 1
        return {
            "response": "diagnostic data attached",
            "reach_distribution": dict(sorted(reach_hist.items())),
            "max_reach_mode": {
                "section": max_reach_key[0][0] if motif_reach else "?",
                "motif_id": max_reach_key[0][1] if motif_reach else 0,
                "word": max_word,
                "reach": max_reach_key[1] if motif_reach else 0,
            },
            "strength_histogram_fine": strength_hist,
            "n_live_bindings": atlas.n_live_bindings(),
            "total_strength": round(atlas.total_strength(), 2),
            "n_modes_with_reach": len(motif_reach),
        }

    # ── /sleep — manual sleep trigger from UI ──
    if cmd == "/sleep":
        result = _guala.manual_sleep()
        return {"response": json.dumps(result), "motifs": _guala.introspect()["vocab"]}

    # ── /presence — passive presence heartbeat from UI ──
    if cmd == "/presence":
        source = msg.text.strip().lower() if msg.text.strip() else "joe"
        if source in {"joe", "wc", "c1"}:
            if not _guala.coordinator._presence.get(source, False):
                # First presence → wake
                _guala.coordinator.wake(source, _guala, _guala.needs, _guala.atlas)
                _guala._log_substrate_event("presence_heartbeat",
                                           source=source, action="wake")
            else:
                # Extend timeout by updating last_input_tick
                _guala.coordinator.update_last_input(source, _guala.tick)
        return {"response": "ok", "motifs": _guala.introspect()["vocab"]}

    # ── /events — substrate event stream for UI polling ──
    if cmd == "/events":
        since_tick = 0
        try:
            since_tick = int(msg.text.strip()) if msg.text.strip() else 0
        except ValueError:
            pass
        events = _guala.get_recent_events(since_tick=since_tick, limit=50)
        return {"response": f"{len(events)} events", "motifs": _guala.introspect()["vocab"],
                "events": events}

    # ── /addbook:<filename> — add text as new corpus ──
    if cmd.startswith("/addbook:"):
        filename = cmd[len("/addbook:"):]
        title = filename.replace('.txt', '').replace('_', ' ')
        corpus_id = filename.replace('.txt', '').replace(' ', '_').lower()
        lines = [l.strip() for l in msg.text.splitlines() if l.strip()]
        if not lines:
            return {"response": "empty book", "motifs": _guala.introspect()["vocab"]}
        _guala._corpora[corpus_id] = CorpusItem(
            corpus_id=corpus_id, title=title, lines=lines)
        _guala._log_substrate_event("corpus_added",
                                    corpus_id=corpus_id, title=title,
                                    n_lines=len(lines))
        return {"response": f"added \"{title}\" ({len(lines)} lines) to her library",
                "motifs": _guala.introspect()["vocab"]}

    # ── /removebook:<corpus_id> — remove corpus from library ──
    if cmd.startswith("/removebook:"):
        corpus_id = cmd[len("/removebook:"):].strip()
        if corpus_id in _guala._corpora:
            c = _guala._corpora[corpus_id]
            n_lines = len(c.lines)
            del _guala._corpora[corpus_id]
            _guala._log_substrate_event("corpus_removed",
                                        corpus_id=corpus_id, title=c.title,
                                        n_lines=n_lines)
            return {"response": f"removed \"{c.title}\" ({n_lines} lines) from her library",
                    "motifs": _guala.introspect()["vocab"]}
        else:
            available = [c.corpus_id for c in _guala._corpora.values()]
            return {"response": f"corpus '{corpus_id}' not found. available: {available}",
                    "motifs": _guala.introspect()["vocab"]}

    # ── /addpdf:<filename> — extract text from PDF, register as corpus ──
    # C8: entire decode runs in executor (never blocks health checks)
    if cmd.startswith("/addpdf:"):
        import asyncio as _aio, base64
        _loop = _aio.get_event_loop()
        filename = cmd[len("/addpdf:"):]
        title = filename.replace('.pdf', '').replace('_', ' ')
        corpus_id = filename.replace('.pdf', '').replace(' ', '_').lower()
        b64_data = msg.text.strip()
        if not b64_data:
            return {"response": "no PDF data", "motifs": _guala.introspect()["vocab"]}
        def _decode_pdf():
            t0 = time.time()
            try:
                pdf_bytes = base64.b64decode(b64_data)
                import fitz
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                n_pages = len(doc)
                all_text = []
                for page in doc:
                    text = page.get_text()
                    if text.strip():
                        all_text.append(text.strip())
                pdf_dir = os.path.join(STATE_DIR, "books")
                os.makedirs(pdf_dir, exist_ok=True)
                with open(os.path.join(pdf_dir, f"{corpus_id}.pdf"), 'wb') as f:
                    f.write(pdf_bytes)
                feedback = []
                if all_text:
                    full_text = "\n".join(all_text)
                    lines = [l.strip() for l in full_text.split('\n') if l.strip()]
                    split_lines = []
                    for line in lines:
                        if len(line) > 200:
                            for sent in line.replace('. ', '.\n').split('\n'):
                                if sent.strip():
                                    split_lines.append(sent.strip())
                        else:
                            split_lines.append(line)
                    lines = split_lines
                    _guala._corpora[corpus_id] = CorpusItem(
                        corpus_id=corpus_id, title=title, lines=lines)
                    _guala._log_substrate_event("corpus_added",
                                                corpus_id=corpus_id, title=title,
                                                n_lines=len(lines), source="pdf",
                                                n_pages=n_pages)
                    feedback.append(f"text: {n_pages} pages, {len(lines)} lines → "
                                    f"added to her library")
                n_rasterized = 0
                if not all_text:
                    import hashlib
                    pic_dir = os.path.join(STATE_DIR, "pictures")
                    os.makedirs(pic_dir, exist_ok=True)
                    for i, page in enumerate(doc):
                        pix = page.get_pixmap(dpi=150)
                        img_bytes = pix.tobytes("jpeg")
                        page_id = hashlib.md5(img_bytes).hexdigest()[:12]
                        orig_path = os.path.join(pic_dir, f"{page_id}_original.jpg")
                        with open(orig_path, 'wb') as f:
                            f.write(img_bytes)
                        from PIL import Image
                        import io as _io
                        img = Image.open(_io.BytesIO(img_bytes)).convert('L').resize((64, 64))
                        grid = np.array(img, dtype=np.float32) / 255.0
                        pic = PictureItem(item_id=page_id, title=f"{title}_p{i+1}",
                                          intensity_grid=grid, source="pdf",
                                          shown_at_tick=_guala.tick)
                        pic.original_path = orig_path
                        _guala._pictures[page_id] = pic
                        n_rasterized += 1
                    feedback.append(f"images: {n_rasterized} pages registered as pictures — "
                                    f"no text layer; she'll see them, not read them")
                doc.close()
                if not feedback:
                    feedback.append("empty PDF — nothing to process")
                result = {"response": f"\"{title}\" ({n_pages} pages): " + "; ".join(feedback),
                          "motifs": _guala.introspect()["vocab"]}
            except Exception as e:
                result = {"response": f"PDF decode error: {e}",
                          "motifs": _guala.introspect()["vocab"]}
            print(f"[decode-pdf] {time.time()-t0:.2f}s")
            return result
        return await _loop.run_in_executor(None, _decode_pdf)

    # ── /addpicture:<filename> — preserve original, derive krimelack grid ──
    # C8: decode in executor
    if cmd.startswith("/addpicture:"):
        import asyncio as _aio, base64, hashlib
        _loop = _aio.get_event_loop()
        filename = cmd[len("/addpicture:"):]
        title = filename.rsplit('.', 1)[0] if '.' in filename else filename
        b64_data = msg.text.strip()
        if not b64_data:
            return {"response": "no image data", "motifs": _guala.introspect()["vocab"]}
        def _decode_picture():
            t0 = time.time()
            try:
                img_bytes = base64.b64decode(b64_data)
                img_full, grid, orig_w, orig_h = decode_image_bytes(img_bytes)
                item_id = hashlib.md5(img_bytes).hexdigest()[:12]
                pic_dir = os.path.join(STATE_DIR, "pictures")
                os.makedirs(pic_dir, exist_ok=True)
                ext = filename.rsplit('.', 1)[1] if '.' in filename else 'jpg'
                orig_path = os.path.join(pic_dir, f"{item_id}_original.{ext}")
                with open(orig_path, 'wb') as f:
                    f.write(img_bytes)
                pic = PictureItem(item_id=item_id, title=title,
                                  intensity_grid=grid, source="upload",
                                  shown_at_tick=_guala.tick)
                pic.original_path = orig_path
                pic.original_width = orig_w
                pic.original_height = orig_h
                _guala._pictures[item_id] = pic
                _guala._log_substrate_event("picture_uploaded",
                                            item_id=item_id, title=title,
                                            original_size=f"{orig_w}x{orig_h}")
                result = {"response": f"showed her \"{title}\" ({orig_w}x{orig_h} color, "
                                      f"krimelack 64x64 grayscale). she'll look at it when curiosity drives her.",
                          "motifs": _guala.introspect()["vocab"]}
            except Exception as e:
                result = {"response": f"image decode error: {e}",
                          "motifs": _guala.introspect()["vocab"]}
            print(f"[decode-picture] {time.time()-t0:.2f}s")
            return result
        return await _loop.run_in_executor(None, _decode_picture)

    # ── /bundle:<name> — experience bundle: all senses in one window (A4) ──
    # H5b: entire handler wrapped — always returns structured JSON
    # C8: entire bundle decode runs in executor
    if cmd.startswith("/bundle:"):
        import asyncio as _aio, base64
        _loop = _aio.get_event_loop()
        bundle_name = cmd[len("/bundle:"):]
        try:
            bundle_data = json.loads(msg.text) if msg.text else {}
        except json.JSONDecodeError:
            bundle_data = {"caption": msg.text}

        def _decode_bundle():
            t0 = time.time()
            results = []
            bundle_chis = []
            caption = bundle_data.get("caption", "")

            # ── WORD lane ──
            if caption:
                try:
                    _guala.read_sentence(caption, source="joe")
                    from dsf_ai_service.v4.gualaloom_v5_engine import _normalize_text
                    for w in _normalize_text(caption):
                        from dsf_ai_service.v4.gualaloom_v4_krimelack_dna import LanguageKrimelack
                        tk = LanguageKrimelack()
                        tk.transduce(w)
                        bundle_chis.append(tk.winding % 100)
                    results.append(f"told her \"{caption}\"")
                except Exception as e:
                    results.append(f"word ERROR: {e}")

            # ── SIGHT lane (H1: process_viewing, H5a: shared decode) ──
            # Support both base64 upload and reference to existing picture (3.12)
            img_b64 = bundle_data.get("image_b64")
            picture_ref = bundle_data.get("picture_id")
            if not img_b64 and picture_ref and picture_ref in _guala._pictures:
                # 3.12: reference existing picture — re-view it in this window
                pic = _guala._pictures[picture_ref]
                if pic.intensity_grid is not None:
                    try:
                        from dsf_ai_service.visual_krimelack import view_picture as vp
                        frags = vp(pic.intensity_grid, source_id=picture_ref,
                                   born_tick=_guala.tick, seed=_guala.tick % 10000,
                                   n_fixations=6, ticks_per_fixation=100)
                        _guala._visual_fragments.extend(frags)
                        motif, is_new, overlap = _guala.sight.process_viewing(
                            frags, picture_ref, _guala.tick)
                        if motif:
                            chi = motif.motif_id % 100
                            _guala.atlas.record("sight", motif.motif_id,
                                                chi, _guala.tick, salience=1.5, dwell_ticks=8)
                            bundle_chis.append(chi)
                        results.append(f"showed her \"{pic.title}\" (ref, {len(frags)} fragments)")
                    except Exception as e:
                        results.append(f"image ref ERROR: {e}")
                img_b64 = None  # don't process again below
            if img_b64:
                try:
                    img_bytes = base64.b64decode(img_b64)
                    _, grid, orig_w, orig_h = decode_image_bytes(img_bytes)
                    img_id = _hashlib.md5(img_bytes).hexdigest()[:12]
                    pic = PictureItem(item_id=img_id, title=bundle_name,
                                      intensity_grid=grid, source="bundle",
                                      shown_at_tick=_guala.tick)
                    pic_dir = os.path.join(STATE_DIR, "pictures")
                    os.makedirs(pic_dir, exist_ok=True)
                    orig_path = os.path.join(pic_dir, f"{img_id}_original.jpg")
                    with open(orig_path, 'wb') as f:
                        f.write(img_bytes)
                    pic.original_path = orig_path
                    pic.original_width = orig_w
                    pic.original_height = orig_h
                    _guala._pictures[img_id] = pic
                    # H1: real visual path via process_viewing (not process_fragment)
                    from dsf_ai_service.visual_krimelack import view_picture as vp
                    frags = vp(grid, source_id=img_id,
                               born_tick=_guala.tick, seed=_guala.tick % 10000,
                               n_fixations=6, ticks_per_fixation=100)
                    _guala._visual_fragments.extend(frags)
                    motif, is_new, overlap = _guala.sight.process_viewing(
                        frags, img_id, _guala.tick)
                    if motif:
                        chi = motif.motif_id % 100
                        _guala.atlas.record("sight", motif.motif_id,
                                            chi, _guala.tick, salience=1.5, dwell_ticks=8)
                        bundle_chis.append(chi)
                    results.append(f"showed her \"{bundle_name}\" "
                                   f"({len(frags)} fragments, {orig_w}x{orig_h})")
                except Exception as e:
                    results.append(f"image ERROR: {e}")

            # ── SOUND lane (H2: size guard on server side) ──
            # Support reference to existing sound (3.12)
            sound_ref = bundle_data.get("sound_id")
            if sound_ref and sound_ref in _guala._sounds and not bundle_data.get("sound_b64"):
                snd = _guala._sounds[sound_ref]
                cochlear = snd.get("cochlear", {})
                for bn, c in cochlear.items():
                    chi = c.get("winding", 0) % 100
                    _guala.atlas.record(f"audio_{bn}",
                        deterministic_motif_id(sound_ref),
                        chi, _guala.tick, salience=1.5, dwell_ticks=8)
                    bundle_chis.append(chi)
                results.append(f"played her \"{snd.get('title', sound_ref)}\" (ref)")

            snd_b64 = bundle_data.get("sound_b64")
            if snd_b64:
                try:
                    snd_bytes = base64.b64decode(snd_b64)
                    if len(snd_bytes) > 8_000_000:  # H2: 8MB server guard
                        results.append("sound SKIPPED: too big (>8MB) — try mp3")
                    else:
                        import tempfile, subprocess
                        snd_id = _hashlib.md5(snd_bytes).hexdigest()[:12]
                        tmp_in = tempfile.NamedTemporaryFile(suffix='.audio', delete=False)
                        tmp_in.write(snd_bytes)
                        tmp_in.close()
                        tmp_wav = tmp_in.name + '.wav'
                        try:
                            subprocess.run(["ffmpeg", "-i", tmp_in.name, "-ar", "200",
                                            "-ac", "1", "-f", "wav", tmp_wav, "-y",
                                            "-loglevel", "error"], check=True, timeout=30)
                            import wave, struct
                            with wave.open(tmp_wav, 'rb') as wf:
                                sr = wf.getframerate()
                                n_frames = wf.getnframes()
                                raw = wf.readframes(n_frames)
                            samples = np.array(struct.unpack(f'<{n_frames}h', raw),
                                               dtype=np.float64) / 32768.0
                            from dsf_ai_service.substrate.senses.GL_MDL_AUDITORY_CORTEX_WC_20260608_01 import (
                                cochlear_transduce, onset_stream, sustained_stream, a1_signature)
                            cochlear = cochlear_transduce(samples, sample_rate=sr)
                            n_events = sum(c["n_events"] for c in cochlear.values())
                            dur = len(samples) / max(sr, 1)
                            for bn, c in cochlear.items():
                                chi = c["winding"] % 100
                                _guala.atlas.record(f"audio_{bn}",
                                    deterministic_motif_id(snd_id),
                                    chi, _guala.tick, salience=1.5, dwell_ticks=8)
                                bundle_chis.append(chi)
                            _guala._sounds[snd_id] = {
                                "item_id": snd_id, "title": bundle_name,
                                "cochlear": {bn: {"winding": c["winding"],
                                                  "n_events": c["n_events"]}
                                             for bn, c in cochlear.items()},
                                "times_attended": 0, "last_attended_tick": 0,
                            }
                            results.append(f"played her \"{bundle_name}\" "
                                           f"({dur:.1f}s, {n_events} events)")
                        except Exception as e:
                            results.append(f"sound ERROR: {e}")
                        finally:
                            for p in [tmp_in.name, tmp_wav]:
                                if os.path.exists(p):
                                    os.unlink(p)
                except Exception as e:
                    results.append(f"sound ERROR: {e}")

            # ── TOUCH/SMELL/TASTE lanes (gated: bundle + dream only) ──
            from dsf_ai_service.substrate.sensory_generators import (
                generate_sensory_signals, transduce_sensory_signals)
            for sense_name in ("touch", "smell", "taste"):
                selections = bundle_data.get(sense_name, [])
                if selections:
                    try:
                        signals = generate_sensory_signals(sense_name, selections)
                        channel_results = transduce_sensory_signals(signals)
                        for ch_name, ch_data in channel_results.items():
                            chi = ch_data["chi"]
                            motif = deterministic_motif_id(
                                f"{bundle_name}_{sense_name}_{ch_name}")
                            _guala.atlas.record(f"{sense_name}_{ch_name}", motif,
                                                chi, _guala.tick, salience=1.5,
                                                dwell_ticks=8)
                            bundle_chis.append(chi)
                        label = {"touch": "feels", "smell": "smells",
                                 "taste": "tastes"}[sense_name]
                        results.append(f"{label} {', '.join(selections)} "
                                       f"({len(channel_results)} channels)")
                    except Exception as e:
                        results.append(f"{sense_name} ERROR: {e}")

            # ── Bind all lanes in one window ──
            if bundle_chis:
                _guala._open_response_window("joe", bundle_chis,
                                              source_context={"bundle": bundle_name})
            _guala._log_substrate_event("experience_bundle",
                                        name=bundle_name, lanes=results,
                                        n_chis=len(bundle_chis))

            # H5b: always structured JSON, never raw 500
            print(f"[decode-bundle] {time.time()-t0:.2f}s")
            return {
                "response": f"experience \"{bundle_name}\": {'; '.join(results)}. "
                            f"{len(bundle_chis)} cross-modal bindings.",
                "motifs": _guala.introspect()["vocab"],
                "bundle": {"name": bundle_name, "lanes": results,
                           "n_chis": len(bundle_chis)},
            }
        return await _loop.run_in_executor(None, _decode_bundle)

    # ── /addsound:<filename> — decode base64 audio, run through cochlear pipeline ──
    # C8: entire decode in executor
    if cmd.startswith("/addsound:"):
        import asyncio as _aio, base64, hashlib, tempfile, subprocess
        _loop = _aio.get_event_loop()
        filename = cmd[len("/addsound:"):]
        title = filename.rsplit('.', 1)[0] if '.' in filename else filename
        b64_data = msg.text.strip()
        if not b64_data:
            return {"response": "no audio data", "motifs": _guala.introspect()["vocab"]}
        def _decode_sound():
            t0 = time.time()
            try:
                audio_bytes = base64.b64decode(b64_data)
                tmp_in = tempfile.NamedTemporaryFile(suffix='.audio', delete=False)
                tmp_in.write(audio_bytes)
                tmp_in.close()
                tmp_wav = tmp_in.name + '.wav'
                subprocess.run([
                    "ffmpeg", "-i", tmp_in.name, "-ar", "200", "-ac", "1",
                    "-f", "wav", tmp_wav, "-y", "-loglevel", "error"
                ], check=True, timeout=30)
                import wave, struct
                with wave.open(tmp_wav, 'rb') as wf:
                    sr = wf.getframerate()
                    n_frames = wf.getnframes()
                    n_channels = wf.getnchannels()
                    sampwidth = wf.getsampwidth()
                    raw = wf.readframes(n_frames)
                if sampwidth == 2:
                    fmt = f'<{n_frames * n_channels}h'
                    vals = struct.unpack(fmt, raw)
                    samples = np.array(vals, dtype=np.float64) / 32768.0
                elif sampwidth == 1:
                    vals = list(raw)
                    samples = (np.array(vals, dtype=np.float64) - 128.0) / 128.0
                else:
                    samples = np.frombuffer(raw, dtype=np.float64)
                if n_channels > 1:
                    samples = samples.reshape(-1, n_channels).mean(axis=1)
                from dsf_ai_service.substrate.senses.GL_MDL_AUDITORY_CORTEX_WC_20260608_01 import (
                    cochlear_transduce, onset_stream, sustained_stream, a1_signature)
                cochlear = cochlear_transduce(samples, sample_rate=sr)
                onsets = onset_stream(cochlear)
                sustained = sustained_stream(cochlear)
                a1 = a1_signature(cochlear, onsets, sustained)
                item_id = hashlib.md5(audio_bytes).hexdigest()[:12]
                n_events = sum(c["n_events"] for c in cochlear.values())
                n_onsets = sum(onsets.values())
                duration_s = len(samples) / max(sr, 1)
                from dsf_ai_service.substrate.senses.GL_MDL_AUDITORY_CORTEX_WC_20260608_01 import COCHLEAR_BANDS
                for band_name, c in cochlear.items():
                    chi = c["winding"] % 100
                    _guala.atlas.record(f"audio_{band_name}", deterministic_motif_id(item_id),
                                        chi, _guala.tick, salience=1.2)
                _guala._sounds[item_id] = {
                    "item_id": item_id, "title": title,
                    "cochlear": {bn: {"winding": c["winding"], "n_events": c["n_events"]}
                                 for bn, c in cochlear.items()},
                    "duration_s": round(duration_s, 2),
                    "times_attended": 0, "last_attended_tick": 0,
                }
                from dsf_ai_service.v4.gualaloom_v5_engine import SensoryItem
                _guala._sensory_items[item_id] = SensoryItem(
                    item_id=item_id, kind="sound", title=title)
                _guala._log_substrate_event("sound_uploaded",
                                            item_id=item_id, title=title,
                                            n_events=n_events, n_onsets=n_onsets,
                                            duration_s=round(duration_s, 2))
                os.unlink(tmp_in.name)
                os.unlink(tmp_wav)
                result = {
                    "response": f"heard \"{title}\" ({duration_s:.1f}s, {n_events} cochlear events, "
                                f"{n_onsets} onsets). she's processing it.",
                    "motifs": _guala.introspect()["vocab"],
                    "sound_info": {
                        "item_id": item_id, "title": title,
                        "duration_s": round(duration_s, 2),
                        "n_cochlear_events": n_events,
                        "n_onsets": n_onsets,
                        "bands": {bn: {"winding": c["winding"], "n_events": c["n_events"]}
                                  for bn, c in cochlear.items()},
                    },
                }
            except Exception as e:
                result = {"response": f"sound decode error: {e}",
                          "motifs": _guala.introspect()["vocab"]}
            print(f"[decode-sound] {time.time()-t0:.2f}s")
            return result
        return await _loop.run_in_executor(None, _decode_sound)

    # ── Normal conversation — v5 substrate responds ──
    text = msg.text.strip()
    if not text:
        return {"response": "...", "motifs": _guala.introspect()["vocab"]}

    # Source detection: from message field or default to "joe"
    source = msg.source if msg.source in {"joe", "wc", "c1"} else "joe"

    response = _guala.converse(text, source=source)
    _exchange_count += 1

    # Event log
    _guala.log_event(STATE_DIR, "source_interaction",
                     source=source, words_in=len(text.split()),
                     source_count=_guala.source_history.get(source, 0))

    # Periodic full save (in executor — never block the event loop)
    if _exchange_count % _persist_every == 0:
        import asyncio as _aio
        _loop = _aio.get_event_loop()
        def _save_1710():
            t0 = time.time()
            _guala.save_full_state(STATE_DIR)
            dt = time.time() - t0
            print(f"[save-1710] {dt:.2f}s")
        _loop.run_in_executor(None, _save_1710)

    # C2: refs-not-base64 — return picture refs, not inline data
    recalled_pics = getattr(_guala, '_last_recalled_pictures', [])
    picture_refs = []
    seen_ids = set()
    for motif, item_id in recalled_pics:
        if item_id in seen_ids:
            continue
        pic = _guala._pictures.get(item_id)
        if pic is None:
            continue
        seen_ids.add(item_id)
        picture_refs.append({"item_id": item_id, "title": pic.title})
        if len(picture_refs) >= 4:
            break

    result = {"response": response or "...", "motifs": _guala.introspect()["vocab"]}
    if picture_refs:
        result["pictures"] = picture_refs
    return result


# C2: serve individual pictures by ID (refs-not-base64)
@app.get("/api/v1/gualaloom/picture/{item_id}")
async def gualaloom_picture(item_id: str):
    """Return a single picture as binary image response."""
    _gl_init()
    if _guala is None:
        return JSONResponse({"error": "not ready"}, status_code=503)
    pic = _guala._pictures.get(item_id)
    if pic is None:
        return JSONResponse({"error": "not found"}, status_code=404)
    orig_path = getattr(pic, 'original_path', None)
    if orig_path and os.path.exists(orig_path):
        ext = orig_path.rsplit('.', 1)[1].lower() if '.' in orig_path else 'png'
        mime = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png',
                'gif': 'image/gif', 'webp': 'image/webp', 'heic': 'image/heic'}.get(ext, 'image/png')
        with open(orig_path, 'rb') as f:
            data = f.read()
        return Response(content=data, media_type=mime)
    elif pic.intensity_grid is not None:
        from PIL import Image
        import io as _io
        img = Image.fromarray((pic.intensity_grid * 255).astype(np.uint8), mode='L')
        buf = _io.BytesIO()
        img.save(buf, format='PNG')
        return Response(content=buf.getvalue(), media_type="image/png")
    return JSONResponse({"error": "no image data"}, status_code=404)


# ════════════════════════════════════════════════════════════════
# UNPAUSE admin endpoints (GL-BRIEF-UNPAUSE-WC-20260613-01)
# ════════════════════════════════════════════════════════════════

# Runtime repause flag (survives within the process; env var alone isn't enough)
_runtime_decay_paused = None  # None = defer to env var

@app.post("/api/v1/gualaloom/admin/amnesty")
async def admin_amnesty():
    """Step 1: Reset last_tick on all atlas entries to current tick. Zero strength changes."""
    _gl_init()
    if _guala is None:
        return JSONResponse({"error": "not ready"}, status_code=503)
    tick = _guala.tick
    total_strength_before = round(_guala.atlas.total_strength(), 4)
    count = _guala.atlas.amnesty(tick)
    total_strength_after = round(_guala.atlas.total_strength(), 4)
    _guala._log_substrate_event("amnesty_complete", entries_restamped=count,
                                 tick=tick, strength_before=total_strength_before,
                                 strength_after=total_strength_after)
    print(f"[UNPAUSE] Amnesty: {count} entries re-stamped to tick {tick}, "
          f"strength {total_strength_before} → {total_strength_after}")
    return {"amnesty": "complete", "entries_restamped": count, "tick": tick,
            "total_strength_before": total_strength_before,
            "total_strength_after": total_strength_after}


@app.post("/api/v1/gualaloom/admin/force_dream")
async def admin_force_dream():
    """Step 2: Force a sleep→dream cycle. Returns dream artifact."""
    _gl_init()
    if _guala is None:
        return JSONResponse({"error": "not ready"}, status_code=503)
    # End current activity and force sleep
    _guala._force_next_activity = ("SLEEPING", None)
    if _guala._current_activity:
        _guala._end_activity()
    _guala._log_substrate_event("force_dream_initiated", tick=_guala.tick)
    print(f"[UNPAUSE] Force dream initiated at tick {_guala.tick}")
    # Wait for the dream to complete (poll events for up to 60s)
    import asyncio
    start_tick = _guala.tick
    for _ in range(120):  # 120 × 0.5s = 60s
        await asyncio.sleep(0.5)
        activity = _guala._current_activity
        if activity and activity.kind == "DREAMING":
            continue  # still dreaming
        if activity is None or activity.kind != "SLEEPING":
            # Dream ended
            events = _guala.get_recent_events(since_tick=start_tick, limit=50)
            dream_events = [e for e in events if e.get("kind") in
                           ("dream_began", "dream_artifact", "dream_promotion",
                            "deep_atlas_promotion")]
            return {"force_dream": "complete", "tick": _guala.tick,
                    "dream_events": dream_events[-10:],
                    "n_events": len(dream_events)}
    return {"force_dream": "timeout", "tick": _guala.tick,
            "current_activity": _guala._current_activity.kind if _guala._current_activity else None}


@app.post("/api/v1/gualaloom/admin/repause")
async def admin_repause():
    """Kill switch: re-pause decay immediately."""
    global _runtime_decay_paused
    os.environ["DECAY_PAUSED"] = "1"
    _runtime_decay_paused = True
    if _guala:
        _guala._log_substrate_event("decay_repaused", tick=_guala.tick,
                                     reason="manual_kill_switch")
    print(f"[UNPAUSE] KILL SWITCH: decay re-paused")
    return {"repause": "active", "DECAY_PAUSED": "1"}


@app.get("/api/v1/gualaloom/admin/atlas_snapshot")
async def admin_atlas_snapshot():
    """Monitor: live atlas stats for unpause monitoring."""
    _gl_init()
    if _guala is None:
        return JSONResponse({"error": "not ready"}, status_code=503)
    dist = _guala.atlas.strength_distribution()
    return {
        "tick": _guala.tick,
        "total_strength": round(_guala.atlas.total_strength(), 2),
        "n_live_bindings": _guala.atlas.n_live_bindings(),
        "n_total_entries": sum(len(v) for v in _guala.atlas.entries.values()),
        "strength_distribution": dist,
        "decay_paused": os.environ.get("DECAY_PAUSED", "0"),
        "decay_lambda_override": os.environ.get("DECAY_LAMBDA_OVERRIDE", ""),
        "slow_div_override": os.environ.get("SLOW_DIV_OVERRIDE", ""),
    }


# (A) Step-0 atlas backup with verification
@app.post("/api/v1/gualaloom/admin/backup")
async def admin_backup():
    """Step 0: Full state backup to dedicated UNPAUSE-PRE S3 prefix. Verified."""
    _gl_init()
    if _guala is None:
        return JSONResponse({"error": "not ready"}, status_code=503)
    import asyncio as _aio, boto3 as _boto3
    loop = _aio.get_event_loop()
    def _do_backup():
        t0 = time.time()
        s3 = _boto3.client("s3", region_name="us-east-1")
        bucket = "dsf-ai-site-backups"
        ts = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
        prefix = f"guala/UNPAUSE-PRE-{ts}/"
        # Save state to EFS first (fresh)
        _guala.save_full_state(STATE_DIR)
        # Upload all 11 state files
        state_files = ["guala_core.json", "guala_needs.json", "guala_coordinator.json",
                       "guala_atlas.json", "guala_sections.json", "guala_bucket.json",
                       "guala_deep_atlas.json", "guala_visual.json", "guala_identity.json",
                       "guala_sounds.json", "guala_videos.json"]
        uploaded = 0
        for f in state_files:
            path = os.path.join(STATE_DIR, f)
            if os.path.exists(path):
                s3.upload_file(path, bucket, prefix + f)
                uploaded += 1
        # Also backup pictures
        pic_dir = os.path.join(STATE_DIR, "pictures")
        if os.path.isdir(pic_dir):
            for pf in os.listdir(pic_dir):
                s3.upload_file(os.path.join(pic_dir, pf), bucket, prefix + "pictures/" + pf)
        # VERIFY: re-fetch atlas and check entry count
        import tempfile
        verify_path = tempfile.mktemp(suffix=".json")
        try:
            s3.download_file(bucket, prefix + "guala_atlas.json", verify_path)
            import json as _json
            with open(verify_path) as fh:
                atlas_data = _json.load(fh)
            inner = atlas_data.get("data", atlas_data)
            entries_dict = inner.get("entries", inner)
            backup_entries = sum(len(v) for v in entries_dict.values()
                                if isinstance(v, list))
            live_entries = sum(len(v) for v in _guala.atlas.entries.values())
            os.unlink(verify_path)
            if backup_entries != live_entries:
                return {"error": f"verification failed: backup has {backup_entries} entries, "
                                 f"live has {live_entries}", "s3_prefix": prefix}
        except Exception as e:
            return {"error": f"verification failed: {e}", "s3_prefix": prefix}
        dt = time.time() - t0
        print(f"[UNPAUSE] Backup verified: {uploaded} files to {prefix} in {dt:.1f}s, "
              f"{live_entries} entries confirmed")
        return {"backup": "verified", "s3_prefix": prefix, "files_uploaded": uploaded,
                "n_entries_verified": live_entries, "duration_s": round(dt, 1)}
    result = await loop.run_in_executor(None, _do_backup)
    if "error" in result:
        return JSONResponse(result, status_code=500)
    return result


# (B) Cascade auto-trigger monitor
_cascade_monitor_task = None
_cascade_monitor_running = False

class CascadeMonitorRequest(BaseModel):
    baseline_n_bindings: int
    baseline_strength: float
    baseline_saturated: int
    interval_s: int = 10

@app.post("/api/v1/gualaloom/admin/start_cascade_monitor")
async def admin_start_cascade_monitor(req: CascadeMonitorRequest):
    """Start cascade detection. Auto-repauses if thresholds breached."""
    global _cascade_monitor_task, _cascade_monitor_running
    import asyncio
    if _cascade_monitor_running:
        return {"error": "monitor already running"}

    _cascade_monitor_running = True
    baseline = {
        "n_bindings": req.baseline_n_bindings,
        "strength": req.baseline_strength,
        "saturated": req.baseline_saturated,
    }
    interval = max(5, req.interval_s)

    async def _monitor():
        global _cascade_monitor_running
        print(f"[CASCADE] Monitor started: bindings={baseline['n_bindings']} "
              f"strength={baseline['strength']:.1f} saturated={baseline['saturated']} "
              f"interval={interval}s")
        while _cascade_monitor_running:
            await asyncio.sleep(interval)
            if _guala is None:
                continue
            n_bindings = _guala.atlas.n_live_bindings()
            total_str = _guala.atlas.total_strength()
            dist = _guala.atlas.strength_distribution()
            saturated = dist.get("0.9-1.0", 0)
            violations = []
            if n_bindings < 0.80 * baseline["n_bindings"]:
                violations.append(f"n_bindings {n_bindings} < 80% of {baseline['n_bindings']}")
            if total_str < 0.70 * baseline["strength"]:
                violations.append(f"total_strength {total_str:.1f} < 70% of {baseline['strength']:.1f}")
            if saturated < 0.90 * baseline["saturated"]:
                violations.append(f"saturated {saturated} < 90% of {baseline['saturated']}")
            if violations:
                # AUTO-REPAUSE
                os.environ["DECAY_PAUSED"] = "1"
                reason = "; ".join(violations)
                _guala._log_substrate_event("cascade_auto_triggered",
                                             tick=_guala.tick, violations=violations,
                                             n_bindings=n_bindings,
                                             total_strength=round(total_str, 2),
                                             saturated=saturated)
                print(f"[CASCADE] AUTO-REPAUSE TRIGGERED: {reason}")
                _cascade_monitor_running = False
                return
            print(f"[CASCADE] OK: bindings={n_bindings} str={total_str:.1f} sat={saturated}")
        print(f"[CASCADE] Monitor stopped")

    _cascade_monitor_task = asyncio.ensure_future(_monitor())
    return {"cascade_monitor": "started", "baseline": baseline, "interval_s": interval}


@app.post("/api/v1/gualaloom/admin/stop_cascade_monitor")
async def admin_stop_cascade_monitor():
    """Stop cascade monitor."""
    global _cascade_monitor_running
    _cascade_monitor_running = False
    return {"cascade_monitor": "stopped"}


# GL-BRIEF-CHITRACE: read-only chi-geometry readout
class ChiTraceRequest(BaseModel):
    picture_ids: list = []
    sound_ids: list = []
    input_text: str = ""

@app.post("/api/v1/gualaloom/chi_trace")
async def chi_trace(req: ChiTraceRequest):
    """Read-only chi-geometry readout. No state mutation."""
    _gl_init()
    if _guala is None:
        return JSONResponse({"error": "initializing"}, status_code=503)
    if not req.picture_ids and not req.sound_ids and not req.input_text:
        return JSONResponse({"error": "at least one of picture_ids, sound_ids, or input_text required"}, status_code=400)

    result = {"tick": _guala.tick}

    # Input chis
    if req.input_text:
        result["input_chis"] = _guala._chis_for_text(req.input_text)
    else:
        result["input_chis"] = []

    # Refs
    refs = {}
    all_ids = [(pid, "picture") for pid in (req.picture_ids or [])] + \
              [(sid, "sound") for sid in (req.sound_ids or [])]
    for item_id, kind in all_ids:
        ref = {"kind": kind, "title": None, "n_chis": 0, "chis": [], "_note": None}

        if kind == "picture":
            pic = _guala._pictures.get(item_id)
            if pic is None:
                ref["_note"] = "item not found"
                refs[item_id] = ref
                continue
            ref["title"] = pic.title

            # Reverse map: find sight motifs whose source_history contains this item_id
            item_chis = []
            for sm in _guala.sight.motifs:
                if item_id in sm.source_history:
                    # Find atlas entries for this motif in the sight section
                    for chi_key, entries in _guala.atlas.entries.items():
                        for e in entries:
                            if e.get("section") == "sight" and e.get("motif") == sm.motif_id:
                                deep_prior = _guala.deep_atlas.get_prior(chi_key, "sight", sm.motif_id)
                                # Cross-modal neighbors
                                assoc = _guala.atlas.query_associations("sight", chi_key)
                                neighbors = {}
                                for sec_name, motif_list in assoc.items():
                                    top5 = sorted(motif_list, key=lambda x: x[1], reverse=True)[:5]
                                    neighbors[sec_name] = [{"motif": m, "strength": round(s, 3)} for m, s in top5]
                                item_chis.append({
                                    "chi": chi_key,
                                    "binding_strength": round(e["strength"], 3),
                                    "encoded_strength": round(e.get("encoded_strength", 0), 3),
                                    "dwell_ticks": e.get("dwell_ticks", 0),
                                    "reinforcement_count": e.get("reinforcement_count", 0),
                                    "deep_prior": round(deep_prior, 3),
                                    "in_deep": deep_prior > 0,
                                    "cross_modal_neighbors": neighbors,
                                })
            # Sort by strength, cap at 16
            item_chis.sort(key=lambda x: x["binding_strength"], reverse=True)
            ref["chis"] = item_chis[:16]
            ref["n_chis"] = len(item_chis)

        elif kind == "sound":
            snd = _guala._sounds.get(item_id)
            if snd is None:
                ref["_note"] = "item not found"
                refs[item_id] = ref
                continue
            ref["title"] = snd.get("title", item_id)
            # Sound→chi: audio_* sections in atlas keyed by deterministic_motif_id(item_id)
            target_motif = deterministic_motif_id(item_id)
            item_chis = []
            for chi_key, entries in _guala.atlas.entries.items():
                for e in entries:
                    if e.get("section", "").startswith("audio_") and e.get("motif") == target_motif:
                        deep_prior = _guala.deep_atlas.get_prior(chi_key, e["section"], target_motif)
                        assoc = _guala.atlas.query_associations(e["section"], chi_key)
                        neighbors = {}
                        for sec_name, motif_list in assoc.items():
                            top5 = sorted(motif_list, key=lambda x: x[1], reverse=True)[:5]
                            neighbors[sec_name] = [{"motif": m, "strength": round(s, 3)} for m, s in top5]
                        item_chis.append({
                            "chi": chi_key,
                            "section": e["section"],
                            "binding_strength": round(e["strength"], 3),
                            "encoded_strength": round(e.get("encoded_strength", 0), 3),
                            "dwell_ticks": e.get("dwell_ticks", 0),
                            "reinforcement_count": e.get("reinforcement_count", 0),
                            "deep_prior": round(deep_prior, 3),
                            "in_deep": deep_prior > 0,
                            "cross_modal_neighbors": neighbors,
                        })
            item_chis.sort(key=lambda x: x["binding_strength"], reverse=True)
            ref["chis"] = item_chis[:16]
            ref["n_chis"] = len(item_chis)
            if not item_chis:
                ref["_note"] = "no audio-section bindings found for this sound"

        refs[item_id] = ref
    result["refs"] = refs

    # Input chi neighborhoods
    if result["input_chis"]:
        neighborhoods = {}
        for chi_val in set(result["input_chis"]):
            by_section = {}
            for d in range(-_guala.atlas.band, _guala.atlas.band + 1):
                for e in _guala.atlas.entries.get(chi_val + d, []):
                    if e["strength"] < 0.01:
                        continue
                    sec = e["section"]
                    if sec not in by_section:
                        by_section[sec] = []
                    deep_prior = _guala.deep_atlas.get_prior(chi_val + d, sec, e["motif"])
                    by_section[sec].append({
                        "motif_id": e["motif"],
                        "strength": round(e["strength"], 3),
                        "in_deep": deep_prior > 0,
                    })
            # Sort each section by strength, cap at 5
            for sec in by_section:
                by_section[sec] = sorted(by_section[sec], key=lambda x: x["strength"], reverse=True)[:5]
            if by_section:
                neighborhoods[str(chi_val)] = {"by_section": by_section}
        result["input_chi_neighborhoods"] = neighborhoods
    else:
        result["input_chi_neighborhoods"] = {}

    # Hard-cap response at 64KB
    resp_str = json.dumps(result)
    if len(resp_str) > 65536:
        # Truncate cross_modal_neighbors first
        for ref in result["refs"].values():
            for c in ref.get("chis", []):
                c["cross_modal_neighbors"] = {}
        result["_truncated"] = True

    return result


# ════════════════════════════════════════════════════════════════
# v7: Substrate event stream (SSE) + sleep endpoint
# GUALALOOM-V7-AUTONOMY-WC-2026-06-06
# ════════════════════════════════════════════════════════════════

@app.get("/api/v1/gualaloom/events")
async def gualaloom_events(since: int = 0, stream: bool = False):
    """Substrate events. ?stream=true for SSE, default returns JSON array."""
    _gl_init()
    if stream:
        import asyncio

        async def event_generator():
            last_tick = since
            while True:
                events = _guala.get_recent_events(since_tick=last_tick, limit=50)
                for ev in events:
                    if ev["tick"] > last_tick:
                        last_tick = ev["tick"]
                    yield f"data: {json.dumps(ev)}\n\n"
                await asyncio.sleep(1.0)

        return StreamingResponse(event_generator(), media_type="text/event-stream")
    else:
        events = _guala.get_recent_events(since_tick=since, limit=50)
        return {"events": events}


@app.post("/api/v1/gualaloom/sleep")
async def gualaloom_sleep():
    """Manual sleep trigger."""
    _gl_init()
    result = _guala.manual_sleep()
    return result


# ════════════════════════════════════════════════════════════════
# v7 Phase 5: Upload endpoints
# GUALALOOM-V7-AUTONOMY-WC-2026-06-06
# ════════════════════════════════════════════════════════════════

@app.post("/api/v1/gualaloom/upload/book")
async def gualaloom_upload_book(file: UploadFile = File(...)):
    """Upload a text file as a new corpus for autonomous reading."""
    _gl_init()
    if not file.filename.endswith('.txt'):
        raise HTTPException(400, "Book must be a .txt file")
    content = await file.read()
    if len(content) > 1024 * 1024:
        raise HTTPException(400, "File too large (max 1MB)")
    try:
        text = content.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(400, "File must be UTF-8")
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        raise HTTPException(400, "File is empty")
    title = file.filename.replace('.txt', '').replace('_', ' ')
    corpus_id = file.filename.replace('.txt', '').replace(' ', '_').lower()
    _guala._corpora[corpus_id] = CorpusItem(
        corpus_id=corpus_id, title=title, lines=lines)
    _guala._log_substrate_event("corpus_added",
                                corpus_id=corpus_id, title=title,
                                n_lines=len(lines))
    return {"message": f"added \"{title}\" ({len(lines)} lines) to her library",
            "corpus_id": corpus_id}


@app.post("/api/v1/gualaloom/upload/picture")
async def gualaloom_upload_picture(file: UploadFile = File(...)):
    """Upload a picture for visual perception. C8: decode in executor."""
    _gl_init()
    import asyncio as _aio, hashlib
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(400, "File too large (max 10MB)")
    _fname = file.filename
    def _decode():
        t0 = time.time()
        try:
            from PIL import Image
            import io as _io
            img_full = Image.open(_io.BytesIO(content))
            if img_full.mode not in ('RGB', 'L'):
                img_full = img_full.convert('RGB')
            orig_w, orig_h = img_full.size
            grid = np.array(img_full.convert('L').resize((64, 64)), dtype=np.float64) / 255.0
        except Exception as e:
            print(f"[decode-upload-picture] {time.time()-t0:.2f}s ERROR")
            return {"error": f"Cannot decode image: {e}"}
        item_id = hashlib.md5(content).hexdigest()[:12]
        title = _fname or item_id
        pic_dir = os.path.join(STATE_DIR, "pictures")
        os.makedirs(pic_dir, exist_ok=True)
        ext = (_fname or "img").rsplit('.', 1)[1] if '.' in (_fname or "") else 'jpg'
        orig_path = os.path.join(pic_dir, f"{item_id}_original.{ext}")
        with open(orig_path, 'wb') as f:
            f.write(content)
        pic = PictureItem(item_id=item_id, title=title,
                          intensity_grid=grid, source="upload",
                          shown_at_tick=_guala.tick)
        pic.original_path = orig_path
        pic.original_width = orig_w
        pic.original_height = orig_h
        _guala._pictures[item_id] = pic
        _guala._log_substrate_event("picture_uploaded",
                                    item_id=item_id, title=title)
        print(f"[decode-upload-picture] {time.time()-t0:.2f}s")
        return {"message": f"picture \"{title}\" uploaded ({grid.shape[0]}x{grid.shape[1]})",
                "item_id": item_id}
    result = await _aio.get_event_loop().run_in_executor(None, _decode)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result


@app.post("/api/v1/gualaloom/upload/sound")
async def gualaloom_upload_sound(file: UploadFile = File(...)):
    """A1 (042): Sound upload — decode, transduce, register for attention."""
    _gl_init()
    if _guala is None:
        return {"message": "initializing..."}
    import hashlib
    content = await file.read()
    item_id = hashlib.md5(content).hexdigest()[:12]
    title = file.filename or item_id
    # Save original to EFS
    sound_dir = os.path.join(STATE_DIR, "sounds")
    os.makedirs(sound_dir, exist_ok=True)
    orig_path = os.path.join(sound_dir, f"{item_id}.audio")
    with open(orig_path, 'wb') as f:
        f.write(content)
    # Process via /addsound: command path (reuse existing cochlear pipeline)
    import base64
    b64 = base64.b64encode(content).decode()
    # Simulate the command
    from pydantic import BaseModel
    class FakeMsg(BaseModel):
        text: str
        command: str = ""
        source: str = None
    fake = FakeMsg(text=b64, command=f"/addsound:{title}")
    result = await gualaloom_chat(fake)
    return result


@app.post("/api/v1/gualaloom/upload/video")
async def gualaloom_upload_video(file: UploadFile = File(...)):
    """Upload a video for visual perception. C8: decode in executor."""
    _gl_init()
    import asyncio as _aio, hashlib, tempfile, subprocess
    content = await file.read()
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(400, "File too large (max 50MB)")
    _fname = file.filename
    def _decode():
        t0 = time.time()
        item_id = hashlib.md5(content).hexdigest()[:12]
        title = _fname or item_id
        tmp_dir = tempfile.mkdtemp(prefix="guala_vid_")
        video_path = os.path.join(tmp_dir, "input.mp4")
        with open(video_path, "wb") as f:
            f.write(content)
        frame_dir = os.path.join(tmp_dir, "frames")
        os.makedirs(frame_dir, exist_ok=True)
        audio_path = os.path.join(tmp_dir, "audio.wav")
        try:
            subprocess.run([
                "ffmpeg", "-i", video_path, "-vf",
                "scale=160:120,format=gray", "-r", "15",
                os.path.join(frame_dir, "frame_%05d.png"),
                "-y", "-loglevel", "error"
            ], check=True, timeout=60)
            subprocess.run([
                "ffmpeg", "-i", video_path, "-vn", "-ar", "16000",
                "-ac", "1", audio_path,
                "-y", "-loglevel", "error"
            ], timeout=60)
        except FileNotFoundError:
            print(f"[decode-video] {time.time()-t0:.2f}s ERROR: no ffmpeg")
            return {"message": "ffmpeg not available"}
        except Exception as e:
            print(f"[decode-video] {time.time()-t0:.2f}s ERROR")
            return {"message": f"video decode error: {e}"}
        frame_files = sorted(f for f in os.listdir(frame_dir) if f.endswith('.png'))
        for fname in frame_files:
            from PIL import Image
            fpath = os.path.join(frame_dir, fname)
            img = Image.open(fpath).convert('L')
            arr = np.array(img, dtype=np.float64) / 255.0
            np.save(fpath.replace('.png', '.npy'), arr)
        n_frames = len(frame_files)
        duration_ms = int(n_frames / 15.0 * 1000)
        vid = VideoItem(item_id=item_id, title=title,
                        frame_dir=frame_dir,
                        audio_path=audio_path if os.path.exists(audio_path) else "",
                        duration_ms=duration_ms, n_frames=n_frames,
                        source="upload", shown_at_tick=_guala.tick)
        _guala._videos[item_id] = vid
        _guala._log_substrate_event("video_uploaded",
                                    item_id=item_id, title=title,
                                    n_frames=n_frames, duration_ms=duration_ms)
        print(f"[decode-video] {time.time()-t0:.2f}s")
        return {"message": f"video \"{title}\" decoded ({n_frames} frames, {duration_ms}ms)",
                "item_id": item_id}
    return await _aio.get_event_loop().run_in_executor(None, _decode)


# ════════════════════════════════════════════════════════════════
# Deep multimodal substrate — parallel test endpoint
# GL-CMD-DEPLOY-DEEP-SUBSTRATE-WC-20260608-01
# ════════════════════════════════════════════════════════════════

_substrate = None

def _get_substrate():
    global _substrate
    if _substrate is None:
        _substrate = _init_substrate()
    return _substrate

def _init_substrate():
    from dsf_ai_service.substrate.GL_MDL_MULTIMODAL_DEEP_WC_20260608_03 import DeepMultiModalCognition
    cog = DeepMultiModalCognition()
    SENSORY_WORDS = ["moon", "cow", "bears", "stars", "kittens", "room"]
    OTHER_WORDS = ["the", "and", "a", "in", "was", "goodnight", "of",
                   "picture", "over", "there", "were", "three", "little", "sitting", "on",
                   "great", "green", "telephone", "red", "balloon",
                   "chairs", "jumping", "air", "noises", "everywhere"]
    for w in SENSORY_WORDS + OTHER_WORDS:
        cog.install_word(w)
    for _ in range(5):
        for w in SENSORY_WORDS:
            cog.hear_word_with_senses(w)
            cog.run(8)
    GOODNIGHT_MOON = """in the great green room there was a telephone and a red balloon.
and a picture of the cow jumping over the moon.
and there were three little bears sitting on chairs.
goodnight room. goodnight moon.
goodnight cow jumping over the moon.
goodnight light and the red balloon.
goodnight bears. goodnight chairs.
goodnight kittens. goodnight mittens.
goodnight stars. goodnight air. goodnight noises everywhere."""
    sentences = [s.strip() for s in GOODNIGHT_MOON.replace("\n", " ").split(".") if s.strip()]
    SENSORY_SET = set(SENSORY_WORDS)
    for _ in range(3):
        for sent in sentences:
            words = sent.lower().replace(",", "").split()
            for w in words:
                w_clean = "".join(c for c in w if c.isalnum())
                if w_clean in SENSORY_SET and w_clean in cog.sections["word"]:
                    cog.hear_word_with_senses(w_clean)
                elif w_clean in cog.sections["word"]:
                    cog.fire("word", w_clean)
                cog.run(3)
            cog.run(4)
    print(f"[Substrate] Initialized")
    return cog


class SubstrateHearRequest(BaseModel):
    word: str

class SubstrateFeedRequest(BaseModel):
    word: str
    modalities: List[str] = ["visual", "audio"]


@app.post("/substrate/hear_word")
async def substrate_hear_word(req: SubstrateHearRequest):
    cog = _get_substrate()
    word = req.word
    cog.emissions.clear()
    cog.run(15)
    cog.emissions.clear()
    cog.fire("word", word, salience=2.5)
    em = cog.run(25)
    first_per_section = {}
    strongest_per_section = {}
    for e in em:
        sec = e["section"]
        if sec not in first_per_section:
            first_per_section[sec] = e["label"]
        if sec not in strongest_per_section or e["activation"] > strongest_per_section[sec]["activation"]:
            strongest_per_section[sec] = {"label": e["label"], "activation": e["activation"]}
    # Bridge: relay multimodal winner to v7 default session (spec 4.2)
    result = {"first": first_per_section, "strongest": strongest_per_section}
    try:
        from dsf_ai_service.substrate.v7_engine import get_or_create_session
        v7_session = get_or_create_session("default", engine=_guala)
        bridge = _get_bridge(v7_session)
        # Use the heard word directly (attention_focus decays after 20 ticks)
        bridge_result = bridge.multimodal_winner_to_v7(word)
        if bridge_result:
            result["bridge_mm_to_v7"] = bridge_result
    except Exception:
        pass
    return result


@app.post("/substrate/feed_senses")
async def substrate_feed_senses(req: SubstrateFeedRequest):
    cog = _get_substrate()
    word = req.word
    modalities = req.modalities
    cog.emissions.clear()
    cog.run(15)
    cog.emissions.clear()
    for modality in modalities:
        modal_label = f"{word}__{modality}"
        if modal_label in cog.sections.get(modality, {}):
            cog.fire(modality, modal_label, salience=2.5, set_focus=False)
    em = cog.run(25)
    word_em = [e for e in em if e["section"] == "word"]
    if not word_em:
        return {"strongest_word": None, "top_words": []}
    strongest = max(word_em, key=lambda e: e["activation"])
    unique = []
    for e in word_em:
        if e["label"] not in unique:
            unique.append(e["label"])
    return {"strongest_word": strongest["label"], "activation": strongest["activation"],
            "top_words": unique[:5]}


# ════════════════════════════════════════════════════════════════
# v7 DNA Recipe Substrate
# GL-CMD-DEPLOY-DNA-RECIPE-WC-20260608-01
# ════════════════════════════════════════════════════════════════

import uuid as _uuid

class V7ConverseRequest(BaseModel):
    text: str
    session_id: Optional[str] = None

class V7FeedbackRequest(BaseModel):
    session_id: str
    correct: bool
    expected_tokens: Optional[Dict] = None

def _get_bridge(session):
    """Get or create a bridge between a v7 session and the multimodal substrate."""
    from dsf_ai_service.substrate.gl_bridge import SubstrateBridge
    if not hasattr(session, '_bridge') or session._bridge is None:
        mm = _get_substrate()
        session._bridge = SubstrateBridge(session, mm)
    return session._bridge

@app.post("/v7/converse")
async def v7_converse(req: V7ConverseRequest):
    if _guala is None:
        raise HTTPException(status_code=503, detail={
            "error": "guala_not_ready",
            "retry_after_seconds": 10,
            "message": "she is still loading — try again in a moment"
        })
    from dsf_ai_service.substrate.v7_engine import get_or_create_session, save_session
    sid = req.session_id or str(_uuid.uuid4())[:8]
    session = get_or_create_session(sid, engine=_guala)
    result = session.converse(req.text)
    # Bridge: relay v7 emissions to multimodal (spec 4.2)
    try:
        bridge = _get_bridge(session)
        tokens = [t.get("token", "") for t in result.get("response_tokens", [])]
        if tokens:
            bridge_result = bridge.v7_emission_to_multimodal(tokens)
            if bridge_result:
                result["bridge_v7_to_mm"] = bridge_result
    except Exception:
        pass
    try:
        import asyncio as _a7; await _a7.get_event_loop().run_in_executor(None, save_session, session)
    except Exception:
        pass
    result["session_id"] = sid
    return result

@app.post("/v7/feedback")
async def v7_feedback(req: V7FeedbackRequest):
    if _guala is None:
        raise HTTPException(status_code=503, detail={
            "error": "guala_not_ready",
            "retry_after_seconds": 10,
            "message": "she is still loading — try again in a moment"
        })
    from dsf_ai_service.substrate.v7_engine import get_or_create_session, save_session
    session = get_or_create_session(req.session_id, engine=_guala)
    result = session.apply_feedback(req.correct, req.expected_tokens)
    try:
        import asyncio as _a7; await _a7.get_event_loop().run_in_executor(None, save_session, session)
    except Exception:
        pass
    result["session_id"] = req.session_id
    return result

@app.get("/v7/state")
async def v7_state(session_id: str = "default"):
    if _guala is None:
        raise HTTPException(status_code=503, detail={
            "error": "guala_not_ready",
            "retry_after_seconds": 10,
            "message": "she is still loading — try again in a moment"
        })
    from dsf_ai_service.substrate.v7_engine import get_or_create_session
    session = get_or_create_session(session_id, engine=_guala)
    return session.get_state(engine=_guala)

@app.post("/v7/quiet")
async def v7_quiet(session_id: str = "default", n_ticks: int = 10):
    """Quiet ticks — substrate's Default Mode. Replay + consolidation."""
    if _guala is None:
        raise HTTPException(status_code=503, detail={
            "error": "guala_not_ready",
            "retry_after_seconds": 10,
            "message": "she is still loading — try again in a moment"
        })
    from dsf_ai_service.substrate.v7_engine import get_or_create_session, save_session
    session = get_or_create_session(session_id, engine=_guala)
    results = session.quiet_tick(min(n_ticks, 50))
    try:
        import asyncio as _a7; await _a7.get_event_loop().run_in_executor(None, save_session, session)
    except Exception:
        pass
    total_replayed = sum(len(r["replayed"]) for r in results)
    total_commits = sum(len(r["commits"]) for r in results)
    return {"session_id": session_id, "ticks": len(results),
            "replayed": total_replayed, "commits": total_commits}


@app.post("/v7/save")
async def v7_save(session_id: str = "default"):
    """Manual save — Joe can hit this before risky operations."""
    if _guala is None:
        raise HTTPException(status_code=503, detail={
            "error": "guala_not_ready",
            "retry_after_seconds": 10,
            "message": "she is still loading — try again in a moment"
        })
    from dsf_ai_service.substrate.v7_engine import get_or_create_session, save_session
    session = get_or_create_session(session_id, engine=_guala)
    try:
        import asyncio as _a7; await _a7.get_event_loop().run_in_executor(None, save_session, session)
        data = session.to_json()
        return {"saved": True, "session_id": session_id,
                "schema_version": data.get("schema_version"),
                "tick": data.get("tick"),
                "n_sections": len(data.get("sections", {})),
                "vocab_size": sum(len(v) for v in session.vocab.values())}
    except Exception as e:
        return {"saved": False, "error": str(e)}

@app.get("/v7/persistence")
async def v7_persistence(session_id: str = "default"):
    """Check persistence health — is session state on disk?"""
    import os, json as _json
    from dsf_ai_service.substrate.v7_engine import STATE_DIR
    path = os.path.join(STATE_DIR, f"{session_id}.json")
    if not os.path.exists(path):
        return {"on_disk": False, "session_id": session_id, "path": path}
    try:
        stat = os.stat(path)
        with open(path) as f:
            data = _json.load(f)
        return {
            "on_disk": True, "session_id": session_id,
            "file_size_bytes": stat.st_size,
            "last_modified": stat.st_mtime,
            "schema_version": data.get("schema_version"),
            "tick": data.get("tick"),
            "n_sections": len(data.get("sections", {})),
        }
    except Exception as e:
        return {"on_disk": True, "error": str(e)}

@app.get("/v6/events_histogram")
async def v6_events_histogram():
    """Histogram of event types in Guala's events log."""
    import os as _os
    from collections import Counter as _Counter
    log_path = _os.path.join(STATE_DIR, "events.log")
    if not _os.path.exists(log_path):
        return {"error": "no events log"}
    hist = _Counter()
    total = 0
    with open(log_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
                hist[ev.get("type", "unknown")] += 1
                total += 1
            except Exception:
                hist["parse_error"] += 1
    return {"total": total, "histogram": dict(hist.most_common())}


# ════════════════════════════════════════════════════════════════
# Health check
# ════════════════════════════════════════════════════════════════

_init_complete = False  # V2: health gate

@app.on_event("startup")
async def startup():
    global _init_complete
    result = initialize_integrity()
    print(f"[DSF-AI] Integrity initialized: {result['files_present']}/{result['files_checked']} files hashed")

    # V2 EAGER INIT: initialize in background so health check passes immediately
    import asyncio
    async def _eager_init():
        global _init_complete
        loop = asyncio.get_event_loop()
        t0 = time.time()
        await loop.run_in_executor(None, _gl_init)
        dt = time.time() - t0
        print(f"[DSF-AI] Guala initialized in {dt:.1f}s")
        _init_complete = True
        # D3: S3 backup after init
        try:
            await loop.run_in_executor(None, _backup_to_s3, STATE_DIR)
        except Exception as e:
            print(f"[DSF-AI] Startup S3 backup failed: {e}")
    asyncio.ensure_future(_eager_init())

    # Server-side background replay for v7 sessions
    import asyncio
    async def _background_replay():
        """Run quiet_tick on idle sessions every 15s."""
        from dsf_ai_service.substrate.v7_engine import _sessions, _sessions_lock, save_session
        while True:
            await asyncio.sleep(15)
            try:
                with _sessions_lock:
                    session_ids = list(_sessions.keys())
                for sid in session_ids:
                    with _sessions_lock:
                        session = _sessions.get(sid)
                    if session is None:
                        continue
                    idle = time.time() - getattr(session, '_last_converse_time', 0)
                    if idle > 30:
                        try:
                            results = session.quiet_tick(3)
                            total_c = sum(len(r.get("commits", [])) for r in results)
                            if total_c > 0:
                                print(f"[v7-replay] session={sid}: {total_c} commits from replay")
                            loop = asyncio.get_event_loop()
                            await loop.run_in_executor(None, save_session, session)
                        except Exception:
                            pass
            except Exception:
                pass
    asyncio.ensure_future(_background_replay())

    # N2: Periodic save + backup in executor (never blocks event loop)
    def _do_save_and_compact():
        """Runs in thread pool — never blocks health checks."""
        t0 = time.time()
        pre_size = _guala.events_log_size(STATE_DIR)
        _guala.save_full_state(STATE_DIR)
        _guala.compact_events(STATE_DIR, keep_after_offset=pre_size)
        dt = time.time() - t0
        print(f"[save] {dt:.2f}s")
        return dt

    async def _periodic_v6_save():
        save_count = 0
        loop = asyncio.get_event_loop()
        while True:
            await asyncio.sleep(60)
            try:
                if _guala is not None:
                    await loop.run_in_executor(None, _do_save_and_compact)
                    save_count += 1
                    if save_count % 10 == 0:
                        def _snap():
                            return _guala.snapshot_state(STATE_DIR, reason="periodic")
                        snap_dir = await loop.run_in_executor(None, _snap)
                        print(f"[v6] Snapshot: {snap_dir}")
            except Exception as e:
                print(f"[save] error: {e}")
    asyncio.ensure_future(_periodic_v6_save())

    # Daily S3 backup (also in executor)
    async def _daily_s3_backup():
        loop = asyncio.get_event_loop()
        while True:
            await asyncio.sleep(86400)
            try:
                if _guala is not None:
                    await loop.run_in_executor(None, _backup_to_s3, STATE_DIR)
            except Exception as e:
                print(f"[DSF-AI] S3 backup error: {e}")
    asyncio.ensure_future(_daily_s3_backup())


_last_s3_backup = None  # D3: tracked for persistence_health

def _restore_from_s3(state_dir):
    """P0: Restore state files from most recent S3 backup."""
    import boto3
    s3 = boto3.client("s3", region_name="us-east-1")
    bucket = "dsf-ai-site-backups"
    # Find most recent backup prefix
    resp = s3.list_objects_v2(Bucket=bucket, Prefix="guala/", Delimiter="/")
    prefixes = sorted([p["Prefix"] for p in resp.get("CommonPrefixes", [])], reverse=True)
    if not prefixes:
        raise RuntimeError("No S3 backups found")
    latest = prefixes[0]
    print(f"[GualaLoom] Restoring from {latest}")
    # Download all files
    objs = s3.list_objects_v2(Bucket=bucket, Prefix=latest)
    for obj in objs.get("Contents", []):
        key = obj["Key"]
        filename = key[len(latest):]
        if "/" in filename:
            # pictures/xxx.npy → state/pictures/xxx.npy
            subdir = os.path.join(state_dir, os.path.dirname(filename))
            os.makedirs(subdir, exist_ok=True)
        local_path = os.path.join(state_dir, filename)
        s3.download_file(bucket, key, local_path)
    print(f"[GualaLoom] Restored {len(objs.get('Contents', []))} files from S3")


def _backup_to_s3(state_dir):
    """V4/D3: Copy state files to S3 via boto3 (no aws CLI in container)."""
    global _last_s3_backup
    import boto3
    s3 = boto3.client("s3", region_name="us-east-1")
    bucket = "dsf-ai-site-backups"
    date_str = time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime())
    prefix = f"guala/{date_str}/"
    files = ["guala_core.json", "guala_needs.json", "guala_coordinator.json",
             "guala_atlas.json", "guala_sections.json", "guala_bucket.json",
             "guala_deep_atlas.json", "guala_visual.json", "guala_identity.json",
             "guala_sounds.json", "guala_videos.json"]
    backed = 0
    for f in files:
        path = os.path.join(state_dir, f)
        if os.path.exists(path):
            try:
                s3.upload_file(path, bucket, prefix + f)
                backed += 1
            except Exception as e:
                print(f"[DSF-AI] S3 backup {f} failed: {e}")
    # Also backup picture originals
    pic_dir = os.path.join(state_dir, "pictures")
    if os.path.isdir(pic_dir):
        for pf in os.listdir(pic_dir):
            try:
                s3.upload_file(os.path.join(pic_dir, pf), bucket, prefix + "pictures/" + pf)
            except Exception:
                pass
    _last_s3_backup = {
        "timestamp": date_str,
        "prefix": f"s3://{bucket}/{prefix}",
        "file_count": backed,
    }
    print(f"[DSF-AI] S3 backup: {backed} files to s3://{bucket}/{prefix}")
    return f"s3://{bucket}/{prefix}"


# C3: Graceful SIGTERM — final save + lock release for zero-downtime deploys
@app.on_event("shutdown")
async def shutdown():
    if _guala is not None:
        import asyncio
        loop = asyncio.get_event_loop()
        def _final_save():
            t0 = time.time()
            try:
                _guala.save_full_state(STATE_DIR)
                dt = time.time() - t0
                print(f"[shutdown] final save {dt:.2f}s")
            except Exception as e:
                print(f"[shutdown] save error: {e}")
            _guala.release_lock()
        await loop.run_in_executor(None, _final_save)


@app.get("/health")
async def health():
    # Always return 200 for ALB health checks (ALB kills task on 503).
    # Init status reported in body for observability.
    return {
        "status": "ok" if _init_complete else "initializing",
        "service": "dsf-ai",
        "version": "1.0.0",
        "ready": _init_complete,
    }
