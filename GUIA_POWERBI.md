# Guía de Integración con Power BI – Proyecto **K‑NN Dinamita**

Esta guía paso a paso te muestra cómo crear un dashboard profesional en **Power BI Desktop** a partir de los archivos generados por el proyecto:

- `resultados/resultados_prueba.csv`
- `resultados/metrics_summary.csv`

> **Nota**: No se modifica ningún archivo Python ni los CSV originales; la guía solo describe las operaciones en Power BI.

---

## 1. Importar los CSV a Power BI

1. Abre **Power BI Desktop**.
2. En la cinta superior, selecciona **Obtener datos → Texto/CSV**.
3. Navega a la carpeta del proyecto:
   ```text
   C:\Users\USUARIO\OneDrive\Desktop\K‑NN‑Dinamita‑main\K‑NN‑Dinamita‑main\resultados
   ```
4. **Primera tabla** – `resultados_prueba.csv`:
   - Selecciona el archivo y pulsa **Abrir**.
   - Power BI mostrará una vista previa. Verifica que la codificación sea **UTF‑8‑BOM** (Power BI la detecta automáticamente).
   - Haz clic en **Cargar**.
5. **Segunda tabla** – `metrics_summary.csv`:
   - Repite los pasos 2‑4 con este archivo.
   - Después de cargar ambos archivos, pasarás al **Editor de consultas** (opcional) donde puedes renombrar las consultas:
     - `resultados_prueba` → **ResultadosPrueba**
     - `metrics_summary` → **ResumenMetricas**
   - Pulsa **Cerrar y aplicar**.

---

## 2. Configuración de relaciones entre tablas

| Tabla | Clave primaria | Clave foránea | Necesaria? |
|-------|----------------|---------------|------------|
| **ResultadosPrueba** | (ninguna) – cada fila es una muestra de prueba | — | **No** |
| **ResumenMetricas** | `K` (valor del k usado) | — | **No** |

Los dos conjuntos de datos no comparten columnas, por lo que **no se necesita crear relaciones**.  Cada tabla se usará de forma independiente en visualizaciones diferentes.  Si deseas filtrar métricas por el mejor `K`, crearás un *segmentador* sobre la columna `K` de **ResumenMetricas**.

---

## 3. Diseño del Dashboard profesional

### Layout sugerido (ejemplo de pantalla)
```
+-----------------------------------------------------------+
|  KPI Row (4 tarjetas)                                     |
|  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────┐ |
|  │ Accuracy    │ │ Precision   │ │ Recall      │ │ F1    │ |
|  └─────────────┘ └─────────────┘ └─────────────┘ └───────┘ |
+-----------------------------------------------------------+
|  Gráfico comparativo de K (línea/bar)                     |
+-----------------------------------------------------------+
|  Matriz de confusión (heatmap)       | Segmentadores     |
|  (Clase_Real vs Clase_Predicha)      | – Variedad (Clase_Real) |
|                                      | – Acierto (True/False) |
+-----------------------------------------------------------+
|  Distribución de predicciones correctas/incorrectas      |
|  (barras apiladas o donut)                              |
+-----------------------------------------------------------+
```

### Paleta de colores recomendada
| Elemento | Color principal | Comentario |
|----------|----------------|------------|
| Fondo del reporte | **#F7F9FC** (gris muy claro) | Reduce fatiga visual |
| Tarjetas KPI | **#0078D4** (azul corporativo) para el valor; texto negro |
| Gráfica de K | **#2E7D32** (verde) para Accuracy, **#C2185B** (magenta) para F1 |
| Heatmap (matriz) | Escala **Blues** – más oscuro = mayor frecuencia |
| Segmentadores | colores neutros (gris) con borde azul activo |

---

## 4. Tarjetas KPI (Accuracy, Precision, Recall, F1‑Score)

1. En la vista **Informe**, inserta **Tarjeta** cuatro veces.
2. Arrastra los siguientes **valores** desde **ResumenMetricas** a cada tarjeta (puedes usar una medida DAX para obtener el mejor `K` automáticamente):
   ```DAX
   MejorK = CALCULATE(MAX(ResumenMetricas[K]),
                     FILTER(ResumenMetricas, ResumenMetricas[F1_Macro] = MAX(ResumenMetricas[F1_Macro])))
   
   AccuracyK = CALCULATE(SELECTEDVALUE(ResumenMetricas[Accuracy]), ResumenMetricas[K] = [MejorK])
   PrecisionK = CALCULATE(SELECTEDVALUE(ResumenMetricas[Precision_Macro]), ResumenMetricas[K] = [MejorK])
   RecallK = CALCULATE(SELECTEDVALUE(ResumenMetricas[Recall_Macro]), ResumenMetricas[K] = [MejorK])
   F1K = CALCULATE(SELECTEDVALUE(ResumenMetricas[F1_Macro]), ResumenMetricas[K] = [MejorK])
   ```
3. Formatea cada tarjeta como **Porcentaje** (ej. `0.9270` → `92.70 %`).
4. Cambia el **título** de cada tarjeta a *Accuracy*, *Precision (Macro)*, *Recall (Macro)* y *F1‑Score (Macro)*.

---

## 5. Gráfico comparativo de K = 1, 3 y 5

1. Inserta un **Gráfico de líneas y marcadores** (o **gráfico de columnas agrupadas**).
2. Campos:
   - **Eje X** → `ResumenMetricas[K]`
   - **Valores** → `ResumenMetricas[Accuracy]` (formato porcentaje)
   - **Leyenda** → **Series** → agrega también `ResumenMetricas[F1_Macro]` (puedes crear una segunda serie usando **Valores** → `ResumenMetricas[F1_Macro]`).
3. Opcional: Usa **Eje Y secundario** para mostrar simultáneamente Accuracy y F1‑macro con escalas idénticas.
4. Aplica colores: verde para Accuracy, magenta para F1‑macro.
5. Añade **etiquetas de datos** para ver los valores exactos.

---

## 6. Matriz de confusión (Clase_Real vs Clase_Predicha)

1. Crea una **visualización de matriz**.
2. Arrastra los campos de **ResultadosPrueba**:
   - **Filas** → `Clase_Real`
   - **Columnas** → `Clase_Predicha`
   - **Valores** → `Acierto` (cambia la agregación a **Cuenta**).
3. En **Formato → Valores**, activa **Mostrar como porcentaje** y elige **Formato de número → Porcentaje** (para ver proporciones dentro de cada fila).  También puedes mantener la cuenta absoluta.
4. En **Formato → Estilo de cuadrícula**, elige **Bordes** y aplica una **Escala de colores** (p.ej., **Blues**) para resaltar los aciertos (celdas con valores altos).
5. (Opcional) Crea una medida DAX para la **Precisión por clase**:
   ```DAX
   PrecisionClase = DIVIDE(
       CALCULATE(COUNTROWS(ResultadosPrueba), ResultadosPrueba[Clase_Real] = EARLIER(ResultadosPrueba[Clase_Real]), ResultadosPrueba[Acierto] = TRUE()),
       CALCULATE(COUNTROWS(ResultadosPrueba), ResultadosPrueba[Clase_Real] = EARLIER(ResultadosPrueba[Clase_Real]))
   )
   ```
   Luego añádela como **Valor** adicional si deseas comparar precisiones por clase.

---

## 7. Segmentadores (Variedad y Acierto)

1. Inserta **Segmentador** → **Clase_Real** (etiquetado “Variedad”).
2. Inserta otro **Segmentador** → **Acierto** (etiquetado “Solo aciertos / errores”).
3. Configura ambos en modo **Lista** o **Cuadro de lista** y habilita **Selección múltiple**.
4. Al usarlos, todas las visualizaciones (matriz, KPI, gráficos) se filtrarán automáticamente.

---

## 8. Medidas DAX necesarias

| Medida | Definición DAX | Comentario |
|--------|----------------|------------|
| **TotalPredicciones** | `TotalPredicciones = COUNTROWS(ResultadosPrueba)` | Número total de filas de prueba. |
| **Aciertos** | `Aciertos = CALCULATE(COUNTROWS(ResultadosPrueba), ResultadosPrueba[Acierto] = TRUE)` |
| **Errores** | `Errores = CALCULATE(COUNTROWS(ResultadosPrueba), ResultadosPrueba[Acierto] = FALSE)` |
| **PctAciertos** | `PctAciertos = DIVIDE([Aciertos], [TotalPredicciones])` (formato porcentaje) |
| **PctErrores** | `PctErrores = DIVIDE([Errores], [TotalPredicciones])` |
| **MejorK** (ver sección 4) | `MejorK = CALCULATE(MAX(ResumenMetricas[K]), ResumenMetricas[F1_Macro] = MAX(ResumenMetricas[F1_Macro]))` |
| **AccuracyK**, **PrecisionK**, **RecallK**, **F1K** (ver sección 4) | Véanlas en el bloque de código DAX de la sección 4. |
| **DistribucionCorrecta** | `DistribucionCorrecta = CALCULATE(COUNTROWS(ResultadosPrueba), ResultadosPrueba[Acierto] = TRUE)` (se usa para el visual de barras apiladas). |
| **DistribucionIncorrecta** | `DistribucionIncorrecta = CALCULATE(COUNTROWS(ResultadosPrueba), ResultadosPrueba[Acierto] = FALSE)` |

---

## 9. Visualización de distribución de predicciones correctas e incorrectas

1. Insertar **Gráfico de columnas apiladas**.
2. **Eje X** → `Clase_Real` (para ver la distribución por variedad).
3. **Valores** → `DistribucionCorrecta` y `DistribucionIncorrecta` (ambas como **Cuenta**).
4. En **Formato → Serie**, asigna colores contrastantes (verde para correctos, rojo para errores).
5. Añade **etiquetas de datos** y activa **% del total** si deseas comparar proporciones.

---

## 10. Recomendaciones de diseño y presentación

| Aspecto | Recomendación |
|---------|---------------|
| **Tipografía** | Usa la fuente **Segoe UI** (estándar Power BI) con tamaños 12 pt para texto y 18 pt para títulos. |
| **Espaciado** | Deja margen suficiente entre tarjetas KPI y el gráfico comparativo (≈ 10 px). |
| **Orden visual** | Prioriza KPIs en la parte superior, seguido del análisis de K, luego la matriz de confusión y los segmentadores. |
| **Colores** | Mantén una paleta limitada a 3‑4 colores corporativos (azul, verde, magenta, gris). Evita colores demasiado brillantes que dificulten la lectura. |
| **Accesibilidad** | Usa contraste >= 4.5:1 (consultar WCAG). Añade *tooltip* descriptivo a cada visual. |
| **Interactividad** | Habilita **Cross‑filtering** entre los segmentadores y la matriz para que el usuario pueda inspeccionar clases específicas. |
| **Exportación** | El reporte puede exportarse a PDF o a Power BI Service para compartir con colegas. |
| **Actualización** | Si vuelves a ejecutar `evaluar_knn.py`, simplemente **Actualizar** (Refresh) en Power BI; los cambios se reflejarán automáticamente. |

---

## 📋 Resumen rápido de pasos
1. **Obtener datos → CSV** (dos archivos).<br>
2. **Cargar** → **ResultadosPrueba** y **ResumenMetricas**.<br>
3. No crear relaciones (tablas independientes).<br>
4. Construir **KPIs** con medidas DAX (`MejorK`, `AccuracyK`, …).<br>
5. Dibujar **gráfico comparativo** de K.<br>
6. Añadir **matriz de confusión** (Clase_Real vs Clase_Predicha).<br>
7. Insertar **segmentadores** de variedad y acierto.<br>
8. crear medidas DAX de porcentajes y totales.<br>
9. Visualizar **distribución** de aciertos/errores por clase.<br>
10. Aplicar estilo y colores según la tabla de recomendaciones.

¡Con estos pasos tendrás un dashboard listo para presentar los resultados del modelo K‑NN y permitir a los usuarios explorar su rendimiento de forma interactiva en Power BI!   

---

*Esta guía está escrita para Power BI Desktop (versión 2.128 o superior).  Si utilizas Power BI Service, los pasos de importación son idénticos, pero la publicación se realiza mediante **Publicar** en la cinta superior.*