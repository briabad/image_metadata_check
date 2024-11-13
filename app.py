import streamlit as st
import json
import os
from PIL import Image
from streamlit_image_zoom import image_zoom
from utilerias import create_image_status_file, get_next_available_image,save_status, download_from_s3, create_image_status_file_s3
# Agregar la línea roja en la parte superior
st.markdown("""
    <div style="border-top: 5px solid red;"></div>
""", unsafe_allow_html=True)

# Agregar el logo de la empresa (asegúrate de tener el archivo de imagen del logo)
logo_path = "mapfre.jpg"  # Reemplaza con la ruta de tu logo
st.image(logo_path, width=200)  # Ajusta el tamaño según lo necesites

st.title("Tipo de daño")

#/mnt/c/Users/bmoreno/Desktop/proyectos/mapfre/app_image_metadata/
# s3://detect-dano-perito-app/images/prueba/001.jpg

# Set folder paths
bucket_name = "detect-dano-perito-app"
image_folder_path = "images/prueba/"
json_folder_path = "metadata/prueba/"
# config_file_path = "/mnt/c/Users/bmoreno/Desktop/proyectos/mapfre/app_image_metadata/config.txt"  # Path to config file with image IDs
status_file_path = "status.json"  # Archivo para el estado de imágenes


    
if not os.path.isfile(status_file_path):
    create_image_status_file_s3(bucket_name,image_folder_path, json_folder_path, status_file_path)



# Cargar el estado de las imágenes
with open(status_file_path, "r") as status_file:
    image_status = json.load(status_file)
# Guardar el estado de las imágenes en el archivo JSON




if "current_image_id" not in st.session_state:
    st.session_state["current_image_id"] = get_next_available_image(image_status,status_file_path)



# Check if there are images to process
if not st.session_state["current_image_id"]:

    st.success("All images have associated JSON files!")
else:
    # Initialize current_index in session state if it doesn't exist
    # if "current_index" not in st.session_state:
    #     st.session_state["current_index"] = 0

    
    image_id = st.session_state["current_image_id"]

    download_from_s3(bucket_name,f"{image_folder_path}/{image_id}.jpg", f"{image_id}.jpg" )
 
    image_path = os.path.join("app", f"{image_id}.jpg")
    json_path = os.path.join("app", f"{image_id}.json")
    print(image_path)
    
    # Display the current image with zoom functionality
    st.subheader(f"Image ID: {image_id}")
    img = Image.open(image_path)
    image_zoom(img, mode="scroll")  # Display zoomable image
# image_zoom(image, mode="scroll", size=(800, 600), keep_aspect_ratio=False, zoom_factor=4.0, increment=0.2)

    # JSON fields
    description = st.text_input("Usuario")
    id_caso = st.text_input("id_caso")
    damage_level = st.selectbox("Damage Level", ["Low", "Medium", "High"])
    comentario = st.text_input("comentario")

    if st.button("Save JSON"):
        new_json_data = {
            "id": image_id,
            "Usuario": description,
            "damage_level": damage_level,
            "comentario":comentario
        }

        os.makedirs(json_folder_path, exist_ok=True)
        with open(json_path, "w") as json_file:
            json.dump(new_json_data, json_file)

        st.success(f"JSON file created for {image_id}.")
                # Actualizar el estado a "processed"
        image_status[image_id] = "processed"
        
        save_status(status_file_path,image_status)
        
        # Actualizar a la siguiente imagen disponible
        st.session_state["current_image_id"] = get_next_available_image()
        st.rerun()
