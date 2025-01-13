# Image to 3D Processing Scripts

Este repositório contém três scripts principais em Python para processamento de imagens 2D e conversão para objetos 3D. Abaixo está uma descrição detalhada de cada um deles e da estrutura de diretórios necessária para o funcionamento correto.

## Scripts Principais

### 1. **processing.py**
- Processa uma única imagem 2D e gera um objeto 3D correspondente.
- Entrada: Caminho para a imagem 2D a ser processada.
- Saída: Um arquivo 3D gerado no diretório `results/`.

### 2. **mult_process.py**
- Processa todas as imagens localizadas no diretório `data/`.
- Para cada imagem, gera um arquivo 3D correspondente no diretório `results/`.

### 3. **mult_process_benchmarks.py**
- Realiza a mesma funcionalidade do `mult_process.py`, mas adicionalmente captura e armazena informações de benchmark (tempo de processamento, uso de CPU, etc.).
- Os benchmarks são salvos em um arquivo no diretório `results/`.

## Estrutura de Diretórios

Para garantir o funcionamento correto dos scripts, siga a estrutura de diretórios abaixo:

```
project-root/
├── data/          # Diretório para as imagens 2D de entrada
│   ├── image1.png
│   ├── image2.jpg
│   └── ...
├── results/       # Diretório para os objetos 3D e benchmarks gerados
├── processing.py
├── mult_process.py
├── mult_process_benchmarks.py
└── README.md
```

## Como Usar

1. Certifique-se de que as imagens 2D que deseja processar estejam no diretório `data/`.
2. Escolha o script adequado para sua necessidade:
   - Para processar uma única imagem: `python processing.py <caminho_da_imagem>`
   - Para processar todas as imagens no diretório `data/`: `python mult_process.py`
   - Para processar todas as imagens com captura de benchmarks: `python mult_process_benchmarks.py`
3. Verifique os resultados no diretório `results/`.

## Requisitos

- Python 3.12 ou superior.
- Dependências adicionais podem ser instaladas utilizando o comando:
  ```
  pip install -r requirements.txt
  ```
