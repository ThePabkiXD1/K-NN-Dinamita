from pathlib import Path
import pandas as pd

# Carpeta donde está este script (así funciona sin importar desde dónde se ejecute)
CARPETA = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()

# 1. Leer el Excel
df = pd.read_excel(CARPETA / "Dry_Bean_Dataset.xlsx", sheet_name="Dry_Beans_Dataset")
filas_antes = len(df)
print("Filas antes de limpiar:", filas_antes)
print("Columnas:", df.shape[1])

# 2. Revisar celdas vacías
print("Celdas vacías:", df.isna().sum().sum())

# 3. Revisar el formato de los datos
print("\nTipos de dato:")
print(df.dtypes)

medidas = df.drop(columns="Class").columns
print("\n¿Las 16 medidas son numéricas?",
      all(pd.api.types.is_numeric_dtype(t) for t in df[medidas].dtypes))
print("¿Hay medidas con valor cero o negativo?",
      (df[medidas] <= 0).any().any())

print("\nVariedades encontradas:")
print(df["Class"].value_counts())

# 4. Quitar filas con datos inválidos
filas_invalidas = (
    df.isna().any(axis=1) |
    (df[medidas] <= 0).any(axis=1)
)
print("\nFilas con vacíos o medidas menores o iguales a cero:",
      filas_invalidas.sum())
df = df.loc[~filas_invalidas].copy()
print("Filas eliminadas por datos inválidos:", filas_invalidas.sum())

# 5. Revisar y quitar los duplicados exactos
print("\nFilas duplicadas:", df.duplicated().sum())
df = df.drop_duplicates()
filas_despues = len(df)
print("Filas después de limpiar:", filas_despues)
print("Filas eliminadas:", filas_antes - filas_despues)

# 6. Guardar la tabla limpia
df.to_csv(CARPETA / "datos_limpios.csv", index=False)
print("\nArchivo guardado: datos_limpios.csv")
