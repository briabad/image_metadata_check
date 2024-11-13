import os
import streamlit as st
import json
import boto3
import os


def print_json_file(json_file_path):
    """
    Lee un archivo JSON y muestra su contenido en Streamlit.

    Args:
        json_file_path (str): Ruta al archivo JSON.
    """
    with open(json_file_path, "r") as file:
        data = json.load(file)
        st.subheader("Contenido del archivo JSON:")
        st.json(data)




def print_directory_contents(directory_path):
    """
    Lista y muestra los elementos de un directorio en Streamlit.

    Args:
        directory_path (str): Ruta al directorio.
    """
    st.subheader(f"Contenido del directorio {directory_path}:")
    if os.path.isdir(directory_path):
        items = os.listdir(directory_path)
        for item in items:
            st.write(item)  # Muestra cada elemento en una nueva línea
    else:
        st.error("El directorio especificado no existe.")




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


# Find images without an associated JSON
def get_images_without_json(image_ids, image_folder, json_folder):
    images_without_json = []
    for image_id in image_ids:
        image_path = os.path.join(image_folder, f"{image_id}.jpg")
        json_path = os.path.join(json_folder, f"{image_id}.json")
        if os.path.isfile(image_path) and not os.path.isfile(json_path):
            images_without_json.append(image_id)
    return images_without_json

# Función para obtener la primera imagen disponible
def get_next_available_image(image_status,status_file_path):
    for image_id, status in image_status.items():
        if status == "available":
            # Marcar como "in use" para evitar acceso de otros usuarios
            image_status[image_id] = "reserved"
            save_status(status_file_path,image_status)
            return image_id
    return None


def save_status(status_file_path,image_status):
    with open(status_file_path, "w") as status_file:
        json.dump(image_status, status_file)


def download_from_s3(bucket_name, s3_key, local_directory, aws_access_key_id=None, aws_secret_access_key=None):
    """
    Download a file from an S3 bucket to a specified local directory.
    
    :param bucket_name: str, name of the S3 bucket
    :param s3_key: str, S3 object key (file path in the bucket)
    :param local_directory: str, local directory path where the file should be saved
    :param aws_access_key_id: str, AWS access key ID (optional, if credentials are set in the environment)
    :param aws_secret_access_key: str, AWS secret access key (optional)
    """
    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
    s3 = session.resource('s3')
    bucket = s3.Bucket(bucket_name)
    
    # Prepare local file path
    local_file_path = os.path.join(local_directory, os.path.basename(s3_key))
    
    # Download the file
    try:
        bucket.download_file(s3_key, local_file_path)
        print(f"Downloaded {s3_key} to {local_file_path}")
    except Exception as e:
        print(f"Failed to download {s3_key}: {e}")





def create_image_status_file_s3(image_bucket_name, image_folder_path, json_folder_path, status_file_path, aws_access_key_id=None, aws_secret_access_key=None):
    """
    Creates a JSON file containing the status of each image in specified S3 folders.
    If a JSON file exists for an image, the status will be "processed". If not, it will be "available".
    
    Args:
        image_bucket_name (str): Name of the S3 bucket where images and JSON files are stored.
        image_folder_path (str): S3 folder path where images are located.
        json_folder_path (str): S3 folder path where JSON metadata files are located.
        status_file_path (str): Local path where the status JSON file will be saved.
        aws_access_key_id (str): AWS access key ID (optional, if credentials are set in the environment).
        aws_secret_access_key (str): AWS secret access key (optional).
    """
    # Set up S3 session
    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )
    s3 = session.resource('s3')
    bucket = s3.Bucket(image_bucket_name)

    # Dictionary to store the status of each image
    image_status = {}

    # List all .jpg images in the image_folder_path
    image_files = [obj.key for obj in bucket.objects.filter(Prefix=image_folder_path) if obj.key.endswith('.jpg')]
    print(image_files)
    # List all .json metadata files in the json_folder_path
    json_files = {os.path.splitext(os.path.basename(obj.key))[0] for obj in bucket.objects.filter(Prefix=json_folder_path) if obj.key.endswith('.json')}
    print(json_files)
    # Determine the status of each image
    for image_key in image_files:
        image_id = os.path.splitext(os.path.basename(image_key))[0]  # Extract image ID without extension

        # Check if there's an associated JSON file
        if image_id in json_files:
            image_status[image_id] = "processed"
        else:
            image_status[image_id] = "available"
    
    print(image_status)

    # Save the status dictionary as a JSON file locally
    with open(status_file_path, "w") as status_file:
        json.dump(image_status, status_file, indent=4)
    
    print(f"Status file created at: {status_file_path}")
