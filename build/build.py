import pandas as pd, json, os, sys, re

HERE = os.path.dirname(os.path.abspath(__file__))
# Carpeta con los Excel exportados de Moodle (por defecto, la raíz del repositorio; no se suben a GitHub)
POS = [a for a in sys.argv[1:] if not a.startswith("--")]
SRC = POS[0] if POS else os.path.dirname(HERE)
# --fragment: genera solo el contenido (sin <html>/<head>), para publicarlo como Artifact
# --out=RUTA: archivo de salida (por defecto index.html en la raíz del repositorio)

# Periodos a comparar, en orden cronológico: (archivo, etiqueta, fecha inicial, fecha final)
PERIODOS = [
    ("07-13sep.xlsx", "7–13 sep", "2026-09-07", "2026-09-13"),
    ("14-20sep.xlsx", "14–20 sep", "2026-09-14", "2026-09-20"),
    ("21-24sep.xlsx", "21–24 sep", "2026-09-21", "2026-09-24"),
]
K = ["userid", "course_id"]

frames, meta = [], []
for i, (f, label, ini, fin) in enumerate(PERIODOS):
    d = pd.read_excel(os.path.join(SRC, f))
    ini, fin = pd.Timestamp(ini), pd.Timestamp(fin)
    fin_exclusivo = fin + pd.Timedelta(days=1)
    # Si el informe se generó antes de terminar el periodo, los días se cuentan hasta la última acción
    ult = pd.to_datetime(d.ultima_accion_periodo.replace("Sin actividad", None).dropna()).max()
    parcial = pd.notna(ult) and ult < fin_exclusivo - pd.Timedelta(hours=1)
    dias = round((ult - ini).total_seconds() / 86400, 2) if parcial else (fin_exclusivo - ini).days
    meta.append({"label": label, "days": dias,
                 "note": f"corte {ult.strftime('%d/%m %H:%M')}" if parcial else "semana completa" if dias == 7 else f"{dias} días"})
    frames.append(d.set_index(K).add_suffix(f"__{i}"))

m = pd.concat(frames, axis=1, join="outer").reset_index()
N = len(PERIODOS)

def first(r, col):
    for i in range(N):
        v = r.get(f"{col}__{i}")
        if pd.notna(v):
            return v
    return ""

def num(r, col, i):
    v = r.get(f"{col}__{i}")
    return int(v) if pd.notna(v) else 0

def split(h):
    parts = [p.strip() for p in str(h).split(" > ")][1:]
    fac = parts[0] if parts else "Sin facultad"
    prog = " > ".join(parts[1:]) if len(parts) > 1 else "(Cursos directos de la facultad)"
    return fac, prog

cats, cat_idx, courses, course_idx, teachers, teacher_idx, rows = [], {}, [], {}, [], {}, []
TIPOS = ("contenidos_creados_periodo", "tareas_creadas_periodo", "cuestionarios_creados_periodo", "foros_creados_periodo")
for _, r in m.iterrows():
    fp = split(first(r, "categorias_jerarquia"))
    if fp not in cat_idx:
        cat_idx[fp] = len(cats); cats.append(list(fp))
    cid, uid = r["course_id"], r["userid"]
    if cid not in course_idx:
        course_idx[cid] = len(courses)
        courses.append([str(first(r, "course_shortname")).strip(), str(first(r, "course_name")).strip(), cat_idx[fp]]
                       + [[num(r, t, i) for t in TIPOS] for i in range(N)])
    if uid not in teacher_idx:
        teacher_idx[uid] = len(teachers)
        teachers.append([str(first(r, "nombre_profesor")).strip(), str(first(r, "profesor")).strip()])
    rows.append([teacher_idx[uid], course_idx[cid],
                 [num(r, "tiempo_dedicado_minutos", i) for i in range(N)],
                 [num(r, "acciones_edicion_periodo", i) for i in range(N)]])

data = {"p": meta, "cats": cats, "courses": courses, "teachers": teachers, "rows": rows}
tpl = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
js = re.sub("�+", "Ñ", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
out = tpl.replace("/*__DATA__*/null", js)
if "--fragment" not in sys.argv:
    # Documento HTML completo para abrirlo directo en el navegador
    out = ('<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
           '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
           '<meta name="robots" content="noindex, nofollow">\n'
           + out.replace("</style>\n", "</style>\n</head>\n<body>\n", 1) + "\n</body>\n</html>\n")
dest = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--out=")), os.path.join(os.path.dirname(HERE), "index.html"))
open(dest, "w", encoding="utf-8").write(out)
print("ok", len(rows), len(courses), len(teachers), len(cats), [p["days"] for p in meta], len(out), dest)
