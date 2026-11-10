# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 14:33:13 2026

@author: HP
"""
# K-NN para clasificar frijoles.
# Guardar este archivo junto a datos_limpios1.csv.
# En Spyder, eligir esta carpeta como carpeta de trabajo.

# %% 1. Cargar las herramientas
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline


# %% 2. Abrir la tabla
# read_csv abre el archivo y datos guarda su contenido.
datos = pd.read_csv("datos_limpios1.csv")

print("Filas y columnas:", datos.shape)
print(datos.head())  # Muestra las primeras cinco filas.


# %% 3. Separar las medidas y la variedad
X = datos.drop(columns=["Class"])  # Las medidas, sin la respuesta.
y = datos["Class"]                 # La variedad real del frijol.

# Estas revisiones detienen el programa si el archivo no está listo.
if X.shape[1] != 16:
    raise ValueError("El CSV debe tener 16 medidas y la columna Class.")

if datos.duplicated().any():
    raise ValueError("El CSV contiene filas repetidas. Revisa su limpieza.")


# %% 4. Apartar los datos de prueba
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,    # Reserva el 20 % para la prueba final.
    random_state=42,  # Repite el reparto con los mismos datos y orden.
    stratify=y        # Mantiene proporciones parecidas de las variedades.
)

print("Frijoles para entrenar:", len(X_train))
print("Frijoles para la prueba final:", len(X_test))


# %% 5. Preparar los valores de k
valores_k = list(range(1, 26))  # Lista de números del 1 al 25.

# Cada k se compara en cinco partes del entrenamiento.
# Las cinco partes no son cinco vecinos: los vecinos los indica k.
comparacion = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

porcentajes = []       # Aquí guardaremos el resultado de cada k.
mejor_k = 1
mejor_exactitud = -1   # Así, el primer resultado será el ganador inicial.


# %% 6. Comparar cada valor de k
for k in valores_k:
    # Pipeline une el escalado y el clasificador en ese orden.
    candidato = Pipeline([
        ("escalador", StandardScaler()),  # Hace comparables las medidas.
        ("knn", KNeighborsClassifier(n_neighbors=k))  # Usa k vecinos.
    ])

    # Solo usamos entrenamiento; la prueba final queda apartada.
    # El escalador se ajusta dentro de cada comparación.
    resultados = cross_val_score(
        candidato,
        X_train,
        y_train,
        cv=comparacion,
        scoring="accuracy",  # Mide la proporción de aciertos.
        error_score="raise"
    )

    exactitud = resultados.mean()       # Promedio de las cinco comparaciones.
    porcentajes.append(exactitud * 100) # Guarda el resultado como porcentaje.

    print("k =", k, "| Exactitud media (%):", round(exactitud * 100, 2))

    # Si este resultado mejora al anterior, guardamos el nuevo ganador.
    if exactitud > mejor_exactitud:
        mejor_exactitud = exactitud
        mejor_k = k

# En un empate queda el primer k, porque la lista va de menor a mayor.
# El ganador es el mejor entre los candidatos según este promedio.
print("Mejor k:", mejor_k)
print("Exactitud media (%):", round(mejor_exactitud * 100, 2))

tabla_k = pd.DataFrame({
    "k": valores_k,
    "exactitud_porcentaje": porcentajes
})


# %% 7. Preparar el modelo final
modelo = Pipeline([
    ("escalador", StandardScaler()),
    ("knn", KNeighborsClassifier(n_neighbors=mejor_k))
])

# fit prepara el modelo usando todo el entrenamiento y el k ganador.
modelo.fit(X_train, y_train)

print("Modelo final preparado con k =", mejor_k)


# %% 8. Dibujar la comparación
plt.figure(figsize=(10, 5))
plt.plot(valores_k, porcentajes, marker="o")
plt.xlabel("k: número de vecinos")
plt.ylabel("Exactitud media en validación (%)")
plt.title("Comparación de valores de k")
plt.xticks(valores_k)
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()

# El siguiente integrante usará modelo, X_test y y_test para la prueba final.

