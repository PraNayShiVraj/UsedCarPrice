"""Used Car Price Predictor — Streamlit app with premium UI.

Run the notebook (used_car_bda.ipynb) first so that models/price_model and
models/model_metadata.json exist, then start this app with:

    streamlit run app.py
"""
import datetime as dt
import json
import math
from pathlib import Path

import pandas as pd
import streamlit as st

BASE = Path(__file__).resolve().parent
META_PATH = BASE / "models" / "model_metadata.json"
MODEL_PATH = BASE / "models" / "price_model"

# ──────────────────────────────────────────────────────────────────────────────
# Page config & global CSS
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Used Car Price Predictor",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Root / Background ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background: linear-gradient(135deg, #0f0c29, #1a1a2e, #16213e);
    min-height: 100vh;
}

/* ── Hide default header/footer ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Hero banner ── */
.hero {
    background: linear-gradient(135deg, rgba(99,102,241,0.25), rgba(168,85,247,0.15));
    border: 1px solid rgba(99,102,241,0.35);
    border-radius: 20px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    backdrop-filter: blur(12px);
    text-align: center;
}
.hero h1 {
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(90deg, #818cf8, #c084fc, #f472b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 0.4rem 0;
    letter-spacing: -1px;
}
.hero p {
    color: #94a3b8;
    font-size: 1.05rem;
    margin: 0;
}
.hero .badge {
    display: inline-block;
    background: rgba(99,102,241,0.2);
    border: 1px solid rgba(99,102,241,0.4);
    color: #a5b4fc;
    padding: 0.25rem 0.9rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    margin-bottom: 1rem;
}

/* ── Section cards ── */
.section-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 16px;
    padding: 1.6rem 1.8rem 1rem;
    margin-bottom: 1.5rem;
    backdrop-filter: blur(8px);
}
.section-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #c084fc;
    letter-spacing: 0.03em;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1.1rem;
    border-bottom: 1px solid rgba(192,132,252,0.15);
    padding-bottom: 0.6rem;
}

/* ── Streamlit widget tweaks ── */
div[data-baseweb="select"] > div {
    background-color: rgba(255,255,255,0.06) !important;
    border-color: rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}
div[data-baseweb="select"] > div:hover {
    border-color: rgba(99,102,241,0.6) !important;
}
input[type="number"] {
    background-color: rgba(255,255,255,0.06) !important;
    border-color: rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}
label {
    color: #cbd5e1 !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
}

/* ── Primary button ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 2.5rem !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.03em !important;
    color: #fff !important;
    box-shadow: 0 4px 24px rgba(99,102,241,0.45) !important;
    transition: all 0.25s ease !important;
    width: 100%;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 32px rgba(139,92,246,0.55) !important;
}

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: rgba(99,102,241,0.12);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 14px;
    padding: 1rem 1.4rem !important;
    backdrop-filter: blur(8px);
}
[data-testid="metric-container"] label {
    color: #a5b4fc !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 1.9rem !important;
    font-weight: 800 !important;
    color: #f0f4ff !important;
}

/* ── Price-drop table ── */
.stTable table {
    background: rgba(255,255,255,0.03) !important;
    border-radius: 12px !important;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.07) !important;
}
.stTable thead tr th {
    background: rgba(99,102,241,0.2) !important;
    color: #c084fc !important;
    font-size: 0.85rem !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    border: none !important;
}
.stTable tbody tr td {
    color: #e2e8f0 !important;
    border-color: rgba(255,255,255,0.05) !important;
    font-size: 0.9rem !important;
}

/* ── Result banner ── */
.result-banner {
    background: linear-gradient(135deg, rgba(99,102,241,0.18), rgba(168,85,247,0.12));
    border: 1px solid rgba(99,102,241,0.35);
    border-radius: 16px;
    padding: 1.4rem 2rem;
    margin: 1.2rem 0;
    color: #cbd5e1;
    font-size: 0.95rem;
    line-height: 1.7;
}
.result-banner strong { color: #a5b4fc; }
.result-banner .price-best { color: #34d399; font-weight: 700; }

/* ── Caption ── */
.stCaption { color: #475569 !important; }

/* ── Checkbox ── */
.stCheckbox label { color: #cbd5e1 !important; font-size: 0.9rem !important; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# Hero
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="badge">🤖 AI-Powered &nbsp;·&nbsp; Apache Spark</div>
    <h1>🚗 Used Car Price Predictor</h1>
    <p>Get an instant, data-driven fair market valuation for any used car —<br>
       factoring in condition, damage, history, and more.</p>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# Model check
# ──────────────────────────────────────────────────────────────────────────────
if not META_PATH.exists() or not MODEL_PATH.exists():
    st.error("⚠️ Model files not found. Run **used_car_bda.ipynb** first (it creates the `models/` folder), then reload this page.")
    st.stop()

meta = json.loads(META_PATH.read_text(encoding="utf-8"))
today = dt.date.today()

col_date1, col_date2, _ = st.columns([1, 1, 4])
col_date1.caption(f"📅 Today: **{today:%d %b %Y}**")
col_date2.caption(f"🧠 Model trained: **{meta['trained_at']}**")


# ──────────────────────────────────────────────────────────────────────────────
# Load Spark model
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="⚡ Starting Spark engine and loading the model…")
def load_model():
    import os
    import sys

    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

    if os.name == "nt":
        hh = Path(os.environ.get("HADOOP_HOME", r"C:\hadoop"))
        if (hh / "bin" / "winutils.exe").exists() and (hh / "bin" / "hadoop.dll").exists():
            os.environ["HADOOP_HOME"] = str(hh)
            os.environ["PATH"] = str(hh / "bin") + os.pathsep + os.environ["PATH"]

    from pyspark.ml import PipelineModel
    from pyspark.sql import SparkSession

    spark = (SparkSession.builder.master("local[*]").appName("UsedCarApp")
             .config("spark.driver.host", "127.0.0.1")
             .config("spark.driver.bindAddress", "127.0.0.1")
             .config("spark.ui.enabled", "false")
             .config("spark.sql.shuffle.partitions", "4")
             .config("spark.driver.memory", "2g")
             .getOrCreate())
    spark.sparkContext.setLogLevel("ERROR")
    return spark, PipelineModel.load(str(MODEL_PATH))


spark, model = load_model()

choices    = meta["choices"]
specs      = meta["model_specs"]
rng        = meta["ranges"]
parts      = meta["parts"]
components = meta["components"]
LEVELS     = ["None", "Minor", "Major"]


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
def inr(x):
    """Format a number with Indian digit grouping."""
    x = int(round(x))
    s = str(abs(x))
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        groups = []
        while len(head) > 2:
            groups.insert(0, head[-2:])
            head = head[:-2]
        if head:
            groups.insert(0, head)
        s = ",".join(groups + [tail])
    return f"Rs {'-' if x < 0 else ''}{s}"


def pretty(name):
    return name.replace("_ok", "").replace("_", " ").title()


# ──────────────────────────────────────────────────────────────────────────────
# SECTION 1 · Car Details
# ──────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-card"><div class="section-title">🚙 Car Details</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
brand        = c1.selectbox("Brand", choices["brand"])
model_name   = c2.selectbox("Model", meta["brand_models"][brand])
fuel         = c3.selectbox("Fuel type", list(specs[brand][model_name].keys()))
spec         = specs[brand][model_name][fuel]
transmission = c4.selectbox("Transmission", choices["transmission"])

c5, c6, c7, c8 = st.columns(4)
min_year     = int(rng["year"]["min"])
default_year = int(min(max(rng["year"]["median"], min_year), today.year))
year         = c5.slider("Manufacturing year", min_year, today.year, default_year)
km           = c6.number_input("Km driven", min_value=0,
                               max_value=int(rng["km_driven"]["max"] * 1.5),
                               value=int(rng["km_driven"]["median"]), step=1000)
owner        = c7.selectbox("Owner type", choices["owner"])
location     = c8.selectbox("Location", choices["location"])

key = f"{brand}|{model_name}|{fuel}"
c9, c10, c11, c12 = st.columns(4)
engine  = c9.selectbox("Engine (CC)", spec["engine"], key=f"engine|{key}")
power   = c10.number_input("Max power (bhp)", min_value=1.0, value=float(spec["power"]),
                           step=1.0, key=f"power|{key}")
mileage = c11.number_input("Mileage (kmpl)", min_value=1.0, value=float(spec["mileage"]),
                           step=0.5, key=f"mileage|{key}")
seats   = c12.number_input("Seats", min_value=1, max_value=12, value=int(spec["seats"]),
                           step=1, key=f"seats|{key}")

st.markdown('</div>', unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# SECTION 2 · History & Papers
# ──────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-card"><div class="section-title">📋 History & Papers</div>', unsafe_allow_html=True)

h1, h2, h3, h4, h5 = st.columns(5)
accident  = h1.checkbox("🚨 Accident history", value=False)
acc_count = h2.number_input("# of accidents", min_value=1, max_value=10, value=1, disabled=not accident)
insurance = h3.checkbox("🛡️ Insurance valid", value=True)
service   = h4.checkbox("🔧 Service history", value=True)
tamper    = h5.checkbox("⚠️ Odometer tamper?", value=False)

st.markdown('</div>', unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# SECTION 3 · Working Condition
# ──────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-card"><div class="section-title">⚙️ Working Condition <span style="font-size:0.75rem;font-weight:400;color:#64748b;text-transform:none;">(tick = working)</span></div>', unsafe_allow_html=True)

w_cols  = st.columns(4)
working = {}
for i, comp in enumerate(components):
    working[comp] = w_cols[i % 4].checkbox(pretty(comp), value=True, key=f"work|{comp}")

st.markdown('</div>', unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# SECTION 4 · Damaged Parts
# ──────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-card"><div class="section-title">🔩 Damaged Parts</div>', unsafe_allow_html=True)

d_cols = st.columns(4)
damage = {}
for i, part in enumerate(parts):
    damage[part] = LEVELS.index(d_cols[i % 4].selectbox(pretty(part), LEVELS, key=f"dmg|{part}"))

st.markdown('</div>', unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# Asking price
# ──────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-card"><div class="section-title">💰 Asking Price</div>', unsafe_allow_html=True)
asking = st.number_input(
    "Seller's asking price in INR (leave 0 to skip deal analysis)",
    min_value=0, value=0, step=10000
)
st.markdown('</div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# Prediction helpers
# ──────────────────────────────────────────────────────────────────────────────
def finish(cond):
    c = dict(cond)
    c["damage_score"]  = sum(c[f"{p}_damage"] * w for p, w in meta["part_weights"].items())
    c["working_score"] = (sum(c[k] * w for k, w in meta["component_weights"].items())
                          / sum(meta["component_weights"].values()))
    return c


def build_row(cond):
    age = max(0, today.year - year)
    row = {
        "brand": brand, "model": model_name, "location": location, "fuel": fuel,
        "transmission": transmission, "owner": owner,
        "brand_tier": meta["brand_tier_map"].get(brand, meta["default_brand_tier"]),
        "car_age": float(age), "km_driven": float(km), "km_per_year": float(km) / max(age, 1),
        "engine": float(engine), "power": float(power), "seats": float(seats), "mileage": float(mileage),
        "power_per_cc": float(power) / float(engine),
    }
    row.update({k: float(v) for k, v in finish(cond).items()})
    return row


def predict(conds):
    pdf = pd.DataFrame([build_row(c) for c in conds])[meta["input_columns"]]
    out = model.transform(spark.createDataFrame(pdf)).select("prediction").toPandas()["prediction"]
    return [math.exp(v) for v in out]


def grade_of(cond):
    c = finish(cond)
    r = meta["grade_rule"]
    idx = (r["w_working"] * c["working_score"]
           + r["w_damage"] * (1 - c["damage_score"] / r["damage_max"])
           - r["w_accident"] * c["accident_history"])
    for cutoff, label in zip(r["cutoffs"], r["labels"]):
        if idx < cutoff:
            return label
    return r["labels"][-1]


# ──────────────────────────────────────────────────────────────────────────────
# Predict button (centered)
# ──────────────────────────────────────────────────────────────────────────────
_, btn_col, _ = st.columns([2, 3, 2])
with btn_col:
    predict_clicked = st.button("✨  Predict Price", type="primary", use_container_width=True)

if predict_clicked:
    entered = {
        "accident_history": int(accident), "accident_count": int(acc_count) if accident else 0,
        "insurance_valid": int(insurance), "service_history_available": int(service),
        "odometer_tamper_suspected": int(tamper),
        **{c: int(working[c]) for c in components},
        **{f"{p}_damage": damage[p] for p in parts},
    }
    perfect      = {**entered, "accident_history": 0, "accident_count": 0, "insurance_valid": 1,
                    "service_history_available": 1, "odometer_tamper_suspected": 0,
                    **{c: 1 for c in components}, **{f"{p}_damage": 0 for p in parts}}
    fix_accident = {**entered, "accident_history": 0, "accident_count": 0}
    fix_damage   = {**entered, **{f"{p}_damage": 0 for p in parts}}
    fix_faults   = {**entered, **{c: 1 for c in components}}
    fix_papers   = {**entered, "insurance_valid": 1, "service_history_available": 1, "odometer_tamper_suspected": 0}

    with st.spinner("🔮 Running prediction engine…"):
        price, best, p_acc, p_dmg, p_flt, p_pap = predict(
            [entered, perfect, fix_accident, fix_damage, fix_faults, fix_papers]
        )

    st.markdown("---")

    # Key metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("💎 Fair Market Price", inr(price))
    m2.metric("🏅 Condition Grade", grade_of(entered))
    m3.metric("📉 Discount vs Perfect", inr(max(0, best - price)))

    # Summary banner
    pct_diff = (best - price) / best * 100 if best > 0 else 0
    st.markdown(f"""
    <div class="result-banner">
        🏷️ <strong>Same car in perfect condition</strong> would be valued at
        <span class="price-best">{inr(best)}</span> —
        the current condition lowers the price by approximately
        <strong>{inr(max(0, best - price))}</strong>
        ({pct_diff:.1f}% below ideal).
    </div>
    """, unsafe_allow_html=True)

    # Price drop breakdown
    st.markdown('<div class="section-card"><div class="section-title">📊 Price Drop Breakdown</div>', unsafe_allow_html=True)
    df_issues = pd.DataFrame({
        "Issue": [
            "🚨 Accident history",
            "🔩 Damaged parts",
            "⚙️ Faulty components",
            "📋 Papers (insurance / service / odometer)",
        ],
        "Price lost (approx.)": [
            inr(max(0, p_acc - price)),
            inr(max(0, p_dmg - price)),
            inr(max(0, p_flt - price)),
            inr(max(0, p_pap - price)),
        ],
    })
    st.table(df_issues)
    st.caption("Each row shows how much higher the price would be if only that issue were fixed.")
    st.markdown('</div>', unsafe_allow_html=True)

    # Deal analysis
    if asking > 0:
        ratio = asking / price
        tol   = meta["deal_tolerance"]
        if ratio < 1 - tol:
            st.success(f"✅ **Great deal!** The asking price is **{100*(1-ratio):.0f}%** below the predicted fair price.")
        elif ratio <= 1 + tol:
            st.info("⚖️ **Fair price.** The asking price is close to the predicted market value.")
        else:
            st.warning(f"⚠️ **Overpriced.** The asking price is **{100*(ratio-1):.0f}%** above the predicted fair price.")

# ──────────────────────────────────────────────────────────────────────────────
# Model details expander
# ──────────────────────────────────────────────────────────────────────────────
with st.expander("🔬 Model details"):
    st.write(
        f"**Model:** {meta['best_model']}  |  "
        f"**Trained on:** {meta['rows_used']:,} rows  |  "
        f"**Spark:** {meta['spark_version']}"
    )
    t = meta["metrics"]["test"]
    st.write(
        f"**Test R²:** {t['r2']:.3f}  |  "
        f"**MAE:** {inr(t['mae'])}  |  "
        f"**RMSE:** {inr(t['rmse'])}"
    )
    st.caption("Condition, damage and price-deduction data are simulated assumptions (see the notebook).")
