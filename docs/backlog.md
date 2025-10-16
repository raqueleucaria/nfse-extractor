# Requisitos e Backlog

Este documento detalha os requisitos do projeto e o backlog de tarefas para o desenvolvimento.

## Requisitos

Os requisitos estão divididos em funcionais (RF) e não funcionais (RNF), com o status de implementação.


| ID    | Descrição                                                                                                 | Implementação        |
| ----- | --------------------------------------------------------------------------------------------------------- | -------------------- |
| RF01  | O sistema deve aceitar o upload de arquivos nos formatos PDF e imagem.                                    | ✅ |
| RF02  | A solução deve analisar o texto do documento e extrair o CNPJ do prestador (formato `XX.XXX.XXX/XXXX-XX`). | ✅  |
| RF03  | A solução deve analisar o texto e extrair a Razão Social do prestador (geralmente próxima a "Nome/Razão Social"). | ✅  |
| RF04  | O processo de extração deve lidar com variações comuns no texto, como múltiplos espaços e quebras de linha. | ✅ |
| RF05  | A solução deve gerar e exibir uma string no formato JSON contendo as chaves `cnpj_prestador` e `nome_prestador`. | ✅ |
| RF06  | (Melhoria) A solução deve permitir a persistência dos dados extraídos, associando-os ao fornecedor e ao mês. |  |
| RNF01 | O código-fonte completo deve ser disponibilizado em um repositório no GitHub.                             | ✅  |
| RNF02 | O processo de desenvolvimento deve ser organizado em tarefas (GitHub Projects).             | ✅ |
| RNF03 | Um vídeo curto demonstrando a usabilidade da aplicação deve ser gravado e compartilhado (Google Drive).    | -    |
| RNF04 | A solução deve ter testes para garantir a corretude da extração de dados. ([Modelo de nfse](./NFSe_ficticia_layout_completo.pdf))  | ✅ |
| RNF05 | Criar funcionalidades de melhoria.  | Parcial - Algumas melhorias já foram implementadas, como testes automatizados; Melhorar apresentação dos resultados na interface; Botão "Copiar para área de transferência" para o JSON... Porém outras funcionalidades sugeridas no backlog persistência dos dados ainda estão pendentes. |

## Backlog

### Feature 1 - Documentação Inicial
**Objetivo**: Estabelecer a base do projeto, definindo as necessidades do usuário, planejando a arquitetura e organizando as tarefas de desenvolvimento.
- Backlog
- Diagramas (opcional)
- Criar todas as issues no GitHub
- Configurar o GitHub Projects para gerenciamento das tarefas.
- **Requisitos relacionados**: `RNF02`.


### Feature 2 — Configuração do Ambiente
**Objetivo**: Preparar o ambiente de desenvolvimento, controle de versão.

- Criar o repositório no GitHub.
- Pesquisar e escolher bibliotecas/ferramentas necessárias
- Definir a linguagem principal
- Inicializar a estrutura base de diretórios
- Hello World com linguagem/tecnologia escolhida
- **Requisitos relacionados**: `RNF01`.

### Feature 3 — Backend
**Objetivo**: Implementar a lógica de processamento e extração.

- Criar exemplos de documentos fiscais (PDF e imagem) com variações.
- Implementar leitura de texto de PDFs.
- Implementar leitura de texto de imagens.
- Implementar extração de CNPJ.
- Implementar extração da Razão Social do prestador.
- Tratar variações no texto (espaços, quebras de linha, caracteres especiais).
- Desenvolver função que formata os dados extraídos em JSON.
- **Requisitos relacionados**: `RF01`, `RF02`, `RF03`, `RF04`, `RF05`. 

### Feature 4 — Testes
**Objetivo**: Garantir a qualidade e robustez do código de extração.
- Implementar tratamento de erros para arquivos inválidos ou dados não encontrados.
- Escrever testes unitários para funções de extração (atende RNF04).
- **Requisitos relacionados**: `RNF04`.

### Feature 5 — Frontend
**Objetivo**: Permitir interação do usuário com o sistema.
- Desenvolver interface para upload de arquivos.
- Conectar a interface ao core de extração.
- Exibir o resultado JSON ao usuário.
- **Requisitos relacionados**: `RF01`, `RF05`. 

### Feature 7 — Funcionalidades Adicionais (OPCIONAL)
**Objetivo**: Melhorar usabilidade e robustez.

- Suporte a upload de múltiplos arquivos / processamento em lote.
- Melhorar apresentação dos resultados na interface.
- Adicionar botão "Copiar para área de transferência" para o JSON.
- Implementar persistência local (CSV/JSON) para associar fornecedor e mês (atende RF06).
- Hostagem da aplicação.
  
- **Requisitos relacionados**: `RF01`, `RF-05` 

### Feature 7 — Finalização e Documentação
**Objetivo**: Preparar entrega e materiais de apoio.

- Criar README.md completo no repositório.
- Gravar vídeo curto demonstrando a usabilidade.
- Fazer upload do vídeo para Google Drive e gerar link compartilhável.
- Revisar código, commits e organização do repositório.
- Enviar e-mail final com links e documentação.
- **Requisitos relacionados**: `RNF-01`, `RNF03`. 
