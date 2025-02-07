# 🚀 FileFlow - Seu Organizador de Arquivos Inteligente

E aí, pessoal! Criei esse projeto pra resolver um problema que todo mundo tem: aquela pasta bagunçada cheia de arquivos misturados. O **FileFlow** organiza tudo automaticamente, deixando seu PC mais limpo que armário de Marie Kondo! 

<div align="center">
  <img src="https://github.com/Jeffinp/file_organizer/blob/main/image/Screenshot_1051.png" alt="Interface Moderna" width="600">
  <p><i>Interface limpa e moderna - até seu avô vai saber usar!</i></p>
</div>

## 💡 Por que usar?

- **Organização ninja** em pastas categorizadas (documentos, imagens, músicas, etc)
- **Detector de duplicatas** usando hash SHA-256 (não repete arquivo igual!)
- **Segurança total** com verificação de permissões e lock de arquivos
- **Interface moderna** com dark mode, animações suaves e feedback visual
- **Logs detalhados** pra saber exatamente o que aconteceu

## 🛠️ Como Funciona por Baixo dos Panos

### 🔍 Núcleo Python
```python
# Exemplo do sistema anti-duplicatas
def is_duplicate(file1, file2):
    return calculate_hash(file1) == calculate_hash(file2)  # Comparação via SHA-256
```
- **Sistema de Travas**: Usa `threading.Lock` pra evitar que múltiplos processos meçam os arquivos
- **Verificação de Permissões**: Testa leitura/escrita antes de qualquer operação
- **Logging Avançado**: Gera logs rotativos (5MB cada) com info de threads e timestamps

### 🌐 Interface Web
- **Frontend**: HTML/CSS/JS com design responsivo e 60+ animações
- **Backend**: Flask rodando localmente na porta 5000
- **Bridge**: Webview cria janela desktop integrada com o Python

## ⚙️ Tecnologias Usadas

| Camada          | Ferramentas                                                                 |
|-----------------|-----------------------------------------------------------------------------|
| **Backend**     | Python 3.10+, Flask, hashlib, logging                                       |
| **Frontend**    | HTML5, CSS3 (Custom Properties), JavaScript ES6+                           |
| **Interface**   | Webview (para janela desktop), Font Awesome 6                              |
| **Segurança**   | SHA-256, Verificação de permissões, File locking                           |

## 🎮 Como Usar

1. **Instalação Relâmpago** ⚡
```bash
git clone https://github.com/Jeffinp/file_organizer
cd file_organizer
pip install -r requirements.txt
```

2. **Rodando o Programa** 🚀
```bash
python app.py
```

3. **Passo a Passo Mágico** ✨
   - Clique em "Procurar" e escolha a pasta
   - Veja a prévia das categorias
   - Clique em "Organizar" e assista a mágica acontecer!

## 🗂️ Sistema de Categorias

| Pasta         | Extensões Suportadas                                  |
|---------------|-------------------------------------------------------|
| **Imagens**   | .jpg, .png, .webp, .svg, .gif (+7 formatos)           |
| **Documentos**| .pdf, .docx, .xlsx, .pptx, .txt (+10 formatos)        |
| **Mídia**     | .mp3, .mp4, .mkv, .flac, .wav (+15 codecs)            |
| **Códigos**   | .py, .js, .html, .css, .java (+8 linguagens)          |
| **Outros**    | Qualquer extensão não listada                         |

## 🚨 E Se...?

- **Arquivo em uso?** → O programa detecta e pula temporariamente
- **Sem permissão?** → Avisa claramente onde está o problema
- **Erro desconhecido?** → Gera log detalhado com stack trace

## 💡 Dicas Pro

- Use **CTRL+CLICK** no campo de diretório para colar caminhos
- **Duplo clique** nos itens recentes para seleção rápida
- Tecla **ESC** fecha qualquer diálogo aberto

## 📈 Próximos Passos

- [ ] Upload de arquivos via arrastar-e-soltar
- [ ] Sistema de regras personalizadas
- [ ] Suporte a cloud storage (Dropbox, Google Drive)

---

Quer ver como ficou na prática? Dá uma olhada no código e se achar algum bug ou tiver ideia massa, abre uma issue! 🐛💡