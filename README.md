Iniciar o projeto:

1 - Instale o projeto:
2 - Instale os pacotes necessários para o funcionamento do programa na sua máquina ou em um ambiente virtual: 'pip install -r requirements. txt' 
3 - Crie um arquivo .env na raíz do projeto e o preencha com as variáveis de ambiente:

DB_HOST=meu_host
DB_USER=meu_user
DB_PASSWORD=minha_senha
DB_NAME=meu_banco
DB_PORT=minha_porta
PREFIX=meu_prefixo

SECRET_KEY=minha_chave_secreta
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=tempo_de_duracao_dos_tokens_de_acesso

ROLLBAR_TOKEN=meu_token_do_rollbar

SECRET_KEY_USER=minha_chave_secreta_de_usuario

4 - Rode o programa: 'uvicorn main:app'
5 - Acesse o endpoint /docs/firstuser e envie o body com a sua SECRET_KEY_USER.