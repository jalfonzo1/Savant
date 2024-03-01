import requests
from bs4 import BeautifulSoup
import csv
import time

# Función para obtener los productos en oferta de MercadoLibre Colombia
def obtener_productos_mercadolibre():
    url = "https://www.mercadolibre.com.co/ofertas#nav-header"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    productos = []

    for producto in soup.find_all("div", class_="section_promotions_web"):
        nombre = producto.find('p', class_='promotion-item__title').get_text()
        precio = producto.find('span', class_='andes-money-amount__fraction').get_text()
        discount = producto.find('span', class_='promotion-item__discount-text').get_text()
        productos.append({"nombre": nombre, "precio": precio, "descuento": discount})
    return productos

# Función para buscar productos en Amazon Colombia y obtener información de precios y disponibilidad
def buscar_en_amazon(productos):
    for producto in productos:
        nombre = producto["nombre"]
        # Realizar búsqueda en Amazon
        url = f"https://www.amazon.com.co/s?k={nombre.replace(' ', '+')}"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        # Obtener información del primer resultado (asumiendo que es relevante)
        primer_resultado = soup.find("div", class_="s-result-item")
        if primer_resultado:
            precio = primer_resultado.find("span", class_="a-price-whole").text.strip()
            disponibilidad = "Disponible para envío a Colombia" if soup.find(text="Colombia") else "No disponible para envío a Colombia"
            producto["precio_amazon"] = precio
            producto["disponibilidad_amazon"] = disponibilidad
        else:
            producto["precio_amazon"] = "No disponible"
            producto["disponibilidad_amazon"] = "No disponible"
    return productos

# Función para guardar los resultados en un archivo CSV
def guardar_resultados(productos):
    with open("resultados.csv", "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["nombre", "precio", "descuento", "precio_amazon", "disponibilidad_amazon"] 
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for producto in productos:
            writer.writerow(producto)

# Función para actualizar la información periódicamente
def actualizar_info():
    while True:
        productos_mercadolibre = obtener_productos_mercadolibre()
        productos_con_amazon = buscar_en_amazon(productos_mercadolibre)
        guardar_resultados(productos_con_amazon)
        print("Información actualizada. Esperando próximo intervalo de actualización...")
        time.sleep(3600)  # Esperar 1 hora antes de la próxima actualización

# Ejecutar el script
if __name__ == "__main__":
    productos_mercadolibre = obtener_productos_mercadolibre()
    productos_con_amazon = buscar_en_amazon(productos_mercadolibre)
    guardar_resultados(productos_con_amazon)
    actualizar_info()
