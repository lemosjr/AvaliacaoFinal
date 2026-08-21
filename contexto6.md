# Contexto do Sistema

Uma pequena empresa de comércio eletrônico deseja uma aplicação para registrar e processar pedidos de clientes.

O sistema deverá permitir que um cliente selecione produtos, informe quantidades e gere um pedido.

Após a criação, o pedido deverá possuir uma situação que represente seu estado atual.

A empresa precisa de uma solução simples para laboratório, mas espera que o sistema trate corretamente situações inválidas e não permita que uma operação parcialmente executada deixe o pedido em uma situação inconsistente.

A aplicação não precisa possuir uma interface visual sofisticada. Uma aplicação web simples utilizando Flask é suficiente.

## Problema a ser resolvido

Desenvolva uma aplicação capaz de:

- cadastrar produtos;
- consultar produtos;
- criar pedidos;
- adicionar produtos ao pedido;
- calcular o total;
- consultar pedidos;
- alterar a situação do pedido;
- impedir operações incompatíveis com o estado atual.

## Requisitos funcionais mínimos

O sistema deverá possuir, no mínimo:

Produtos

- identificador;
- descrição;
- preço;
- quantidade disponível.

Pedidos

- identificador;
- cliente;
- produtos;
- quantidades;
- valor total;
- situação;
- data de criação.

Operações

A aplicação deverá permitir:

1. cadastrar produto;
2. consultar produto;
3. criar pedido;
4. adicionar produto ao pedido;
5. calcular total;
6. consultar pedido;
7. alterar situação do pedido.

## Regras de negócio

- Um produto deve possuir preço válido.
- A quantidade disponível não pode ser negativa.
- Um pedido deve possuir cliente.
- Um pedido deve possuir pelo menos um produto antes de ser finalizado.
- A quantidade solicitada deve ser positiva.
- Não deve ser possível adicionar quantidade superior ao estoque disponível.
- Um pedido finalizado não deve receber novos produtos.
- Um pedido encerrado não deve ser alterado por uma operação incompatível.
- O total do pedido deve corresponder aos produtos e quantidades registrados.
- Operações inválidas não devem provocar encerramento inesperado da aplicação.

## Estados sugeridos

A aplicação deverá possuir estados coerentes para os pedidos, como:

- criado;
- em processamento;
- finalizado;
- cancelado.

A implementação exata e a estrutura utilizada ficam a critério do aluno.

Tecnologias

Utilize:

- Python;
- Pyqt6.

A persistência poderá ser feita utilizando estrutura em memória, arquivo ou banco de dados, desde que seja suficiente para demonstrar as funcionalidades e o processo de manutenção.

## ETAPA 1 — Construção a partir do contexto

Desenvolva a aplicação exclusivamente a partir do contexto, requisitos e regras apresentados.

Não será fornecido:

- código;
- banco de dados;
- estrutura de projeto;
- arquitetura;
- funções;
- classes;
- solução passo a passo.

Você deverá tomar as decisões técnicas necessárias para construir uma solução funcional.

## A aplicação deverá demonstrar

- cadastro de produto;
- consulta de produto;
- criação de pedido;
- inclusão de itens;
- cálculo do total;
- consulta do pedido;
- alteração de situação.

Documentação

Documente, de forma objetiva:

- objetivo da aplicação;
- funcionalidades;
- estrutura do projeto;
- forma de armazenamento utilizada;
- principais regras implementadas;
- decisões técnicas relevantes.

## Testes iniciais

Antes de avançar para a Etapa 2, demonstre que a aplicação funciona corretamente.

Apresente evidências de pelo menos:

1. criação de produto;
2. criação de pedido;
3. inclusão de item;
4. cálculo do total;
5. consulta do pedido.

## ETAPA 2 — Introdução controlada da falha

Após concluir e validar a versão inicial, introduza uma falha controlada relacionada ao estado do pedido.

A falha deverá permitir provocar uma situação em que uma operação sobre o pedido seja executada em um momento ou condição incompatível com seu estado atual.

O objetivo é produzir um comportamento inconsistente, erro não tratado ou interrupção inesperada durante o processamento.

A prova não informa qual função, classe, rota ou componente deverá ser alterado.

Você deverá identificar, dentro da própria aplicação, um ponto adequado para introduzir a falha.

Importante

A alteração deve ser controlada.

Não destrua o projeto inteiro nem remova funcionalidades que não estejam relacionadas ao cenário.

Evidências

Apresente:

- versão funcional anterior;
- alteração realizada;
- trecho de código relacionado;
- cenário escolhido;
- descrição do comportamento que deverá ser provocado.

ETAPA 3 — Diagnóstico e evidência do incidente

Execute o cenário criado na Etapa 2.

Você deverá atuar como responsável pela sustentação da aplicação.

## Procedimentos obrigatórios

1. reproduza o problema;
2. registre os passos utilizados;
3. identifique a entrada ou condição que provocou a falha;
4. registre o comportamento observado;
5. capture a mensagem de erro ou evidência equivalente;
6. analise o stack trace, quando disponível;
7. identifique a causa técnica;
8. identifique o componente afetado;
9. explique o impacto do problema para o sistema.

## Registro do incidente

Produza um pequeno relatório contendo:

Título do incidente: Nome objetivo para o problema.

## Descrição: O que aconteceu?

Passos para reprodução: Como outra pessoa poderia reproduzir o problema?

## Resultado esperado: O que deveria acontecer?

## Resultado obtido: O que realmente aconteceu?

## Causa técnica: Por que o problema aconteceu?

Componente afetado: Qual parte da aplicação foi impactada?

Impacto: Qual consequência o problema poderia causar para o usuário ou negócio?

Evidências

Apresente:

- captura da aplicação;
- terminal/console, quando aplicável;
- stack trace, quando existente;
- código relacionado;
- relatório do incidente.

## ETAPA 4 — Correção, melhoria e validação

Implemente uma correção para o problema identificado.

A correção deverá solucionar o defeito sem comprometer o funcionamento normal do sistema.

Além da correção, a aplicação deverá possuir mecanismo adequado para lidar com a condição inesperada.

A solução deverá contemplar:

- validação da condição;
- tratamento adequado da exceção ou situação inválida;
- mensagem compreensível;
- manutenção da consistência do pedido;
- registro da ocorrência em arquivo de log;
- data e hora do evento;
- descrição suficiente para posterior diagnóstico.

## Testes obrigatórios

Após a correção, realize no mínimo quatro testes:

## Teste 01 — Cenário que provocava a falha

Demonstre que o problema não ocorre mais.

## Teste 02 — Operação normal

Demonstre que um pedido válido continua funcionando.

## Teste 03 — Regra de negócio

Demonstre uma tentativa de operação incompatível com uma regra do sistema e o tratamento adequado.

## Teste 04 — Regressão

Demonstre outra funcionalidade do sistema que poderia ter sido afetada pela alteração e comprove que continua funcionando.

Evidências

Apresente:

- código corrigido;
- evidência da correção;
- testes realizados;
- resultados dos testes;
- arquivo de log;
- explicação técnica da solução.

## ETAPA 5 — Versionamento e entrega

A manutenção deverá ser realizada utilizando Git.

Crie uma branch específica para o hotfix.

Utilize um nome relacionado ao problema identificado.

Exemplo:

git checkout -b hotfix/estado-pedido

O exemplo acima serve apenas para demonstrar o conceito. O nome final da branch deverá refletir o problema realmente identificado.

## Registro da manutenção

Apresente evidências dos comandos utilizados:

git status

git branch

git add .

git commit

git log --oneline

A mensagem do commit deverá ser técnica e descrever objetivamente a alteração realizada.

Versionamento

A versão inicial deverá ser identificada como:

v1.0.0

Após a correção, crie uma nova versão:

v1.0.1

A criação da tag deverá ser demonstrada no histórico.

Exemplo:

git tag

Caso realize merge da branch de hotfix na branch principal, apresente a evidência.

## Entrega final

A entrega deverá conter:

- código-fonte final;
- documentação;
- relatório do incidente;
- evidências da falha;
- evidências da correção;
- testes;
- arquivo de log;
- histórico Git;
- identificação da versão final;
- explicação das decisões técnicas.
