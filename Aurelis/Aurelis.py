import textwrap
import sys
import os
import json
import random
import tkinter as tk
from tkinter import ttk, messagebox

# =======================================
# 1. FUNÇÕES AUXILIARES DE ARQUIVOS
# =======================================

def obter_diretorio_base():
  caminho_drive = "/content/drive/MyDrive/Colab Notebooks"
  if getattr(sys, 'frozen', False):
    return sys._MEIPASS
  if os.path.exists("/content/drive"):
    return caminho_drive
  if "__file__" in globals():
    return os.path.dirname(os.path.abspath(__file__))
  return os.getcwd()

def carregar_texto(caminho_arquivo, largura=80):
    diretorio_atual = obter_diretorio_base()
    caminho_completo = os.path.join(diretorio_atual, caminho_arquivo)
    try:
        with open(caminho_completo, 'r', encoding='utf-8') as arquivo:
            conteudo = arquivo.read()
            return formatar_texto(conteudo, largura=largura)
    except FileNotFoundError:
        print(f"[!] Arquivo não encontrado: {caminho_completo}")
        return "Texto indisponível no momento."

def formatar_texto(texto, largura=80, recuo_paragrafo="    "):
    if not texto:
        return ""
    linhas_formatadas = []
    novo_paragrafo = True
    for linha in texto.splitlines():
      linha_str = linha.strip()
      if not linha_str:
        linhas_formatadas.append("")
        novo_paragrafo = True
        continue
      if set(linha_str) == {"="} or set(linha_str) == {"-"}:
         linhas_formatadas.append(linha_str)
         novo_paragrafo = True
      elif linha_str.startswith("[") or linha_str.startswith("•"):
        linhas_formatadas.append(
            textwrap.fill(
                linha_str,
                width=largura,
                subsequent_indent="  ",
            )
        )
        novo_paragrafo = True
      else:
        indent_inicial = recuo_paragrafo if novo_paragrafo else ""
        linhas_formatadas.append(
            textwrap.fill(
                linha_str,
                width=largura,
                initial_indent=indent_inicial,
                subsequent_indent="",
            )
        )
        novo_paragrafo = False
    return "\n".join(linhas_formatadas)

# =======================================
# 2. CLASSES DE DOMÍNIO DO JOGO
# =======================================

class Fragmento:
    def __init__(self, id_fragmento, nome, descricao, bonus: dict, slot="reliquia_1", portador_original=None):
        self.id_fragmento = id_fragmento
        self.nome = nome
        self.descricao = descricao
        self.bonus = bonus
        self.slot = slot
        self.portador_original = portador_original

    def to_dict(self):
        return {
            "id": self.id_fragmento,
            "nome": self.nome,
            "slot": self.slot,
            "bonus": self.bonus,
            "descricao": self.descricao
        }

    def exibir_detalhes(self):
        print(f"\n *[{self.nome.upper()}]*")
        print(f"Descrição: {self.descricao}")
        if self.portador_original:
            print(f"Origem/Portador: {self.portador_original}")
        print("Bônus Concedidos:")
        for attr, val in self.bonus.items():
            print(f" • +{val} em {attr.capitalize()}")

# Banco de Dados dos Fragmentos
FRAGMENTOS_REGISTRADOS = {
    "frag_magia": Fragmento(
        id_fragmento="frag_magia",
        nome="Fragmento da Magia",
        descricao="Um pequeno cristal lapitado que brilha com energia arcana, o pulso de seu brilho parece alterar as leis da realidade ao seu redor.",
        bonus={"magia": 2, "forca": 1},
        portador_original="Astrid"
    ),
    "frag_guerra": Fragmento(
        id_fragmento="frag_guerra",
        nome="Fragmento da Guerra",
        descricao="Uma medalha militar que emite um calor sobrenatural, seu pulso ardente parece sedento por sangue.",
        bonus={"forca": 2, "vitalidade": 1},
        portador_original="Tyron"
    ),
    "frag_amor": Fragmento(
        id_fragmento="frag_amor",
        nome="Fragmento do Amor",
        descricao="Um brinco elegante, sua perola rubra parece encantar a todos que olhem diretamente para seu portador.",
        bonus={"destreza": 2, "magia": 1},
        portador_original="Serena"
    ),
    "frag_comercio": Fragmento(
        id_fragmento="frag_comercio",
        nome="Fragmento do Comercio",
        descricao="Um smartphone misterioso, dizem que é único no mundo, seu sistema parece revelar o preço de tudo... e todos.",
        bonus={"sorte": 2, "inteligencia": 1},
        portador_original="Siles"
    ),
    "frag_sabedoria": Fragmento(
        id_fragmento="frag_sabedoria",
        nome="Fragmento da Sabedoria",
        descricao="Um bloco de notas antigo, suas páginas atualizam sua escrita dourada frequentemente e seus textos parecem revelar todos os segredos do mundo.",
        bonus={"inteligencia": 2, "sorte": 1},
        portador_original="Soren"
    ),
        "frag_caca": Fragmento(
        id_fragmento="frag_caca",
        nome="Fragmento da Caça",
        descricao="Um anel de osso que exala uma aura primitiva, ao utilizar nada escapa dos sentidos de seu portador.",
        bonus={"destreza": 2, "forca": 1},
        portador_original="Naira"
    ),
    "frag_entretenimento": Fragmento(
        id_fragmento="frag_entretenimento",
        nome="Fragmento da entretenimento",
        descricao="Um dado de 6 lados colorido, muitos acreditam que ao possuir terá sorte imensa em qualquer jogo.",
        bonus={"sorte": 2, "vitalidade": 1},
        portador_original="Miles"
    ),
    "frag_terra": Fragmento(
        id_fragmento="frag_terra",
        nome="Fragmento da Terra",
        descricao="Uma semente dourada guardada dentro de um frasco de vidro, a semente parece exalar vitaliidade podendo crescer até no solo mais infértil.",
        bonus={"vitalidade": 2, "magia": 1},
        portador_original="Florence"
    ),
}

class NPC:
    def __init__(self, nome, faccao="neutro", fragmento: Fragmento = None):
        self.nome = nome
        self.faccao = faccao #aliado, inimigo, neutro
        self.vivo = True
        self.fragmento = fragmento
        self.imobilizado = False

    def esta_disponivel(self):
        return self.vivo and not self.imobilizado

    def possui_fragmento(self):
        return self.fragmento is not None

    def entregar_fragmento(self):
        if self.fragmento:
            frag = self.fragmento
            self.fragmento = None
            print(f"\n *{self.nome} entregou o '{frag.nome}'!")
            return frag
        return None

    def abater(self):
        self.vivo = False
        print(f"\n [MUNDO] {self.nome} foi abatido!")

    def imobilizar(self):
        self.imobilizado = True
        print(f"\n [MUNDO] {self.nome} está imobilizado!")

# Banco de dados NPC Principais
PORTADORES_PRINCIPAIS = {
    "campeao_astrid": NPC(
        nome="Astrid",
        faccao="aliado",
        fragmento=FRAGMENTOS_REGISTRADOS["frag_magia"]
    ),
    "campeao_tyron": NPC(
        nome="Tyron",
        faccao="inimigo",
        fragmento=FRAGMENTOS_REGISTRADOS["frag_guerra"]
    ),
    "campeao_serena": NPC(
        nome="Serena",
        faccao="inimigo",
        fragmento=FRAGMENTOS_REGISTRADOS["frag_amor"]
    ),
    "campeao_siles": NPC(
        nome="Siles",
        faccao="inimigo",
        fragmento=FRAGMENTOS_REGISTRADOS["frag_comercio"]
    ),
    "campeao_soren": NPC(
        nome="Soren",
        faccao="aliado",
        fragmento=FRAGMENTOS_REGISTRADOS["frag_sabedoria"]
    ),
    "campeao_naira": NPC(
        nome="Naira",
        faccao="aliado",
        fragmento=FRAGMENTOS_REGISTRADOS["frag_caca"]
    ),
    "campeao_miles": NPC(
        nome="Miles",
        faccao="neutro",
        fragmento=FRAGMENTOS_REGISTRADOS["frag_entretenimento"]
    ),
    "campeao_florence": NPC(
        nome="Florence",
        faccao="neutro",
        fragmento=FRAGMENTOS_REGISTRADOS["frag_terra"]
    ),
}

class Personagem:
  def __init__(self,nome):
    self.nome = nome
    self.nivel = 0
    self.experiencia = 0
    self.exp_para_proximo_nivel = 10
    self.pontos_disponiveis = 0
    self.pode_distribuir_pontos = False
# ------ATRIBUTOS BASE------
    self.forca = 0
    self.destreza = 1
    self.inteligencia = 1
    self.sorte = 1
    self.magia = 0
    self.vitalidade = 0
    self.debuffs = {}
# -----INVENTARIO/MOEDAS------
    self.inventario = {}
    self.inventario_unico = []
    self.equipamentos = {}
    self.moedas = 0
#-----SISTEMA DE MEMÓRIA/FLAG-----
    self.conhecimentos = set()
# ------STATUS DERIVADOS------
    self.recalcular_status_maximos()
    self.hp_atual = self.hp_max
    self.mp_atual = self.mp_max
# -----COMPANIONS/INIMIGOS------
    self.npcs = {}
# -----NOTIFICAÇÕES------
    self.notificacoes_pendentes = []
# -----SISTEMA DE CONSULTA DE ATRIBUTOS COM BONUS------
  def permitir_distribuicao(self, permitir: bool):
     self.pode_distribuir_pontos = permitir

  def obter_atributo_total(self, nome_atributo):
        nome = nome_atributo.lower()
        valor_base = getattr(self, nome, 0)
        
        # Sombra dos bônus dos equipamentos
        bonus_equipamentos = 0
        for slot, item in self.equipamentos.items():
            if isinstance(item, dict) and "bonus" in item:
                bonus_equipamentos += item["bonus"].get(nome, 0)

        # Subtrai o debuff ativo (se houver)
        penalidade = self.debuffs.get(nome, 0)

        # Garante que o atributo não fique negativo (mínimo 0)
        return max(0, valor_base + bonus_equipamentos - penalidade)

  def recalcular_status_maximos(self):
    self.hp_max = 20 + (self.obter_atributo_total("vitalidade") * 5)
    self.mp_max = self.obter_atributo_total("magia") * 5

  def alocar_ponto(self, nome_atributo):
     if not self.pode_distribuir_pontos:
        return False, "Você só pode distribur pontos em áreas de descanso!"

     if self.pontos_disponiveis <=0:
        return False, "Você não possui pontos suficientes!"

     attr = nome_atributo.lower()
     if hasattr(self, attr):
        valor_atual = getattr(self, attr)
        setattr(self, attr, valor_atual + 1)
        self.pontos_disponiveis -= 1

        if attr == "vitalidade":
           self.hp_atual += 5
        elif attr == "magia":
           self.mp_atual += 5

        self.recalcular_status_maximos()
        return True, f"+1 ponto aplicado em {nome_atributo.capitalize()}!"
     return False, "Atributo inválido"

  def para_dicionario(self, cena_atual):
    """Converte os dados do personagem para um dicionário serializável em JSON."""
    return {
        "nome": self.nome,
        "nivel": self.nivel,
        "experiencia": self.experiencia,
        "exp_para_proximo_nivel": self.exp_para_proximo_nivel,
        "pontos_disponiveis": self.pontos_disponiveis,
        "atributos": {
            "forca": self.forca,
            "destreza": self.destreza,
            "inteligencia": self.inteligencia,
            "sorte": self.sorte,
            "magia": self.magia,
            "vitalidade": self.vitalidade,
        },
        "inventario": self.inventario,
        "inventario_unico": self.inventario_unico,
        "equipamentos": self.equipamentos,
        "moedas": self.moedas,
        "conhecimentos": list(self.conhecimentos),
        "hp_atual": self.hp_atual,
        "hp_max": self.hp_max,
        "mp_atual": self.mp_atual,
        "mp_max": self.mp_max,
        "cena_atual": cena_atual,
    }

  @classmethod
  def do_dicionario(cls, dados):
    """Reconstrói a instância do personagem a partir de um dicionário."""
    p = cls(dados["nome"])
    p.nivel = dados["nivel"]
    p.experiencia = dados["experiencia"]
    p.exp_para_proximo_nivel = dados["exp_para_proximo_nivel"]
    p.pontos_disponiveis = dados["pontos_disponiveis"]

    p.forca = dados["atributos"]["forca"]
    p.destreza = dados["atributos"]["destreza"]
    p.inteligencia = dados["atributos"]["inteligencia"]
    p.sorte = dados["atributos"]["sorte"]
    p.magia = dados["atributos"]["magia"]
    p.vitalidade = dados["atributos"]["vitalidade"]

    p.hp_atual = dados["hp_atual"]
    p.hp_max = dados["hp_max"]
    p.mp_atual = dados["mp_atual"]
    p.mp_max = dados["mp_max"]
    p.moedas = dados["moedas"]

    p.inventario = dados.get("inventario", {})
    p.inventario_unico = dados.get("inventario_unico", [])
    p.equipamentos = dados.get("equipamentos", {})
    p.conhecimentos = set(dados.get("conhecimentos", []))

    return p, dados["cena_atual"]

# ------TESTE ATRIBUTOS-----
  def tem_atributo(self, nome_atributo, valor_minimo):
    return self.obter_atributo_total(nome_atributo) >= valor_minimo

  def tem_mp(self, custo_mp):
    return self.mp_atual >= custo_mp
# -----ALTERA ATRIBUTOS-----
  def consumir_mp(self, quantidade):
    if self.tem_mp(quantidade):
      self.mp_atual -= quantidade
      return True
    return False

  def receber_dano(self, dano):
    self.hp_atual = max(0, self.hp_atual - dano)
    self.adicionar_notificacao(f"[DANO] Você sofreu {dano} de dano! HP: {self.hp_atual}/{self.hp_max}")

  def descansar(self):
    self.hp_atual = self.hp_max
    self.mp_atual = self.mp_max

# ----- SISTEMA DE DEBUFFS / CURA -----
  def aplicar_debuff(self, nome_atributo, quantidade):
        """Aplica uma penalidade a um atributo e gera notificação."""
        nome = nome_atributo.lower()
        self.debuffs[nome] = self.debuffs.get(nome, 0) + quantidade
        
        # Recalcula HP/MP se o debuff for em Vitalidade ou Magia
        self.recalcular_status_maximos()
        
        self.adicionar_notificacao(
            f"[CONDIÇÃO] Você sofreu uma penalidade! (-{quantidade} em {nome.upper()})"
        )

  def remover_debuff(self, nome_atributo, quantidade=None):
        """Remove total ou parcialmente a penalidade de um atributo e notifica."""
        nome = nome_atributo.lower()
        if nome in self.debuffs:
            if quantidade is None or quantidade >= self.debuffs[nome]:
                del self.debuffs[nome]
            else:
                self.debuffs[nome] -= quantidade
                
            self.recalcular_status_maximos()
            self.adicionar_notificacao(
                f"[CURA] Sua condição melhorou! (Penalidade de {nome.upper()} removida/reduzida)"
            )

  def curar_todos_debuffs(self):
        """Limpa todos os debuffs (ex: ao descansar ou usar poção completa)."""
        if self.debuffs:
            self.debuffs.clear()
            self.recalcular_status_maximos()
            self.adicionar_notificacao("[CURA] Todos os seus ferimentos e debuffs foram totalmente curados!")

# -----METODOS DE INVENTARIO UNICO/CONSUMIVEL------
  def equipar_item(self, item):
        if hasattr(item, "to_dict"):
            item_dict = item.to_dict()
        elif isinstance(item, dict):
            item_dict = item
        else:
            return False

        nome_item = item_dict.get("nome", "Item Desconhecido")
        slot = item_dict.get("slot", "reliquia_1")

        if not self.tem_item(nome_item):
            self.adicionar_item(nome_item)

        if slot in self.equipamentos:
            self.desequipar_item(slot)

        self.equipamentos[slot] = item_dict
        self.recalcular_status_maximos()

        # MONTAGEM DA NOTIFICAÇÃO COM BÔNUS
        texto_bonus = ""
        if "bonus" in item_dict and isinstance(item_dict["bonus"], dict):
            lista_bonus = [f"+{val} {attr.upper()[:3]}" for attr, val in item_dict["bonus"].items()]
            if lista_bonus:
                texto_bonus = f", BÔNUS: {', '.join(lista_bonus)}"

        self.adicionar_notificacao(
            f"[EQUIPAMENTO] Você equipou '{nome_item}' no slot [{slot.upper()}]{texto_bonus}!"
        )
        return True

  def desequipar_item(self, slot):
        """
        Remove o item do slot especificado, recalcula status e retorna o item removido.
        """
        if slot in self.equipamentos:
            item_removido = self.equipamentos.pop(slot)
            nome_item = item_removido.get("nome", "Item") if isinstance(item_removido, dict) else str(item_removido)

            # Recalcula HP/MP máximos (caso o item desse bônus de Vitalidade/Magia)
            self.recalcular_status_maximos()

            # Gera notificação para a tela
            self.adicionar_notificacao(f"[EQUIPAMENTO] '{nome_item}' foi desequipado do slot [{slot.upper()}].")

            return item_removido
        return None

  def adicionar_item(self, nome_item, quantidade=1):
    self.inventario[nome_item] = (
        self.inventario.get(nome_item, 0) + quantidade
    )

  def remover_item(self, nome_item, quantidade=1):
    if self.inventario.get(nome_item, 0) >= quantidade:
      self.inventario[nome_item] -= quantidade
      if self.inventario[nome_item] <= 0:
        del self.inventario[nome_item]
      return True
    return False

  def adicionar_item_unico(self, item):
    if item not in self.inventario_unico:
      self.inventario_unico.append(item)

  def remover_item_unico(self, item):
    if item in self.inventario_unico:
      self.inventario_unico.remove(item)
      return True
    return False

  def tem_item_unico(self, item):
    return item in self.inventario_unico

  def tem_item(self, nome_item, quantidade=1):
    return self.inventario.get(nome_item, 0) >= quantidade
# -----METODOS DE MOEDAS------
  def tem_moedas(self, quantidade):
    return self.moedas >= quantidade

  def adicionar_moedas(self, quantidade, multiplicador=1):
    self.moedas += int(quantidade * multiplicador)
    self.adicionar_notificacao(f"[MOEDAS] +{quantidade}C (Total: {self.moedas}C).")

  def gastar_moedas(self, quantidade):
    if self.tem_moedas(quantidade):
      self.moedas -= quantidade
      self.adicionar_notificacao(f"[MOEDAS] -{quantidade}C (Total: {self.moedas}C).")
      return True
    return False
#-----SISTEMA DE CONHECIMENTO INVISÍVEL-----
  def adicionar_conhecimento(self, chave_conhecimento):
    self.conhecimentos.add(chave_conhecimento)

  def tem_conhecimento(self, chave_conhecimento):
    return chave_conhecimento in self.conhecimentos
# -----SISTEMA DE NIVEL E EXPERIENCIA-----
  def ganhar_xp(self, quantidade_xp):
    self.experiencia += quantidade_xp
    self.adicionar_notificacao(f"[XP] Você ganhou {quantidade_xp} de experiência!")

    while self.experiencia >= self.exp_para_proximo_nivel:
        self.experiencia -= self.exp_para_proximo_nivel
        self.nivel += 1
        self.pontos_disponiveis += 1
        self.exp_para_proximo_nivel = int(self.exp_para_proximo_nivel * 1.5)
        self.adicionar_notificacao(
           f"[LEVEL UP!] Você alcançou o Nível {self.nivel}! "
           f"Você possui {self.pontos_disponiveis} pontos de atributos disponíveis!"
        )
# -----METODOS DE NPCS------
  def registrar_npc(self, id_npc, npc_objeto=None, nome=None, faccao="neutro"):
    if id_npc not in self.npcs:
      if isinstance(npc_objeto, NPC):
        self.npcs[id_npc] = npc_objeto
      else:
        self.npcs[id_npc] = NPC(nome=nome, faccao=faccao)

  def obter_npc(self, id_npc):
    return self.npcs.get(id_npc)

  def aplicar_efeitos_npc(self, id_npc, acao, nova_faccao=None):
    # Busca um NPC Registrado e aplica uma alteração de estado.
    npc = self.obter_npc(id_npc)
    if npc:
       if acao == "imobilizar":
          npc.imobilizar()
       elif acao == "abater":
          npc.abater()
       elif acao == "mudar_faccao" and nova_faccao:
          npc.faccao = nova_faccao

  def adicionar_notificacao(self, mensagem):
        """Guarda uma notificação para ser exibida no próximo carregamento de cena."""
        self.notificacoes_pendentes.append(f"✨ {mensagem}")

  def consumir_notificacoes(self):
        """Retorna todas as notificações acumuladas e limpa a fila."""
        notifs = list(self.notificacoes_pendentes)
        self.notificacoes_pendentes.clear()
        return notifs
  
# =======================================
# FUNÇÃO DE SALVAR/CARREGAR
# =======================================
ARQUIVO_SAVE = "savegame_aurelis.json"


def salvar_progresso(jogador, cena_atual):
  """Salva o estado do jogador e cena em arquivo JSON."""
  caminho = os.path.join(obter_diretorio_base(), ARQUIVO_SAVE)
  try:
    dados = jogador.para_dicionario(cena_atual)
    with open(caminho, "w", encoding="utf-8") as f:
      json.dump(dados, f, ensure_ascii=False, indent=4)
    return True
  except Exception as e:
    print(f"[!] Erro ao salvar: {e}")
    return False


def carregar_progresso():
  """Carrega o estado do jogo a partir do arquivo JSON."""
  caminho = os.path.join(obter_diretorio_base(), ARQUIVO_SAVE)
  if not os.path.exists(caminho):
    return None, None
  try:
    with open(caminho, "r", encoding="utf-8") as f:
      dados = json.load(f)
    return Personagem.do_dicionario(dados)
  except Exception as e:
    print(f"[!] Erro ao carregar save: {e}")
    return None, None

# ============================================
# 3. INTERFACE GRÁFICA DO JOGO & MOTOR DE JOGO
# ============================================

class InterfaceRPG:
  def __init__(self, root, banco_cenas):
    self.root = root
    self.root.title("Aurelis: O Caminho da Alvorada")
    self.root.geometry("850x650")
    self.root.minsize(700, 500)

    self.cenas = banco_cenas

    #configuração inicial de tema (Pradrão: Escuro)
    self.modo_escuro = True
    self.definir_cores()

    #janela raiz
    self.root.configure(bg=self.cor_fundo)

    #controle de estado de jogo
    self.jogo_em_andamento = False

    #atributos de estado de jogo
    self.jogador = None
    self.cena_atual_id = "prologo"

    #barra superior
    self.frame_topo = tk.Frame(self.root, bg=self.cor_fundo)
    self.frame_topo.pack(fill="x", padx=15, pady=10)

    self.btn_tema = tk.Button(
      self.frame_topo,
      text="☀️ Modo Claro" if self.modo_escuro else "🌙 Modo Escuro",
      command=self.alternar_tema,
      bg=self.cor_botao,
      fg=self.cor_texto,
      activebackground=self.cor_botao_hover,
      activeforeground=self.cor_texto,
      relief="flat",
      font=("Helvetica", 9, "bold"),
      padx=10,
      pady=4,
      cursor="hand2",
    )
    self.btn_tema.pack(side="right")

    #container principal (Alterna entre o menu e o jogo)
    self.container_principal = tk.Frame(self.root, bg=self.cor_fundo)
    self.container_principal.pack(expand=True, fill="both", padx=20, pady=10)

    #constroi as duas telas principais
    self.criar_tela_menu()
    self.criar_tela_jogo()

    #inicia mostrando o Menu Inicial
    self.exibir_menu_inicial()

  def definir_cores(self):
      """Define as paletas de cores baseadas no tema ativo."""
      if self.modo_escuro:
        self.cor_fundo = "#1a1a1a"
        self.cor_painel = "#2a2a2a"
        self.cor_texto = "#e0e0e0"
        self.cor_destaque = "#7289da"
        self.cor_botao = "#7289da"
        self.cor_botao_hover = "#4f545c"
      else:
        self.cor_fundo = "#f2f3f5"
        self.cor_painel = "#ffffff"
        self.cor_texto = "#2e3338"
        self.cor_destaque = "#4e5d94"
        self.cor_botao = "#4e5d94"
        self.cor_botao_hover = "#d1d5da"

# =======================================
# 3.1 TELA DO MENU INICIAL
# =======================================
  def criar_tela_menu(self):
    self.frame_menu = tk.Frame(self.container_principal, bg=self.cor_fundo)
    #título / logotipo do rpg
    self.lbl_titulo = tk.Label(
        self.frame_menu,
        text="Aurelis",
        font=("Georgia", 28, "bold"),
        bg=self.cor_fundo,
        fg=self.cor_destaque,
    )
    self.lbl_titulo.pack(pady=(40, 10))

    self.lbl_subtitulo = tk.Label(
        self.frame_menu,
        text="O Caminho da Alvorada",
        font=("Helvetica", 11, "italic"),
        bg=self.cor_fundo,
        fg=self.cor_texto,
    )
    self.lbl_subtitulo.pack(pady=(0, 40))

    #Painel de botoes do Menu
    self.frame_botoes_menu = tk.Frame(self.frame_menu, bg=self.cor_fundo)
    self.frame_botoes_menu.pack(pady=10)

    #Botões do Menu
    self.btn_iniciar = self.criar_botao_menu("⚔️  Iniciar Novo Jogo", self.iniciar_novo_jogo)
    self.btn_carregar = self.criar_botao_menu("📜  Carregar Jogo", self.carregar_jogo)
    self.btn_sair = self.criar_botao_menu("ℹ️  Sobre o Jogo", self.exibir_sobre)
    self.btn_sair = self.criar_botao_menu("🚪  Sair do Jogo", self.sair_jogo)

  def criar_botao_menu(self, texto, comando):
     btn = tk.Button(
        self.frame_botoes_menu,
        text=texto,
        command=comando,
        bg=self.cor_botao,
        fg=self.cor_texto,
        activebackground=self.cor_botao_hover,
        activeforeground=self.cor_texto,
        font=("Helvetica", 11, "bold"),
        width=25,
        pady=8,
        relief="flat",
        cursor="hand2",
     )
     btn.pack(pady=8)
     return btn

# =======================================
# 3.2 TELA DE JOGO
# =======================================
  def criar_tela_jogo(self):
     self.frame_jogo = tk.Frame(self.container_principal, bg=self.cor_fundo)

     #Área de narrativa
     self.area_texto = tk.Text(
        self.frame_jogo,
        wrap="word",
        bg=self.cor_painel,
        fg=self.cor_texto,
        insertbackground=self.cor_texto,
        font=("Georgia", 11),
        padx=15,
        pady=15,
        relief="flat",
        state="disabled"
     )
     self.area_texto.pack(
        side="top", expand=True, fill="both", padx=10, pady=(0, 10)
     )

     #Painel de botões de escolha
     self.frame_escolhas = tk.Frame(self.frame_jogo, bg=self.cor_fundo)
     self.frame_escolhas.pack(side="bottom", fill="x", padx=10, pady=5)

# =======================================
# 3.3 NAVEGAÇÃO E AÇÕES DO MENU
# =======================================
  def exibir_menu_inicial(self):
     self.frame_jogo.pack_forget()
     self.frame_menu.pack(expand=True, fill="both")

  def iniciar_novo_jogo(self):
     self.jogador = Personagem("Kael")
     self.cena_atual_id = "prologo"
     self.jogo_em_andamento = True
     self.frame_menu.pack_forget()
     self.frame_jogo.pack(expand=True, fill="both")
     self.carregar_cena(self.cena_atual_id)

  def salvar_jogo_atual(self):
      if hasattr(self, "jogador") and self.jogador and self.cena_atual_id:
        sucesso = salvar_progresso(self.jogador, self.cena_atual_id)
        if sucesso:
          messagebox.showinfo("Jogo Salvo", "Seu progresso foi salvo com sucesso!")
        else:
          messagebox.showerror("Erro", "Não foi possível salvar o jogo.")

  def carregar_jogo(self):
      jogador, cena_salva = carregar_progresso()

      if jogador and cena_salva:
        self.jogador = jogador
        self.cena_atual_id = cena_salva
        self.jogo_em_andamento = True

        self.frame_menu.pack_forget()
        self.frame_jogo.pack(expand=True, fill="both")

        messagebox.showinfo(
            "Sucesso", f"Progresso de {jogador.nome} carregado com sucesso!"
        )
        self.carregar_cena(self.cena_atual_id)
      else:
        messagebox.showwarning(
            "Aviso", "Nenhum arquivo de salvamento encontrado ou arquivo corrompido."
        )

  def exibir_sobre(self):
     detalhes = (
        "Aurelis - O Caminho da Alvorada\n"
        "Versão: 1.1\n\n"
        "Desenvolvido por: Jupeid\n"
        "Direitos Autorais: Todos os direitos reservados © 2026\n\n"
        "Desenvolvido em Python com suporte a interface gráfica nativa Tkinter."
     )
     messagebox.showinfo("Sobre o Jogo", detalhes)

  def sair_jogo(self):
     if messagebox.askyesno("Sair", "Deseja realmente fechar o jogo?"):
        self.root.destroy()

# =======================================
# 3.4 FUNÇÕES AUXILIARES E TEMAS
# ======================================
  def escrever_narrativa(self, texto, limpar=True):
    self.area_texto.config(state="normal")
    
    # Se limpar=True, apaga o texto antigo. Se limpar=False, apenas faz um append no final!
    if limpar:
        self.area_texto.delete("1.0", tk.END)
    
    # Insere o novo trecho de texto
    self.area_texto.insert(tk.END, texto + "\n\n")
    
    self.area_texto.config(state="disabled")
    
    # Rola automaticamente a caixa para o final para mostrar o novo texto
    self.area_texto.yview_moveto(0.0)
      
  def atualizar_botoes_escolha(self, opcoes_botoes):
    for widget in self.frame_escolhas.winfo_children():
        widget.destroy()

    for rotulo, texto_opcao, acao in opcoes_botoes:
        btn = tk.Button(
            self.frame_escolhas,
            text=f"[{rotulo}] {texto_opcao}",
            command=acao,
            bg=self.cor_botao,
            fg=self.cor_texto,
            activebackground=self.cor_botao_hover,
            activeforeground=self.cor_texto,
            font=("Helvetica", 10),
            anchor="w",
            padx=15,
            pady=8,
            relief="flat",
            cursor="hand2",
        )
        btn.pack(fill="x", pady=4)

  def alternar_tema(self):
      """Inverte o tema entre Claro e Escuro e atualiza as cores na tela."""
      self.modo_escuro = not self.modo_escuro
      self.definir_cores()
      #aplica as cores atualizadas em todos os elementos da janela
      self.root.configure(bg=self.cor_fundo)
      self.frame_topo.configure(bg=self.cor_fundo)
      self.container_principal.configure(bg=self.cor_fundo)

      self.frame_menu.configure(bg=self.cor_fundo)
      self.lbl_titulo.configure(bg=self.cor_fundo, fg=self.cor_destaque)
      self.lbl_subtitulo.configure(bg=self.cor_fundo, fg=self.cor_texto)
      self.frame_botoes_menu.configure(bg=self.cor_fundo)

      self.frame_jogo.configure(bg=self.cor_fundo)
      self.area_texto.configure(bg=self.cor_painel, fg=self.cor_texto)
      self.frame_escolhas.configure(bg=self.cor_fundo)

      self.btn_tema.configure(
          text="☀️ Modo Claro" if self.modo_escuro else "🌙 Modo Escuro",
          bg=self.cor_botao,
          fg=self.cor_texto,
          activebackground=self.cor_botao_hover,
          activeforeground=self.cor_texto,
      )

      #Atualiza a cor dos botões de escolha caso existam na tela
      for frame in (self.frame_botoes_menu, self.frame_escolhas):
        for child in frame.winfo_children():
          if isinstance(child, tk.Button):
            child.configure(
              bg=self.cor_botao,
              fg=self.cor_texto,
              activebackground=self.cor_botao_hover,
              activeforeground=self.cor_texto,
          )

# ===========================================
# INTEGRAÇÃO DO MOTOR DE JOGO COM A INTERFACE
# ===========================================

  def obter_texto_hud(self):
    j = self.jogador
    itens_str = (
        ", ".join([f"{k} (x{v})" for k, v in j.inventario.items()])
        if j.inventario else "Vazio"
    )
    unicos_str = (
        ", ".join(j.inventario_unico) if j.inventario_unico else "Vazio"
    )
    if j.equipamentos:
            lista_eq = []
            for slot, item in j.equipamentos.items():
                nome_item = item.get("nome", "Item") if isinstance(item, dict) else str(item)
                lista_eq.append(f"{slot.capitalize()}: {nome_item}")
            equipamentos_str = ", ".join(lista_eq)
    else:
            equipamentos_str = "Nenhum item equipado"
        
    hud = (
        f"Nome: {j.nome} | Nível: {j.nivel} EXP: {j.experiencia}/{j.exp_para_proximo_nivel} | Pontos Disponíveis: {j.pontos_disponiveis} ===\n"
        f"HP: {j.hp_atual}/{j.hp_max} | MP: {j.mp_atual}/{j.mp_max}\n"
        f"FOR: {j.obter_atributo_total('forca')} | DES: {j.obter_atributo_total('destreza')}\n"
        f"INT: {j.obter_atributo_total('inteligencia')} | SOR: {j.obter_atributo_total('sorte')}\n"
        f"MAG: {j.obter_atributo_total('magia')} | VIT: {j.obter_atributo_total('vitalidade')}\n"
        f"Moedas: {j.moedas}C\n"
        f"Equipamento: {equipamentos_str}\n"
        f"Inventário: {itens_str}\n"
        f"Itens Únicos: {unicos_str}\n"
        + "=" * 60
    )
    return hud

  def avaliar_condicao_oculta(self, condicao):
        """Atalho de compatibilidade que repassa para a função global."""
        return avaliar_condicao_oculta(self.jogador, condicao)

  def carregar_cena(self, id_cena):
# 1. PRIMEIRO: Intercepta o comando do menu antes de checar self.cenas
    if id_cena == "MENU_INICIAL":
        self.frame_jogo.pack_forget()
        self.frame_menu.pack(expand=True, fill="both")
        self.jogo_em_andamento = False
        return

    # 2. SEGUNDO: Checa se a cena existe no JSON
    if id_cena not in self.cenas:
        self.escrever_narrativa(
            "[CAPÍTULO EM CONSTRUÇÃO]\n\nEsta parte da história ainda não foi escrita."
        )
        
        # Passa a tupla (rotulo, texto_opcao, acao) esperada pelo seu for
        self.atualizar_botoes_escolha([
            (
                "M", 
                "Voltar ao Menu Inicial", 
                lambda: self.carregar_cena("MENU_INICIAL")
            )
        ])
        return

    # 3. TERCEIRO: Carrega a cena normal
    self.cena_atual_id = id_cena
    cena = self.cenas[id_cena]
# -----SISTEMA DE CHECKS INVISIVEIS-----
    if "checks_ocultos" in cena:
        for cond in cena["checks_ocultos"]:
            if self.avaliar_condicao_oculta(cond):
              self.carregar_cena(cond["cena_sucesso"])
              return
        self.carregar_cena(cena["cena_falha"])
        return

# -----PROCESSAMENTO DE EFEITOS IN CENA -----
    if "novos_npcs" in cena:
       for dados in cena["novos_npcs"]:
          id_npc = dados["id_npc"]
          faccao = dados.get("faccao", "neutro")

          #1. Se for um dos 8 portadores
          if id_npc in PORTADORES_PRINCIPAIS:
             npc_obj = PORTADORES_PRINCIPAIS[id_npc]
             npc_obj.faccao = faccao
             self.jogador.registrar_npc(id_npc=id_npc, npc_objeto=npc_obj)

          #2. Se for um NPC Secundário
          else:
             self.jogador.registrar_npc(
                id_npc=id_npc,
                nome=dados.get("nome"),
                faccao=faccao
             )

    if "efeito_npc" in cena:
       efeito = cena["efeito_npc"]
       self.jogador.aplicar_efeitos_npc(
          id_npc=efeito["id_npc"],
          acao=efeito["acao"],
          nova_faccao=efeito.get("nova_faccao")
       )

    if "dano_recebido" in cena:
       self.jogador.receber_dano(cena["dano_recebido"])

    if "item_unico_adquirido" in cena:
        for item in cena["item_unico_adquirido"]:
            self.jogador.adicionar_item_unico(item)
    if "item_adquirido" in cena:
        for entrada in cena["item_adquirido"]:
            if isinstance(entrada, dict):
              self.jogador.adicionar_item(
                entrada["item"], entrada.get("quantidade", 1)
              )
            else:
              self.jogador.adicionar_item(entrada, 1)

    if "equipar_item" in cena:
       item = cena["equipar_item"]
       if isinstance(item, str) and item in FRAGMENTOS_REGISTRADOS:
          item = FRAGMENTOS_REGISTRADOS[item]

       self.jogador.equipar_item(item)
    
    if "xp_ganha" in cena:
      self.jogador.ganhar_xp(cena["xp_ganha"])
    if "moedas_ganhas" in cena:
      self.jogador.adicionar_moedas(cena["moedas_ganhas"])
    if "adicionar_conhecimento" in cena:
      for segredo in cena["adicionar_conhecimento"]:
        self.jogador.adicionar_conhecimento(segredo)

    permite_pontos = cena.get("permite_pontos", False) or cena.get("permite_descanso", False)
    self.jogador.permitir_distribuicao(permite_pontos)

    if cena.get("permite_descanso", False):
      self.jogador.descansar()

    processar_efeitos_debuff(self.jogador, cena)

# ----- CONSTRUÇÃO DA NARRATIVA VISUAL -----
    notificacoes_completas = self.jogador.consumir_notificacoes()
    if "notificacao" in cena:
        notif_estatica = cena["notificacao"]
        if isinstance(notif_estatica, list):
            notificacoes_completas.extend([f"✨ {m}" for m in notif_estatica])
        else:
            notificacoes_completas.append(f"✨ {notif_estatica}")    

    texto_exibicao = ""
    if cena.get("HUD", False):
        texto_exibicao += self.obter_texto_hud() + "\n\n"

    if cena.get("titulo"):
        texto_exibicao += f"=== {cena['titulo']} ===\n\n"

    if notificacoes_completas:
        for msg in notificacoes_completas:
            texto_exibicao += f"{msg}\n"
        texto_exibicao += "─" * 45 + "\n\n"

    # CHAMA A FUNÇÃO AUXILIAR: Concatena narrativa + blocos sequenciais em um só texto!
    texto_narrativa, proxima_dinamica = construir_texto_narrativa(self.jogador, cena)
    texto_exibicao += texto_narrativa

    self.escrever_narrativa(texto_exibicao)

    # Se a cena em árvore já definiu uma próxima cena automática (ex: fase_2 ou game_over)
    # E a cena original NÃO tinha botões manuais de opção:
    if proxima_dinamica and "opcoes" not in cena:
        cena["proxima_cena"] = proxima_dinamica

# Contrução dos Botões de escolha
    opcoes_botoes = []

    if cena.get("permite_descanso", False):
       opcoes_botoes.append(("💾", "Salvar Jogo", self.salvar_jogo_atual))

    if (
       self.jogador.pode_distribuir_pontos
       and self.jogador.pontos_disponiveis > 0
    ):
       opcoes_botoes.append((
          "✨",
          (
             f"Distribuir Pontos de Atributo ({self.jogador.pontos_disponiveis}"
             " disponíveis)"
          ),
          self.abrir_janela_distribuicao,
       ))

    if "opcoes" in cena and cena["opcoes"]:
      for letra, dados in cena["opcoes"].items():
        texto_btn = formatar_texto(dados["texto"])
        acao = lambda opt=dados: self.selecionar_opcao(opt)
        opcoes_botoes.append((letra, texto_btn, acao))
    elif "proxima_cena" in cena:
      proxima = cena["proxima_cena"]
      opcoes_botoes.append(
        ("➡️", "Continuar", lambda: self.carregar_cena(proxima))
      )

    self.atualizar_botoes_escolha(opcoes_botoes)

  def abrir_janela_distribuicao(self):
     janela_pontos = tk.Toplevel(self.root)
     janela_pontos.title("Distribuição de Atributos")
     janela_pontos.geometry("350x400")
     janela_pontos.configure(bg=self.cor_fundo)
     janela_pontos.grab_set()

     lbl_titulo = tk.Label(
        janela_pontos,
        text=(
           f"Pontos Disponíveis: {self.jogador.pontos_disponiveis}"
        ),
        font=("Helvetica", 12, "bold"),
        bg=self.cor_fundo,
        fg=self.cor_destaque,
     )
     lbl_titulo.pack(pady=10)

     atributos = [
          ("Força", "forca"),
          ("Destreza", "destreza"),
          ("Inteligência", "inteligencia"),
          ("Sorte", "sorte"),
          ("Magia", "magia"),
          ("Vitalidade", "vitalidade"),
      ]

     def atribuir(attr_key):
        sucesso, msg = self.jogador.alocar_ponto(attr_key)
        if sucesso:
          lbl_titulo.config(
              text=f"Pontos Disponíveis: {self.jogador.pontos_disponiveis}"
          )
          # Atualiza a tela de jogo principal
          self.carregar_cena(self.cena_atual_id)
          if self.jogador.pontos_disponiveis <= 0:
            janela_pontos.destroy()
        else:
          messagebox.showwarning("Aviso", msg)

     for nome_exibicao, attr_key in atributos:
        frame_attr = tk.Frame(janela_pontos, bg=self.cor_fundo)
        frame_attr.pack(fill="x", padx=20, pady=4)

        val_atual = getattr(self.jogador, attr_key)
        lbl_attr = tk.Label(
            frame_attr,
            text=f"{nome_exibicao}: {val_atual}",
            font=("Helvetica", 10),
            bg=self.cor_fundo,
            fg=self.cor_texto,
            width=15,
            anchor="w",
        )
        lbl_attr.pack(side="left")

        btn_add = tk.Button(
            frame_attr,
            text="+1",
            command=lambda k=attr_key: atribuir(k),
            bg=self.cor_botao,
            fg=self.cor_texto,
            relief="flat",
            width=5,
        )
        btn_add.pack(side="right")
# BOTÃO PARA RECUSAR / GUARDAR PONTOS
     def fechar_e_guardar():
      messagebox.showinfo(
          "Pontos Guardados",
          "Seus pontos restantes foram guardados para o próximo Ponto de"
          " Descanso!",
      )
      janela_pontos.destroy()

     btn_guardar = tk.Button(
        janela_pontos,
        text="💾 Guardar Pontos para Depois",
        command=fechar_e_guardar,
        bg=self.cor_botao,
        fg=self.cor_texto,
        activebackground=self.cor_botao_hover,
        activeforeground=self.cor_texto,
        font=("Helvetica", 10, "bold"),
        pady=5,
        relief="flat",
        cursor="hand2",
     )
     btn_guardar.pack(pady=15)

  def testar_requisitos(self, lista_requisitos):
    for req in lista_requisitos:
        tipo = req["tipo"]
        if tipo == "atributo" and not self.jogador.tem_atributo(
          req["nome"], req["valor"]
        ):
          return False
        elif tipo == "magia":
          if not (
            self.jogador.tem_atributo(req["nome"], req["valor"])
            and self.jogador.tem_mp(req["custo_mp"])
          ):
            return False
        elif tipo == "item" and not self.jogador.tem_item(
            req["nome"], req.get("quantidade", 1)
        ):
            return False
        elif tipo == "item_unico" and not self.jogador.tem_item_unico(req["nome"]):
            return False
        elif tipo == "moedas" and not self.jogador.tem_moedas(req["valor"]):
            return False
    return True

  def selecionar_opcao(self, opcao_escolhida):
        if "proxima_cena" in opcao_escolhida and "modos" not in opcao_escolhida:
            self.carregar_cena(opcao_escolhida["proxima_cena"])
            return

        modos = opcao_escolhida.get("modos", [])
        modo_bem_sucedido = None

        for modo in modos:
            if self.testar_requisitos(modo.get("requisitos", [])):
                modo_bem_sucedido = modo
                break

        if modo_bem_sucedido:
            # 1. Consumo de Recursos e Recompensas
            for req in modo_bem_sucedido.get("requisitos", []):
                if req["tipo"] == "magia":
                    self.jogador.consumir_mp(req["custo_mp"])

            if "conhecimento_adquirido" in modo_bem_sucedido:
                for segredo in modo_bem_sucedido["conhecimento_adquirido"]:
                    self.jogador.adicionar_conhecimento(segredo)

            if "item_unico_adquirido" in modo_bem_sucedido:
                for item in modo_bem_sucedido["item_unico_adquirido"]:
                    self.jogador.adicionar_item_unico(item)
                    self.jogador.adicionar_notificacao(f"[INVENTÁRIO] Você adquiriu o item único: {item}")

            if "item_unico_removido" in modo_bem_sucedido:
                for item in modo_bem_sucedido["item_unico_removido"]:
                    self.jogador.remover_item_unico(item)
                    self.jogador.adicionar_notificacao(f"[INVENTÁRIO] O item único {item} foi perdido!")

            if "item_adquirido" in modo_bem_sucedido:
                for entrada in modo_bem_sucedido["item_adquirido"]:
                    if isinstance(entrada, dict):
                        nome_item = entrada["item"]
                        quantidade = entrada.get("quantidade", 1)
                        self.jogador.adicionar_item(nome_item, quantidade)
                        self.jogador.adicionar_notificacao(f"[INVENTÁRIO] Você recebeu {quantidade}x {nome_item}!")
                    else:
                        nome_item = entrada
                        quantidade = 1
                        self.jogador.adicionar_item(nome_item, quantidade)
                        self.jogador.adicionar_notificacao(f"[INVENTÁRIO] Você recebeu {quantidade}x {nome_item}!")

            if "item_removido" in modo_bem_sucedido:
                for entrada in modo_bem_sucedido["item_removido"]:
                    if isinstance(entrada, dict):
                        nome_item = entrada["item"]
                        quantidade = entrada.get("quantidade", 1)            
                        self.jogador.remover_item(nome_item, quantidade)
                        self.jogador.adicionar_notificacao(f"[INVENTÁRIO] {quantidade}x {nome_item} foram perdidos!")
                    else:
                        nome_item = entrada
                        quantidade = 1            
                        self.jogador.remover_item(nome_item, quantidade)
                        self.jogador.adicionar_notificacao(f"[INVENTÁRIO] {quantidade}x {nome_item} foi perdido!")

            if "equipar_item" in modo_bem_sucedido:
                item = modo_bem_sucedido["equipar_item"]
                if isinstance(item, str) and item in FRAGMENTOS_REGISTRADOS:
                    item = FRAGMENTOS_REGISTRADOS[item]
                self.jogador.equipar_item(item)

            if "perder_equipamento_slot" in modo_bem_sucedido:
                slot = modo_bem_sucedido["perder_equipamento_slot"]
                item_perdido = self.jogador.desequipar_item(slot)
                if item_perdido and isinstance(item_perdido, dict) and "nome" in item_perdido:
                    self.jogador.remover_item(item_perdido["nome"])

            if "xp_ganha" in modo_bem_sucedido:
                self.jogador.ganhar_xp(modo_bem_sucedido["xp_ganha"])

            if "dano_recebido" in modo_bem_sucedido:
                self.jogador.receber_dano(modo_bem_sucedido["dano_recebido"])

            if self.jogador.hp_atual <= 0:
                messagebox.showerror(
                    "Game Over", "Você sucumbiu aos ferimentos na jornada..."
                )
                self.exibir_menu_inicial()
                return

            if "novo_npc" in modo_bem_sucedido:
                dados = modo_bem_sucedido["novo_npc"]
                id_npc = dados["id_npc"]
                if id_npc in PORTADORES_PRINCIPAIS:
                    npc_obj = PORTADORES_PRINCIPAIS[id_npc]
                    npc_obj.faccao = dados.get("faccao", "neutro")
                    self.jogador.registrar_npc(id_npc=id_npc, npc_objeto=npc_obj)
                else:
                    self.jogador.registrar_npc(
                        id_npc=id_npc,
                        nome=dados.get("nome"),
                        faccao=dados.get("faccao", "neutro"),
                    )

            if "efeito_npc" in modo_bem_sucedido:
                efeito = modo_bem_sucedido["efeito_npc"]
                self.jogador.aplicar_efeitos_npc(
                    id_npc=efeito["id_npc"],
                    acao=efeito["acao"],
                    nova_faccao=efeito.get("nova_faccao")
                )

            if "ganho_moedas" in modo_bem_sucedido:
                self.jogador.adicionar_moedas(
                    modo_bem_sucedido["ganho_moedas"],
                    multiplicador=modo_bem_sucedido.get("multiplicador_moedas", 1),
                )

            if "gasto_moedas" in modo_bem_sucedido:
                self.jogador.gastar_moedas(modo_bem_sucedido["gasto_moedas"])

            processar_efeitos_debuff(self.jogador, modo_bem_sucedido)

            # 2. Transição de Cena ou Exibição da Narrativa Intermediária
            proxima = modo_bem_sucedido["proxima_cena"]
            narrativa_modo = modo_bem_sucedido.get("narrativa")

            if narrativa_modo:
                # Exibe a narrativa do modo sem apagar o histórico atual
                self.escrever_narrativa(formatar_texto(narrativa_modo), limpar=False)
                
                # Substitui os botões anteriores por um único botão 'Continuar'
                self.atualizar_botoes_escolha([
                    ("➡️", "Continuar", lambda: self.carregar_cena(proxima))
                ])
            else:
                # Se não houver narrativa no modo, carrega a próxima cena diretamente
                self.carregar_cena(proxima)

        else:
            messagebox.showwarning(
                "Requisitos não atendidos",
                "Você não possui os requisitos necessários para escolher esta opção.",
            )

# =======================================
# FUNÇÕES GLOBAIS
# =======================================
def avaliar_condicao_oculta(jogador, condicao):
    tipo = condicao.get("tipo")
    
    if tipo in ["sorte", "chance_sorte"]:
        base = condicao.get("requisito_base", 90)
        bonus = condicao.get("bonus_por_ponto", 10)
        sorte_total = jogador.obter_atributo_total("sorte")
        limite = max(0, base - ((sorte_total - 1) * bonus))
        dado = random.randint(0, 100)
        
        sucesso = dado >= limite
        if sucesso:
            jogador.adicionar_notificacao(
                f"[SORTE] Rolou {dado}/100 (Meta: {limite}+ | SOR: {sorte_total}) - SUCESSO!"
            )
        else:
            jogador.adicionar_notificacao(
                f"[SORTE] Rolou {dado}/100 (Meta: {limite}+ | SOR: {sorte_total}) - FALHA!"
            )
        return sucesso

    elif tipo == "atributo":
        return jogador.tem_atributo(condicao["nome"], condicao["valor"])

    elif tipo == "item":
        return jogador.tem_item(condicao["nome"], condicao.get("quantidade", 1))

    elif tipo == "item_unico":
        return jogador.tem_item_unico(condicao["nome"])

    elif tipo == "moedas":
        return jogador.tem_moedas(condicao["valor"])

    elif tipo == "hp_minimo":
        return jogador.hp_atual >= condicao["valor"]

    elif tipo == "mp_minimo":
        return jogador.mp_atual >= condicao["valor"]

    elif tipo in ["conhecimento", "flag"]:
        return jogador.tem_conhecimento(condicao["nome"])

    return False

def processar_efeitos_debuff(jogador, origem_dados):
    if "aplicar_debuff" in origem_dados:
        dados = origem_dados["aplicar_debuff"]
        if isinstance(dados, dict):
            jogador.aplicar_debuff(dados["atributo"], dados.get("valor", 1))
        elif isinstance(dados, list):
            for item in dados:
                jogador.aplicar_debuff(item["atributo"], item.get("valor", 1))

    if "remover_debuff" in origem_dados:
        dados = origem_dados["remover_debuff"]
        if dados == "todos":
            jogador.curar_todos_debuffs()
        elif isinstance(dados, dict):
            jogador.remover_debuff(dados["atributo"], dados.get("valor"))

def construir_texto_narrativa(jogador, cena):
    paragrafos = []
    proxima_cena_dinamica = None

    # 1. Narrativa base
    if cena.get("narrativa"):
        paragrafos.append(formatar_texto(cena["narrativa"]))

    # 2. Processamento dos blocos em árvore
    if "blocos_sequenciais" in cena:
        for bloco in cena["blocos_sequenciais"]:
            
            if "check_oculto" in bloco:
                # Executa o check principal
                passou_principal = avaliar_condicao_oculta(jogador, bloco["check_oculto"])
                
                # INJETAR NOTIFICAÇÃO DO CHECK PRINCIPAL NO TEXTO (Evita o delay)
                notifs_temp = jogador.consumir_notificacoes()
                if notifs_temp:
                    paragrafos.append("\n".join(notifs_temp))

                if passou_principal:
                    ramo = bloco.get("sucesso", {})
                    if ramo.get("texto"):
                        paragrafos.append(formatar_texto(ramo["texto"]))

                    # Processa Sub-Checks
                    sub_passou = False
                    if "sub_checks" in ramo:
                        for sub in ramo["sub_checks"]:
                            if avaliar_condicao_oculta(jogador, sub["check"]):
                                sub_passou = True
                                
                                # Captura a notificação de dado/efeito gerada por este subcheck e insere no texto!
                                notifs_sub = jogador.consumir_notificacoes()
                                if notifs_sub:
                                    paragrafos.append("\n".join(notifs_sub))

                                paragrafos.append(formatar_texto(sub["texto"]))
                                
                                # Processa efeitos do sub-check (ex: cura)
                                if "efeitos" in sub:
                                    ef = sub["efeitos"]
                                    if "curar_hp" in ef: 
                                        jogador.hp_atual = min(jogador.hp_max, jogador.hp_atual + ef["curar_hp"])
                                    if "curar_mp" in ef: 
                                        jogador.mp_atual = min(jogador.mp_max, jogador.mp_atual + ef["curar_mp"])

                                proxima_cena_dinamica = sub.get("proxima_cena")
                                break

                    if not sub_passou:
                        if ramo.get("texto_falha_sub_checks"):
                            paragrafos.append(formatar_texto(ramo["texto_falha_sub_checks"]))
                        if ramo.get("proxima_cena"):
                            proxima_cena_dinamica = ramo["proxima_cena"]

                else:
                    # Ramo de Falha Principal
                    ramo = bloco.get("falha", {})
                    if ramo.get("texto"):
                        paragrafos.append(formatar_texto(ramo["texto"]))

                    # Aplica punições imediatas da falha
                    if "dano_recebido" in ramo:
                        jogador.receber_dano(ramo["dano_recebido"])
                    if "aplicar_debuff" in ramo:
                        processar_efeitos_debuff(jogador, ramo)

                    # Captura notificações geradas pelo dano/debuff
                    notifs_falha = jogador.consumir_notificacoes()
                    if notifs_falha:
                        paragrafos.append("\n".join(notifs_falha))

                    # Check de Resgate (Sorte/Vitalidade)
                    dados_resgate = ramo.get("check_resgate") or ramo.get("cheque_resgate")
                    if dados_resgate:
                        passou_resgate = avaliar_condicao_oculta(jogador, dados_resgate)
                        
                        # Captura e injeta a notificação da rolagem de sorte no texto!
                        notifs_resgate = jogador.consumir_notificacoes()
                        if notifs_resgate:
                            paragrafos.append("\n".join(notifs_resgate))

                        if passou_resgate:
                            resg = ramo.get("sucesso_resgate", {})
                            if resg.get("texto"): 
                                paragrafos.append(formatar_texto(resg["texto"]))
                            proxima_cena_dinamica = resg.get("proxima_cena")
                        else:
                            resg = ramo.get("falha_resgate", {})
                            if resg.get("texto"): 
                                paragrafos.append(formatar_texto(resg["texto"]))
                            proxima_cena_dinamica = resg.get("proxima_cena")
                    elif ramo.get("proxima_cena"):
                        proxima_cena_dinamica = ramo["proxima_cena"]

            elif "texto" in bloco:
                paragrafos.append(formatar_texto(bloco["texto"]))

    texto_final = "\n\n".join(paragrafos)
    return texto_final, proxima_cena_dinamica

# ============================================
# 4. BANCO DE DADOS DE CENAS E NARRATIVAS
# ============================================

cenas = {
    "prologo": {
        "titulo": "PRÓLOGO - O JOGO DIVINO",
        "narrativa": carregar_texto("prologo.txt"),
        "proxima_cena": "capitulo_1",
    },
#----- CAPITULO 1 -----
    "capitulo_1": {
      "HUD": True,
      "titulo": "Capítulo 1 – O Primeiro Encontro",
      "narrativa": carregar_texto("capitulo_1.txt"),
      "opcoes": {
            "A": {
                "texto": """Tentar atrair a atenção dos lobos, criando uma brecha para que a garota finalize a conjuração do feitiço. (Inteligência 1)""",
                "modos": [
                    {
                      "requisitos": [
                            {
                                "tipo": "atributo",
                                "nome": "inteligencia",
                                "valor":1
                            }
                        ],
                      "narrativa": """Noto que, próximo aos incensos, há algumas flores que, quando queimadas junto ao odor da erva, geram o efeito oposto: em vez de atrair, afastam os predadores. Chuto os incensos com força na direção do arbusto florido. Os lobos se assustam com o movimento repentino e recuam alguns passos.""",
                      "proxima_cena": "capitulo_1_resgate",
                      "xp_ganha": 5,
                    }
                ]
            },
          "B": {
              "texto": """Colocar-me entre os lobos e a garota, destruindo os incensos na esperança de dispersar a agressividade dos predadores.""",
              "modos": [
                  {
                      "requisitos": [],
                      "narrativa": """Corro na direção da garota, colocando-me entre os lobos e sua presa. Um deles salta no mesmo instante, fazendo com que eu caia ao lado de um dos incensos. Aproveitando o momento de impacto no chão, arremesso o incenso na direção dos animais. Ele cai sobre um arbusto florido, que começa a queimar e exalar uma fumaça densa, deixando os lobos desorientados por um breve momento.""",
                      "dano_recebido": 5,
                      "xp_ganha": 5,
                      "proxima_cena": "capitulo_1_resgate",
                  }
              ]
            },
#          "C": {
#              "texto": """Ignorar o apelo da garota e a notificação do Sistema, virando as costas e indo embora.""",
#              "modos": [
#                  {
#                      "requisitos": [],
#                      "narrativa": """Decido que não vale a pena arriscar minha vida por uma desconhecida. Viro as costas e me preparo para ir embora.""",
#                      "proxima_cena": "capitulo_1_abandono",
#                  }
#              ],
#            },
        }
    },

    "capitulo_1_resgate": {
        "narrativa": carregar_texto("capitulo_1_resgate.txt"),
        "opcoes": {
            "A": {
                "texto": "Apresentar-me e dizer meu nome.",
                "modos": [
                    {
                        "requisitos": [],
                        "narrativa": """— Meu nome é Kael — respondo, ajudando-a a se sentar. — Sou morador de um vilarejo próximo e notei a movimentação incomum na mata. Ainda bem que consegui chegar a tempo.""",
                        "novo_npc": {
                            "id_npc": "campeao_astrid",
                            "nome": "Astrid",
                        },
                        "proxima_cena": "capitulo_1_lobo",

                    }
                ]
            },
            "B": {
                "texto": "Ignorar a pergunta e focar em sair do local rapidamente.",
                "modos": [
                    {
                        "requisitos": [],
                        "narrativa": """— Meu nome não é importante no momento — digo de forma calma. — Vamos cuidar das suas feridas antes de pensarmos em retornar ao vilarejo.""",
                        "novo_npc": {
                            "id_npc": "campeao_astrid",
                            "nome": "Astrid",
                        },
                        "proxima_cena": "capitulo_1_lobo",
                    }
                ]
            },
        }
    },

    "capitulo_1_lobo": {
        "narrativa": carregar_texto("capitulo_1_lobo.txt"),
        "opcoes": {
            "A": {
                "texto": "Pedir para que Astrid finalize o lobo e complete a missão extra.",
                "modos":[
                    {
                        "requisitos": [],
                        "narrativa": """Astrid reúne o restante das forças que lhe sobram e dispara mais uma lâmina de vento, cortando a garganta do lobo ferido.
===========================================================
[Missão Concluída!]
Aura está satisfeita, garantindo ao hospedeiro uma
oportunidade de evolução. Escolha com sabedoria!

[Nota Extra de Nox]
Você completou a missão extra. Com isso, tem o direito de
salvar uma vida para manter o equilíbrio sobre a vida perdida.
Use com sabedoria.
===========================================================
RECOMPENSAS:
[+5 XP]
[Pílula de Restauração]
[Bênção de Nox] (Permite sentir quando alguém está próximo
de se encontrar com o Deus da Morte)
=========================================================== """,
                    "item_adquirido": ["Pílula de Restauração"],
                    "item_unico_adquirido": ["Bênção de Nox"],
                    "xp_ganha": 5,
                    "proxima_cena": "capitulo_1_casa",
                    }
                ]
            },
#            "B": {
#                "texto": "Deixar o lobo escapar para preservar a mana da garota até sairmos da floresta.",
#                "modos": [
#                    {
#                        "requisitos": [],
#                        "narrativa": """Decido poupar as energias de Astrid. Deixo o animal assustado fugir manco pela vegetação.
#===========================================================
#[Missão Concluída!]
#Aura está satisfeita, garantindo ao hospedeiro uma
#oportunidade de evolução. Escolha com sabedoria!
#===========================================================
#RECOMPENSAS:
#[+5 XP]
#=========================================================== """,
#                        "xp_ganha": 5,
#                        "proxima_cena": "capitulo_1_casa",
#                    }
#                ]
#            },
        }
    },

    "capitulo_1_casa": {
        "narrativa": carregar_texto("capitulo_1_casa.txt"),
        "novos_npcs": [
           {"id_npc": "father_eskil", "nome": "Eskil", "faccao": "aliado"},
           {"id_npc": "mother_yvaine", "nome": "Yvaine", "faccao": "aliado"},
           {"id_npc": "sister_iris", "nome": "Iris", "faccao": "aliado"}
        ],
        "proxima_cena": "cap_1_check_reacao_eskil"
    },

    "cap_1_check_reacao_eskil": {
        "checks_ocultos": [
            {
                "tipo": "hp_minimo",
                "valor": 20,
                "cena_sucesso": "capitulo_1_casa_A"
            }
        ],
        "cena_falha": "capitulo_1_casa_B",
    },

    "capitulo_1_casa_A": {
        "narrativa": """Eskil mostra aos presentes os restos das ervas queimadas, identificando o "repelente" improvisado que criei na batalha. Olho impressionado para o meu pai; ele conseguiu deduzir minha estratégia observando apenas os poucos rastros do combate.""",
        "proxima_cena": "capitulo_1_casa_final",
    },

    "capitulo_1_casa_B": {
        "narrativa": """Eskil mostra as ervas queimadas que formaram o repelente. Um suor frio escorre pela minha testa. Mal sabem eles que tudo não passou de uma grata e desesperada coincidência...""",
        "proxima_cena": "capitulo_1_casa_final",
    },

    "capitulo_1_casa_final": {
        "narrativa": carregar_texto("capitulo_1_casa_final.txt"),
        "checks_ocultos": [
            {
                "tipo": "item_unico",
                "nome": "Bênção de Nox",
                "cena_sucesso": "capitulo_1_casa_final_bencao",
            }
        ],
        "cena_falha": "capitulo_1_casa_final_sem_bencao",
    },

    "capitulo_1_casa_final_bencao": {
        "narrativa": """Enquanto observo Iris puxar Astrid pela mão em direção ao meu quarto, noto uma névoa escura e opaca flutuando ao redor da minha irmã.
A interface translúcida do Sistema surge imediatamente diante dos meus olhos:

===========================================================
[Aviso de Nox]
• Você pode utilizar a [Pílula de Restauração] para curar Iris.
• Instruções: Misture o medicamento na sopa dela durante o
  jantar. A condição crônica será curada após uma noite de sono.
=========================================================== """,
        "opcoes": {
            "A": {
                "texto": "Usar a Pílula na sopa de Iris (-1 Pílula de Restauração)",
                "modos": [
                    {
                        "requisitos": [
                            {
                                "tipo": "item",
                                "nome": "Pílula de Restauração"
                            }
                        ],
                        "narrativa": """Durante o jantar, misturo a Pílula de Restauração na sopa de Iris. Ela come sem perceber, é possível notar a névoa escura ao redor dela se dissipando lentamente.""",
                        "item_removido": ["Pílula de Restauração"],
                        "proxima_cena": "capitulo_1_casa_jantar_bencao_A",
                    }
                ],
            },

#            "B": {
#                "texto": "Guardar a Pílula e não fazer nada",
#                "modos": [
#                    {
#                        "requisitos": [],
#                        "proxima_cena": "capitulo_1_casa_jantar_bencao_B",
#                    }
#                ],
#            },
        },
    },

    "capitulo_1_casa_jantar_bencao_A": {
        "narrativa": carregar_texto("capitulo_1_casa_jantar_bencao_A.txt"),
        "proxima_cena": "tutorial_ponto_de_descanso",
    },

    "capitulo_1_casa_jantar_bencao_B": {
        "narrativa": carregar_texto("capitulo_1_casa_jantar_bencao_B.txt"),
        "proxima_cena": "tutorial_ponto_de_descanso"
    },

    "tutorial_ponto_de_descanso": {
        "HUD": True,
        "permite_descanso": True,
        "permite_pontos": True,
        "titulo": "[Tutorial - Ponto de Descanso]",
        "narrativa": """[(^o^)/] Você chegou a um ponto de descanso! Aqui você pode distribuir pontos, salvar seu progresso, checar seus status e seu HP e MP serão restaurados!
        
        A distribuição é opcional, clique em 'Continuar' para prosseguir sem distribuir pontos.
        
        [!o!] Cuidado só possível distribuir pontos e salvar em áreas de descanso, então lembre-se de salvar seu progresso antes de continuar!!""",
        "proxima_cena": "cap_1_check_pos_jantar"
    },

    "cap_1_check_pos_jantar": {
        "checks_ocultos": [
            {
                "tipo": "item",
                "nome": "Pílula de Restauração",
                "cena_sucesso": "capitulo_1_casa_pos_jantar_sem_pilula",
            },
        ],
        "cena_falha": "capitulo_1_casa_pos_jantar_pilula",
    },

    "capitulo_1_casa_pos_jantar_pilula": {
        "HUD": True,
        "narrativa": carregar_texto("capitulo_1_casa_pos_jantar_pilula.txt"),
        "item_adquirido": [
            {"item": "Ervas Repelentes", "quantidade": 5}
        ],
        "opcoes": {
#            "A": {
#                "texto": "Ficar em casa e tentar conversar mais a fundo com o Espírito de Apoio.",
#                "modos": [
#                    {
#                      "requisitos": [
#                          {
#                              "tipo": "atributo",
#                              "nome": "inteligencia",
#                              "valor": 2
#                          }
#                      ],
#                      "proxima_cena": "capitulo_1_casa_conversa_com_espirito",
#                    }
#                ]
#            },
            "B": {
                "texto": "Levar Astrid para conhecer o vilarejo.",
                "modos": [
                    {
                      "requisitos": [],
                      "proxima_cena": "capitulo_1_vilarejo",
                    }
                ]
            },
#            "C": {
#                "texto": "Ir com Astrid para a floresta para começar a praticar os princípios de magia.",
#                "modos": [
#                    {
#                     "requisitos": [
#                         {
#                             "tipo": "atributo",
#                             "nome": "magia",
#                             "valor": 1
#                         }
#                     ],
#                     "xp_ganha": 2,
#                     "proxima_cena": "capitulo_1_treino_na_floresta",
#                    }
#                ]
#            },
#            "D": {
#                "texto": "Treinar suas habilidades de caça e tiro utilizando o arco e flecha de Eskil.",
#                "modos": [
#                    {
#                     "requisitos": [
#                         {
#                             "tipo": "atributo",
#                             "nome": "destreza",
#                             "valor": 1
#                         }
#                     ],
#                     "xp_ganha": 2,
#                     "proxima_cena": "capitulo_1_treino_de_destreza",
#                    },
#                ]
 #           },
        },
    },

    "capitulo_1_casa_pos_jantar_sem_pilula": {
        "narrativa": carregar_texto("capitulo_1_casa_pos_jantar_sem_pilula.txt"),
        "adicionar_conhecimento": "Cath Palug - Floresta",
        "item_adquirido": [
            {"item": "Ervas Repelentes", "quantidade": 5}
        ],
        "opcoes": {
            "A": {
                "texto": "Ficar em casa e tentar conversar mais a fundo com o Espírito de Apoio.",
                "modos": [
                    {
                      "requisitos": [
                          {
                              "tipo": "atributo",
                              "nome": "inteligencia",
                              "valor": 2
                          }
                      ],
                      "proxima_cena": "capitulo_1_casa_conversa_com_espirito",
                    }
                ]
            },
            "B": {
                "texto": "Levar Astrid para conhecer o vilarejo.",
                "modos": [
                    {
                      "requisitos": [],
                      "proxima_cena": "capitulo_1_vilarejo_B",
                    }
                ]
            },
            "C": {
                "texto": "Ir com Astrid para a floresta para começar a praticar os princípios de magia.",
                "modos": [
                    {
                     "requisitos": [
                         {
                             "tipo": "atributo",
                             "nome": "magia",
                             "valor": 1
                         }
                     ],
                     "xp_ganha": 2,
                     "proxima_cena": "capitulo_1_treino_na_floresta",
                    }
                ]
            },
            "D": {
                "texto": "Treinar suas habilidades de caça e tiro utilizando o arco e flecha de Eskil.",
                "modos": [
                    {
                     "requisitos": [
                         {
                             "tipo": "atributo",
                             "nome": "destreza",
                             "valor": 1
                         }
                     ],
                     "xp_ganha": 2,
                     "proxima_cena": "capitulo_1_treino_de_destreza",
                    },
                ]
            },
        },
    },

    "capitulo_1_vilarejo": {
        "narrativa": carregar_texto("capitulo_1_vilarejo.txt"),
        "moedas_ganhas": 150,
        "opcoes": {
#            "A": {
#                "texto": "Praça Central e Feira de Comidas: Ir até a praça do vilarejo, repleta de barracas de espetinhos, guloseimas locais e uma bela fonte onde podem comer e apreciar a paisagem.",
#                "modos": [ {
#                    "requisitos": [],
#                    "proxima_cena": "capitulo_1_praca_central",
#                    },
#                ],
#            },
#            "B": {
#                "texto": "Loja de Equipamentos: Visitar o armazém de caça e usinagem. Com a possibilidade de ir até a floresta em breve, você decide se equipar adequadamente.",
#                "modos": [
#                    {
#                      "requisitos": [],
#                      "proxima_cena": "capitulo_1_loja_equipamentos",
#                    },
#                ],
#            },
            "C": {
                "texto": "Livraria e Sebo: Ir à pequena livraria do vilarejo. Astrid pareceu fascinada pelo local quando passaram mais cedo.",
                "modos": [
                    {
                      "requisitos": [],
                      "proxima_cena": "capitulo_1_livraria",
                    },
                ],
            },
        },

    },

    "capitulo_1_livraria": {
        "narrativa": carregar_texto("capitulo_1_livraria.txt"),
        "novos_npcs": [{"id_npc": "mage_eldrin", "nome": "Eldrin", "faccao": "neutro"}],
        "opcoes": {
#            "A": {
#                "texto": "Recusar o convite de Eldrin e acompanhar Astrid em sua busca por livros e grimórios pela biblioteca.",
#                "modos": [
#                    {
#                      "requisitos": [],
#                      "proxima_cena": "capitulo_1_livraria_busca_com_astrid",
#                    }
#                ]
#            },
            "B": {
                "texto": "Aceitar o convite e deixar Astrid explorando as prateleiras enquanto conversa a sós com o arquimago elfo.",
                "modos": [
                    {
                      "requisitos": [],
                      "proxima_cena": "capitulo_1_livraria_conversa_com_eldrin",
                    }
                ]
            },
        }
    },

    "capitulo_1_livraria_conversa_com_eldrin": {
        "narrativa": carregar_texto("capitulo_1_livraria_conversa_com_eldrin.txt"),
        "adicionar_conhecimento": "Cath Palug - Floresta",        
        "opcoes": {
           "A": {
              "texto": "Contar toda a verdade sobre o ataque dos sequestradores, a aparição do espírito e as bênçãos/recompensas de Aura e Nox.",
              "modos": [
                 {
                    "requisitos": [],
                    "proxima_cena": "capitulo_1_eldrin_truth",
                 }
              ]
           },
           "B": {
              "texto": "Contar apenas sobre o combate e o resgate de Astrid, mas omitir a presença das entidades e o aparecimento do Sistema.",
              "modos": [
                 {
                    "requisitos": [],
                    "proxima_cena": "cap_1_check_eldrin_B",
                 }
              ]
           },
           "C": {
              "texto": "Tentar mudar de assunto e ignorar a pergunta, ocultando todos os detalhes do arquimago.",
              "modos": [
                 {
                    "requisitos": [],
                    "proxima_cena": "cap_1_check_eldrin_C",
                 }
              ]
           },
        }
    },

    "cap_1_check_eldrin_B": {
       "checks_ocultos": [
          {
             "tipo": "chance_sorte",
             "requisito_base": 95,
             "bonus_por_ponto": 10,
             "cena_sucesso": "capitulo_1_eldrin_halftruth"
          },
       ],
       "cena_falha": "capitulo_1_eldrin_forced_answer",
    },   

    "cap_1_check_eldrin_C": {
       "checks_ocultos": [
          {
             "tipo": "atributo",
             "nome": "inteligencia",
             "valor": 2,
             "cena_sucesso": "capitulo_1_eldrin_lie"
          },
       ],
       "cena_falha": "capitulo_1_eldrin_lie_fail",
    },   

    "capitulo_1_eldrin_lie_fail": {
       "narrativa": """— Sabe o que é, Eldrin... Acho que você está vendo coisas — digo, soltando uma risadinha forçada e me inclinando para trás no sofá. 
       
       — Talvez o tônico que minha colocou na sopa de manhã tinha algum efeito inesperado, você sabe como ela estava correndo atrás desesperada por uma solução para a maldição de Iris.

       Tento mudar de assunto com a maior naturalidade que consigo produzir. Mas o silêncio que se segue na sala é absoluto. O estalar da lareira parece sumir, e a temperatura do recinto despenca bruscamente.

       Eldrin não pisca. O olhar acolhedor do velho bibliotecário desaparece por completo, dando lugar às pupilas frias e afiadas de um ser antigo que sobreviveu a guerras, massacres e séculos de conspirações políticas.

       — Você debocha da minha inteligência na minha própria casa, Kael? — a voz dele não é alta, mas ressoa diretamente dentro do meu crânio, pesada como chumbo.

       — Calma, velhote, eu só...

       — Você surge na minha porta exalando uma energia desconhecida, oculta intenções, traz a herdeira da casa Sylvaris sob circunstâncias suspeitas e, quando questionado, decide mentir e desdenhar.

       Tento me levantar do sofá, mas meu corpo sequer responde. A pressão esmagadora da mana de Eldrin se expande pelo hall em uma fração de segundo, colando meus membros ao estofado. Não consigo respirar. O ar ao meu redor tornou-se tão denso quanto pedra.

       — Eu conheço o Eskill. Conheço a Yvaine. E sei do que forças obscuras são capazes quando tomam o corpo de um garoto ingênuo — diz ele, levantando-se devagar. Os olhos do elfo brilham em um tom violeta profundo, e a sala começa a distorcer ao seu redor. — Não posso permitir que uma ameaça desconhecida ponha em risco este vilarejo, nem que a Confederação use a presença da garota como pretexto para exterminar o seu povo.

       — E-Eldrin... espera... — tento balbuciar, mas minha garganta está sendo esmagada por mãos invisíveis de pura força arcana.

       — Lamento, garoto. Se ainda restava algo do verdadeiro Kael aí dentro... que você encontre a paz.

       Ele apenas estala os dedos da mão direita.

       A magia espacial ao redor da minha cabeça colapsa instantaneamente. A última coisa que sinto é o espaço se contorcendo e rasgando, antes que a escuridão absoluta consuma todos os meus sentidos.""",
       "proxima_cena": "tutorial_game_over",
    },

    "tutorial_game_over": {
       "titulo": "[Tutorial - Game Over]",
       "narrativa": """[ (^.^)/ ] Você chegou a sua primeira cena de morte… Ouch… Meus pêsames... 
Há algumas maneiras de chegar ao game-over durante o livro, seja por seu HP chegar a 0, ou uma escolha mal feita. 
Como foi esse caso. [(._. ')]

Cuidado com suas próximas escolhas!

Causa da Morte: Subestimar a percepção e o poder de um Arquimago
Conselho: Eldrineth não é apenas um dono de livraria ranzinza. 
Ele é Teodor Auster, uma lenda viva. 
Diante de figuras com poder avassalador, a arrogância ou a mentira descarada podem ser fatais.
 """,
       "opcoes": {
          "Game Over": {
             "texto": "Fim de jogo",
             "modos": [
                {
                   "requisitos": [],
                   "dano_recebido": 99,                   
                   "proxima_cena": "",
                }
             ],
          },
       },
    },

    "capitulo_1_eldrin_forced_answer": {
        "narrativa": """— Bom... quando encontrei a Astrid, ela estava sendo atacada por alguns lobos — começo a explicar, tentando manter a voz firme e omitindo qualquer menção ao painel translúcido ou às entidades. — Eu apenas lutei com o que tinha em mãos, usei o terreno a meu favor e consegui resgatá-la. Essa energia deve ser só algum resíduo da magia dela ou do combate...

        Tento soar o mais convincente possível, mas Eldrin permanece em silêncio, apenas me encarando. O olhar dele, antes curioso, torna-se frio e calculista.

        — Você sempre foi um péssimo mentiroso, Kael — murmura ele, balançando a cabeça desapontado.

        Antes que eu possa reagir ou me esquivar, os olhos do elfo brilham em um tom carmesim vibrante. No mesmo milissegundo, uma luz vermelha idêntica à que paralisou Astrid na entrada surge ao meu redor, prendendo meu corpo como correntes invisíveis e pesadas. O ar foge dos meus pulmões e não consigo mover um único músculo do pescoço para baixo.

        — O que você...?! — tento gritar, mas até minha mandíbula parece congelada.

        — Não gaste suas energias — diz Eldrineth, levantando-se do sofá com uma serenidade assustadora. — Não tenho tempo para jogos de adivinhação quando a segurança da minha casa e do vilarejo está em jogo. Se você não quer me contar por vontade própria, eu mesmo verei.

        Ele estende a mão direita em direção à minha testa. Uma pequena runa translúcida surge na ponta do seu indicador e, ao tocar minha fonte, uma descarga elétrica percorre minha mente.

        Minha visão fica turva. Sinto meus pensamentos e memórias recentes serem folheados como as páginas de um livro: o ataque na floresta, o desespero do combate, a interface mágica surgindo no ar, as notificações sobre a Pílula de Restauração, as mensagens de Nox e Aura... Tudo é exposto.

        Após alguns segundos de uma pressão insuportável no meu cérebro, Eldrin recua a mão e desfaz a paralisia de estalo. Desabo no sofá, puxando o ar com força e massageando as têmporas enquanto tento recuperar o equilíbrio.

        O arquimago me encara com os olhos arregalados, uma reação raríssima para alguém com quase três séculos de vida.

        — Entidades divinas... espíritos de apoio... — murmura ele, visivelmente impactado pelo que acabou de testemunhar nas minhas memórias. — Então você se tornou um espiritualista...""",
        "proxima_cena": "capitulo_1_eldrin_truth"
    },

    "capitulo_1_eldrin_truth": {
        "narrativa": carregar_texto("capitulo_1_eldrin_truth.txt"),
        "opcoes": {
#           "A": {
#              "texto": "Revelar a conversa que teve com Eldrin e confrontar Astrid sobre suas reais intenções.",
#              "modos": [
#                 {
#                    "requisitos": [],
#                    "proxima_cena": "capitulo_1_Astrid_reasons"
#                 }
#              ]
#           },
           "B": {
              "texto": "Desviar do assunto e seguir imediatamente para a clínica de Yvaine.",
              "modos": [
                 {
                    "requisitos": [],
                    "proxima_cena": "capitulo_1_clinica"
                 }
              ]
           },
        }
    },

    "capitulo_1_clinica": {
        "narrativa": carregar_texto("capitulo_1_clinica.txt"),
        "opcoes": {
#           "A": {
#              "texto": "Contar toda a verdade sobre o que aconteceu na livraria.",
#              "modos": [
#                 {
#                    "requisitos": [],
#                    "proxima_cena": "capitulo_1_yvaine_reveal"
#                 }
#              ]
#           },
#           "B": {
#              "texto": "Contar sobre a conversa com Eldrineth e o aviso do perigo, mas omitir a presença e as falas do Espírito de Apoio.",
#              "modos": [
#                 {
#                    "requisitos": [],
#                    "proxima_cena": "capitulo_1_yvaine_halfreveal"
#                 }
#              ]
#           },
           "C": {
             "texto": "Sugerir que esperem a volta de Eskil e a chegada de Eldrineth para iniciarem uma reunião com a família reunida.",
             "modos": [
                {
                   "requisitos": [],
                   "proxima_cena": "capitulo_1_reuniao"
                }
             ]
           },
        }
    }, 

    "capitulo_1_reuniao": {
        "narrativa": carregar_texto("capitulo_1_reuniao.txt"),
        "moedas_ganhas": 500,
        "proxima_cena": "capitulo_1_floresta_heroica"
    }, 

    "capitulo_1_floresta_heroica": {
        "HUD": True,
        "narrativa": carregar_texto("capitulo_1_floresta_heroica.txt"),
        "equipar_item": {
           "nome": "Armadura de Couro",
           "slot": "Armaduras",
           "bonus": {"destreza": 1}
        },
        "proxima_cena": "cap_1_check_reacao_floresta"
    }, 

    "cap_1_check_reacao_floresta": {
       "checks_ocultos": [
          {
             "tipo": "sorte",
             "requisito_base": 60,
             "bonus_por_ponto": 10,
             "cena_sucesso": "cap_1_check_reacao_floresta_sucesso"
          },
       ],
       "cena_falha": "cap_1_check_reacao_floresta_resgate",
    }, 

    "cap_1_check_reacao_floresta_resgate": {
       "checks_ocultos": [
          {
             "tipo": "atributo",
             "nome": "destreza",
             "valor": 3,
             "cena_sucesso": "cap_1_check_reacao_floresta_sucesso"
          },
       ],
       "cena_falha": "cap_1_check_reacao_floresta_fail",
    },       
    
    "cap_1_check_reacao_floresta_sucesso": {
       "narrativa": """Sinto o vento cortar a minha lateral e reajo por puro instinto. Dou um salto lateral rente ao tronco de uma árvore antiga. A garra afiada do Barghest rasga apenas o ar onde meu peito estava há um segundo. Ganho impulso na casca da árvore e caio em base firme, empunhando a espada, pronto para o combate! 
       
       As duas criaturas me cercam, rosnando baixo e babando uma essência escura, buscando minha próxima falha para banquetear-se com a presa.
       
       (Hospedeiro, cuidado! Essas criaturas são inteligentes. Provavelmente a matilha principal está distraindo seus pais e o elfo enquanto você é o alvo real!) — avisa Lumina.""",
       "opcoes": {
          "A": {
             "texto": "Tentar gritar chamando a atenção do Trio para me ajudar",
             "modos": [
                {
                   "requisitos": [],
                   "proxima_cena": "cap_1_check_atk_barghests",
                }
             ]
          },
          "B": {
             "texto": "Desferir um golpe na criatura à frente mantendo a guarda contra a segunda (Força 1, Destreza 2)",
             "modos": [
              {
                "requisitos": [
                   {
                      "tipo": "atributo",
                      "nome": "forca",
                      "valor": 1,
                   },
                   {
                      "tipo": "atributo",
                      "nome": "destreza",
                      "valor": 2,
                   }                   
                ],
                "narrativa": 
                """Não perco tempo. Passo a perna à frente, fincando os pés no solo, e desfiro um corte transversal limpo no pescoço do Barghest à minha frente. A lâmina passa sem encontrar resistência e o sangue negro da fera espirra na vegetação.

                (Atrás de você!) — Lumina brada na minha mente.

                Abaixo a cabeça por um fio de segundo; o segundo monstro salta por cima de mim. Giro o corpo sobre o próprio eixo e cravo a espada de baixo para cima na barriga da fera enquanto ela ainda está no ar. O cadáver cai pesado no chão.

                Eskil, que vinha recuando para me apoiar, para o passo e abre um sorriso orgulhoso:

                — Bom reflexo, garoto! Corte limpo e base firme. A armadura nova caiu bem em você!""",
                "proxima_cena": "capitulo_1_transicao_batalha_final",
              }
            ]
          },
          "C": {
             "texto": "Observar o movimento das criaturas e contra-atacar na abertura (Inteligencia 2, Destreza 1)",
             "modos": [
                {
                   "requisitos": [
                      {
                         "tipo": "atributo",
                         "nome": "inteligencia",
                         "valor": 2,
                      },
                      {
                         "tipo": "atributo",
                         "nome": "destreza",
                         "valor": 1,                         
                      }
                   ],
                   "narrativa": 
                   """Relembro rapidamente as instruções táticas que vi Yvaine usar momentos atrás. Observo os pés das feras e a inclinação da vegetação baixa ao redor. Dou dois passos calculados para trás, atraindo a primeira criatura para um emaranhado de raízes expostas. Ela prende as patas traseiras e hesita por uma fração de segundo.

                   É o suficiente. Avanço com uma estocada precisa no peito do monstro preso. Antes que a segunda besta perceba a armadilha, uso a carcaça da primeira como apoio, impulso-me para o lado e desfiro um golpe rápido na espinha da garra restante, paralisando-a de imediato.

                   Yvaine nota a movimentação de longe, estufa o peito visivelmente orgulhosa e dá um breve sorriso:

                   — Usando o terreno e a paciência ao seu favor… É o meu garoto!.
""",
                   "proxima_cena": "capitulo_1_transicao_batalha_final",
                }
             ]
          },
       }
    },

    "cap_1_check_atk_barghests": {
       "checks_ocultos": [
          {
             "tipo": "sorte",
             "requisito_base": 70,
             "bonus_por_ponto": 10,
             "cena_sucesso": "cap_1_atk_barghests_sucesso"
          }
       ],
       "cena_falha": "cap_1_atk_barghests_fail", 
    },

    "cap_1_atk_barghests_sucesso": {
       "narrativa": """— Mãe! Atrás de mim! — grito no topo dos meus pulmões.

       Yvaine nem sequer vira o corpo inteiro. Com um movimento fluido e quase imperceptível de braço, ela arremessa duas adagas prateadas que cortam o ar como relâmpagos. As lâminas atingem precisamente a testa de ambas as criaturas antes que elas possam saltar sobre mim, caindo mortas aos meus pés.

       Eldrin dá uma olhada rápida por cima do ombro e comenta com um sorriso de canto:

       — Fique atento às sombras, garoto. Criaturas deste território usam o calor da batalha dos líderes para caçar os retardatários. É a tática de abate mais antiga da floresta.""",
       "proxima_cena": "capitulo_1_transicao_batalha_final"
    },

    "cap_1_atk_barghests_fail": {
       "narrativa": """— Mãe! — tento gritar, mas o som da batalha principal e as explosões mágicas de Eldrin abafam minha voz.
Antes que eu possa recuar, as duas feras saltam simultaneamente. Consigo fincar minha lâmina na garganta da primeira, matando-a instantaneamente, mas a segunda me atinge em cheio no peito, jogando-me brutalmente contra o chão. Quando as mandíbulas do monstro estão a centímetros do meu pescoço, uma lâmina de sombra trespassa a cabeça da besta. Yvaine surge ao meu lado, arfando, e remove a criatura de cima de mim.
Eldrin se aproxima com o olhar severo e me adverte:
— Em um campo de batalha real, Kael, hesitar e esperar que outros lutem por você é o caminho mais rápido para a cova. Mantenha os olhos abertos e a lâmina pronta!""",
       "dano_recebido": 3,
       "proxima_cena": "capitulo_1_transicao_batalha_final"
    },

    "cap_1_check_reacao_floresta_fail": {
       "narrativa": 
       """Tento me esquivar, mas a minha reação é lenta. As garras afiadas da fera cortam de raspão o meu ombro esquerdo. Uma dor aguda e quente se espalha pelo meu braço. A ardência me faz rosnar de dor, ao mesmo tempo sinto o veneno da criatura deixando meu corpo entorpecido.
       
       As duas criaturas me cercam, rosnando baixo e babando uma essência escura, buscando minha próxima falha para banquetear-se com a presa.
       
       (Hospedeiro, cuidado! Essas criaturas são inteligentes. Provavelmente a matilha principal está distraindo seus pais e o elfo enquanto você é o alvo real!) — avisa Lumina.""",
       "dano_recebido": 5,
       "aplicar_debuff": {
          "atributo": "destreza",
          "valor": 1
       },
       "opcoes": {
                 "A": {
                    "texto": "Tentar gritar chamando a atenção do Trio para me ajudar",
                    "modos": [
                       {
                          "requisitos": [],
                          "proxima_cena": "cap_1_check_atk_barghests",
                       }
                    ]
                 },
                 "B": {
                    "texto": "Desferir um golpe na criatura à frente mantendo a guarda contra a segunda (Força 1, Destreza 2)",
                    "modos": [
                     {
                       "requisitos": [
                          {
                             "tipo": "atributo",
                             "nome": "forca",
                             "valor": 1,
                          },
                          {
                             "tipo": "atributo",
                             "nome": "destreza",
                             "valor": 2,
                          }                   
                       ],
                       "narrativa": 
                       """Não perco tempo. Passo a perna à frente, fincando os pés no solo, e desfiro um corte transversal limpo no pescoço do Barghest à minha frente. A lâmina passa sem encontrar resistência e o sangue negro da fera espirra na vegetação.
       
       (Atrás de você!) — Lumina brada na minha mente.
       
       Abaixo a cabeça por um fio de segundo; o segundo monstro salta por cima de mim. Giro o corpo sobre o próprio eixo e cravo a espada de baixo para cima na barriga da fera enquanto ela ainda está no ar. O cadáver cai pesado no chão.
       
       Eskil, que vinha recuando para me apoiar, para o passo e abre um sorriso orgulhoso:
       
       Bom reflexo, garoto! Corte limpo e base firme. A armadura nova caiu bem em você!""",
                       "proxima_cena": "capitulo_1_transicao_batalha_final",
                     }
                   ]
                 },
                 "C": {
                    "texto": "Observar o movimento das criaturas e contra-atacar na abertura (Inteligencia 2, Destreza 1)",
                    "modos": [
                       {
                          "requisitos": [
                             {
                                "tipo": "atributo",
                                "nome": "inteligencia",
                                "valor": 2,
                             },
                             {
                                "tipo": "atributo",
                                "nome": "destreza",
                                "valor": 1,                         
                             }
                          ],
                          "narrativa": 
                          """Relembro rapidamente as instruções táticas que vi Yvaine usar momentos atrás. Observo os pés das feras e a inclinação da vegetação baixa ao redor. Dou dois passos calculados para trás, atraindo a primeira criatura para um emaranhado de raízes expostas. Ela prende as patas traseiras e hesita por uma fração de segundo.
       
       É o suficiente. Avanço com uma estocada precisa no peito do monstro preso. Antes que a segunda besta perceba a armadilha, uso a carcaça da primeira como apoio, impulso-me para o lado e desfiro um golpe rápido na espinha da garra restante, paralisando-a de imediato.
       
       Yvaine nota a movimentação de longe, estufa o peito visivelmente orgulhosa e dá um breve sorriso:
       
       — Usando o terreno e a paciência ao seu favor… É o meu garoto!.
       """,
                          "proxima_cena": "capitulo_1_transicao_batalha_final",
                       }
                    ]
                 },
              }
    },

    "capitulo_1_transicao_batalha_final": {
       "HUD": True,
       "narrativa": carregar_texto("capitulo_1_transicao_batalha_final.txt"),
       "proxima_cena": "capitulo_1_batalha_final_heroica"
    },

    "capitulo_1_batalha_final_heroica": {
       "narrativa": """O Cath Palug ruge, os olhos brilhando em uma tonalidade carmesim profana. Suas garras demoníacas cintilam em um tom rubi fulgurante à medida que a fera avança contra mim. Sinto o perigo no ar: as garras de um Palug não ferem apenas a carne, mas dilaceram a própria alma. """,
       "blocos_sequenciais": [
          {
             "check_oculto": {
                "tipo": "atributo",
                "nome": "destreza",
                "valor": 2
             },
             "sucesso": {
                "texto": "Dou um salto lateral no exato milissegundo em que as garras rubras cortam o ar onde meu peito estava. O impacto da patada da besta estilhaça o solo de pedra ao meu lado, abrindo a guarda do monstro.",
                "sub_checks": [
                   {
                      "check": {"tipo": "atributo", "nome": "forca", "valor": 1},
                      "texto": "Aproveito a abertura e desfiro um golpe brutal com minha espada banhada pela essência negra de Nix. A lâmina atravessa a carapaça do Palug, deixando um corte profundo em seu flanco. A fera urra de dor enquanto sangue negro goteja no solo.",
                      "proxima_cena": "capitulo_1_batalha_final_heroica_fase_2A"
                   },
                   {
                      "check": {"tipo": "atributo", "nome": "magia", "valor": 1},
                      "texto": "Com o suporte de Nix, canalizo uma chama negra de essência sombria em minha mão e o manifesto diretamente na pata apoiada da criatura. O fogo profano queima a carne do felino enquanto drena sua energia.",
                      "proxima_cena": "capitulo_1_batalha_final_heroica_fase_2A"
                   },
                   {
                      "check": {"tipo": "atributo", "nome": "inteligencia", "valor": 2},
                      "texto": "Lembro-me da conversa com Lumina sobre moldar a essência. Com a energia de Nix, imagino envolvendo meu punho com uma densa manopla de essência negra cristalizada e desfiro um soco devastador diretamente no crânio da fera, fazendo-a desnortear com o impacto.",
                      "proxima_cena": "capitulo_1_batalha_final_heroica_fase_2A"
                   },                      
                ],
                "texto_falha_sub_checks": "Consigo esquivar a tempo, recompondo minha postura enquanto o felino se vira rapidamente para mim, arfando.",
                "proxima_cena": "capitulo_1_batalha_final_heroica_fase_2B",
             },
             "falha": {
                "texto": "Tento desviar, mas o veneno dos barghests ainda afeta meu equilibrio. As garras rubi rasgam meu peito. A dor não é apenas física; sinto como se minha própria vitalidade e energia fossem arrancadas de mim!",
                "dano_recebido": 5,
                "aplicar_debuff": {"atributo": "magia", "valor": 1},
                "check_resgate": {
                   "tipo": "chance_sorte",
                   "requisito_base": 25,
                   "bonus_por_ponto": 10,
                },
                "sucesso_resgate": {
                   "texto": "Por um tris! Consigo esquivar a cabeça no último milissegundo. Os dentes do monstro estalam no ar, raspando meu ombro.",
                   "proxima_cena": "capitulo_1_batalha_final_heroica_fase_2B"
                },
                "falha_resgate": {
                   "texto": "Minha visão escurece. A dor do ferimento me impede de erguer a lâmina a tempo. As mandíbulas da besta se fecham ao redor do meu pescoço... O mundo se apaga...",
                   "proxima_cena": "game_over"
                }
             },
          }
       ],
    },

    "game_over": {"dano_recebido": 99, "proxima_cena": ""},

    "capitulo_1_batalha_final_heroica_fase_2A": {
       "narrativa": """Após o primeiro contato, a criatura cambaleia. Yvaine finaliza o tratamento de Astrid, saca suas adagas com rapidez e habilidade, eliminando um dos imps que cercavam Eskil.
       Sem perder tempo, o guerreiro faz uma investida contra o último diabo, decepando sua cabeça com um corte limpo. O casal se prepara para se unir a Eldrin na batalha mágica.
       O conjurador continua invocando criaturas demoníacas — seres que parecem sombras vivas — e os comanda para cima do arquimago. Eldrin, por sua vez, utiliza magia de luz para eliminar as sombras em um piscar de olhos. É possível notar a impaciência no olhar do daemon tamer. Em um rito desesperado, ele invoca uma enorme gárgula que voa diretamente na direção do elfo. Dessa vez, a conjuração rápida de feitiços de Eldrin não é suficiente, pois a besta parece ser imune à magia.
       No entanto, o rito cobra seu preço: o invocador tosse sangue e aparenta ter perdido a capacidade de se teleportar. Ele tenta aproveitar a confusão no campo de batalha para fugir, mas uma adaga cintilante voa da direção de uma das árvores, atingindo em cheio o seu calcanhar. Não sei quem a lançou, mas a mira foi impecável. Com o calcanhar ferido, mesmo que o mago corra sem descanso, não irá muito longe, deixando um rastro de sangue fácil de seguir.
       Yvaine e Eskil se juntam a Eldrin para conter a gárgula.

       Ouço um leve rosnado à minha frente; a criatura me observa, aguardando meu próximo movimento. Com o Cath Palug se recompondo do primeiro encontro, a iniciativa está totalmente em minhas mãos!""",
       "opcoes": {
          "A": {
             "texto": "Observar a criatura, aguardando seu próximo movimento",
             "proxima_cena": "capitulo_1_palug_atk_final_heroico"
          },
          "B": {
             "texto": "Investir contra a criatura com a espada embanhada em essência negra de Nix",
             "conhecimento_adquirido": "Palug - Espada Negra",
             "proxima_cena": "cap_1_check_death_palugA"
          }, 
          "C": {
             "texto": "Atacar a criatura utlizando a chama negra, buscando queimá-la por inteiro (Magia 1)",
             "conhecimento_adquirido": "Palug - Chama Negra",
             "proxima_cena": "cap_1_check_death_palugA"
          },  
          "D": {
             "texto": "Investir contra a criatura utilizando a manopla de essencia para esmagá-la (Inteligência 2)",
             "conhecimento_adquirido": "Palug - Manopla Negra",
             "proxima_cena": "cap_1_check_death_palugA"
          },                     
       }
    },

    "cap_1_check_death_palugA": {
       "blocos_sequenciais":[
          {
             "check_oculto": {
                "tipo": "chance_sorte",
                "requisito_base": 50,
                "bonus_por_ponto": 10,
             },
             "sucesso": {
                "texto": "Meu ataque passa direto pela guarda da besta!",
                "sub_checks": [
                   {
                     "check": {"tipo": "conhecimento", "nome": "Palug - Espada Negra"},
                     "texto": """O golpe atinge o Cath Palug em cheio causando um corte profundo.
                     O felino desaba, sangrando profusamente e agonizando. Quando a criatura faz um esforço para se levantar e tentar um último arranhão, sinto uma onda de energia aquecer minhas costas: Astrid conjura suas últimas forças, cobrindo meu corpo com uma aura de mana radiante!
                     Sinto minha força se multiplicar, desfiro outro golpe minha lâmina aumenta com o encanto de Astrid e a essência de Nix, dividindo a fera ao meio com um corte vertical devastador.""", 
                     "proxima_cena": "capitulo_1_final"
                   },
                   {
                     "check": {"tipo": "conhecimento", "nome": "Palug - Chama Negra"},
                     "texto": """O golpe atinge o Cath Palug em cheio seus pelo se incendeiam com o fogo negro.
                     O felino desaba agonizando. Quando a criatura faz um esforço para se levantar e tentar um último arranhão, sinto uma onda de energia aquecer minhas costas: Astrid conjura suas últimas forças, cobrindo meu corpo com uma aura de mana radiante!
                     Canalizo o poder de Astrid junto à essência de Nix, criando uma lança de chama sombria que atravessa o coração do Cath Palug e o vaporiza por dentro.""", 
                     "proxima_cena": "capitulo_1_final"
                   },  
                   {
                     "check": {"tipo": "conhecimento", "nome": "Palug - Manopla Negra"},
                     "texto": """O golpe atinge o Cath Palug em cheio um soco certeiro na base de seu crânio.
                     O felino desaba, sangrando profusamente e agonizando. Quando a criatura faz um esforço para se levantar e tentar um último arranhão, sinto uma onda de energia aquecer minhas costas: Astrid conjura suas últimas forças, cobrindo meu corpo com uma aura de mana radiante!
                     A manopla de essência duplica de tamanho sob o efeito do brilho de Astrid. Desfiro um soco sísmico no peito da besta, colapsando seu corpo contra o solo.""", 
                     "proxima_cena": "capitulo_1_final"
                   },                                      
                ],
             }
          },
       ]
    },

    "capitulo_1_batalha_final_heroica_fase_2B": {
       "narrativa": """Após o primeiro contato, a criatura me ronda, me encarando como se tivesse encontrado a presa perfeita. Enquanto isso Yvaine finaliza o tratamento de Astrid, saca suas adagas com rapidez e habilidade, eliminando um dos imps que cercavam Eskil.
Sem perder tempo, o guerreiro faz uma investida contra o último diabo, decepando sua cabeça com um corte limpo. O casal se prepara para se unir a Eldrin na batalha mágica.
O conjurador continua invocando criaturas demoníacas — seres que parecem sombras vivas — e os comanda para cima do arquimago. Eldrin, por sua vez, utiliza magia de luz para eliminar as sombras em um piscar de olhos. É possível notar a impaciência no olhar do daemon tamer. Em um rito desesperado, ele invoca uma enorme gárgula que voa diretamente na direção do elfo. Dessa vez, a conjuração rápida de feitiços de Eldrin não é suficiente, pois a besta parece ser imune à magia.
No entanto, o rito cobra seu preço: o invocador tosse sangue e aparenta ter perdido a capacidade de se teleportar. Ele tenta aproveitar a confusão no campo de batalha para fugir, mas uma adaga cintilante voa da direção de uma das árvores, atingindo em cheio o seu calcanhar. Não sei quem a lançou, mas a mira foi impecável. Com o calcanhar ferido, mesmo que o mago corra sem descanso, não irá muito longe, deixando um rastro de sangue fácil de seguir.
Yvaine e Eskil se juntam a Eldrin para conter a gárgula.

Ouço um leve rosnado à minha frente; a criatura aguarda meu próximo movimento. A iniciativa está totalmente em minhas mãos!""",
       "opcoes": {
          "A": {
             "texto": "Observar a criatura, aguardando seu próximo movimento",
             "proxima_cena": "capitulo_1_palug_atk_final_heroico"
          },
          "B": {
             "texto": "Investir contra a criatura com a espada embanhada em essência negra de Nix",
             "conhecimento_adquirido": "Palug - Espada Negra",
             "proxima_cena": "cap_1_check_death_palugB"
          }, 
          "C": {
             "texto": "Atacar a criatura utlizando a chama negra, buscando queimá-la por inteiro (Magia 1)",
             "conhecimento_adquirido": "Palug - Chama Negra",
             "proxima_cena": "cap_1_check_death_palugB"
          },  
          "D": {
             "texto": "Investir contra a criatura utilizando a manopla de essencia para esmagá-la (Inteligência 2)",
             "conhecimento_adquirido": "Palug - Manopla Negra",
             "proxima_cena": "cap_1_check_death_palugB"
          },                     
       }
    },

    "cap_1_check_death_palugB": {
           "blocos_sequenciais":[
              {
                 "check_oculto": {
                    "tipo": "chance_sorte",
                    "requisito_base": 80,
                    "bonus_por_ponto": 10,
                 },
                 "sucesso": {
                    "texto": "Meu ataque passa direto pela guarda da besta!",
                    "sub_checks": [
                       {
                         "check": {"tipo": "conhecimento", "nome": "Palug - Espada Negra"},
                         "texto": """O golpe atinge o Cath Palug em cheio causando um corte profundo.
                         O felino desaba, sangrando profusamente e agonizando. Quando a criatura faz um esforço para se levantar e tentar um último arranhão, sinto uma onda de energia aquecer minhas costas: Astrid conjura suas últimas forças, cobrindo meu corpo com uma aura de mana radiante!
                         Sinto minha força se multiplicar, desfiro outro golpe minha lâmina aumenta com o encanto de Astrid e a essência de Nix, dividindo a fera ao meio com um corte vertical devastador.""", 
                         "proxima_cena": "capitulo_1_final"
                       },
                       {
                         "check": {"tipo": "conhecimento", "nome": "Palug - Chama Negra"},
                         "texto": """O golpe atinge o Cath Palug em cheio seus pelo se incendeiam com o fogo negro.
                         O felino desaba agonizando. Quando a criatura faz um esforço para se levantar e tentar um último arranhão, sinto uma onda de energia aquecer minhas costas: Astrid conjura suas últimas forças, cobrindo meu corpo com uma aura de mana radiante!
                         Canalizo o poder de Astrid junto à essência de Nix, criando uma lança de chama sombria que atravessa o coração do Cath Palug e o vaporiza por dentro.""", 
                         "proxima_cena": "capitulo_1_final"
                       },  
                       {
                         "check": {"tipo": "conhecimento", "nome": "Palug - Manopla Negra"},
                         "texto": """O golpe atinge o Cath Palug em cheio um soco certeiro na base de seu crânio.
                         O felino desaba, sangrando profusamente e agonizando. Quando a criatura faz um esforço para se levantar e tentar um último arranhão, sinto uma onda de energia aquecer minhas costas: Astrid conjura suas últimas forças, cobrindo meu corpo com uma aura de mana radiante!
                         A manopla de essência duplica de tamanho sob o efeito do brilho de Astrid. Desfiro um soco sísmico no peito da besta, colapsando seu corpo contra o solo.""", 
                         "proxima_cena": "capitulo_1_final"
                       },                                      
                    ],
                 },
                "falha": {
                   "texto": """A fera antecipa o meu movimento, usa a cauda para desviar meu ataque e me atinge com um golpe de impacto violento nas costelas!.
                   Caio de joelhos, sem ar. O Cath Palug escancara as mandíbulas e salta para mordida!""",
                   "dano_recebido": 5,
                   "check_resgate": {
                        "tipo": "chance_sorte",
                        "requisito_base": 25,
                        "bonus_por_ponto": 10,
                    },
                    "sucesso_resgate": {
                        "texto": "Consigo esquivar no último milissegundo! Os dentes do monstro estalam no ar.",
                        "proxima_cena": "capitulo_1_palug_atk_final_heroico"
                    },
                    "falha_resgate": {
                        "texto": "Minha visão escurece. A dor do ferimento me impede de erguer a lâmina a tempo. As mandíbulas da besta se fecham ao redor do meu pescoço... O mundo se apaga...",
                        "proxima_cena": "game_over"
                    }                   
                },
              },
           ]
        },

    "capitulo_1_palug_atk_final_heroico": {
       "narrativa": """Recuo um passo, desacelerando a respiração e analisando detalhadamente cada tremor na postura da fera.
O Cath Palug se lança em uma sequência de ataques. Prevejo sua trajetória e, ao realizar uma esquiva em ângulo perfeito, giro o corpo e desfiro um golpe cirúrgico: degolo parte do pescoço do felino e decepo uma de suas patas dianteiras!
A besta desaba rugindo de dor. Tenta se levantar cambaleando e faz uma última investida cega. Astrid projeta uma barreira de luz à minha frente, bloqueando o ataque residual. O Cath Palug colide contra a barreira e cai morto, sucumbindo à hemorragia.""",
       "proxima_cena": "capitulo_1_final",
    },
#----- CAPITULOS A SEREM ESCRITOS-----
    "capitulo_1_abandono": {
        "narrativa": "[CAPITULO EM CONSTRUÇÃO]",
        "proxima_cena": "menu_principal"
    },

    "capitulo_1_casa_final_sem_bencao": {
        "narrativa": "[CAPITULO EM CONSTRUÇÃO]",
        "proxima_cena": "menu_principal"
    },

    "capitulo_1_casa_conversa_com_espirito": {
        "narrativa": "[CAPITULO EM CONSTRUÇÃO]",
        "proxima_cena": "menu_principal"
    },

    "capitulo_1_treino_na_floresta": {
        "narrativa": "[CAPITULO EM CONSTRUÇÃO]",
        "proxima_cena": "menu_principal"
    },

    "capitulo_1_treino_de_destreza": {
        "narrativa": "[CAPITULO EM CONSTRUÇÃO]",
        "proxima_cena": "menu_principal"
    },

    "capitulo_1_praca_central": {
        "narrativa": "[CAPITULO EM CONSTRUÇÃO]",
        "proxima_cena": "menu_principal"
    },

    "capitulo_1_loja_equipamentos": {
        "narrativa": "[CAPITULO EM CONSTRUÇÃO]",
        "proxima_cena": "menu_principal"
    },

    "capitulo_1_livraria_busca_com_astrid": {
        "narrativa": "[CAPITULO EM CONSTRUÇÃO]",
        "proxima_cena": "menu_principal"
    },

    "capitulo_1_eldrin_halftruth": {
        "narrativa": "[CAPITULO EM CONSTRUÇÃO]",
        "proxima_cena": "menu_principal"
    },
     
    "capitulo_1_eldrin_lie": {
        "narrativa": "[CAPITULO EM CONSTRUÇÃO]",
        "proxima_cena": "menu_principal"
    }, 

    "capitulo_1_Astrid_reasons": {
        "narrativa": "[CAPITULO EM CONSTRUÇÃO]",
        "proxima_cena": "menu_principal"
    }, 

    "capitulo_1_vilarejo_B": {
        "narrativa": "[CAPITULO EM CONSTRUÇÃO]",
        "proxima_cena": "menu_principal"
    }, 

    "capitulo_1_yvaine_reveal": {
        "narrativa": "[CAPITULO EM CONSTRUÇÃO]",
        "proxima_cena": "menu_principal"
    }, 

    "capitulo_1_yvaine_halfreveal": {
        "narrativa": "[CAPITULO EM CONSTRUÇÃO]",
        "proxima_cena": "menu_principal"
    }, 

    "capitulo_1_final": {
        "narrativa": "[CAPITULO EM CONSTRUÇÃO]",
        "proxima_cena": "menu_principal"
    }, 

}

# ============================================
# 5. EXECUÇÃO DO JOGO
# ============================================
if __name__ == "__main__":
  root = tk.Tk()
  app = InterfaceRPG(root, cenas)
  root.mainloop()