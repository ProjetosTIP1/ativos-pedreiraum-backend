# PROMPT — Especificação de Aplicativo: Catálogo de Ativos Usados | Grupo Pedreira Um Valemix

---

## CONTEXTO GERAL

Desenvolva um aplicativo web full-stack responsivo para o **Grupo Pedreira Um Valemix**, com o objetivo de **exibir e comercializar equipamentos, máquinas e peças usadas** do grupo. O aplicativo deve ser visualmente profissional, de fácil navegação, e facilitar o contato comercial via WhatsApp.

---

## IDENTIDADE VISUAL

- Nome do aplicativo: **Catálogo de Ativos** (ou sugestão similar)
- Público-alvo: construtoras, mineradoras, revendedores de equipamentos, operadores independentes
- Tom visual: industrial, robusto, confiável — paleta sugerida: tons de cinza escuro, laranja/amarelo construção, branco
- Logo: usar logotipo do Grupo Pedreira Um Valemix (anexo)

---

## FUNCIONALIDADES PRINCIPAIS

### 1. LISTAGEM DE ATIVOS
- Exibir cards com foto principal, nome do equipamento, categoria, ano, estado de conservação e preço (ou "Consultar")
- Suporte a múltiplas fotos por ativo (galeria/carrossel)
- Indicador visual de estado de conservação: Ótimo / Bom / Regular

### 2. FILTROS E BUSCA
Painel de filtros lateral ou superior com os seguintes campos:
- **Categoria** (ex: Caminhões, Escavadeiras, Britadores, Compactadores, Motoniveladoras, Peças, Outros)
- **Subcategoria** (dinâmica conforme categoria selecionada)
- **Ano de fabricação** (range: de / até)
- **Marca** (ex: Caterpillar, Volvo, Komatsu, Mercedes, etc.)
- **Estado de conservação** (Ótimo, Bom, Regular)
- **Disponibilidade** (Disponível / Vendido / Reservado)
- Campo de **busca por texto livre** (nome, modelo, nº de série)

### 3. PÁGINA DE DETALHE DO ATIVO
Cada ativo terá uma página de detalhe com:

#### Dados gerais:
- Nome / Denominação
- Categoria e Subcategoria
- Fabricante / Marca
- Modelo
- Ano de fabricação
- Número de série / Patrimônio
- Horimetro (horas de uso) — para máquinas
- Quilometragem — para caminhões e veículos
- Estado de conservação (Ótimo / Bom / Regular)
- Localização atual (cidade/UF)
- Disponibilidade

#### Especificações técnicas por categoria:

**Caminhões / Veículos:**
- Tipo (basculante, carroceria, betoneira, etc.)
- Capacidade de carga (ton)
- Motor (potência, cilindradas, tipo combustível)
- Tração (4x2, 6x4, 8x4, etc.)
- RENAVAM / Placa (opcional)
- Revisões / Manutenções recentes

**Escavadeiras / Retroescavadeiras:**
- Peso operacional (ton)
- Potência do motor (HP/CV)
- Profundidade máxima de escavação (m)
- Capacidade da caçamba (m³)
- Tipo de trem de rolamento (esteira / pneu)
- Opcionais (martelo hidráulico, etc.)

**Britadores / Peneiras:**
- Tipo (mandíbula, cônico, impacto, etc.)
- Capacidade de produção (t/h)
- Abertura de alimentação (mm)
- Granulometria de saída (mm)
- Motor elétrico ou diesel (potência)
- Número de decks (peneiras)

**Motoniveladoras / Compactadores:**
- Peso operacional (ton)
- Potência (HP/CV)
- Largura da lâmina / tambor (m)
- Tipo de compactação (liso, pé-de-carneiro, pneumático)
- Número de passadas recomendado

**Correias Transportadoras / Equipamentos de Planta:**
- Comprimento (m)
- Largura da correia (mm)
- Inclinação (graus)
- Capacidade (t/h)
- Motor (potência, tensão)

**Peças e Componentes:**
- Equipamento compatível
- Número da peça / código OEM
- Estado (nova, recondicionada, usada)
- Quantidade disponível

#### Galeria de fotos:
- Mínimo de 1 foto, suporte a até 20 imagens
- Visualizador com zoom e navegação
- Legenda opcional por foto

#### Observações livres:
- Campo de texto para informações adicionais relevantes

---

### 4. BOTÃO DE CONTATO VIA WHATSAPP

Em cada ativo, exibir um botão **"Tenho interesse — Falar no WhatsApp"** que, ao clicar, abre o WhatsApp com uma **mensagem pré-preenchida** no seguinte formato:

```
Olá! Tenho interesse no seguinte equipamento do catálogo Valemix Ativos:

📋 *[Nome do Equipamento]*
🏷️ Categoria: [Categoria]
🏭 Marca/Modelo: [Marca] [Modelo]
📅 Ano: [Ano]
🔗 Link: [URL da página do ativo]

Poderia me passar mais informações sobre disponibilidade e valor?
```

- Número de WhatsApp configurável pelo administrador no painel
- O link deve redirecionar para `https://wa.me/55XXXXXXXXXXX?text=[mensagem codificada]`

---

### 5. PAINEL ADMINISTRATIVO (back-office)

Acesso restrito por login (admin). Funcionalidades:

- **Cadastro de ativos**: formulário completo com upload de fotos (arrastar e soltar), todos os campos de especificação por categoria
- **Edição e exclusão de ativos**
- **Gestão de categorias e subcategorias**
- **Alterar status** do ativo: Disponível / Reservado / Vendido
- **Configuração do número de WhatsApp** de contato
- **Destaque de ativos** (aparecem no topo ou em banner)
- **Dashboard simples**: total de ativos, visualizações, cliques no WhatsApp por ativo

---

## ARQUITETURA TÉCNICA SUGERIDA

| Camada | Tecnologia sugerida |
|---|---|
| Frontend | React.js + TypeScript + Zod + Zustand |
| Backend | Python + FastApi + Pydantic |
| Banco de dados | PostgreSQL |
| Upload de imagens | Cloudinary ou armazenamento próprio (S3-compatible) |
| Autenticação | JWT (admin) | Google |
| Deploy | Vercel / Railway / Render |

---

## EXPERIÊNCIA DO USUÁRIO (UX)

- Interface **mobile-first** — maioria dos contatos virá pelo celular
- Carregamento rápido dos cards com lazy loading nas imagens
- Página de detalhe com URL amigável (ex: `/ativos/escavadeira-cat-336-2018`)
- Compartilhamento fácil: botão de copiar link ou compartilhar
- SEO básico por ativo (meta title, description, imagem OG)

---

## DIFERENCIAIS DESEJADOS

- Ativo marcado como **"Destaque"** aparece em banner rotativo na home
- Contador de visualizações por ativo (não precisa de login do usuário)
- Possibilidade de o cliente **solicitar mais fotos** via WhatsApp com mensagem automática

---

## ENTREGÁVEIS ESPERADOS

1. Aplicação web completa (front + back + banco)
2. Painel admin funcional
3. Deploy em ambiente de produção com URL acessível
4. Documentação básica de uso do painel admin

---
