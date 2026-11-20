# Neighborhood Action Dashboard
# Global Solution 2026.2 - CitizenTech
# Tema: ocorrencias de problemas causados pela chuva em bairros (dados simulados)

import os

# ---------------- Caminhos dos arquivos ----------------
PASTA = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_OCORRENCIAS = os.path.join(PASTA, "..", "data", "ocorrencias.csv")
ARQUIVO_HISTORICO = os.path.join(PASTA, "..", "data", "historico.csv")

# ---------------- Valores padronizados ----------------
CATEGORIAS = ["iluminacao", "acessibilidade", "limpeza", "conservacao"]
NOMES_CATEGORIAS = {
    "iluminacao": "Iluminação",
    "acessibilidade": "Acessibilidade",
    "limpeza": "Limpeza",
    "conservacao": "Conservação",
}

STATUS = ["aberta", "em_analise", "concluida"]
NOMES_STATUS = {
    "aberta": "Aberta",
    "em_analise": "Em análise",
    "concluida": "Concluída",
}

# ---------------- Estruturas de dados ----------------
ocorrencias = []   # Zista com todas as ocorrencias validas
por_id = {}        # dicionario: codigo > ocorrencia
fila = []          # fila: codigos ainda nao examinados (ordem de registro)
pilha = []         # pilha: eventos de historico (o ultimo e o topo)
historico = []     # lista com todos os eventos
invalidos = []     # registros do arquivo que nao passaram na validacao


# ---------------- leitura de arquivos ----------------
def ler_arquivo(caminho):
    # devolve as linhas do arquivo sem o cabecalho (ou None se nao achar)
    try:
        arq = open(caminho, "r", encoding="utf-8")
    except FileNotFoundError:
        return None
    linhas = arq.readlines()
    arq.close()
    resultado = []
    for i in range(1, len(linhas)):   # pula a linha 0 (cabecalho)
        linha = linhas[i].strip()
        if linha != "":
            resultado.append(linha)
    return resultado


def validar_registro(reg):
    # devolve uma mensagem de erro, ou "" se estiver tudo certo
    if not reg["id"].isdigit():
        return "código inválido (precisa ser número)"
    if reg["id"] in por_id:
        return "código repetido"
    if reg["categoria"] == "" or reg["descricao"] == "" or reg["bairro"] == "":
        return "campo obrigatório vazio (categoria, descrição ou bairro)"
    if reg["categoria"] not in CATEGORIAS:
        return "categoria desconhecida"
    if reg["status"] not in STATUS:
        return "situação desconhecida"
    if not reg["dia"].isdigit() or int(reg["dia"]) < 1:
        return "dia inválido"
    return ""


def carregar_ocorrencias():
    linhas = ler_arquivo(ARQUIVO_OCORRENCIAS)
    if linhas is None:
        print("Arquivo de ocorrências não encontrado!")
        return
    for linha in linhas:
        partes = linha.split(";")
        if len(partes) != 6:
            invalidos.append({"id": "?", "linha": linha, "motivo": "quantidade de colunas errada"})
            continue
        reg = {
            "id": partes[0].strip(),
            "categoria": partes[1].strip(),
            "descricao": partes[2].strip(),
            "bairro": partes[3].strip(),
            "dia": partes[4].strip(),
            "status": partes[5].strip(),
        }
        erro = validar_registro(reg)
        if erro != "":
            invalidos.append({"id": reg["id"], "linha": linha, "motivo": erro})
        else:
            reg["dia"] = int(reg["dia"])
            ocorrencias.append(reg)
            por_id[reg["id"]] = reg
            if reg["status"] == "aberta":
                fila.append(reg["id"])


def carregar_historico():
    linhas = ler_arquivo(ARQUIVO_HISTORICO)
    if linhas is None:
        print("Arquivo de histórico não encontrado!")
        return
    for linha in linhas:
        partes = linha.split(";")
        if len(partes) == 4 and partes[0] in por_id and partes[1].isdigit():
            registrar_historico(partes[0], int(partes[1]), partes[2], partes[3])
        else:
            print("Evento de histórico ignorado:", linha)


def registrar_historico(codigo, dia, de, para):
    evento = {"id": codigo, "dia": dia, "de": de, "para": para}
    historico.append(evento)
    pilha.append(evento)   # empilha (topo = ultimo da lista)


# ---------------- funcoes auxiliares ----------------
def gerar_novo_id():
    maior = 0
    for o in ocorrencias:
        if int(o["id"]) > maior:
            maior = int(o["id"])
    for r in invalidos:
        if r["id"].isdigit() and int(r["id"]) > maior:
            maior = int(r["id"])
    return f"{maior + 1:03d}"


def pedir_dia(minimo):
    texto = input("Dia simulado (número): ").strip()
    if not texto.isdigit() or int(texto) < minimo:
        print(f"Dia inválido! Use um número maior ou igual a {minimo}.")
        return None
    return int(texto)


def mostrar_ocorrencia(o):
    print("-" * 40)
    print("Código:", o["id"])
    print("Categoria:", NOMES_CATEGORIAS[o["categoria"]])
    print("Descrição:", o["descricao"])
    print("Bairro:", o["bairro"])
    print("Aberta no dia:", o["dia"])
    print("Situação:", NOMES_STATUS[o["status"]])
    print("Histórico:")
    achou = False
    for e in historico:
        if e["id"] == o["id"]:
            print(f"  dia {e['dia']}: {e['de']} -> {e['para']}")
            achou = True
    if not achou:
        print("  (nenhuma alteração ainda)")


def listar(lista):
    if len(lista) == 0:
        print("Nenhuma ocorrência encontrada.")
        return
    print(f"{'Código':<8}{'Categoria':<16}{'Bairro':<20}{'Situação':<12}")
    print("-" * 56)
    for o in lista:
        print(f"{o['id']:<8}{NOMES_CATEGORIAS[o['categoria']]:<16}{o['bairro']:<20}{NOMES_STATUS[o['status']]:<12}")
    print("Total:", len(lista))


# ---------------- opcoes do menu ----------------
def cadastrar():
    print("\n--- Cadastrar ocorrência ---")
    print("Categorias:", ", ".join(CATEGORIAS))
    categoria = input("Categoria: ").strip().lower()
    descricao = input("Descrição breve: ").strip()
    bairro = input("Bairro (local genérico): ").strip()
    dia = pedir_dia(1)
    if dia is None:
        print("Cadastro cancelado.")
        return
    reg = {
        "id": gerar_novo_id(),
        "categoria": categoria,
        "descricao": descricao,
        "bairro": bairro,
        "dia": str(dia),
        "status": "aberta",
    }
    erro = validar_registro(reg)
    if erro != "":
        print("Cadastro cancelado:", erro)
        return
    reg["dia"] = dia
    ocorrencias.append(reg)
    por_id[reg["id"]] = reg
    fila.append(reg["id"])
    print("Ocorrência cadastrada com o código", reg["id"])


def buscar_por_codigo():
    print("\n--- Buscar por código ---")
    codigo = input("Código: ").strip()
    if codigo.isdigit():
        codigo = codigo.zfill(3)   # 14 vira 014
    if codigo in por_id:
        mostrar_ocorrencia(por_id[codigo])
    else:
        print("Ocorrência não encontrada.")


def filtrar():
    print("\n--- Filtrar ocorrências ---")
    print("Categorias:", ", ".join(CATEGORIAS), "ou todas")
    categoria = input("Categoria: ").strip().lower()
    print("Situações:", ", ".join(STATUS), "ou todos")
    status = input("Situação: ").strip().lower()

    if categoria != "todas" and categoria not in CATEGORIAS:
        print("Categoria inválida!")
        return
    if status != "todos" and status not in STATUS:
        print("Situação inválida!")
        return

    resultado = []
    for o in ocorrencias:
        # expressao booleana do filtro (esta no README)
        if (categoria == "todas" or o["categoria"] == categoria) and (status == "todos" or o["status"] == status):
            resultado.append(o)
    listar(resultado)


def atualizar_status():
    print("\n--- Atualizar situação ---")
    codigo = input("Código da ocorrência: ").strip()
    if codigo.isdigit():
        codigo = codigo.zfill(3)
    if codigo not in por_id:
        print("Ocorrência não encontrada.")
        return
    o = por_id[codigo]
    print("Situação atual:", NOMES_STATUS[o["status"]])
    print("Novas situações:", ", ".join(STATUS))
    novo = input("Nova situação: ").strip().lower()

    if novo not in STATUS:
        print("Situação desconhecida! Nada foi alterado.")
        return
    if o["status"] == "concluida" and novo != "concluida":
        print("Uma ocorrência concluída não pode ser alterada.")
        return
    if o["status"] != "aberta" and novo == "aberta":
        print("Uma ocorrência já examinada não volta para aberta.")
        return
    if novo == o["status"]:
        print("A ocorrência já está nessa situação.")
        return

    dia = pedir_dia(o["dia"])
    if dia is None:
        return
    anterior = o["status"]
    o["status"] = novo
    registrar_historico(codigo, dia, anterior, novo)
    if codigo in fila:
        fila.remove(codigo)   # saiu da fila porque ja foi examinada
    print("Situação atualizada e histórico registrado!")


def ver_fila():
    print("\n--- Fila de ocorrências ainda não examinadas ---")
    if len(fila) == 0:
        print("A fila está vazia.")
        return
    posicao = 1
    for codigo in fila:
        o = por_id[codigo]
        print(f"{posicao}º - {codigo} | {NOMES_CATEGORIAS[o['categoria']]} | {o['bairro']} | aberta no dia {o['dia']}")
        posicao += 1


def examinar_proxima():
    print("\n--- Examinar próxima da fila ---")
    if len(fila) == 0:
        print("A fila está vazia, nada para examinar.")
        return
    codigo = fila[0]   # primeiro da fila
    o = por_id[codigo]
    print("Próxima ocorrência:", codigo, "-", o["descricao"])
    dia = pedir_dia(o["dia"])
    if dia is None:
        return
    fila.pop(0)        # sai da fila (primeiro a entrar, primeiro a sair)
    o["status"] = "em_analise"
    registrar_historico(codigo, dia, "aberta", "em_analise")
    print("Ocorrência", codigo, "agora está em análise.")


def ver_pilha():
    print("\n--- Últimas atualizações (mais recente primeiro) ---")
    if len(pilha) == 0:
        print("Ainda não há atualizações.")
        return
    topo = len(pilha) - 1
    quantidade = 0
    while topo >= 0 and quantidade < 5:
        e = pilha[topo]
        print(f"dia {e['dia']}: ocorrência {e['id']} foi de {e['de']} para {e['para']}")
        topo = topo - 1
        quantidade = quantidade + 1


def mostrar_hierarquia():
    # bairro -> categoria -> lista de codigos
    hierarquia = {}
    for o in ocorrencias:
        bairro = o["bairro"]
        cat = o["categoria"]
        if bairro not in hierarquia:
            hierarquia[bairro] = {}
        if cat not in hierarquia[bairro]:
            hierarquia[bairro][cat] = []
        hierarquia[bairro][cat].append(o["id"])

    print("\n--- Hierarquia: bairro -> categoria -> ocorrências ---")
    for bairro in hierarquia:
        print(bairro)
        for cat in hierarquia[bairro]:
            print("   ", NOMES_CATEGORIAS[cat], ":", ", ".join(hierarquia[bairro][cat]))


def montar_matriz():
    # matriz (lista de listas): linhas = categorias, colunas = situacoes
    matriz = []
    for cat in CATEGORIAS:
        linha = []
        for st in STATUS:
            cont = 0
            for o in ocorrencias:
                if o["categoria"] == cat and o["status"] == st:
                    cont = cont + 1
            linha.append(cont)
        matriz.append(linha)
    return matriz


def mostrar_indicadores():
    total = len(ocorrencias)
    print("\n=========== INDICADORES ===========")
    if total == 0:
        print("Não há ocorrências cadastradas.")
        return
    print("Total de ocorrências:", total)

    matriz = montar_matriz()

    # tabela categoria x situacao
    print("\nQuantidade por categoria e situação:")
    cabecalho = f"{'':<16}"
    for st in STATUS:
        cabecalho = cabecalho + f"{NOMES_STATUS[st]:<12}"
    print(cabecalho + "Total")
    totais_status = [0, 0, 0]
    totais_categoria = []
    for i in range(len(CATEGORIAS)):
        texto = f"{NOMES_CATEGORIAS[CATEGORIAS[i]]:<16}"
        soma_linha = 0
        for j in range(len(STATUS)):
            texto = texto + f"{matriz[i][j]:<12}"
            soma_linha = soma_linha + matriz[i][j]
            totais_status[j] = totais_status[j] + matriz[i][j]
        totais_categoria.append(soma_linha)
        print(texto + str(soma_linha))

    # proporcoes
    print("\nProporção por categoria (fórmula: qtd da categoria / total * 100):")
    for i in range(len(CATEGORIAS)):
        p = totais_categoria[i] / total * 100
        print(f"  {NOMES_CATEGORIAS[CATEGORIAS[i]]:<16}{totais_categoria[i]} de {total} = {p:.1f}%")

    print("\nProporção por situação (fórmula: qtd da situação / total * 100):")
    for j in range(len(STATUS)):
        p = totais_status[j] / total * 100
        print(f"  {NOMES_STATUS[STATUS[j]]:<16}{totais_status[j]} de {total} = {p:.1f}%")

    # pendencias
    pendencias = totais_status[0] + totais_status[1]
    print("\nPendências (abertas + em análise):", pendencias)

    # tempo medio de conclusao
    print("\nTempo simulado até a conclusão (dia da conclusão - dia da abertura):")
    soma = 0
    qtd = 0
    for o in ocorrencias:
        if o["status"] == "concluida":
            for e in historico:
                if e["id"] == o["id"] and e["para"] == "concluida":
                    tempo = e["dia"] - o["dia"]
                    print(f"  {o['id']}: dia {o['dia']} -> dia {e['dia']} = {tempo} dias")
                    soma = soma + tempo
                    qtd = qtd + 1
    if qtd > 0:
        print(f"Tempo médio = {soma} / {qtd} = {soma / qtd:.2f} dias")
    else:
        print("Ainda não há ocorrências concluídas.")

    # interpretacao simples
    maior = 0
    nome_maior = ""
    for i in range(len(CATEGORIAS)):
        if totais_categoria[i] > maior:
            maior = totais_categoria[i]
            nome_maior = NOMES_CATEGORIAS[CATEGORIAS[i]]
    print("\nInterpretação:")
    empates = 0
    for i in range(len(CATEGORIAS)):
        if totais_categoria[i] == maior:
            empates = empates + 1
    if empates > 1:
        print("- Mais de uma categoria empatou com o maior número de ocorrências.")
    else:
        print(f"- A categoria com mais ocorrências é {nome_maior} ({maior} registros).")
    print(f"- {pendencias} de {total} ocorrências ainda estão pendentes.")


def mostrar_invalidos():
    print("\n--- Registros do arquivo que foram ignorados ---")
    if len(invalidos) == 0:
        print("Nenhum registro inválido.")
        return
    for r in invalidos:
        print(f"Linha: {r['linha']}")
        print(f"   Motivo: {r['motivo']}")


def mostrar_menu():
    print("\n===== NEIGHBORHOOD ACTION DASHBOARD =====")
    print("   Ocorrências causadas pela chuva")
    print("1  - Listar ocorrências")
    print("2  - Cadastrar nova ocorrência")
    print("3  - Buscar por código")
    print("4  - Filtrar por categoria e/ou situação")
    print("5  - Atualizar situação")
    print("6  - Ver fila de espera")
    print("7  - Examinar próxima da fila")
    print("8  - Ver últimas atualizações")
    print("9  - Ver indicadores")
    print("10 - Ver hierarquia por bairro")
    print("11 - Ver registros inválidos")
    print("0  - Sair")


# ---------------- programa principal ----------------
def main():
    carregar_ocorrencias()
    carregar_historico()
    print(f"\n{len(ocorrencias)} ocorrências carregadas, {len(invalidos)} registros inválidos ignorados.")

    while True:
        mostrar_menu()
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            print()
            listar(ocorrencias)
        elif opcao == "2":
            cadastrar()
        elif opcao == "3":
            buscar_por_codigo()
        elif opcao == "4":
            filtrar()
        elif opcao == "5":
            atualizar_status()
        elif opcao == "6":
            ver_fila()
        elif opcao == "7":
            examinar_proxima()
        elif opcao == "8":
            ver_pilha()
        elif opcao == "9":
            mostrar_indicadores()
        elif opcao == "10":
            mostrar_hierarquia()
        elif opcao == "11":
            mostrar_invalidos()
        elif opcao == "0":
            print("Encerrando o sistema. Até mais!")
            break
        else:
            print("Opção inválida! Digite um número do menu.")


main()
