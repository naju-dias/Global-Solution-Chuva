# Neighborhood Action Dashboard – Ocorrências da Chuva

Global Solution 2026.2 – CitizenTech (FIAP)

## 1. Equipe

- Ana Julia Alves Dias – RM: 576930

## 2. Bairro simulado, problema e público

O projeto simula um painel de ocorrências para bairros que sofrem com os efeitos da chuva forte. Os bairros são fictícios: **Centro**, **Vila Nova** e **Jardim das Flores**.

Depois de temporais é comum aparecer poste apagado, calçada destruída, bueiro entupido, árvore caída, goteira em prédio público e outros problemas. Muitas vezes essas reclamações ficam espalhadas e ninguém sabe o que já foi resolvido. O sistema organiza essas ocorrências para os moradores acompanharem a situação e para quem cuida do bairro ver quais problemas são mais frequentes.

Todos os dados são **inventados**. Não existe nome de pessoa, endereço exato, telefone nem nenhum dado pessoal.

## 3. Como executar

Precisa do Python 3 instalado. Na pasta principal do repositório:

```
python src/sistema.py
```

Os arquivos de dados ficam na pasta `data/` e são lidos automaticamente.

## 4. Estrutura do repositório

```
README.md
src/sistema.py          -> código do sistema
data/ocorrencias.csv    -> ocorrências simuladas
data/historico.csv      -> histórico simulado de mudanças de situação
docs/uso_ia.md          -> como a IA foi usada
```

## 5. Formato dos dados

**ocorrencias.csv** (separado por `;`):

| Campo | Obrigatório | Descrição |
|---|---|---|
| id | sim | código único, só números (ex: 001) |
| categoria | sim | iluminacao, acessibilidade, limpeza ou conservacao |
| descricao | sim | descrição breve do problema |
| bairro | sim | localidade genérica |
| dia_abertura | sim | dia simulado em que foi aberta (número ≥ 1) |
| status | sim | aberta, em_analise ou concluida |

**historico.csv**: `id;dia;de;para` (cada linha é uma mudança de situação).

**Situações:**
- **aberta**: foi registrada e ninguém examinou ainda.
- **em_analise**: alguém já está avaliando o problema.
- **concluida**: o problema foi resolvido.

O arquivo tem 14 linhas: 12 válidas e **2 inválidas de propósito** para testar a validação (a 013 está sem categoria e a 014 tem situação "resolvido", que não existe no sistema). O histórico tem 11 eventos.

## 6. Estruturas de dados usadas e por quê

| Estrutura | Onde usei | Por que |
|---|---|---|
| **Lista** (`ocorrencias`) | guarda todas as ocorrências | dá para percorrer com `for` para listar, filtrar e contar |
| **Dicionário** (`por_id`) | acha uma ocorrência pelo código | busca direta, sem precisar percorrer a lista toda |
| **Fila** (`fila`) | ocorrências ainda não examinadas | a primeira que foi registrada é a primeira a ser examinada (FIFO) |
| **Pilha** (`pilha`) | últimas atualizações de status | a última alteração fica no topo, então é fácil mostrar as mais recentes (LIFO) |
| **Hierarquia** (dicionário dentro de dicionário) | bairro → categoria → códigos | organiza os problemas por lugar e por tipo; ajuda a ver onde cada tipo de problema acontece |
| **Matriz** (lista de listas) | categoria × situação | resume as quantidades numa tabela e facilita os totais |

## 7. Regras lógicas

**Cadastro e validação** (`validar_registro`): o sistema recusa o registro se
- o código não for número ou já existir;
- categoria, descrição ou bairro estiverem vazios;
- a categoria ou a situação não estiverem nas listas padronizadas;
- o dia não for um número válido.

**Atualização de status** (`atualizar_status`):
- código não encontrado → avisa que não existe;
- situação desconhecida → não altera nada;
- ocorrência concluída não pode mudar;
- ocorrência já examinada não volta para "aberta";
- se tudo estiver certo, altera e grava no histórico (e tira da fila, se estava nela).

**Consulta:** busca por código e filtro por categoria e/ou situação.

### Expressão booleana do filtro

```python
if (categoria == "todas" or o["categoria"] == categoria) and (status == "todos" or o["status"] == status):
```

Funciona assim: a ocorrência entra no resultado quando **a categoria combina** (ou o usuário escolheu "todas") **E** **a situação combina** (ou o usuário escolheu "todos"). Exemplo: categoria = limpeza e status = aberta → só entra ocorrência de limpeza que esteja aberta. Se o usuário digitar "todas" e "todos", entram todas.

### Onde uso AND, OR e NOT

1. **AND / OR** no filtro (acima).
2. **OR** na validação: `categoria == "" or descricao == "" or bairro == ""` → se qualquer campo obrigatório estiver vazio, o cadastro é cancelado.
3. **NOT** na validação: `not reg["id"].isdigit()` e `categoria not in CATEGORIAS` → mensagem de código inválido ou categoria desconhecida.
4. **AND** na atualização: `o["status"] == "concluida" and novo != "concluida"` → ocorrência concluída não pode ser alterada.

## 8. Indicadores

Todos calculados com laços e contas simples:

- **Total por categoria e por situação** (matriz).
- **Proporção** = quantidade / total × 100.
- **Pendências** = abertas + em análise.
- **Tempo médio simulado até concluir** = soma de (dia da conclusão − dia da abertura) / quantidade de concluídas.

Resultado com os dados iniciais:

```
                Aberta      Em análise  Concluída   Total
Iluminação      1           1           1           3
Acessibilidade  1           0           1           2
Limpeza         2           1           1           4
Conservação     1           1           1           3

Aberta 5 de 12 = 41.7% | Em análise 3 de 12 = 25.0% | Concluída 4 de 12 = 33.3%
Pendências: 8
Tempo médio = 13 / 4 = 3.25 dias
```

**Interpretação:** a categoria de limpeza teve mais ocorrências (4 de 12, 33,3%), o que faz sentido porque a chuva leva lixo e lama para as ruas e entope bueiros. Além disso, 8 das 12 ocorrências (66,7%) ainda estão pendentes e só 4 foram concluídas, em média 3,25 dias depois da abertura. Isso sugere que o bairro precisa de mais atenção na limpeza e na rapidez do atendimento depois das chuvas.

## 9. Exemplo de uso

**Cadastro**
```
Escolha uma opção: 2
Categorias: iluminacao, acessibilidade, limpeza, conservacao
Categoria: iluminacao
Descrição breve: Poste apagado na rua da escola
Bairro (local genérico): Centro
Dia simulado (número): 12
Ocorrência cadastrada com o código 015
```

**Consulta por código**
```
Escolha uma opção: 3
Código: 001
Código: 001
Categoria: Iluminação
Descrição: Poste apagado depois de temporal
Bairro: Centro
Aberta no dia: 1
Situação: Concluída
Histórico:
  dia 2: aberta -> em_analise
  dia 4: em_analise -> concluida
```

**Alteração de status**
```
Escolha uma opção: 5
Código da ocorrência: 003
Situação atual: Aberta
Nova situação: em_analise
Dia simulado (número): 8
Situação atualizada e histórico registrado!
```

**Erros tratados**
```
Nova situação: resolvida
Situação desconhecida! Nada foi alterado.

Uma ocorrência concluída não pode ser alterada.
Ocorrência não encontrada.
```

**Saída**
```
Escolha uma opção: 0
Encerrando o sistema. Até mais!
```

## 10. Acessibilidade, inclusão e privacidade

- Menu numerado e mensagens curtas e claras, sem depender de cores ou imagens (funciona com leitor de tela).
- Os erros explicam o que aconteceu e o que fazer.
- Nomes de situações e categorias aparecem com acentos e de forma legível para o usuário.
- Nenhum dado pessoal: só dados fictícios e locais genéricos (bairros).
- O sistema não promete atendimento nem se conecta a órgãos públicos.

## 11. Vídeo de apresentação

Link no YouTube (não listado): **[COLAR O LINK AQUI]**

## 12. Conclusões, limitações e aprendizados

- Foi possível usar lista, dicionário, fila, pilha, matriz e uma hierarquia para organizar as ocorrências, cada uma com um motivo.
- Limitações: os dados são simulados; as alterações feitas no programa **não são salvas** nos arquivos (ao fechar, volta tudo ao início); os dias são números simples, não datas de verdade; a interface é só de texto; o sistema não verifica se o bairro digitado já existe.
- Aprendi a separar o programa em funções, validar entradas do usuário e calcular indicadores usando laços.
- Para melhorar no futuro: salvar os dados nos arquivos e permitir mais categorias.
