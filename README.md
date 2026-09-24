# Usabilidad docentes · Campus Virtual

Dashboard interactivo que compara el uso del aula virtual (Moodle) por parte de los docentes de **Pregrado Presencial 2026-2** en dos periodos:

- **Periodo 1:** 7 al 20 de septiembre de 2026 (14 días)
- **Periodo 2:** 21 al 24 de septiembre de 2026 (corte 24/09/2026 09:39, 3,4 días)

Abre `index.html` en el navegador. No necesita servidor.

## Qué muestra

- Tiempo de uso docente, en general y por curso.
- Recursos y actividades creados (contenidos, tareas, cuestionarios, foros).
- Porcentaje de docentes y cursos con actividad.
- Filtro jerárquico Facultad → Programa → Curso, construido a partir de `categorias_jerarquia`, y buscador por docente o curso.
- Vista en totales o en promedio por día. La variación siempre compara el ritmo diario, porque los periodos no duran lo mismo.
- Tablas de detalle por curso y por docente.

## Cómo actualizarlo

1. Exporta el informe de Configurable Reports de cada periodo a Excel y guárdalo en la raíz del repositorio como `07-20sep.xlsx` y `21-24sep.xlsx`. Los Excel no se suben a GitHub.
2. Ejecuta:

   ```bash
   python build/build.py
   ```

   El script lee los dos Excel, cruza profesor + curso y genera `index.html` con los datos incluidos.

Requisitos: Python 3 con `pandas` y `openpyxl`.

## Notas de cálculo

- **Tiempo de uso:** es una estimación a partir del log de Moodle. Se suma el tiempo entre clics consecutivos y se descartan las pausas de más de 30 minutos.
- **Recursos creados:** se cuentan por curso (`course_modules.added`), una sola vez aunque el curso tenga varios docentes.
- `index.html` contiene nombres y usuarios de docentes: mantén este repositorio **privado**.
