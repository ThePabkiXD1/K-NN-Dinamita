from pathlib import Path

import pandas as pd


CARPETA = Path(__file__).resolve().parent
ARCHIVO_ENTRADA = CARPETA / "Dry_Bean_Dataset.xlsx"
ARCHIVO_SALIDA = CARPETA / "datos_limpios1.csv"


def main() -> None:
    """Lee el Excel, revisa su calidad, elimina duplicados exactos y guarda un CSV."""
    datos = pd.read_excel(ARCHIVO_ENTRADA)

    filas_antes = len(datos)
    celdas_vacias = int(datos.isna().sum().sum())
    duplicados = int(datos.duplicated(keep="first").sum())

    print(f"Filas antes de limpiar: {filas_antes}")
    print(f"Celdas vacías: {celdas_vacias}")
    print(f"Duplicados exactos: {duplicados}")
    print("Tipos de datos:")
    print(datos.dtypes.to_string())

    datos_limpios = datos.drop_duplicates().copy()
    filas_despues = len(datos_limpios)
    datos_limpios.to_csv(ARCHIVO_SALIDA, index=False)

    print(f"Filas después de limpiar: {filas_despues}")
    print(f"Archivo guardado en: {ARCHIVO_SALIDA}")


if __name__ == "__main__":
    main()
