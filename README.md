# Organizador de Arquivos

Ae galera, criei um programa bem bacana pra organizar arquivos no computador! 

Ele pega um diretório que você escolher e organiza tudo bonitinho em pastas separadas por tipo: **imagens**, **documentos**, **músicas**, **vídeos**, e por aí vai. Assim, fica muito mais fácil achar as coisas depois! 

## Funcionalidades

- **Organização inteligente:** O programa organiza automaticamente os arquivos nas pastas corretas com base no tipo de cada um.
- **Tratamento de erros e logging:** Caso algo dê errado, o programa gera logs detalhados tanto no console quanto em um arquivo, facilitando o diagnóstico de problemas.
- **Verificação de permissões:** Antes de mexer nos arquivos, o app verifica se tem permissão de leitura e escrita na pasta.
- **Tratamento de arquivos duplicados:** Ele usa um hash SHA-256 para identificar arquivos idênticos e evita mover cópias desnecessárias. 
- **Travamento de arquivos:** Impede que vários processos tentem acessar o mesmo arquivo ao mesmo tempo, evitando conflitos.

## Tecnologias Usadas

- **Python**: Linguagem de programação principal.
- **Flask**: Framework web que cuida da comunicação entre o frontend e o backend.
- **Webview**: Biblioteca que cria uma interface gráfica simples, usando HTML, CSS e JavaScript em uma janela desktop.

> A interface é bem simples e intuitiva
![Print da Interface](https://github.com/Jeffinp/file_organizer/blob/main/image/Screenshot_1051.webp)

## Como Usar

1. Clone o repositório:
    ```bash
    git clone https://github.com/Jeffinp/file_organizer
    ```

2. Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

3. Execute o programa:
    ```bash
    python app.py
    ```

4. Escolha o diretório que deseja organizar e pronto!

## Exemplo de Organização

O programa vai criar as seguintes pastas no diretório escolhido:

- **Imagens**
    - `.jpg`, `.png`, `.gif`, `.svg`, etc.
- **Documentos**
    - `.pdf`, `.docx`, `.txt`, `.xlsx`, etc.
- **Músicas**
    - `.mp3`, `.wav`, `.flac`, etc.
- **Vídeos**
    - `.mp4`, `.avi`, `.mkv`, etc.
- **Outros**
    - Arquivos que não se encaixam nas categorias acima.

## Feedback

De vez em quando eu faço algumas atualizações, mas já pode testar como quiser! O programa está totalmente funcional e qualquer feedback é **bem-vindo**. 

Agora organiza esse computador aí, cara, ele tá precisando.
