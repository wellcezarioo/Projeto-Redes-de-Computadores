from PIL import Image

# Novo tamanho baseado nas dimensões do tabuleiro
nova_largura = 75  # Arredondado de 112.5
nova_altura = 30

nome = "balsa.png"

imagem_original = Image.open(nome)

# Redimensionar a imagem com LANCZOS
imagem_redimensionada = imagem_original.resize((2*nova_largura, nova_altura), Image.LANCZOS)

# Salvar a imagem redimensionada como um novo arquivo
imagem_redimensionada.save(nome)
