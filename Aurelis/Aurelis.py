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
    self.destreza = 0
    self.inteligencia = 1
    self.sorte = 1
    self.magia = 0
    self.vitalidade = 0
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
# -----SISTEMA DE CONSULTA DE ATRIBUTOS COM BONUS------
  def permitir_distribuicao(self, permitir: bool):
     self.pode_distribuir_pontos = permitir

  def obter_atributo_total(self, nome_atributo):
    valor_base = getattr(self, nome_atributo.lower(), 0)
    bonus_equipamentos =  0
    for slot, item, in self.equipamentos.items():
      if isinstance(item, dict) and "bonus" in item:
        bonus_equipamentos += item["bonus"].get(nome_atributo, 0)
    return valor_base + bonus_equipamentos

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

  def descansar(self):
    self.hp_atual = self.hp_max
    self.mp_atual = self.mp_max
# -----METODOS DE INVENTARIO UNICO/CONSUMIVEL------
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

  def gastar_moedas(self, quantidade):
    if self.tem_moedas(quantidade):
      self.moedas -= quantidade
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
    while self.experiencia >= self.exp_para_proximo_nivel:
        self.experiencia -= self.exp_para_proximo_nivel
        self.nivel += 1
        self.pontos_disponiveis += 1
        self.exp_para_proximo_nivel = int(self.exp_para_proximo_nivel * 1.5)
# -----METODOS DE NPCS------
  def registrar_npc(self, id_npc, npc_objeto=None, nome=None, faccao="neutro"):
    if id_npc not in self.npcs:
      if isinstance(npc_objeto, NPC):
        self.npcs[id_npc] = npc_objeto
      else:
        self.npcs[id_npc] = NPC(nome=nome, faccao=faccao)

  def obter_npc(self, id_npc):
    return self.npcs.get(id_npc)

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
        self.cor_botao = "#36393f"
        self.cor_botao_hover = "#4f545c"
      else:
        self.cor_fundo = "#f2f3f5"
        self.cor_painel = "#ffffff"
        self.cor_texto = "#2e3338"
        self.cor_destaque = "#4e5d94"
        self.cor_botao = "#e3e5e8"
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
      if limpar:
        self.area_texto.delete("1.0", tk.END)
      self.area_texto.insert(tk.END, texto + "\n\n")
      self.area_texto.config(state="disabled")
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
    hud = (
        f"Nome: {j.nome} | Nível: {j.nivel} EXP: {j.experiencia}/{j.exp_para_proximo_nivel} | Pontos Disponíveis: {j.pontos_disponiveis} ===\n"
        f"HP: {j.hp_atual}/{j.hp_max} | MP: {j.mp_atual}/{j.mp_max}\n"
        f"FOR: {j.obter_atributo_total('forca')} | DES: {j.obter_atributo_total('destreza')}\n"
        f"INT: {j.obter_atributo_total('inteligencia')} | SOR: {j.obter_atributo_total('sorte')}\n"
        f"MAG: {j.obter_atributo_total('magia')} | VIT: {j.obter_atributo_total('vitalidade')}\n"
        f"Moedas: {j.moedas}C\n"
        f"Inventário: {itens_str}\n"
        f"Itens Únicos: {unicos_str}\n"
        + "=" * 60
    )
    return hud

  def avaliar_condicao_oculta(self, condicao):
    j = self.jogador
    tipo = condicao.get("tipo")
    if tipo in ["sorte", "chance_sorte"]:
      base = condicao.get("requisito_base", 90)
      bonus = condicao.get("bonus_por_ponto", 10)
      limite = max(0, base - ((j.obter_atributo_total("sorte") - 1) * bonus))
      return random.randint(0, 100) >= limite
    elif tipo == "atributo":
        return j.tem_atributo(condicao["nome"], condicao["valor"])
    elif tipo == "item":
        return j.tem_item(condicao["nome"], condicao.get("quantidade", 1))
    elif tipo == "item_unico":
        return j.tem_item_unico(condicao["nome"])
    elif tipo == "moedas":
        return j.tem_moedas(condicao["valor"])
    elif tipo == "hp_minimo":
        return j.hp_atual >= condicao["valor"]
    elif tipo == "mp_minimo":
        return j.mp_atual >= condicao["valor"]
    elif tipo in ["conhecimento", "flag"]:
        return j.tem_conhecimento(condicao["nome"])
    return False

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

# Construçao da narrativa visual
    texto_exibicao = ""
    if cena.get("HUD", False):
      texto_exibicao += self.obter_texto_hud() + "\n\n"

    if cena.get("titulo"):
      texto_exibicao += f"=== {cena['titulo']} ===\n\n"

    narrativa = cena.get("narrativa")
    if narrativa:
      texto_exibicao += formatar_texto(narrativa)

    self.escrever_narrativa(texto_exibicao)

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
      for req in modo_bem_sucedido.get("requisitos", []):
        if req["tipo"] == "magia":
          self.jogador.consumir_mp(req["custo_mp"])

      if "conhecimento_adquirido" in modo_bem_sucedido:
        for segredo in modo_bem_sucedido["conhecimento_adquirido"]:
          self.jogador.adicionar_conhecimento(segredo)

      if "item_unico_adquirido" in modo_bem_sucedido:
        for item in modo_bem_sucedido["item_unico_adquirido"]:
          self.jogador.adicionar_item_unico(item)

      if "item_unico_removido" in modo_bem_sucedido:
        for item in modo_bem_sucedido["item_unico_removido"]:
          self.jogador.remover_item_unico(item)

      if "item_adquirido" in modo_bem_sucedido:
        for entrada in modo_bem_sucedido["item_adquirido"]:
          if isinstance(entrada, dict):
            self.jogador.adicionar_item(
                entrada["item"], entrada.get("quantidade", 1)
            )
          else:
            self.jogador.adicionar_item(entrada, 1)

      if "item_removido" in modo_bem_sucedido:
        for entrada in modo_bem_sucedido["item_removido"]:
          if isinstance(entrada, dict):
            self.jogador.remover_item(
                entrada["item"], entrada.get("quantidade", 1)
            )
          else:
            self.jogador.remover_item(entrada, 1)

      if "equipar_item" in modo_bem_sucedido:
         item = modo_bem_sucedido["equipar_item"]
         # Garante que está no inventário e equipa no slot indicado
         if not self.jogador.tem_item(item["nome"]):
          self.jogador.adicionar_item(item["nome"])
         self.jogador.equipar_item(item)  # Recalcula HP, MP e bônus automaticamente

      if "perder_equipamento_slot" in modo_bem_sucedido:
        slot = modo_bem_sucedido["perder_equipamento_slot"]
        item_perdido = self.jogador.desequipar_item(slot)
        if item_perdido:
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

      if "ganho_moedas" in modo_bem_sucedido:
        self.jogador.adicionar_moedas(
            modo_bem_sucedido["ganho_moedas"],
            multiplicador=modo_bem_sucedido.get("multiplicador_moedas", 1),
        )

      if "gasto_moedas" in modo_bem_sucedido:
        self.jogador.gastar_moedas(modo_bem_sucedido["gasto_moedas"])

      proxima = modo_bem_sucedido["proxima_cena"]
      self.carregar_cena(proxima)
    else:
      messagebox.showwarning(
          "Requisitos não atendidos",
          "Você não possui os requisitos necessários para escolher esta opção.",
      )

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
          "C": {
              "texto": """Ignorar o apelo da garota e a notificação do Sistema, virando as costas e indo embora.""",
              "modos": [
                  {
                      "requisitos": [],
                      "narrativa": """Decido que não vale a pena arriscar minha vida por uma desconhecida. Viro as costas e me preparo para ir embora.""",
                      "proxima_cena": "capitulo_1_abandono",
                  }
              ],
            },
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
            "B": {
                "texto": "Deixar o lobo escapar para preservar a mana da garota até sairmos da floresta.",
                "modos": [
                    {
                        "requisitos": [],
                        "narrativa": """Decido poupar as energias de Astrid. Deixo o animal assustado fugir manco pela vegetação.
===========================================================
[Missão Concluída!]
Aura está satisfeita, garantindo ao hospedeiro uma
oportunidade de evolução. Escolha com sabedoria!
===========================================================
RECOMPENSAS:
[+5 XP]
=========================================================== """,
                        "xp_ganha": 5,
                        "proxima_cena": "capitulo_1_casa",
                    }
                ]
            },
        }
    },

    "capitulo_1_casa": {
        "narrativa": carregar_texto("capitulo_1_casa.txt"),
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

            "B": {
                "texto": "Guardar a Pílula e não fazer nada",
                "modos": [
                    {
                        "requisitos": [],
                        "proxima_cena": "capitulo_1_casa_jantar_bencao_B",
                    }
                ],
            },
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
                      "proxima_cena": "capitulo_1_vilarejo",
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
        "moedas_ganhas": 15,
        "opcoes": {
            "A": {
                "texto": "Praça Central e Feira de Comidas: Ir até a praça do vilarejo, repleta de barracas de espetinhos, guloseimas locais e uma bela fonte onde podem comer e apreciar a paisagem.",
                "modos": [ {
                    "requisitos": [],
                    "proxima_cena": "capitulo_1_praca_central",
                    },
                ],
            },
            "B": {
                "texto": "Loja de Equipamentos: Visitar o armazém de caça e usinagem. Com a possibilidade de ir até a floresta em breve, você decide se equipar adequadamente.",
                "modos": [
                    {
                      "requisitos": [],
                      "proxima_cena": "capitulo_1_loja_equipamentos",
                    },
                ],
            },
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
        "opcoes": {
            "A": {
                "texto": "Recusar o convite de Eldrin e acompanhar Astrid em sua busca por livros e grimórios pela biblioteca.",
                "modos": [
                    {
                      "requisitos": [],
                      "proxima_cena": "capitulo_1_livraria_busca_com_astrid",
                    }
                ]
            },
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
           "A": {
              "texto": "Revelar a conversa que teve com Eldrin e confrontar Astrid sobre suas reais intenções.",
              "modos": [
                 {
                    "requisitos": [],
                    "proxima_cena": "capitulo_1_Astrid_reasons"
                 }
              ]
           },
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

    "capitulo_1_clinica": {
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

}

# ============================================
# 5. EXECUÇÃO DO JOGO
# ============================================
if __name__ == "__main__":
  root = tk.Tk()
  app = InterfaceRPG(root, cenas)
  root.mainloop()