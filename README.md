# To-Do API

API REST simple para gestionar tareas, construida con **FastAPI**, **SQLAlchemy** y **SQLite**.

Este proyecto sirve como base para practicar desarrollo backend con Python, estructura de endpoints, validaciones, persistencia en base de datos local y pruebas automatizadas.

## ✨ Funcionalidades

- Crear tareas.
- Listar todas las tareas.
- Ver el detalle de una tarea por ID.
- Actualizar una tarea existente.
- Eliminar una tarea.
- Validación de datos con Pydantic.
- Persistencia local con SQLite.

## 🧰 Stack utilizado

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Pytest
- HTTPX

## 📦 Instalación

Clona el repositorio:

```bash
git clone https://github.com/NoisGit/todo-api.git
cd todo-api
```

Crea y activa un entorno virtual:

```bash
python -m venv venv
```

En Windows:

```bash
venv\Scripts\activate
```

En macOS/Linux:

```bash
source venv/bin/activate
```

Instala las dependencias:

```bash
pip install -r requirements.txt
```

## 🚀 Ejecutar el proyecto

```bash
uvicorn main:app --reload
```

Luego abre la documentación interactiva:

```text
http://127.0.0.1:8000/docs
```

## 📌 Endpoints principales

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Verifica que la API esté funcionando. |
| GET | `/tasks` | Lista todas las tareas. |
| POST | `/tasks` | Crea una nueva tarea. |
| GET | `/tasks/{details_id}` | Obtiene el detalle de una tarea. |
| PUT | `/tasks/{update_id}` | Actualiza una tarea. |
| DELETE | `/tasks/{delete_id}` | Elimina una tarea. |

## 🧪 Ejecutar pruebas

```bash
pytest
```

## 📝 Ejemplo de tarea

```json
{
  "title": "Estudiar FastAPI",
  "description": "Practicar endpoints CRUD y pruebas automatizadas",
  "status": "pendiente",
  "date": "2026-04-27"
}
```

## 🗺️ Mejoras futuras

- Separar el proyecto en módulos (`routers`, `schemas`, `models`, `database`).
- Agregar autenticación.
- Agregar filtros por estado y fecha.
- Agregar Docker.
- Agregar configuración por variables de entorno.
- Preparar deploy.

## 👤 Autor

Desarrollado por [NoisGit](https://github.com/NoisGit).
