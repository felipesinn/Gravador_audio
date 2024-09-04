# SoudMasterPro

## Instalação

1. **Clone o repositório**:
    ```bash
    git clone https://github.com/seu-usuario/sancast_recorder.git
    cd sancast_recorder
    ```

2. **Instale as dependências**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Execute o aplicativo**:
    ```bash
    python main.py
    ```

## Empacotando para Distribuição

1. **Instale o PyInstaller**:
    ```bash
    pip install pyinstaller
    ```

2. **Crie o executável**:
    ```bash
    pyinstaller --onefile --windowed main.py
    ```

O executável será gerado na pasta `dist/` e estará pronto para ser executado no Windows.

## Como Usar

- **Gravar**: Clique no botão "Gravar" para iniciar a gravação.
- **Pausar**: Clique em "Pausar" para pausar a gravação.
- **Parar**: Clique em "Parar" para encerrar a gravação e salvar o arquivo.
- **Selecionar Dispositivo**: Escolha a placa de áudio no menu suspenso antes de iniciar a gravação.
