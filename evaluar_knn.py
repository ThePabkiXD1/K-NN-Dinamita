# -*- coding: utf-8 -*-
"""
Evaluación y validación del modelo K‑Nearest Neighbors.

Este script:
1. Carga el dataset limpio ``datos_limpios1.csv``.
2. Divide los datos 80/20 (estratificado, reproducible, ``random_state=42``).
3. Escala las características numéricas mediante ``StandardScaler`` dentro de un ``Pipeline``.
4. Entrena K‑NN para k = 1, 3 y 5.
5. Calcula métricas de precisión, recall, f1‑macro y exactitud.
6. Selecciona el mejor modelo según ``f1_macro``.
7. Exporta las predicciones del conjunto de prueba a ``resultados/resultados_prueba.csv``.
8. Genera gráficas de comparación y la matriz de confusión del mejor modelo.
9. **Nueva funcionalidad**: genera ``resultados/metrics_summary.csv`` que resume las métricas por cada k.
10. Añade validaciones de integridad de datos y consistencia.
"""

import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)

# ---------------------------
# Configuración de rutas
# ---------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "datos_limpios1.csv"
RESULTS_DIR = BASE_DIR / "resultados"
RESULTS_DIR.mkdir(exist_ok=True)

CSV_OUTPUT = RESULTS_DIR / "resultados_prueba.csv"
METRICS_SUMMARY = RESULTS_DIR / "metrics_summary.csv"

# ---------------------------
# 1. Carga de datos
# ---------------------------
print("Cargando datos …")
df = pd.read_csv(DATA_PATH)
print(f"Registros totales en el CSV: {df.shape[0]}")

# Identificar variable objetivo y características
TARGET_COL = "Class"
if TARGET_COL not in df.columns:
    raise KeyError(f"Columna objetivo '{TARGET_COL}' no encontrada en el dataset")

X = df.drop(columns=[TARGET_COL])
y = df[TARGET_COL]

# Verificar tipos de datos
numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
categorical_cols = X.select_dtypes(exclude=[np.number]).columns.tolist()
print(f"Columnas numéricas: {numeric_cols}")
print(f"Columnas categóricas (no esperadas): {categorical_cols}")

# Comprobar valores nulos y duplicados (ya fueron limpiados en limpieza.py)
if X.isnull().any().any() or y.isnull().any():
    raise ValueError("Se encontraron valores nulos después de la limpieza")
if df.duplicated().any():
    raise ValueError("Se encontraron filas duplicadas después de la limpieza")

# Distribución de clases antes del split
class_counts = y.value_counts().sort_index()
print("Distribución de clases en el dataset completo:")
print(class_counts)

# ---------------------------
# 2. División del dataset
# ---------------------------
print("Dividiendo datos 80/20 …")
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)
print(f"Tamaño entrenamiento: {X_train.shape[0]}  |  prueba: {X_test.shape[0]}")
print("Distribución de clases en entrenamiento:")
print(y_train.value_counts().sort_index())
print("Distribución de clases en prueba:")
print(y_test.value_counts().sort_index())

# ---------------------------
# 3. Entrenamiento y evaluación de varios k
# ---------------------------
ks = [1, 3, 5]
metrics = []  # lista de dicts con métricas por k
best_f1 = -1.0
best_k = None
best_model = None
best_pred = None

for k in ks:
    print(f"\nEntrenando KNN con k={k} …")
    pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("knn", KNeighborsClassifier(n_neighbors=k)),
    ])
    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average="macro", zero_division=0)
    rec = recall_score(y_test, y_pred, average="macro", zero_division=0)
    f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)
    cm = confusion_matrix(y_test, y_pred)

    metrics.append({
        "k": k,
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1_macro": f1,
        "confusion": cm,
    })

    print(f"  Accuracy : {acc:.4f}")
    print(f"  Precision: {prec:.4f}")
    print(f"  Recall   : {rec:.4f}")
    print(f"  F1‑macro : {f1:.4f}")

    if f1 > best_f1:
        best_f1 = f1
        best_k = k
        best_model = pipe
        best_pred = y_pred

# ---------------------------
# 4. Guardado de métricas resumidas
# ---------------------------
summary_df = pd.DataFrame([
    {"K": m["k"], "Accuracy": m["accuracy"], "Precision_Macro": m["precision"], "Recall_Macro": m["recall"], "F1_Macro": m["f1_macro"]}
    for m in metrics
])
summary_df.to_csv(METRICS_SUMMARY, index=False)
print(f"Archivo de métricas resumidas guardado en: {METRICS_SUMMARY}")

# ---------------------------
# 5. Resultados del mejor modelo
# ---------------------------
print("\n=== Selección del mejor modelo ===")
print(f"Mejor k según F1‑macro: {best_k} (F1‑macro = {best_f1:.4f})")

# Exportar predicciones del conjunto de prueba
results_df = pd.DataFrame({
    "Clase_Real": y_test.reset_index(drop=True),
    "Clase_Predicha": best_pred,
})
results_df["Acierto"] = results_df["Clase_Real"] == results_df["Clase_Predicha"]
# Guardar CSV con codificación UTF‑8‑BOM (compatible con Excel/Power BI)
results_df.to_csv(CSV_OUTPUT, index=False, encoding="utf-8-sig")
print(f"Archivo de resultados guardado en: {CSV_OUTPUT}")

# Verificar consistencia entre predicciones y etiquetas reales
assert len(best_pred) == len(y_test), "Número de predicciones no coincide con número de etiquetas de prueba"

# ---------------------------
# 6. Visualizaciones
# ---------------------------
# 6.1 Comparación de Accuracy
acc_vals = [m["accuracy"] for m in metrics]
plt.figure(figsize=(6, 4))
plt.plot(ks, acc_vals, marker="o")
plt.title("Comparación de Accuracy por k")
plt.xlabel("k (número de vecinos)")
plt.ylabel("Accuracy")
plt.grid(True, alpha=0.3)
plt.xticks(ks)
plt.tight_layout()
acc_path = RESULTS_DIR / "accuracy_comparison.png"
plt.savefig(acc_path)
plt.close()
print(f"Gráfica de Accuracy guardada en {acc_path}")

# 6.2 Comparación de F1‑macro
f1_vals = [m["f1_macro"] for m in metrics]
plt.figure(figsize=(6, 4))
plt.plot(ks, f1_vals, marker="o", color="orange")
plt.title("Comparación de F1‑macro por k")
plt.xlabel("k (número de vecinos)")
plt.ylabel("F1‑macro")
plt.grid(True, alpha=0.3)
plt.xticks(ks)
plt.tight_layout()
f1_path = RESULTS_DIR / "f1_comparison.png"
plt.savefig(f1_path)
plt.close()
print(f"Gráfica de F1‑macro guardada en {f1_path}")

# 6.3 Matriz de confusión del mejor modelo
best_cm = confusion_matrix(y_test, best_pred, labels=np.unique(y_test))
plt.figure(figsize=(6, 5))
sns.heatmap(
    best_cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=np.unique(y_test),
    yticklabels=np.unique(y_test),
)
plt.title(f"Matriz de Confusión (k={best_k})")
plt.ylabel("Clase real")
plt.xlabel("Clase predicha")
plt.tight_layout()
cm_path = RESULTS_DIR / "confusion_best.png"
plt.savefig(cm_path)
plt.close()
print(f"Matriz de confusión guardada en {cm_path}")

# 6.4 Distribución de clases reales vs predichas
plt.figure(figsize=(8, 4))
# Real
sns.countplot(x=y_test, order=np.unique(y_test), color="steelblue", label="Real")
# Predicha (sobreplanta ligeramente)
sns.countplot(x=best_pred, order=np.unique(y_test), color="orange", label="Predicha", alpha=0.6)
plt.title("Distribución de clases reales y predichas (conjunto de prueba)")
plt.xlabel("Clase")
plt.ylabel("Frecuencia")
plt.legend()
plt.tight_layout()

dist_path = RESULTS_DIR / "distribution.png"
plt.savefig(dist_path)
plt.close()
print(f"Distribución de clases guardada en {dist_path}")

# ---------------------------
# 7. Resumen en consola
# ---------------------------
print("\n=== Resumen de métricas ===")
summary_table = pd.DataFrame({
    "k": ks,
    "Accuracy": acc_vals,
    "Precision": [m["precision"] for m in metrics],
    "Recall": [m["recall"] for m in metrics],
    "F1‑macro": f1_vals,
})
print(summary_table.to_string(index=False))

print("\nEjecución completada.")
