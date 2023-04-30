# Renovator
Um pequeno script escrito em [Python](https://www.python.org/) que renova automaticamente seus empréstimos das bibliotecas da [UFSM](https://www.ufsm.br/).

## Como usar:
1. Crie um fork do repositório e, dentro dele, siga as instruções seguintes.
2. Vá até a aba `Actions` e ative as workflows.
![image](https://user-images.githubusercontent.com/40345645/235337692-c310da15-b6d6-4af1-9860-7647e3f351ac.png)
3. Vá até a aba `Settings` e entre em `Actions` da seção `Variables and secrets`.
![image](https://user-images.githubusercontent.com/40345645/235337715-f92b9243-499d-4640-ae39-3e070b882257.png)
4. Lá, adicione duas secrets:
- `Username` contendo sua matrícula.
- `Password` content sua senha do portal.
![image](https://user-images.githubusercontent.com/40345645/235337747-6f7a2f7b-804e-48e5-88db-372131f48464.png)
5. Pronto, agora seus livros irão ser renovados diariamente. Na aba `Actions`, você pode ver as logs da execução e rodar o script antes do prazo determinado.

<hr />

Feito por [@jaimeadf](https://github.com/jaimeadf/) para propósitos educacionais.
