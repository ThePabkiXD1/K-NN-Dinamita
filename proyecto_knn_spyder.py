# -*- coding: utf-8 -*-
# K-NN para clasificar variedades de frijol seco.
# Guarda este archivo junto a limpieza.py y Dry_Bean_Dataset.xlsx.
# F5 ejecuta todo; Ctrl + Enter ejecuta el bloque actual en Spyder.


# %% 1. Cargar las herramientas
import sys
import runpy
from pathlib import Path

import pandas as pd
import sklearn
import matplotlib
import openpyxl
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report
from sklearn.metrics import ConfusionMatrixDisplay

# Usa la carpeta del archivo aunque Spyder tenga otra carpeta de trabajo.
CARPETA = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()

print("Python      :", sys.version.split()[0])
print("pandas      :", pd.__version__)
print("scikit-learn:", sklearn.__version__)
print("matplotlib  :", matplotlib.__version__)
print("openpyxl    :", openpyxl.__version__)


# %% 2. Limpiar los datos
# Ejecuta solo la limpieza (similar a %run limpieza.py).
_ = runpy.run_path(str(CARPETA / "limpieza.py"))


# %% 3. Abrir la tabla limpia
datos = pd.read_csv(CARPETA / "datos_limpios.csv")
print("Filas y columnas:", datos.shape)
print(datos.head())  # Muestra las primeras cinco filas.


# %% 4. Contar los frijoles por variedad
conteo = datos["Class"].value_counts()

ax = conteo.plot(kind="bar", figsize=(8, 4), color="#1F4E79")
plt.title("Cantidad de frijoles por variedad (datos limpios)")
plt.xlabel("Variedad")
plt.ylabel("Número de frijoles")
plt.xticks(rotation=45)
for i, valor in enumerate(conteo):
    ax.text(i, valor + 30, str(valor), ha="center")
plt.tight_layout()
plt.savefig(CARPETA / "grafica_variedades.png", dpi=150)
plt.show()

print("Suma de variedades:", conteo.sum(), "| Filas de la tabla:", len(datos))


# %% 5. Separar las medidas y apartar los datos de prueba
X = datos.drop(columns="Class")   # las 16 medidas (las pistas)
y = datos["Class"]                # la variedad real (la respuesta)
print("X tiene", X.shape[1], "columnas | ¿Class está en X?", "Class" in X.columns)

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.20,
    stratify=y,
    random_state=42
)
print("Entrenamiento:", len(X_train), "filas")
print("Prueba:       ", len(X_test), "filas")


# %% 6. Revisar las proporciones de las variedades
proporciones = pd.DataFrame({
    "completo_%": y.value_counts(normalize=True) * 100,
    "entrenamiento_%": y_train.value_counts(normalize=True) * 100,
    "prueba_%": y_test.value_counts(normalize=True) * 100,
}).round(2)
print(proporciones)


# %% 7. Preparar el modelo con k = 5
# Se conserva k = 5, como se decidió en el cuaderno.
K_ELEGIDO = 5

modelo = make_pipeline(
    StandardScaler(),
    KNeighborsClassifier(n_neighbors=K_ELEGIDO)
)
modelo.fit(X_train, y_train)   # el escalador y K-NN solo ven entrenamiento
print("Modelo preparado con k =", K_ELEGIDO)


# %% 8. Comparar los valores de k
# La comparación usa solo entrenamiento; no cambia el k del modelo anterior.
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
valores_k = list(range(1, 26))
exactitudes = []

for k in valores_k:
    candidato = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=k))
    exactitudes.append(cross_val_score(candidato, X_train, y_train, cv=cv).mean() * 100)

mejor_k = valores_k[exactitudes.index(max(exactitudes))]
print("Mejor k:", mejor_k, "->", round(max(exactitudes), 2), "%")
print("k = 5  ->", round(exactitudes[4], 2), "%")

plt.figure(figsize=(9, 4))
plt.plot(valores_k, exactitudes, marker="o", color="#1F4E79")
plt.axvline(5, color="gray", linestyle="--", label="k = 5 (plan)")
plt.axvline(mejor_k, color="red", linestyle="--", label=f"mejor k = {mejor_k}")
plt.xlabel("k (número de vecinos)")
plt.ylabel("Exactitud media en validación (%)")
plt.title("Comparación de valores de k")
plt.xticks(valores_k)
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(CARPETA / "grafica_k.png", dpi=150)
plt.show()


# %% 9. Predecir las variedades de prueba
y_pred = modelo.predict(X_test)

resultados = pd.DataFrame({
    "clase_real": y_test.values,
    "clase_predicha": y_pred,
})
resultados["acierto"] = (resultados["clase_real"] == resultados["clase_predicha"]).astype(int)

print("Respuestas:", len(resultados))
print(resultados.head(10))


# %% 10. Calcular las métricas
exactitud = accuracy_score(y_test, y_pred)
f1_macro = f1_score(y_test, y_pred, average="macro")

print(f"Casos probados: {len(y_test)}")
print(f"Aciertos:       {resultados['acierto'].sum()}")
print(f"Exactitud:      {exactitud:.4f}  ({exactitud*100:.2f} %)")
print(f"F1 macro:       {f1_macro:.4f}")
print()
print(classification_report(y_test, y_pred, digits=3))


# %% 11. Dibujar la matriz de confusión
fig, ax = plt.subplots(figsize=(7, 6))
ConfusionMatrixDisplay.from_predictions(
    y_test, y_pred, ax=ax, xticks_rotation=45, cmap="Blues"
)
ax.set_title("Matriz de confusión (conjunto de prueba)")
ax.set_xlabel("Variedad predicha")
ax.set_ylabel("Variedad real")
plt.tight_layout()
plt.savefig(CARPETA / "matriz_confusion.png", dpi=150)
plt.show()


# %% 12. Revisar las confusiones más frecuentes
errores = (resultados[resultados["acierto"] == 0]
           .groupby(["clase_real", "clase_predicha"]).size()
           .sort_values(ascending=False)
           .head(5))
print("Confusiones más frecuentes (real -> predicha):")
print(errores)


# %% 13. Guardar y verificar los resultados
resultados.to_csv(CARPETA / "resultados_prueba.csv", index=False)

verificacion = pd.read_csv(CARPETA / "resultados_prueba.csv")
print("Filas guardadas:", len(verificacion))
print("Columnas:", list(verificacion.columns))
print("Exactitud desde el CSV:", verificacion["acierto"].mean().round(4))


# %% 14. Hacer una predicción de ejemplo
ejemplo = X_test.iloc[[0]]

print("Medidas del frijol de prueba:")
print(ejemplo.T)
print()
print("Predicción del modelo:", modelo.predict(ejemplo)[0])
print("Variedad real:        ", y_test.iloc[0])
