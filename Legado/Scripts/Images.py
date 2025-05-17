import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Caminho da pasta onde as imagens serão salvas
pasta_imagens = "C:/Users/vilan/COMIC_CREATOR/Images"
os.makedirs(pasta_imagens, exist_ok=True)

# Solicita a URL do site ao usuário
url_site = input("Digite a URL do site para baixar as imagens: ").strip()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

# Faz o request para o site
try:
    print(f"Acessando o site: {url_site}")
    response = requests.get(url_site, headers=headers)
    response.raise_for_status()
    print(f"Status da requisição: {response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"Erro ao acessar o site: {e}")
    exit()

# Parseia o conteúdo HTML do site
soup = BeautifulSoup(response.text, 'html.parser')

# Encontra todas as tags <img> no HTML
tags_imagens = soup.find_all('img')
print(f"Total de tags <img> encontradas: {len(tags_imagens)}")

def obter_url_imagem(tag):
    """Tenta obter uma URL válida da tag de imagem"""
    # Prioriza 'src', mas verifica 'data-src' ou 'data-lazy' se necessário
    for atributo in ['src', 'data-src', 'data-lazy']:
        url = tag.get(atributo)
        if url and not url.startswith("data:"):
            return url
    return None

# Baixa as imagens filtradas
for img in tags_imagens:
    img_url = obter_url_imagem(img)
    if img_url:
        img_url = urljoin(url_site, img_url)
        print(f"Processando imagem: {img_url}")
        if img_url.lower().endswith(('.jpg', '.jpeg', '.webp', '.png')):
            try:
                print(f"Baixando imagem: {img_url}")
                img_data = requests.get(img_url, headers=headers).content
                nome_arquivo = os.path.basename(img_url.split("?")[0])
                caminho_completo = os.path.join(pasta_imagens, nome_arquivo)
                with open(caminho_completo, 'wb') as arquivo:
                    arquivo.write(img_data)
                print(f"Imagem salva: {nome_arquivo}")
            except Exception as e:
                print(f"Erro ao baixar {img_url}: {e}")
    else:
        print("Tag <img> sem URL válida encontrada.")
