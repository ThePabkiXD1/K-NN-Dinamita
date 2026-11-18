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

medidas = df.drop(columns="Class")
print("\n¿Las 16 medidas son numéricas?",
      all(pd.api.types.is_numeric_dtype(t) for t in medidas.dtypes))
print("¿Hay medidas con valor cero o negativo?", (medidas <= 0).any().any())

print("\nVariedades encontradas:")
print(df["Class"].value_counts())

# 4. Revisar y quitar los duplicados exactos
print("\nFilas duplicadas:", df.duplicated().sum())
df = df.drop_duplicates()
filas_despues = len(df)
print("Filas después de limpiar:", filas_despues)
print("Filas eliminadas:", filas_antes - filas_despues)

# 5. Guardar la tabla limpia
df.to_csv(CARPETA / "datos_limpios.csv", index=False)
print("\nArchivo guardado: datos_limpios.csv")


#Cambios realizados en la limpieza:
#- Se leyó la hoja Dry_Beans_Dataset del Excel: 13,611 filas y 17 columnas.
#- Se revisó la calidad: no hay celdas vacías, las 16 medidas son numéricas
#  y ninguna tiene valores de cero o negativos.
#- Se encontraron 68 filas duplicadas exactas y se eliminaron, conservando
#  la primera aparición de cada una.
#- Quedaron 13,543 filas y siguen presentes las 7 variedades.
#- La tabla limpia se guardó en datos_limpios.csv.