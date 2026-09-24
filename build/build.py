import pandas as pd, json, os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
# Carpeta con los Excel exportados de Moodle (por defecto, la raíz del repositorio; no se suben a GitHub)
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(HERE)
a = pd.read_excel(os.path.join(SRC, "07-20sep.xlsx"))
b = pd.read_excel(os.path.join(SRC, "21-24sep.xlsx"))
k = ["userid", "course_id"]
m = a.merge(b, on=k, how="outer", suffixes=("_1", "_2"))

# Días efectivos del periodo 2 (corte = última acción registrada)
cut = pd.to_datetime(b.ultima_accion_periodo.replace("Sin actividad", None).dropna()).max()
d2 = round((cut - pd.Timestamp("2026-09-21")).total_seconds() / 86400, 2)

def split(h):
    parts = [p.strip() for p in str(h).split(" > ")][1:]
    fac = parts[0] if parts else "Sin facultad"
    prog = " > ".join(parts[1:]) if len(parts) > 1 else "(Cursos directos de la facultad)"
    return fac, prog

cats, cat_idx = [], {}
courses, course_idx = [], {}
teachers, teacher_idx = [], {}
rows = []
g = lambda r, c: int(r[c]) if pd.notna(r[c]) else 0
for _, r in m.iterrows():
    h = r["categorias_jerarquia_1"] if pd.notna(r["categorias_jerarquia_1"]) else r["categorias_jerarquia_2"]
    fp = split(h)
    if fp not in cat_idx:
        cat_idx[fp] = len(cats); cats.append(list(fp))
    cid = r["course_id"]
    if cid not in course_idx:
        course_idx[cid] = len(courses)
        sn = r["course_shortname_1"] if pd.notna(r["course_shortname_1"]) else r["course_shortname_2"]
        nm = r["course_name_1"] if pd.notna(r["course_name_1"]) else r["course_name_2"]
        courses.append([str(sn).strip(), str(nm).strip(), cat_idx[fp]] +
            [g(r, f"{c}_creados_periodo_{p}" if c != "tareas" else f"tareas_creadas_periodo_{p}")
             for p in (1, 2) for c in ("contenidos", "tareas", "cuestionarios", "foros")])
    uid = r["userid"]
    if uid not in teacher_idx:
        teacher_idx[uid] = len(teachers)
        nm = r["nombre_profesor_1"] if pd.notna(r["nombre_profesor_1"]) else r["nombre_profesor_2"]
        un = r["profesor_1"] if pd.notna(r["profesor_1"]) else r["profesor_2"]
        teachers.append([str(nm).strip(), str(un).strip()])
    rows.append([teacher_idx[uid], course_idx[cid],
                 g(r, "tiempo_dedicado_minutos_1"), g(r, "tiempo_dedicado_minutos_2"),
                 g(r, "acciones_edicion_periodo_1"), g(r, "acciones_edicion_periodo_2"),
                 g(r, "acciones_totales_periodo_1"), g(r, "acciones_totales_periodo_2")])

data = {"p": {"d1": 14, "d2": d2, "cut": cut.strftime("%d/%m/%Y %H:%M")},
        "cats": cats, "courses": courses, "teachers": teachers, "rows": rows}
tpl = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
js = re.sub("�+", "Ñ", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
out = tpl.replace("/*__DATA__*/null", js)
# Documento HTML completo para abrirlo directo en el navegador
out = ('<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
       '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
       '<meta name="robots" content="noindex, nofollow">\n'
       + out.replace("</style>\n", "</style>\n</head>\n<body>\n", 1) + "\n</body>\n</html>\n")
open(os.path.join(os.path.dirname(HERE), "index.html"), "w", encoding="utf-8").write(out)
print("ok", len(rows), len(courses), len(teachers), len(cats), d2, cut, len(out))
