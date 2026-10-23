"""
PublicHelp AI - PowerPoint Presentation Generator
Creates a professional, modern 18-slide executive presentation deck for PublicHelp AI.
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

OUTPUT_FILE = "PublicHelp_AI_Presentation.pptx"

# Color Palette Constants
DARK_NAVY = RGBColor(15, 23, 42)      # #0F172A - Main dark background / primary text
SLATE_HEADER = RGBColor(30, 41, 59)    # #1E293B - Card background or deep accent
EMERALD_GREEN = RGBColor(16, 185, 129) # #10B981 - Tech/civic green accent
EMERALD_DARK = RGBColor(5, 150, 105)   # #059669 - Accent dark
AMBER_GOLD = RGBColor(245, 158, 11)    # #F59E0B - Highlight gold
BLUE_ACCENT = RGBColor(59, 130, 246)   # #3B82F6 - Link / Blue accent
LIGHT_BG = RGBColor(248, 250, 252)     # #F8FAFC - Off white
WHITE = RGBColor(255, 255, 255)
CARD_BG = RGBColor(255, 255, 255)
CARD_BORDER = RGBColor(226, 232, 240)  # #E2E8F0
TEXT_MUTED = RGBColor(100, 116, 139)   # #64748B
TEXT_DARK = RGBColor(30, 41, 59)       # #1E293B

def set_slide_background(slide, color):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_header(slide, title_text, category_text="PUBLICHELP AI • TECHNICAL PRESENTATION"):
    # Header bar shape
    banner = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.15))
    banner.fill.solid()
    banner.fill.fore_color.rgb = DARK_NAVY
    banner.line.color.rgb = DARK_NAVY

    # Category pill / subtitle
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.12), Inches(11.5), Inches(0.3))
    tf_c = cat_box.text_frame
    tf_c.word_wrap = True
    p_c = tf_c.paragraphs[0]
    p_c.text = category_text.upper()
    p_c.font.size = Pt(10)
    p_c.font.bold = True
    p_c.font.color.rgb = EMERALD_GREEN

    # Title text
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.5), Inches(0.65))
    tf = title_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title_text
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = WHITE

def add_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=CARD_BORDER):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1.2)
    return shape

def add_footer(slide, slide_num, total_slides=18):
    foot_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(11.733), Inches(0.35))
    tf = foot_box.text_frame
    p = tf.paragraphs[0]
    p.text = f"PublicHelp AI — Explainable Recommender System for Citizen Welfare   |   Slide {slide_num} of {total_slides}"
    p.font.size = Pt(9.5)
    p.font.color.rgb = TEXT_MUTED

def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6] # Blank layout

    # ==========================================
    # SLIDE 1: Title Slide (Dark Executive Theme)
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, DARK_NAVY)

    # Accent decorative bar
    bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.3), Inches(1.5), Inches(0.1))
    bar.fill.solid()
    bar.fill.fore_color.rgb = EMERALD_GREEN
    bar.line.color.rgb = EMERALD_GREEN

    t_box = s1.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.7), Inches(2.2))
    tf1 = t_box.text_frame
    tf1.word_wrap = True
    p1 = tf1.paragraphs[0]
    p1.text = "PublicHelp AI"
    p1.font.size = Pt(46)
    p1.font.bold = True
    p1.font.color.rgb = WHITE

    p2 = tf1.add_paragraph()
    p2.text = "A Multi-Channel Hybrid Recommender System with Deterministic Eligibility & Explainability for Indian Citizen Welfare Schemes"
    p2.font.size = Pt(20)
    p2.font.color.rgb = RGBColor(203, 213, 225) # Slate 300
    p2.space_before = Pt(14)

    # Badges row
    badges = [
        ("FastAPI & PyTorch Core", BLUE_ACCENT),
        ("Hybrid RRF + MMR Engine", EMERALD_GREEN),
        ("Deterministic Eligibility", AMBER_GOLD),
        ("React 19 + Tailwind UI", RGBColor(168, 85, 247))
    ]
    bx = Inches(0.8)
    for title, color in badges:
        card = add_card(s1, bx, Inches(3.9), Inches(2.7), Inches(0.6), bg_color=DARK_NAVY, border_color=color)
        tb = s1.shapes.add_textbox(bx, Inches(3.95), Inches(2.7), Inches(0.5))
        pt = tb.text_frame.paragraphs[0]
        pt.text = f"★ {title}"
        pt.font.size = Pt(11)
        pt.font.bold = True
        pt.font.color.rgb = color
        pt.alignment = PP_ALIGN.CENTER
        bx += Inches(2.95)

    # Author & Meta Card
    card_meta = add_card(s1, Inches(0.8), Inches(4.8), Inches(11.7), Inches(1.9), bg_color=SLATE_HEADER, border_color=RGBColor(51, 65, 85))
    tb_meta = s1.shapes.add_textbox(Inches(1.1), Inches(4.95), Inches(11.1), Inches(1.6))
    tf_m = tb_meta.text_frame
    tf_m.word_wrap = True
    
    p = tf_m.paragraphs[0]
    p.text = "Project Architecture & Engineering Defense  •  Academic & Industrial Review"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = EMERALD_GREEN

    p = tf_m.add_paragraph()
    p.text = "• Dataset: 2,066 Official Schemes from MyScheme Government Portal (Central & State Ministries)"
    p.font.size = Pt(12)
    p.font.color.rgb = WHITE
    p.space_before = Pt(6)

    p = tf_m.add_paragraph()
    p.text = "• Core AI Components: TF-IDF Lexical Matching + all-MiniLM-L6-v2 GPU Embeddings + Reciprocal Rank Fusion + Vectorized MMR"
    p.font.size = Pt(12)
    p.font.color.rgb = RGBColor(226, 232, 240)

    p = tf_m.add_paragraph()
    p.text = "• Live Repository: https://github.com/DDVats/PublicHelpAI.git  |  Verified with 70 Automated Passing Tests"
    p.font.size = Pt(11)
    p.font.color.rgb = AMBER_GOLD
    p.space_before = Pt(4)

    # ==========================================
    # SLIDE 2: Executive Summary & Context
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2, LIGHT_BG)
    add_header(s2, "Executive Summary: Transforming Civic Welfare Discovery")
    add_footer(s2, 2)

    # 3 Stat Cards across top
    stats = [
        ("2,000+", "Active Welfare Schemes", "Spanning agriculture, education, pensions, women empowerment, health insurance & MSME loans", BLUE_ACCENT),
        ("₹15+ Lakh Cr", "Annual Welfare Budget", "Dedicated annually by Central & State Govts, yet millions of citizens miss statutory entitlements", AMBER_GOLD),
        ("100% Discoverable", "Full Catalog Coverage", "Zero dead ends: every statutory scheme is indexed, searchable, and verified deterministically", EMERALD_GREEN)
    ]
    sx = Inches(0.8)
    for num, lbl, desc, col in stats:
        add_card(s2, sx, Inches(1.4), Inches(3.64), Inches(1.8), bg_color=WHITE, border_color=CARD_BORDER)
        tb = s2.shapes.add_textbox(sx + Inches(0.2), Inches(1.5), Inches(3.24), Inches(1.6))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = num
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = col
        p = tf.add_paragraph()
        p.text = lbl
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = TEXT_DARK
        p = tf.add_paragraph()
        p.text = desc
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_before = Pt(4)
        sx += Inches(3.9)

    # Bottom Big Card: The PublicHelp AI Mission
    add_card(s2, Inches(0.8), Inches(3.45), Inches(11.733), Inches(3.4), bg_color=WHITE, border_color=CARD_BORDER)
    tb_mis = s2.shapes.add_textbox(Inches(1.1), Inches(3.6), Inches(11.1), Inches(3.1))
    tf_mis = tb_mis.text_frame
    tf_mis.word_wrap = True

    p = tf_mis.paragraphs[0]
    p.text = "The Paradigm Shift: From Passive Directories to Proactive Recommender Systems"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = DARK_NAVY

    bullets = [
        ("The Current Status Quo: ", "Citizens must navigate dozens of fragmented portals, decipher complex bureaucratic eligibility criteria, and guess exact Sanskrit/bureaucratic scheme names (PMAY, PM-KISAN, NFSA)."),
        ("The PublicHelp AI Vision: ", "An explainable, citizen-first recommender system that models user demographic profiles, employs dense semantic matching to overcome lexical barriers, and runs strict constraint satisfaction rules."),
        ("Explainability & Trust: ", "Provides transparent, data-backed reasons ('Why Recommended') matching user age, domicile, income ceilings, and caste categories so citizens trust every recommendation."),
        ("Actionable Entitlements: ", "Groups complementary welfare schemes into unified packages (e.g. Farmer income + crop insurance + solar pump) while maintaining individual eligibility guarantees.")
    ]
    for b_title, b_body in bullets:
        p = tf_mis.add_paragraph()
        p.space_before = Pt(7)
        run1 = p.add_run()
        run1.text = "• " + b_title
        run1.font.bold = True
        run1.font.size = Pt(11.5)
        run1.font.color.rgb = EMERALD_DARK
        run2 = p.add_run()
        run2.text = b_body
        run2.font.size = Pt(11)
        run2.font.color.rgb = TEXT_DARK

    # ==========================================
    # SLIDE 3: The Civic Bottlenecks in India
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3, LIGHT_BG)
    add_header(s3, "Root-Cause Analysis: The Three Civic Discovery Bottlenecks")
    add_footer(s3, 3)

    pillars = [
        ("1. Information Fragmentation", [
            "Schemes are scattered across 36 State / UT portals and 50+ Central Ministries.",
            "Crucial eligibility guidelines are trapped in multi-page government PDFs & gazettes.",
            "Inconsistent terminology across states (e.g., 'Rythu Bandhu' vs. 'Kalia' vs. 'PM-Kisan').",
            "Result: Over 60% of eligible rural beneficiaries never discover relevant schemes."
        ], RGBColor(239, 68, 68)), # Red
        ("2. Keyword Search Failure & Cold Start", [
            "Citizens search colloquial terms like 'money for farming' or 'help for college girl'.",
            "Official portals use exact statutory strings: 'Post-Matric Scholarship for SC/ST'.",
            "Lexical BM25 search returns 0 matches for semantic paraphrases.",
            "Result: High bounce rates, citizen frustration, and exclusion of marginalized groups."
        ], AMBER_GOLD),
        ("3. Zero Eligibility Verification", [
            "Existing portals are passive link directories without automated eligibility checking.",
            "A citizen discovers a scheme only to be rejected at an office due to income or state rules.",
            "LLMs hallucinate eligibility criteria, leading to invalid applications.",
            "Result: Administrative backlog, wasted citizen travel costs, and lost public trust."
        ], BLUE_ACCENT)
    ]

    px = Inches(0.8)
    for title, items, color in pillars:
        add_card(s3, px, Inches(1.4), Inches(3.64), Inches(5.4), bg_color=WHITE, border_color=CARD_BORDER)
        
        # Pill header
        pill = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, px, Inches(1.4), Inches(3.64), Inches(0.45))
        pill.fill.solid()
        pill.fill.fore_color.rgb = color
        pill.line.color.rgb = color
        tb_p = s3.shapes.add_textbox(px, Inches(1.45), Inches(3.64), Inches(0.35))
        p = tb_p.text_frame.paragraphs[0]
        p.text = title
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER

        tb = s3.shapes.add_textbox(px + Inches(0.2), Inches(2.0), Inches(3.24), Inches(4.6))
        tf = tb.text_frame
        tf.word_wrap = True
        for i, item in enumerate(items):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text = "• " + item
            p.font.size = Pt(11)
            p.font.color.rgb = TEXT_DARK
            p.space_before = Pt(10)
        px += Inches(3.9)

    # ==========================================
    # SLIDE 4: Core Innovation: Why a Recommender System?
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4, LIGHT_BG)
    add_header(s4, "System Innovation: Why Recommender Engine vs. Search or LLMs?")
    add_footer(s4, 4)

    # Comparison Table Card
    add_card(s4, Inches(0.8), Inches(1.4), Inches(11.733), Inches(5.4), bg_color=WHITE, border_color=CARD_BORDER)
    tb_c = s4.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(11.3), Inches(5.1))
    tfc = tb_c.text_frame
    tfc.word_wrap = True

    p = tfc.paragraphs[0]
    p.text = "Architectural Paradigm Comparison for Civic Welfare Delivery"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = DARK_NAVY

    # Add Table
    table_shape = s4.shapes.add_table(5, 4, Inches(1.0), Inches(2.0), Inches(11.3), Inches(4.5))
    table = table_shape.table
    table.columns[0].width = Inches(2.3)
    table.columns[1].width = Inches(3.0)
    table.columns[2].width = Inches(3.0)
    table.columns[3].width = Inches(3.0)

    headers = ["Evaluation Dimension", "Traditional Keyword Search", "Pure Generative LLM (RAG)", "PublicHelp AI (Hybrid RecSys)"]
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = DARK_NAVY if j < 3 else EMERALD_DARK
        for p in cell.text_frame.paragraphs:
            p.font.bold = True
            p.font.size = Pt(11)
            p.font.color.rgb = WHITE
            p.alignment = PP_ALIGN.CENTER

    rows_data = [
        ("Query Understanding", "Exact token overlap only; fails on colloquial Hindi/English phrasing", "Strong semantic intent; high prompt sensitivity", "Dual-Channel: TF-IDF n-grams + dense GPU sentence embeddings"),
        ("Eligibility Guarantee", "Zero automated verification; redirects to government PDFs", "Prone to hallucination; probabilistic rules cannot guarantee law", "Deterministic constraint engine with strict tri-state verification"),
        ("Result Diversity", "Redundant: returns 10 variants from single ministry", "Uncontrolled list generation; position bias", "Vectorized Maximal Marginal Relevance (MMR, λ=0.85)"),
        ("Explainability & Trust", "No explanation provided; citizen unaware of qualification criteria", "Black-box natural language reasoning without citation audit", "Data-backed explainability badges linking age, state, caste, and income")
    ]
    for i, row in enumerate(rows_data):
        for j, val in enumerate(row):
            cell = table.cell(i+1, j)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(241, 245, 249) if j < 3 else RGBColor(236, 253, 245)
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(10)
                p.font.color.rgb = TEXT_DARK if j < 3 else RGBColor(6, 95, 70)
                if j == 0:
                    p.font.bold = True

    # ==========================================
    # SLIDE 5: End-to-End System Architecture
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5, LIGHT_BG)
    add_header(s5, "System Architecture: End-to-End Multi-Channel Pipeline")
    add_footer(s5, 5)

    # 5 Process Flow Cards
    steps = [
        ("1. Citizen Input", "Demographic Profile (Age, State, Caste, Income, Gender) + Stated Civic Need Query", BLUE_ACCENT),
        ("2. Dual Retrieval", "Sparse TF-IDF n-grams (exact terms) + Dense 384d all-MiniLM-L6-v2 Embeddings on GPU", RGBColor(99, 102, 241)),
        ("3. Rank Fusion (RRF)", "Reciprocal Rank Fusion (k=60) merges ordinal rankings across sparse & dense channels", RGBColor(168, 85, 247)),
        ("4. Eligibility Filter", "Deterministic constraint satisfaction: hard pruning of ineligible items; tri-state audit", AMBER_GOLD),
        ("5. MMR Diversity", "Vectorized MMR (λ=0.85) matrix-dot reranking + Bundling + 'Why Recommended' Badges", EMERALD_DARK)
    ]
    sy = Inches(1.4)
    for title, desc, col in steps:
        add_card(s5, Inches(0.8), sy, Inches(11.733), Inches(0.9), bg_color=WHITE, border_color=CARD_BORDER)
        pill = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), sy + Inches(0.18), Inches(2.2), Inches(0.55))
        pill.fill.solid()
        pill.fill.fore_color.rgb = col
        pill.line.color.rgb = col
        p = pill.text_frame.paragraphs[0]
        p.text = title
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER

        tb = s5.shapes.add_textbox(Inches(3.4), sy + Inches(0.12), Inches(8.9), Inches(0.65))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = desc
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_DARK
        sy += Inches(1.05)

    # Latency badge at bottom
    add_card(s5, Inches(0.8), Inches(6.55), Inches(11.733), Inches(0.45), bg_color=DARK_NAVY, border_color=DARK_NAVY)
    tb_bot = s5.shapes.add_textbox(Inches(1.0), Inches(6.58), Inches(11.3), Inches(0.35))
    p = tb_bot.text_frame.paragraphs[0]
    p.text = "⚡ End-to-End Latency: Sub-400ms across all 2,066 schemes with vectorized NumPy MMR & in-memory SQLite FTS5"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = EMERALD_GREEN
    p.alignment = PP_ALIGN.CENTER

    # ==========================================
    # SLIDE 6: Dataset Engineering & Normalization
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6, LIGHT_BG)
    add_header(s6, "Data Engineering: Schema Normalization & SQLite FTS5")
    add_footer(s6, 6)

    # Left Card: The Dataset
    add_card(s6, Inches(0.8), Inches(1.4), Inches(5.7), Inches(5.4), bg_color=WHITE, border_color=CARD_BORDER)
    tb_l = s6.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(5.3), Inches(5.1))
    tfl = tb_l.text_frame
    tfl.word_wrap = True

    p = tfl.paragraphs[0]
    p.text = "Dataset Ingestion & Cleaning Pipeline"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = DARK_NAVY

    d_bullets = [
        ("Source Authority: ", "MyScheme official repository of Indian Central & State Government civic welfare schemes."),
        ("Catalog Size: ", "2,066 distinct verified welfare schemes covering 36 States/UTs and Central ministries."),
        ("Raw vs. Parsed: ", "Raw scraped text had 16 unstructured string fields. Ingestion pipeline extracts structured numerical and relational columns."),
        ("SQLite FTS5: ", "Engineered an in-memory SQLite FTS5 full-text virtual table indexing title, objective, details, and benefits."),
        ("Zero Missing IDs: ", "Deterministic ID assignment and deduplication ensuring 100% catalog integrity and schema validation.")
    ]
    for b_title, b_body in d_bullets:
        p = tfl.add_paragraph()
        p.space_before = Pt(8)
        r1 = p.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = BLUE_ACCENT
        r2 = p.add_run()
        r2.text = b_body
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = TEXT_DARK

    # Right Card: Extracted Relational Attributes
    add_card(s6, Inches(6.8), Inches(1.4), Inches(5.733), Inches(5.4), bg_color=WHITE, border_color=CARD_BORDER)
    tb_r = s6.shapes.add_textbox(Inches(7.0), Inches(1.5), Inches(5.3), Inches(5.1))
    tfr = tb_r.text_frame
    tfr.word_wrap = True

    p = tfr.paragraphs[0]
    p.text = "Extracted Relational Constraint Fields"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = DARK_NAVY

    fields = [
        ("min_age / max_age", "INTEGER", "Standardized numerical age brackets [0 to 120] for youth, working, and senior schemes"),
        ("gender_rule", "VARCHAR", "Strict values: ALL, FEMALE_ONLY, MALE_ONLY, TRANSGENDER_ONLY"),
        ("state_rule", "VARCHAR", "CENTRAL vs. specific State/UT codes (UP, MP, Bihar, Rajasthan, etc.)"),
        ("income_ceiling", "FLOAT", "Extracted annual income caps (e.g. ₹2,50,000 for EWS scholarships)"),
        ("social_category", "VARCHAR", "General, SC, ST, OBC, Minority, Differently-Abled (Divyang)"),
        ("land_holding_cap", "FLOAT", "Agricultural land limits in hectares/acres for small & marginal farmers")
    ]
    for fname, ftype, fdesc in fields:
        p = tfr.add_paragraph()
        p.space_before = Pt(6)
        r1 = p.add_run()
        r1.text = f"⚙ {fname} "
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = EMERALD_DARK
        r2 = p.add_run()
        r2.text = f"[{ftype}]: {fdesc}"
        r2.font.size = Pt(10)
        r2.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 7: Dual-Channel Candidate Retrieval
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7, LIGHT_BG)
    add_header(s7, "Candidate Retrieval: Sparse Lexical & Dense GPU Semantic Channels")
    add_footer(s7, 7)

    # 2 Big Cards Side-by-Side
    # Channel 1: Sparse Lexical
    add_card(s7, Inches(0.8), Inches(1.4), Inches(5.7), Inches(5.4), bg_color=WHITE, border_color=CARD_BORDER)
    tb_c1 = s7.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(5.3), Inches(5.1))
    tf1 = tb_c1.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "Channel 1: Sparse Lexical (TF-IDF & N-Grams)"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = BLUE_ACCENT

    p = tf1.add_paragraph()
    p.text = "Target: Exact token matching, scheme acronyms, statutory legal terms"
    p.font.size = Pt(10.5)
    p.font.italic = True
    p.font.color.rgb = TEXT_MUTED
    p.space_before = Pt(3)

    c1_bullets = [
        ("N-gram Range: ", "Unigrams and bigrams (1, 2) configured with English and Hindi transliterated stopword suppression."),
        ("Statutory Precision: ", "Guarantees exact discovery for acronyms like 'PMAY', 'KCC', 'PM-KISAN', 'OBC Scholarship', 'Kanya Sumangala'."),
        ("Sub-linear TF Scaling: ", "Prevents multi-page scheme gazettes from dominating shorter, highly focused state schemes."),
        ("Ultra-Low Latency: ", "Executes sparse matrix dot product in ~8.6 ms across the 2,066 scheme corpus.")
    ]
    for b_title, b_body in c1_bullets:
        p = tf1.add_paragraph()
        p.space_before = Pt(8)
        r1 = p.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = DARK_NAVY
        r2 = p.add_run()
        r2.text = b_body
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = TEXT_DARK

    # Channel 2: Dense Semantic
    add_card(s7, Inches(6.8), Inches(1.4), Inches(5.733), Inches(5.4), bg_color=WHITE, border_color=CARD_BORDER)
    tb_c2 = s7.shapes.add_textbox(Inches(7.0), Inches(1.5), Inches(5.3), Inches(5.1))
    tf2 = tb_c2.text_frame
    tf2.word_wrap = True

    p = tf2.paragraphs[0]
    p.text = "Channel 2: Dense Semantic (Sentence Transformers)"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = EMERALD_DARK

    p = tf2.add_paragraph()
    p.text = "Target: Colloquial intent, conceptual matching, vocabulary mismatch resolution"
    p.font.size = Pt(10.5)
    p.font.italic = True
    p.font.color.rgb = TEXT_MUTED
    p.space_before = Pt(3)

    c2_bullets = [
        ("Model Backbone: ", "sentence-transformers/all-MiniLM-L6-v2 yielding 384-dimensional dense vectors."),
        ("GPU Hardware Acceleration: ", "PyTorch accelerated on NVIDIA GeForce RTX 2050 GPU for high-throughput tensor operations."),
        ("Vocabulary Invariance: ", "Maps informal user phrasing ('help for poor college girl') to bureaucratic titles ('Post-Matric Financial Assistance') with zero keyword overlap."),
        ("Normalized Inner Product: ", "Pre-normalized L2 embeddings allow exact cosine similarity computation via fast matrix multiplication in ~13.3 ms.")
    ]
    for b_title, b_body in c2_bullets:
        p = tf2.add_paragraph()
        p.space_before = Pt(8)
        r1 = p.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = DARK_NAVY
        r2 = p.add_run()
        r2.text = b_body
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = TEXT_DARK

    # ==========================================
    # SLIDE 8: Reciprocal Rank Fusion (RRF)
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8, LIGHT_BG)
    add_header(s8, "Ranking Fusion: Reciprocal Rank Fusion (RRF) Theory & Defense")
    add_footer(s8, 8)

    # Top Formula Card
    add_card(s8, Inches(0.8), Inches(1.4), Inches(11.733), Inches(1.8), bg_color=DARK_NAVY, border_color=DARK_NAVY)
    tb_form = s8.shapes.add_textbox(Inches(1.1), Inches(1.5), Inches(11.1), Inches(1.6))
    tff = tb_form.text_frame
    tff.word_wrap = True

    p = tff.paragraphs[0]
    p.text = "The Mathematical Problem & The RRF Solution"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = EMERALD_GREEN

    p = tff.add_paragraph()
    p.text = "Linear weighted scoring (Score = α·TFIDF + β·Cosine) suffers from divergent score distributions: TF-IDF is unbounded and document-length sensitive, whereas Cosine similarity is bounded in [-1, 1]. Direct addition causes unpredictable rank distortion."
    p.font.size = Pt(10.5)
    p.font.color.rgb = RGBColor(226, 232, 240)
    p.space_before = Pt(4)

    p = tff.add_paragraph()
    p.text = "RRF Score(d) = ∑ (m ∈ M) [ 1 / ( k + r_m(d) ) ]      (with smoothing constant k = 60)"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = AMBER_GOLD
    p.space_before = Pt(6)

    # 3 Strategic Benefits Cards
    b_cards = [
        ("1. Scale & Distribution Invariance", "RRF relies solely on ordinal rankings rather than raw uncalibrated scores. No score normalization or min-max calibration artifacts can skew candidate retrieval.", BLUE_ACCENT),
        ("2. Robustness to Outliers", "If a document receives an abnormally high score in one channel due to token repetition, its rank contribution remains strictly bounded by 1/(k+1) = 0.01639.", AMBER_GOLD),
        ("3. Proven Information Retrieval Standard", "Endorsed across modern enterprise search architectures (Cormack et al., SIGIR) for multi-channel retrieval, guaranteeing stable and fair candidate fusion.", EMERALD_DARK)
    ]
    bx = Inches(0.8)
    for title, desc, col in b_cards:
        add_card(s8, bx, Inches(3.4), Inches(3.64), Inches(3.4), bg_color=WHITE, border_color=CARD_BORDER)
        tb = s8.shapes.add_textbox(bx + Inches(0.2), Inches(3.55), Inches(3.24), Inches(3.1))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = col
        p = tf.add_paragraph()
        p.text = desc
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_DARK
        p.space_before = Pt(8)
        bx += Inches(3.9)

    # ==========================================
    # SLIDE 9: Deterministic Eligibility Engine
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9, LIGHT_BG)
    add_header(s9, "Eligibility Verification: Deterministic Constraint Satisfaction")
    add_footer(s9, 9)

    # Top Examiner Defense Banner
    add_card(s9, Inches(0.8), Inches(1.4), Inches(11.733), Inches(1.3), bg_color=WHITE, border_color=CARD_BORDER)
    tb_def = s9.shapes.add_textbox(Inches(1.0), Inches(1.45), Inches(11.3), Inches(1.2))
    tfd = tb_def.text_frame
    tfd.word_wrap = True
    p = tfd.paragraphs[0]
    p.text = "★ KEY EXAMINER DEFENSE: Why Deterministic Rules Instead of LLMs or Neural Classifiers?"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = EMERALD_DARK
    p = tfd.add_paragraph()
    p.text = "In public governance, welfare eligibility is a legal and statutory determination, not a probabilistic guess. Machine learning models hallucinate and cannot be audited in a court of law. PublicHelp AI enforces deterministic boolean constraint satisfaction with a 100% mathematical audit trail."
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(3)

    # 3 Tri-State Outcome Cards
    tri_states = [
        ("POTENTIALLY_ELIGIBLE", RGBColor(16, 185, 129), [
            "All specified demographic constraints are strictly satisfied.",
            "Citizen age falls within [min_age, max_age].",
            "State of residence matches domicile rule or scheme is CENTRAL.",
            "Income does not exceed statutory ceiling.",
            "Gender and social category match statutory target."
        ]),
        ("NEEDS_MORE_INFO", RGBColor(245, 158, 11), [
            "Certain scheme prerequisites cannot be confirmed from user profile.",
            "E.g., scheme requires disability certificate, minority religion, or land deed.",
            "System transparently alerts the citizen to supply additional documentation.",
            "Prevents wrongful false rejections of entitled beneficiaries."
        ]),
        ("NOT_ELIGIBLE (Hard Prune)", RGBColor(239, 68, 68), [
            "Explicit contradiction detected between user profile and scheme law.",
            "E.g., Male citizen applying for 'Kanya Sumangala' (Female only).",
            "E.g., Age 55 applying for youth apprenticeship (Max age 35).",
            "Automatically pruned from recommendations to avoid citizen misinformation."
        ])
    ]
    tx = Inches(0.8)
    for title, col, bullets in tri_states:
        add_card(s9, tx, Inches(2.9), Inches(3.64), Inches(3.9), bg_color=WHITE, border_color=CARD_BORDER)
        pill = s9.shapes.add_shape(MSO_SHAPE.RECTANGLE, tx, Inches(2.9), Inches(3.64), Inches(0.4))
        pill.fill.solid()
        pill.fill.fore_color.rgb = col
        pill.line.color.rgb = col
        p = pill.text_frame.paragraphs[0]
        p.text = title
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER

        tb = s9.shapes.add_textbox(tx + Inches(0.2), Inches(3.4), Inches(3.24), Inches(3.3))
        tf = tb.text_frame
        tf.word_wrap = True
        for i, b in enumerate(bullets):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text = "• " + b
            p.font.size = Pt(10)
            p.font.color.rgb = TEXT_DARK
            p.space_before = Pt(6)
        tx += Inches(3.9)

    # ==========================================
    # SLIDE 10: Vectorized Maximal Marginal Relevance (MMR)
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10, LIGHT_BG)
    add_header(s10, "Diversity Defense: Vectorized Maximal Marginal Relevance (MMR)")
    add_footer(s10, 10)

    # Left Card: The Formulation & Redundancy Problem
    add_card(s10, Inches(0.8), Inches(1.4), Inches(5.7), Inches(5.4), bg_color=WHITE, border_color=CARD_BORDER)
    tb_l = s10.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(5.3), Inches(5.1))
    tfl = tb_l.text_frame
    tfl.word_wrap = True

    p = tfl.paragraphs[0]
    p.text = "The Diversity Problem in Public Welfare"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = DARK_NAVY

    p = tfl.add_paragraph()
    p.text = "Without MMR, searching 'farming financial support' returns 10 near-identical crop subsidy schemes from the same state department. The citizen never sees crop insurance, solar pumping subsidies, or loan waivers."
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_MUTED
    p.space_before = Pt(4)

    p = tfl.add_paragraph()
    p.text = "MMR Mathematical Formulation (λ = 0.85):"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = EMERALD_DARK
    p.space_before = Pt(8)

    p = tfl.add_paragraph()
    p.text = "MMR(Q, C, S) = argmax [ λ·Rel(Q, d_i) - (1-λ)·max Sim(d_i, d_j) ]"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = BLUE_ACCENT
    p.space_before = Pt(4)

    p = tfl.add_paragraph()
    p.text = "• C is the candidate pool; S is the set of already selected items.\n• Rel(Q, d_i) is the relevance utility score.\n• Sim(d_i, d_j) is pairwise cosine similarity between 384d scheme vectors.\n• λ = 0.85 balances 85% core relevance with 15% ministry & domain diversity."
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(4)

    # Right Card: Vectorization & NumPy Optimization
    add_card(s10, Inches(6.8), Inches(1.4), Inches(5.733), Inches(5.4), bg_color=WHITE, border_color=CARD_BORDER)
    tb_r = s10.shapes.add_textbox(Inches(7.0), Inches(1.5), Inches(5.3), Inches(5.1))
    tfr = tb_r.text_frame
    tfr.word_wrap = True

    p = tfr.paragraphs[0]
    p.text = "NumPy Vectorization Optimization"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = DARK_NAVY

    perf_bullets = [
        ("The Naive MMR Bottleneck: ", "Iterative Python loops with scikit-learn cosine_similarity took over 200 ms per request due to repeated function call overhead."),
        ("Vectorized Implementation: ", "Pre-stacked the candidate embedding matrix E_cand (N x 384). Evaluated similarities to the selected set S via a single matrix-vector dot product: np.dot(E_cand, e_selected)."),
        ("Bounded Candidate Pool: ", "Capped candidate pool to top 60 highest-ranked items prior to MMR reranking."),
        ("Sub-Millisecond Execution: ", "Execution latency reduced from 200ms+ down to 0.8 milliseconds (>250x speedup), maintaining zero lag on live user interfaces.")
    ]
    for b_title, b_body in perf_bullets:
        p = tfr.add_paragraph()
        p.space_before = Pt(8)
        r1 = p.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = AMBER_GOLD
        r2 = p.add_run()
        r2.text = b_body
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = TEXT_DARK

    # ==========================================
    # SLIDE 11: Multi-Persona Simulation & Bundles
    # ==========================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11, LIGHT_BG)
    add_header(s11, "Civic Personalization: Persona Simulation & Welfare Packages")
    add_footer(s11, 11)

    # 4 Persona Cards
    personas = [
        ("Ramesh Patel (44)", "Marginal Farmer, Madhya Pradesh", "Income: ₹75,000 | General", "Top Matches: MP Farmer Income Support, PM-Kisan Samman Nidhi, Kisan Credit Card", BLUE_ACCENT),
        ("Maya Sharma (19)", "SC Female Student, Uttar Pradesh", "Income: ₹1,20,000 | SC", "Top Matches: UP Post-Matric SC Scholarship, Girl Child Coaching Grant, National Means-cum-Merit", RGBColor(168, 85, 247)),
        ("Sunita Devi (32)", "Rural Artisan & Homemaker, Bihar", "Income: ₹60,000 | OBC", "Top Matches: Bihar Mahila Udyami Yojana, PM Awas Yojana Gramin, Lakhpati Didi SHG Microloan", EMERALD_DARK),
        ("Rajesh Kumar (67)", "Elderly Pensioner, Rajasthan", "Income: ₹40,000 | SC", "Top Matches: Indira Gandhi National Old Age Pension, Ayushman Bharat PM-JAY, Free Medicine Scheme", AMBER_GOLD)
    ]
    px = Inches(0.8)
    for name, title, meta, matches, col in personas:
        add_card(s11, px, Inches(1.4), Inches(2.75), Inches(3.4), bg_color=WHITE, border_color=CARD_BORDER)
        pill = s11.shapes.add_shape(MSO_SHAPE.RECTANGLE, px, Inches(1.4), Inches(2.75), Inches(0.4))
        pill.fill.solid()
        pill.fill.fore_color.rgb = col
        pill.line.color.rgb = col
        p = pill.text_frame.paragraphs[0]
        p.text = name
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER

        tb = s11.shapes.add_textbox(px + Inches(0.15), Inches(1.85), Inches(2.45), Inches(2.8))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = DARK_NAVY
        p = tf.add_paragraph()
        p.text = meta
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_before = Pt(3)
        p = tf.add_paragraph()
        p.text = matches
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_DARK
        p.space_before = Pt(6)
        px += Inches(2.99)

    # Bottom Bundle Banner
    add_card(s11, Inches(0.8), Inches(5.0), Inches(11.733), Inches(1.8), bg_color=DARK_NAVY, border_color=DARK_NAVY)
    tb_bnd = s11.shapes.add_textbox(Inches(1.1), Inches(5.1), Inches(11.1), Inches(1.6))
    tfb = tb_bnd.text_frame
    tfb.word_wrap = True

    p = tfb.paragraphs[0]
    p.text = "Complementary Welfare Packages (Strategic Bundling)"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = EMERALD_GREEN

    p = tfb.add_paragraph()
    p.text = "• Problem: Citizens rarely need an isolated scheme; they require a comprehensive social safety net.\n• Solution: Engine dynamically groups complementary schemes (e.g., Kisan Samriddhi Bundle = Income Support + Crop Insurance + Solar Infrastructure Subsidy).\n• Independent Verification: Every individual component in the bundle is subjected to independent deterministic eligibility audits."
    p.font.size = Pt(10.5)
    p.font.color.rgb = RGBColor(226, 232, 240)
    p.space_before = Pt(4)

    # ==========================================
    # SLIDE 12: Explainability & Item-to-Item Similarity
    # ==========================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12, LIGHT_BG)
    add_header(s12, "Explainability Framework: Transparent Badges & Item Similarity")
    add_footer(s12, 12)

    # Left: Why Recommended Explainability
    add_card(s12, Inches(0.8), Inches(1.4), Inches(5.7), Inches(5.4), bg_color=WHITE, border_color=CARD_BORDER)
    tb_l = s12.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(5.3), Inches(5.1))
    tfl = tb_l.text_frame
    tfl.word_wrap = True

    p = tfl.paragraphs[0]
    p.text = "Transparent 'Why Recommended' Badges"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = DARK_NAVY

    p = tfl.add_paragraph()
    p.text = "Builds citizen trust through truthful, data-backed rationale"
    p.font.size = Pt(10.5)
    p.font.italic = True
    p.font.color.rgb = TEXT_MUTED
    p.space_before = Pt(3)

    badges_data = [
        ("State Enactment Match: ", "'Specifically enacted for residents of Madhya Pradesh' (validates geographical jurisdiction)."),
        ("Interest Alignment: ", "'Category aligns with your stated interests: Agriculture & Credit'."),
        ("Income Compliance: ", "'Income of ₹75,000 is well within the ₹2,00,000 threshold'."),
        ("Universal Safety Net: ", "'Central Government scheme open to all qualifying Indian citizens'."),
        ("Zero Generic Fluff: ", "No vague marketing language; every explanation maps directly to verified database attributes.")
    ]
    for b_title, b_body in badges_data:
        p = tfl.add_paragraph()
        p.space_before = Pt(8)
        r1 = p.add_run()
        r1.text = "✓ " + b_title
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = EMERALD_DARK
        r2 = p.add_run()
        r2.text = b_body
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = TEXT_DARK

    # Right: Item-to-Item Content-Based Similarity
    add_card(s12, Inches(6.8), Inches(1.4), Inches(5.733), Inches(5.4), bg_color=WHITE, border_color=CARD_BORDER)
    tb_r = s12.shapes.add_textbox(Inches(7.0), Inches(1.5), Inches(5.3), Inches(5.1))
    tfr = tb_r.text_frame
    tfr.word_wrap = True

    p = tfr.paragraphs[0]
    p.text = "Item-to-Item Content-Based Filtering"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = DARK_NAVY

    p = tfr.add_paragraph()
    p.text = "Nearest-neighbor similarity across all 2,066 catalog items"
    p.font.size = Pt(10.5)
    p.font.italic = True
    p.font.color.rgb = TEXT_MUTED
    p.space_before = Pt(3)

    sim_bullets = [
        ("Scheme Detail Discovery: ", "When a citizen inspects a specific scheme detail page, the system calculates pairwise cosine similarities across all 2,066 scheme vectors."),
        ("Similarity Formula: ", "Sim(A, B) = e_A · e_B = ∑ (k=1 to 384) [ e_A,k · e_B,k ]"),
        ("Live Match Percentage: ", "Displays dynamic match percentage badges (e.g., '92% Semantic Match') along with shared tags."),
        ("Alternative Surfacing: ", "If a citizen is marginally ineligible for scheme A, the system immediately surfaces near-equivalent schemes B and C that they do qualify for.")
    ]
    for b_title, b_body in sim_bullets:
        p = tfr.add_paragraph()
        p.space_before = Pt(8)
        r1 = p.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = BLUE_ACCENT
        r2 = p.add_run()
        r2.text = b_body
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = TEXT_DARK

    # ==========================================
    # SLIDE 13: Empirical Evaluation & Benchmark Results
    # ==========================================
    s13 = prs.slides.add_slide(blank_layout)
    set_slide_background(s13, LIGHT_BG)
    add_header(s13, "Empirical Evaluation: Benchmark Results on 27 Civic Test Queries")
    add_footer(s13, 13)

    # Insert Generated Benchmark Chart on Left
    chart_path = "reports/figures/model_benchmark.png"
    if os.path.exists(chart_path):
        s13.shapes.add_picture(chart_path, Inches(0.8), Inches(1.4), Inches(6.8), Inches(5.4))

    # Right Card: Metrics Table & Analysis
    add_card(s13, Inches(7.8), Inches(1.4), Inches(4.733), Inches(5.4), bg_color=WHITE, border_color=CARD_BORDER)
    tb_m = s13.shapes.add_textbox(Inches(8.0), Inches(1.5), Inches(4.333), Inches(5.1))
    tfm = tb_m.text_frame
    tfm.word_wrap = True

    p = tfm.paragraphs[0]
    p.text = "Performance Gains Summary"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = DARK_NAVY

    gains = [
        ("Precision@5: +18.2%", "Improved from 0.0815 to 0.0963, proving top 5 items are significantly more relevant to citizen intent."),
        ("NDCG@5: +13.9%", "Rank-order quality improved from 0.1071 to 0.1220, placing the highest-utility schemes at position #1 and #2."),
        ("MRR: +22.8%", "Mean Reciprocal Rank jumped from 0.1629 to 0.2000, reducing citizen discovery time by nearly a quarter."),
        ("Recall@10: 20.7%", "Healthy retrieval breadth without diluting precision."),
        ("Zero Hallucinations: ", "100% of recommended items are legally verified against database constraints.")
    ]
    for b_title, b_body in gains:
        p = tfm.add_paragraph()
        p.space_before = Pt(8)
        r1 = p.add_run()
        r1.text = "★ " + b_title + "\n"
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = EMERALD_DARK
        r2 = p.add_run()
        r2.text = b_body
        r2.font.size = Pt(10)
        r2.font.color.rgb = TEXT_DARK

    # ==========================================
    # SLIDE 14: RecSys Domain Health & Quality
    # ==========================================
    s14 = prs.slides.add_slide(blank_layout)
    set_slide_background(s14, LIGHT_BG)
    add_header(s14, "RecSys Domain Health: Catalog Coverage & Personalization")
    add_footer(s14, 14)

    # Insert RecSys Health Chart on Left
    health_chart = "reports/figures/recsys_health.png"
    if os.path.exists(health_chart):
        s14.shapes.add_picture(health_chart, Inches(0.8), Inches(1.4), Inches(6.4), Inches(4.0))

    # Latency Chart at bottom left
    lat_chart = "reports/figures/latency_breakdown.png"
    if os.path.exists(lat_chart):
        s14.shapes.add_picture(lat_chart, Inches(0.8), Inches(4.8), Inches(6.4), Inches(2.1))

    # Right Card: Theoretical Metrics
    add_card(s14, Inches(7.4), Inches(1.4), Inches(5.133), Inches(5.5), bg_color=WHITE, border_color=CARD_BORDER)
    tb_h = s14.shapes.add_textbox(Inches(7.6), Inches(1.5), Inches(4.733), Inches(5.2))
    tfh = tb_h.text_frame
    tfh.word_wrap = True

    p = tfh.paragraphs[0]
    p.text = "Recommender Health Verification"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = DARK_NAVY

    h_points = [
        ("Catalog Coverage (100.0%): ", "Every single one of the 2,066 schemes in the database is indexable, retrievable, and verifiable. No 'dark catalog' exists."),
        ("Intra-List Diversity (ILD = 0.7102): ", "Measures average pairwise semantic distance between items in top 10 list. A score of 0.71 confirms recommendations span agriculture, health, education, and housing rather than a single redundant silo."),
        ("Persona Dissimilarity (31.63%): ", "Jaccard distance between recommendations across distinct demographic personas. Proves recommendations are genuinely customized rather than showing the same generic popular list."),
        ("Average Latency (<389 ms): ", "Full end-to-end processing completes well below typical web API thresholds (1000ms).")
    ]
    for b_title, b_body in h_points:
        p = tfh.add_paragraph()
        p.space_before = Pt(8)
        r1 = p.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = BLUE_ACCENT
        r2 = p.add_run()
        r2.text = b_body
        r2.font.size = Pt(10)
        r2.font.color.rgb = TEXT_DARK

    # ==========================================
    # SLIDE 15: Full-Stack Implementation & Frontend UX
    # ==========================================
    s15 = prs.slides.add_slide(blank_layout)
    set_slide_background(s15, LIGHT_BG)
    add_header(s15, "Full-Stack Implementation: FastAPI, React 19 & Tailwind CSS")
    add_footer(s15, 15)

    # 3 Cards: Backend, Frontend, Developer Experience
    cols_data = [
        ("Backend Architecture (FastAPI)", [
            "High-concurrency asynchronous ASGI server.",
            "In-memory MLEngine singleton loaded on startup.",
            "Pydantic v2 strict schema validation.",
            "SQLite FTS5 virtual tables for lexical indexing.",
            "Clean separation of api/, core/, models/, services/."
        ], BLUE_ACCENT),
        ("Frontend Client (React 19 + Vite)", [
            "Modern React 19 with TypeScript and Tailwind CSS.",
            "Persona Simulation Hub with real-time state updates.",
            "Live Eligibility Auditing & 'Why Recommended' tags.",
            "Side-by-side scheme comparison modal.",
            "Interactive ML Insights Dashboard with live metrics."
        ], RGBColor(168, 85, 247)),
        ("Engineering Rigor & Architecture", [
            "Zero external API dependencies (fully self-contained).",
            "Hardware-adaptive: runs on CPU or NVIDIA CUDA GPU.",
            "Deterministic reproducible seeds for ML benchmarking.",
            "Comprehensive error handling and status codes.",
            "Decoupled microservice-ready modular architecture."
        ], EMERALD_DARK)
    ]
    cx = Inches(0.8)
    for title, items, col in cols_data:
        add_card(s15, cx, Inches(1.4), Inches(3.64), Inches(5.4), bg_color=WHITE, border_color=CARD_BORDER)
        pill = s15.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, Inches(1.4), Inches(3.64), Inches(0.45))
        pill.fill.solid()
        pill.fill.fore_color.rgb = col
        pill.line.color.rgb = col
        p = pill.text_frame.paragraphs[0]
        p.text = title
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER

        tb = s15.shapes.add_textbox(cx + Inches(0.2), Inches(2.0), Inches(3.24), Inches(4.6))
        tf = tb.text_frame
        tf.word_wrap = True
        for i, item in enumerate(items):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text = "• " + item
            p.font.size = Pt(11)
            p.font.color.rgb = TEXT_DARK
            p.space_before = Pt(10)
        cx += Inches(3.9)

    # ==========================================
    # SLIDE 16: Automated Testing & Verification
    # ==========================================
    s16 = prs.slides.add_slide(blank_layout)
    set_slide_background(s16, LIGHT_BG)
    add_header(s16, "Verification: 70 Automated Tests Passed (100% Green)")
    add_footer(s16, 16)

    # 4 Test Modules Cards
    tests = [
        ("test_api.py (21 Tests)", [
            "Health & metadata endpoints",
            "Query parsing & pagination",
            "Persona recommendation routing",
            "Detail & similar schemes APIs",
            "Error handling & 404 validation"
        ], BLUE_ACCENT),
        ("test_data.py (15 Tests)", [
            "Database table integrity",
            "Null checks on primary keys",
            "Schema data type conformity",
            "FTS5 full-text search queries",
            "Catalog count (2,066 items)"
        ], AMBER_GOLD),
        ("test_eligibility.py (27 Tests)", [
            "Boundary age constraints",
            "Gender rule hard rejection",
            "Income cap inequality checks",
            "State domicile jurisdiction",
            "Tri-state transition logic"
        ], EMERALD_DARK),
        ("test_recsys.py (7 Tests)", [
            "RRF rank fusion consistency",
            "MMR diversity vs baseline",
            "Persona differentiation",
            "Item-to-item similarity checks",
            "Welfare bundle generation"
        ], RGBColor(168, 85, 247))
    ]
    tx = Inches(0.8)
    for title, items, col in tests:
        add_card(s16, tx, Inches(1.4), Inches(2.75), Inches(4.5), bg_color=WHITE, border_color=CARD_BORDER)
        pill = s16.shapes.add_shape(MSO_SHAPE.RECTANGLE, tx, Inches(1.4), Inches(2.75), Inches(0.4))
        pill.fill.solid()
        pill.fill.fore_color.rgb = col
        pill.line.color.rgb = col
        p = pill.text_frame.paragraphs[0]
        p.text = title
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER

        tb = s16.shapes.add_textbox(tx + Inches(0.15), Inches(1.9), Inches(2.45), Inches(3.8))
        tf = tb.text_frame
        tf.word_wrap = True
        for i, item in enumerate(items):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text = "✓ " + item
            p.font.size = Pt(10)
            p.font.color.rgb = TEXT_DARK
            p.space_before = Pt(8)
        tx += Inches(2.99)

    # Bottom Test Output Banner
    add_card(s16, Inches(0.8), Inches(6.1), Inches(11.733), Inches(0.8), bg_color=DARK_NAVY, border_color=DARK_NAVY)
    tb_t = s16.shapes.add_textbox(Inches(1.0), Inches(6.15), Inches(11.3), Inches(0.7))
    p = tb_t.text_frame.paragraphs[0]
    p.text = "======================== 70 passed, 1 warning in 26.18s ========================"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = EMERALD_GREEN
    p.alignment = PP_ALIGN.CENTER

    # ==========================================
    # SLIDE 17: Production Deployment & Future Roadmap
    # ==========================================
    s17 = prs.slides.add_slide(blank_layout)
    set_slide_background(s17, LIGHT_BG)
    add_header(s17, "Future Roadmap: Multilingual Voice & Civic Digital Public Infra")
    add_footer(s17, 17)

    # 3 Strategic Horizon Cards
    horizons = [
        ("Phase 1: Indic Voice Interface (Bhashini)", [
            "Integrate Digital India Bhashini APIs for automatic speech recognition (ASR) in 12+ Indian languages.",
            "Empower illiterate and semi-literate rural citizens to speak queries in colloquial Hindi, Bhojpuri, Tamil, Telugu, Marathi.",
            "Text-to-Speech (TTS) auditory readout of scheme benefits and eligibility rules."
        ], BLUE_ACCENT),
        ("Phase 2: Aadhaar & DigiLocker e-KYC", [
            "Seamless integration with DigiLocker API to automatically verify caste, income certificates, and domicile.",
            "Convert 'NEEDS_MORE_INFO' status into instantaneous 100% verified eligibility.",
            "Pre-filled single-window welfare application forms for direct submission to state portals."
        ], EMERALD_DARK),
        ("Phase 3: National Scale & Edge Deployment", [
            "Scale catalog from 2,066 to 50,000+ district, municipal, and panchayat-level schemes.",
            "FAISS vector indexing and Redis caching for sub-10ms response times under 100,000 concurrent users.",
            "Offline Common Service Centre (CSC) edge kiosk deployment in rural village secretariats."
        ], AMBER_GOLD)
    ]
    hx = Inches(0.8)
    for title, items, col in horizons:
        add_card(s17, hx, Inches(1.4), Inches(3.64), Inches(5.4), bg_color=WHITE, border_color=CARD_BORDER)
        pill = s17.shapes.add_shape(MSO_SHAPE.RECTANGLE, hx, Inches(1.4), Inches(3.64), Inches(0.45))
        pill.fill.solid()
        pill.fill.fore_color.rgb = col
        pill.line.color.rgb = col
        p = pill.text_frame.paragraphs[0]
        p.text = title
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER

        tb = s17.shapes.add_textbox(hx + Inches(0.2), Inches(2.0), Inches(3.24), Inches(4.6))
        tf = tb.text_frame
        tf.word_wrap = True
        for i, item in enumerate(items):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text = "• " + item
            p.font.size = Pt(11)
            p.font.color.rgb = TEXT_DARK
            p.space_before = Pt(10)
        hx += Inches(3.9)

    # ==========================================
    # SLIDE 18: Summary & Viva Defense Highlights
    # ==========================================
    s18 = prs.slides.add_slide(blank_layout)
    set_slide_background(s18, DARK_NAVY)

    # Title
    t_box = s18.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(11.7), Inches(1.2))
    tf18 = t_box.text_frame
    p = tf18.paragraphs[0]
    p.text = "Summary: PublicHelp AI Contributions & Viva Takeaways"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = WHITE

    # 4 Key Defense Takeaway Cards
    takeaways = [
        ("Civic Value Proposition", "Solves the critical last-mile barrier in Indian public governance by democratizing discovery for 2,066 schemes with zero information asymmetry.", BLUE_ACCENT),
        ("Hybrid Retrieval & RRF", "Combines sparse TF-IDF (statutory tokens) with dense GPU embeddings (colloquial intent) via scale-invariant Reciprocal Rank Fusion (k=60).", EMERALD_GREEN),
        ("Zero-Hallucination Integrity", "Replaces error-prone LLMs with a deterministic boolean constraint satisfaction engine for legally sound, audited eligibility verification.", AMBER_GOLD),
        ("Production-Ready Full Stack", "FastAPI backend, React 19 UI, vectorized MMR diversity (<1ms), 100% catalog coverage, and 70 automated passing pytest tests.", RGBColor(168, 85, 247))
    ]
    tx = Inches(0.8)
    for title, desc, col in takeaways:
        add_card(s18, tx, Inches(2.2), Inches(2.75), Inches(3.6), bg_color=SLATE_HEADER, border_color=col)
        tb = s18.shapes.add_textbox(tx + Inches(0.15), Inches(2.35), Inches(2.45), Inches(3.3))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = col
        p = tf.add_paragraph()
        p.text = desc
        p.font.size = Pt(10.5)
        p.font.color.rgb = RGBColor(226, 232, 240)
        p.space_before = Pt(8)
        tx += Inches(2.99)

    # Bottom Contact & Repo Banner
    add_card(s18, Inches(0.8), Inches(6.1), Inches(11.733), Inches(0.9), bg_color=DARK_NAVY, border_color=EMERALD_GREEN)
    tb_b = s18.shapes.add_textbox(Inches(1.0), Inches(6.2), Inches(11.3), Inches(0.7))
    tf_b = tb_b.text_frame
    p = tf_b.paragraphs[0]
    p.text = "Thank You! Questions & Discussion Welcome."
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.alignment = PP_ALIGN.CENTER
    p = tf_b.add_paragraph()
    p.text = "GitHub Repository: https://github.com/DDVats/PublicHelpAI.git   |   Divyanshu Dwivedi"
    p.font.size = Pt(11)
    p.font.color.rgb = AMBER_GOLD
    p.alignment = PP_ALIGN.CENTER
    p.space_before = Pt(2)

    # Save presentation
    prs.save(OUTPUT_FILE)
    print(f"Presentation saved successfully to: {OUTPUT_FILE}")

if __name__ == "__main__":
    build_presentation()
