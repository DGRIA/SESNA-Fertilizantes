# SESNA-Fertilizantes

Esta herramienta digital forma parte de la Secretaría Ejecutiva del Sistema Nacional de Anticorrupción de la República
de México https://www.sesna.gob.mx/

## Estructura del Proyecto

Este proyecto está estructurado en varios directorios, cada uno con un propósito específico.
Sus funciones son las siguientes:

- `data/`: Contiene los datos de entrada y salida del proyecto. Así como los diccionarios de datos.
- `docs/`: Contiene la documentación del proyecto.
- `logs/`: Contiene los logs o registros generados por el proyecto.
- `src/`: Contiene el código fuente del proyecto.
- `src/notebooks`: Contiene los Jupyter Notebooks.
- `tests/`: Contiene los tests del proyecto.

## Ejecución Local :house: :computer:

Se recomienda encarecidamente el uso de un entorno virtual para la ejecución de este proyecto.
Para crear un entorno virtual puede consultar la siguiente documentación:

- [Entornos Virtuales en Python](https://docs.python.org/3/library/venv.html)
- [Entornos Virtuales en Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)
- [Entornos Virtuales en Pipenv](https://pipenv-es.readthedocs.io/es/stable/basics.html)

Una vez creado el entorno virtual, actívelo y siga los siguientes pasos para ejecutar el proyecto.

1. **Clonar el repositorio**. Desde un terminal con git instalado, ejecute el siguiente comando:

```bash
git clone https://github.com/MottumData/SESNA-Fertilizantes.git
```

2. **Cambiar de directorio**. Una vez clonado el repositorio, cambie al directorio del proyecto:

```bash
cd SESNA-Fertilizantes
```

3. **Instalar dependencias**. Para instalar las dependencias del proyecto, ejecute el siguiente comando:

```bash
pip install -r requirements.txt
```

4. (Opcional) **Ejecutar test**. Para ejecutar los tests del proyecto, ejecute el siguiente comando:

```python
pytest
```

5. **Ejecución del proyecto**. Para ejecutar el proyecto, ejecute el siguiente comando:

```python
streamlit
main.py
```

A continuación se mostrará un mensaje similar al siguiente:

```bash
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://0.0.0.0:8501
```

## Docker :whale:

_Sección en Desarrollo_

Para ejecutar el proyecto en un contenedor de Docker, ejecute los siguientes comandos:

1. **Clonar el repositorio**. Desde un terminal con git instalado, ejecute el siguiente comando:

```bash
git clone https://github.com/MottumData/SESNA-Fertilizantes.git
```

2. **Cambiar de directorio**. Una vez clonado el repositorio, cambie al directorio del proyecto:

```bash
cd SESNA-Fertilizantes
```

3. **Construir la imagen de Docker**. Ejecute el siguiente comando:

```bash
docker build -t sesna-fertilizantes .
```

4. **Levantar el contenedor de Docker**. Ejecute el siguiente comando:

```bash
docker run -p 8501:8501 8888:8888 sesna-fertilizantes
```
5. Opcional **Levantar el contendor de Docker en segundo plano**. Ejecute el siguiente comando:

```bash
docker run -d -p 8501:8501 -p 8888:8888 sesna-fertilizantes
```