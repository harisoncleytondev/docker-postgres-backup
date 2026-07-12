# Backup Script

Script de backup automático para containers PostgreSQL. Conecta-se ao daemon Docker local, identifica containers com backup habilitado, realiza o dump dos bancos de dados e faz o upload dos arquivos para o Google Drive.

## Funcionamento

1. O script se conecta ao daemon Docker via socket e lista todos os containers em execução.
2. Containers com a label `backup.enabled=true` são selecionados.
3. Para cada container selecionado, as variáveis `POSTGRES_DB`, `POSTGRES_USER` e `POSTGRES_PASSWORD` são lidas e o `pg_dump` é executado dentro do próprio container.
4. O arquivo de dump gerado é salvo em um diretório temporário e enviado para o Google Drive em uma pasta com data no nome.
5. Os arquivos temporários são removidos após o upload.
6. O processo se repete em um intervalo agendado pelo APScheduler.

## Pré-requisitos

- Docker instalado na máquina host
- Containers PostgreSQL em execução com a label `backup.enabled=true`
- Um projeto no Google Cloud com a API Drive ativada
- Credenciais OAuth 2.0 (Client ID e Client Secret) do tipo "Desktop application"

## Configuração

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```
GOOGLE_PROJECT_ID=id-do-seu-projeto
GOOGLE_CLIENT_ID=seu-client-id
GOOGLE_CLIENT_SECRET=seu-client-secret
GOOGLE_FOLDER_ID=id-da-pasta-no-drive-para-os-backups
```

### Autenticação Google Drive

Na primeira execução, o script abrirá uma janela do navegador para o consentimento OAuth. Após a autorização, um arquivo `token.json` será criado localmente e reutilizado nas execuções seguintes.

Quando executado dentro do Docker, esse fluxo requer ajustes:

1. Execute o script localmente uma vez para gerar o `token.json`:
   ```bash
   pip install -r requirements.txt
   python main.py
   ```
2. Monte o `token.json` gerado dentro do container na execução.

### Labels dos containers

Adicione a label `backup.enabled=true` em qualquer container PostgreSQL que deseja fazer backup:

```bash
docker run -d \
  --label backup.enabled=true \
  -e POSTGRES_DB=mydb \
  -e POSTGRES_USER=myuser \
  -e POSTGRES_PASSWORD=mypass \
  postgres:16
```

Para adicionar a label em containers existentes, é necessário recriá-los com a flag `--label`.

## Executando com Docker

### Build da imagem

```bash
docker build -t backup-script .
```

### Execução do container

```bash
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /caminho/para/.env:/app/.env \
  -v /caminho/para/token.json:/app/token.json \
  backup-script
```

Explicação dos volumes montados:

- `/var/run/docker.sock` -- necessário para que o script se comunique com o daemon Docker do host e execute comandos dentro dos containers PostgreSQL.
- `.env` -- variáveis de ambiente com as credenciais do Google e ID da pasta.
- `token.json` -- arquivo de token OAuth gerado após a primeira autenticação.

## Estrutura do projeto

```
backup-script/
  main.py                  ponto de entrada
  requirements.txt         dependências Python
  Dockerfile               definição da imagem Docker
  .dockerignore            arquivos excluídos do build Docker
  scripts/
    docker.py              cliente Docker e lógica do pg_dump
    drive_upload.py        lógica de upload para o Google Drive
    schedule_activate.py   configuração do agendador e orquestração
  temp/                    arquivos de dump temporários (gitignored)
```

## Dependências

- APScheduler -- agendamento
- docker -- SDK Docker para Python
- google-api-python-client / google-auth -- API Google Drive
- python-dotenv -- carregamento de variáveis de ambiente
