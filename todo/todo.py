import reflex as rx
import requests
from typing import List, Dict, Union
import reflex as rx
import requests
from typing import List, Dict, Union
from dotenv import load_dotenv
import os

# Cargar las variables de entorno
load_dotenv()

# Obtener la URL de la API desde las variables de entorno
API_URL = os.getenv("API_URL")


class TodoState(rx.State):
    """Estado para la aplicación de tareas."""

    # Lista de tareas
    todos: List[Dict[str, Union[str, bool]]] = []

    def fetch_todos(self):
        """Obtener las tareas desde la API."""
        response = requests.get(API_URL)
        if response.status_code == 200:
            self.todos = response.json()

    def add_todo(self, form_data: dict):
        """Agregar una nueva tarea."""
        title = form_data.get("title", "").strip()
        description = form_data.get("description", "").strip()

        if not title:
            return

        # Petición para agregar la nueva tarea
        new_todo = {
            "title": title,
            "description": description,
            "completed": False
        }

        response = requests.post(API_URL, json=new_todo)
        if response.status_code == 201:
            self.fetch_todos()  # Actualizar la lista de tareas después de agregar

    def delete_todo(self, todo_id: int):
        """Eliminar una tarea específica."""
        response = requests.delete(f"{API_URL}/{todo_id}")
        if response.status_code == 200:
            self.fetch_todos()  # Recargar la lista de tareas desde la API después de eliminar

    def toggle_complete(self, todo_id: int):
        """Cambiar el estado de completado de una tarea."""
        # Encuentra la tarea correspondiente en la lista local
        todo_to_update = next((todo for todo in self.todos if todo["id"] == todo_id), None)
        if todo_to_update:
            # Cambiar el estado de completado de la tarea
            todo_to_update["completed"] = not todo_to_update["completed"]

            # Crear un objeto con el formato adecuado (según lo que espera la API)
            updated_todo = {
                "completed": todo_to_update["completed"]
            }

            # Realizar la solicitud PUT a la API para actualizar la tarea
            response = requests.put(f"{API_URL}/{todo_id}", json=updated_todo)
            if response.status_code == 200:
                self.fetch_todos()  # Recargar la lista de tareas desde la API después de actualizar

def TodoItem(todo: Dict) -> rx.Component:
    """Componente para un elemento de tarea."""
    return rx.card(
        rx.hstack(
            # La tarjeta se vuelve clickeable para cambiar el estado de la tarea
            rx.vstack(
                rx.text(
                    todo["title"],
                    text_decoration=rx.cond(  # Solo marca el texto de la tarea como "line-through" si está completada
                        todo["completed"],
                        "line-through",
                        "none"
                    )
                ),
                rx.text(
                    todo["description"],
                    color="gray",
                    font_size="0.8em"
                ),
                spacing="1"
            ),
            rx.spacer(),
            rx.button(
                "Eliminar",
                color_scheme="red",
                size="1",
                on_click=TodoState.delete_todo(todo["id"])  # Llama directamente a la función de eliminar
            ),
            width="100%",
            spacing="3",
            on_click=TodoState.toggle_complete(todo["id"])  # Cambia el estado de la tarea al hacer clic en la tarjeta
        )
    )

def index() -> rx.Component:
    """Página principal de la aplicación de tareas."""
    return rx.vstack(
        rx.heading("Todo List", size="8"),

        # Input para nueva tarea
        rx.form(
            rx.vstack(
                rx.input(
                    name="title",
                    placeholder="Título de la tarea",
                    width="100%"
                ),
                rx.text_area(
                    name="description",
                    placeholder="Descripción de la tarea",
                    width="100%"
                ),
                rx.button(
                    "Agregar Tarea",
                    type="submit",
                    width="100%"
                ),
                spacing="3"
            ),
            on_submit=TodoState.add_todo,
            reset_on_submit=True,
            width="100%"
        ),

        # Lista de tareas
        rx.cond(
            TodoState.todos,
            rx.vstack(
                rx.foreach(
                    TodoState.todos,
                    lambda todo: TodoItem(todo)
                )
            ),
            rx.text("No hay tareas pendientes", color="gray")
        ),

        max_width="600px",
        margin="auto",
        spacing="4",
        padding="20px"
    )

# Configuración de la aplicación
app = rx.App()
app.add_page(index)

# Cargar las tareas al iniciar la página
TodoState.fetch_todos()
