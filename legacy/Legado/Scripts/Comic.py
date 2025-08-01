from PIL import Image
import os

# Solicita o nome do arquivo ao usuário
nome_pdf = input("Digite o nome desejado para o PDF (sem extensão): ").strip() + ".pdf"

# Caminho para salvar o PDF gerado
caminho_pasta = "C:/Users/vilan/Comics"

# Certifica que a pasta existe
if not os.path.isdir(caminho_pasta):
    print("Caminho inválido. Verifique se a pasta existe.")
    exit()

# Diretório das imagens
pasta_imagens = "C:/Users/vilan/COMIC_CREATOR/Images"

# Verifica se o diretório das imagens existe
if not os.path.exists(pasta_imagens):
    print("Diretório de imagens não encontrado.")
    exit()

# Carrega as imagens e ordena, filtra arquivos válidos (.jpg e .webp)
arquivos = sorted([f for f in os.listdir(pasta_imagens) if f.lower().endswith(('.jpg', '.webp', '.png'))])
if not arquivos:
    print("Nenhuma imagem válida (.jpg ou .webp) encontrada.")
    exit()

# Carrega as imagens para serem convertidas
imagens = []
for arquivo in arquivos:
    try:
        imagem = Image.open(os.path.join(pasta_imagens, arquivo)).convert("RGB")
        imagens.append(imagem)
    except Exception as e:
        print(f"Erro ao carregar a imagem {arquivo}: {e}")

# Verifica se há imagens válidas para salvar
if not imagens:
    print("Nenhuma imagem válida foi carregada.")
    exit()

# Define o caminho completo do PDF
caminho_completo_pdf = os.path.join(caminho_pasta, nome_pdf)

# Salvar em PDF
imagens[0].save(caminho_completo_pdf, save_all=True, append_images=imagens[1:])
print(f"PDF '{nome_pdf}' criado com sucesso em '{caminho_pasta}'!")

for arquivo in arquivos:
    try:
        os.remove(os.path.join(pasta_imagens, arquivo))
        print(f"Arquivo '{arquivo}' removido com sucesso.")
    except Exception as e:
        print(f"Erro ao tentar remover o arquivo '{arquivo}': {e}")
