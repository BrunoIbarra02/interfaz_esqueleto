# Skeleton Selector

Selector de esqueletos basado en inteligencia artificial para el pipeline de generación y rigging de modelos 3D.

El proyecto recibe una imagen de un animal, la clasifica mediante **OpenAI GPT-5 Nano** y devuelve el esqueleto (`.FBX`) más adecuado para continuar el proceso de rigging.

Actualmente este módulo está desarrollado como un componente independiente con el objetivo de integrarse posteriormente en el pipeline principal.

---

# Características

- Clasificación de imágenes mediante OpenAI GPT-5 Nano.
- Arquitectura modular y sencilla.
- Mapeo automático entre categorías y esqueletos.
- Validación mediante conjunto de imágenes de prueba.
- Diseñado para integrarse fácilmente en el pipeline de rigging.

---

# Arquitectura

```
                Imagen
                   │
                   ▼
          classifier.py
        (OpenAI GPT-5 Nano)
                   │
                   ▼
              Categoría
                   │
                   ▼
             mapping.py
                   │
                   ▼
          Esqueleto (.FBX)
```

---

# Estructura del proyecto

```
skeleton_selector/
│
├── classifier.py
├── mapping.py
├── selector.py
│
tests/
│
├── images/
└── test.py
```

## Descripción de los módulos

### classifier.py

Responsable de enviar una imagen a OpenAI y devolver una categoría válida.

No conoce la existencia de esqueletos ni realiza ningún tipo de mapeo.

---

### mapping.py

Contiene la relación entre cada categoría y el archivo `.FBX` correspondiente.

Ejemplo:

```python
{
    "Bear": "Bear.FBX",
    "Horse": "Horse.FBX",
    ...
}
```

---

### selector.py

Punto de entrada del proyecto.

Coordina el proceso completo:

1. Clasifica la imagen.
2. Obtiene la categoría.
3. Busca el esqueleto asociado.
4. Devuelve el resultado.

---

# Requisitos

- Docker
- Python 3.11
- OpenAI API Key

---

# Configuración

Crear un archivo `.env` con la clave de OpenAI.

```text
OPENAI_API_KEY=tu_api_key
```

---

# Uso

```python
from skeleton_selector.selector import select_skeleton

result = select_skeleton("bear.png")

print(result)
```

Salida:

```python
{
    "category": "Bear",
    "skeleton": "Bear.FBX"
}
```

---

# Ejecución de pruebas

Las pruebas se ejecutan desde el contenedor Docker del proyecto.

Procesar una única imagen:

```bash
python3.11 test.py tests/images/lobo.png
```

Procesar automáticamente todas las imágenes de prueba:

```bash
python3.11 test.py
```

---

# Categorías soportadas

- Bear
- BlackWidow
- Crocodile
- Deer
- DragonFly
- Eagle
- GreatHornedOwl
- HellenicHound
- Horse
- IndianElephant
- Squid
- WhiteShark

---

# Formato de salida

El selector devuelve un diccionario con la categoría detectada y el esqueleto correspondiente.

```python
{
    "category": "Horse",
    "skeleton": "Horse.FBX"
}
```

---

# Validación

El clasificador ha sido validado utilizando un conjunto de **14 imágenes** que cubren las **12 categorías** soportadas por el sistema.

## Resultados

| Imagen | Categoría |
|---------|-----------|
| Aguila | Eagle |
| Araña | BlackWidow |
| Buho | GreatHornedOwl |
| Caballo | Horse |
| Calamar | Squid |
| Cocodrilo | Crocodile |
| Elefante | IndianElephant |
| Libélula | DragonFly |
| Lobo | HellenicHound |
| Perro | HellenicHound |
| Oso pardo | Bear |
| Oso polar | Bear |
| Tiburón | WhiteShark |
| Venado | Deer |

**Resultado obtenido:**

- 14 imágenes procesadas.
- 14 clasificaciones correctas.
- Cobertura de las 12 categorías disponibles.

---

# Dependencias principales

- openai
- python-dotenv

---

# Estado del proyecto

✅ Clasificación mediante OpenAI implementada.

✅ Selección automática del esqueleto implementada.

✅ Conjunto inicial de pruebas validado.

🚧 Pendiente de integración en el pipeline completo de generación y rigging.

