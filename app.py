import streamlit as st
import json
import os
from PIL import Image
from streamlit_image_zoom import image_zoom
# Agregar la línea roja en la parte superior
st.markdown("""
    <div style="border-top: 5px solid red;"></div>
""", unsafe_allow_html=True)

# Agregar el logo de la empresa (asegúrate de tener el archivo de imagen del logo)
logo_path = "mapfre.jpg"  # Reemplaza con la ruta de tu logo
st.image(logo_path, width=200)  # Ajusta el tamaño según lo necesites

st.title("Image and JSON Generator Application")

#/mnt/c/Users/bmoreno/Desktop/proyectos/mapfre/app_image_metadata/

# Set folder paths
image_folder_path = "image"
json_folder_path = "metadata"
# config_file_path = "/mnt/c/Users/bmoreno/Desktop/proyectos/mapfre/app_image_metadata/config.txt"  # Path to config file with image IDs
status_file_path = "status.json"  # Archivo para el estado de imágenes

# # Load image IDs from config file
# if os.path.isfile(config_file_path):
#     with open(config_file_path, "r") as file:
#         image_ids = [line.strip() for line in file if line.strip()]  # Remove any blank lines
# else:
#     st.error("Config file with image IDs not found.")
#     st.stop()


# # Inicializa el archivo de estado de imágenes si no existe
# if not os.path.isfile(status_file_path):
#     image_status = {image_id: "available" for image_id in image_ids}
#     with open(status_file_path, "w") as status_file:
#         json.dump(image_status, status_file)
def print_json_file(json_file_path):
    """
    Lee e imprime el contenido de un archivo JSON.

    Args:
        json_file_path (str): Ruta al archivo JSON.
    """
    with open(json_file_path, "r") as file:
        data = json.load(file)
        print("Contenido del archivo JSON:")
        print(json.dumps(data, indent=4))  # Usa indentación para una impresión legible

def print_directory_contents(directory_path):
    """
    Lista e imprime los elementos de un directorio.

    Args:
        directory_path (str): Ruta al directorio.
    """
    print(f"Contenido del directorio {directory_path}:")
    for item in os.listdir(directory_path):
        print(item)





def create_image_status_file(image_folder_path, json_folder_path, status_file_path):
    """
    Crea un archivo JSON que contiene el estado de cada imagen en la carpeta de imágenes.
    Si existe un archivo JSON para una imagen, el estado será "processed".
    Si no existe, el estado será "available".
    
    Args:
        image_folder_path (str): Ruta de la carpeta donde se encuentran las imágenes.
        json_folder_path (str): Ruta de la carpeta donde se encuentran los archivos JSON de metadatos.
        status_file_path (str): Ruta donde se guardará el archivo JSON de estado.
    """
    # Diccionario para almacenar el estado de cada imagen
    image_status = {}
    
    # Obtener una lista de todas las imágenes en la carpeta de imágenes
    for image_file in os.listdir(image_folder_path):
        if image_file.endswith(".jpg"):  # Asegúrate de que sean archivos de imagen (extensión .jpg)
            image_id = os.path.splitext(image_file)[0]  # Extraer el ID de la imagen sin extensión
            json_path = os.path.join(json_folder_path, f"{image_id}.json")
            
            # Verificar si el archivo JSON asociado existe
            if os.path.isfile(json_path):
                image_status[image_id] = "processed"
            else:
                image_status[image_id] = "available"
    
    # Guardar el diccionario de estados en el archivo JSON
    with open(status_file_path, "w") as status_file:
        json.dump(image_status, status_file, indent=4)
    
    print(f"Archivo de estado creado en: {status_file_path}")

    
if not os.path.isfile(status_file_path):
    create_image_status_file(image_folder_path, json_folder_path, status_file_path)



# Cargar el estado de las imágenes
with open(status_file_path, "r") as status_file:
    image_status = json.load(status_file)
# Guardar el estado de las imágenes en el archivo JSON
def save_status():
    with open(status_file_path, "w") as status_file:
        json.dump(image_status, status_file)



# # Find images without an associated JSON
# def get_images_without_json(image_ids, image_folder, json_folder):
#     images_without_json = []
#     for image_id in image_ids:
#         image_path = os.path.join(image_folder, f"{image_id}.jpg")
#         json_path = os.path.join(json_folder, f"{image_id}.json")
#         if os.path.isfile(image_path) and not os.path.isfile(json_path):
#             images_without_json.append(image_id)
#     return images_without_json

# images_to_process = get_images_without_json(image_ids, image_folder_path, json_folder_path)
# # Obtener la siguiente imagen sin marcarla como "in use" todavía

# Función para obtener la primera imagen disponible
def get_next_available_image():
    for image_id, status in image_status.items():
        if status == "available":
            # Marcar como "in use" para evitar acceso de otros usuarios
            image_status[image_id] = "reserved"
            save_status()
            return image_id
    return None

if "current_image_id" not in st.session_state:
    st.session_state["current_image_id"] = get_next_available_image()

print_json_file(status_file_path)
print_directory_contents(image_folder_path)
# Check if there are images to process
if not st.session_state["current_image_id"]:

    st.success("All images have associated JSON files!")
else:
    # Initialize current_index in session state if it doesn't exist
    # if "current_index" not in st.session_state:
    #     st.session_state["current_index"] = 0

    
    image_id = st.session_state["current_image_id"]
 
    image_path = os.path.join(image_folder_path, f"{image_id}.jpg")
    json_path = os.path.join(json_folder_path, f"{image_id}.json")
    
    # Display the current image with zoom functionality
    st.subheader(f"Image ID: {image_id}")
    img = Image.open(image_path)
    image_zoom(img, mode="scroll")  # Display zoomable image
# image_zoom(image, mode="scroll", size=(800, 600), keep_aspect_ratio=False, zoom_factor=4.0, increment=0.2)

    # JSON fields
    # description = st.text_input("Description")
    damage_level = st.selectbox("Damage Level", ["Low", "Medium", "High"])

    if st.button("Save JSON"):
        new_json_data = {
            "id": image_id,
            # "description": description,
            "damage_level": damage_level,
        }

        os.makedirs(json_folder_path, exist_ok=True)
        with open(json_path, "w") as json_file:
            json.dump(new_json_data, json_file)

        st.success(f"JSON file created for {image_id}.")
                # Actualizar el estado a "processed"
        image_status[image_id] = "processed"
        
        save_status()
        
        # Actualizar a la siguiente imagen disponible
        st.session_state["current_image_id"] = get_next_available_image()
        st.rerun()
