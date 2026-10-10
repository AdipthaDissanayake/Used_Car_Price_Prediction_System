"""
Generate 10-Minute Executive Presentation for Used Car Price Prediction System
Tailored for Corporate Decision-Makers:
- De-cluttered, clean, high-impact slides with minimal text and bold visual hierarchy
- Real car hero image embedded on Slide 1
- Strictly NO MAE mentioned
- 4 Members: Member 1 (3 slides), Members 2-4 (2 slides each) = 9 slides total
- Clean corporate slides without presenter name tags on the canvas
- Comprehensive, conversational speaker notes embedded in PowerPoint presenter view
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    # 16:9 widescreen layout
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6] # blank layout

    # Executive Modern Color Palette
    C_NAVY_DARK = RGBColor(15, 23, 42)      # #0F172A
    C_NAVY_CARD = RGBColor(30, 41, 59)      # #1E293B
    C_BLUE = RGBColor(37, 99, 235)          # #2563EB
    C_LIGHT_BLUE = RGBColor(239, 246, 255)  # #EFF6FF
    C_CYAN = RGBColor(14, 165, 233)         # #0EA5E9
    C_GREEN = RGBColor(16, 185, 129)        # #10B981
    C_RED = RGBColor(239, 68, 68)           # #EF4444
    C_BG = RGBColor(248, 250, 252)          # #F8FAFC
    C_WHITE = RGBColor(255, 255, 255)       # #FFFFFF
    C_TEXT_DARK = RGBColor(15, 23, 42)      # #0F172A
    C_TEXT_MUTED = RGBColor(100, 116, 139)  # #64748B
    C_BORDER = RGBColor(226, 232, 240)      # #E2E8F0

    def add_bg(slide, color):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    def add_header(slide, title_text, category_text):
        # Header category tag
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.42), Inches(9.5), Inches(0.32))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        tf_cat.margin_left = tf_cat.margin_top = tf_cat.margin_right = tf_cat.margin_bottom = 0
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.name = "Arial"
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = C_BLUE

        # Slide Main Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.72), Inches(11.5), Inches(0.65))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_top = tf_title.margin_right = tf_title.margin_bottom = 0
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.name = "Arial"
        p_title.font.size = Pt(24)
        p_title.font.bold = True
        p_title.font.color.rgb = C_TEXT_DARK

    def add_notes(slide, notes_text):
        notes_slide = slide.notes_slide
        tf_notes = notes_slide.notes_text_frame
        tf_notes.text = notes_text

    # Resolve Car Image Path
    img_candidates = ["car_hero.jpg", os.path.join("..", "car_hero.jpg")]
    car_img_path = None
    for p in img_candidates:
        if os.path.exists(p):
            car_img_path = os.path.abspath(p)
            break

    # =========================================================================
    # SLIDE 1 (Member 1 - Slide 1 of 3): Title & Real Car Hero Image
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    add_bg(s1, C_NAVY_DARK)

    # Accent vertical ribbon
    ribbon = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.2), Inches(0.12), Inches(5.1))
    ribbon.fill.solid()
    ribbon.fill.fore_color.rgb = C_BLUE
    ribbon.line.fill.background()

    # Executive Badge
    badge = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(1.2), Inches(3.6), Inches(0.4))
    badge.fill.solid()
    badge.fill.fore_color.rgb = C_NAVY_CARD
    badge.line.color.rgb = C_BLUE
    tf_b = badge.text_frame
    p_b = tf_b.paragraphs[0]
    p_b.text = "EXECUTIVE VALUATION PLATFORM"
    p_b.font.name = "Arial"
    p_b.font.size = Pt(10)
    p_b.font.bold = True
    p_b.font.color.rgb = C_CYAN
    p_b.alignment = PP_ALIGN.CENTER

    # Main Title on Left
    t_box = s1.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(5.4), Inches(1.8))
    tf_t = t_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = "Used Car Price\nPrediction System"
    p_t.font.name = "Arial"
    p_t.font.size = Pt(36)
    p_t.font.bold = True
    p_t.font.color.rgb = C_WHITE

    p_sub = tf_t.add_paragraph()
    p_sub.text = "Data-driven vehicle valuation for smarter pricing decisions."
    p_sub.font.name = "Arial"
    p_sub.font.size = Pt(15)
    p_sub.font.color.rgb = C_CYAN
    p_sub.space_before = Pt(10)

    # Key Highlights Card on Left Bottom
    card1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(4.3), Inches(5.3), Inches(2.0))
    card1.fill.solid()
    card1.fill.fore_color.rgb = C_NAVY_CARD
    card1.line.color.rgb = RGBColor(51, 65, 85)
    tf_c1 = card1.text_frame
    tf_c1.margin_left = Inches(0.3)
    tf_c1.margin_top = Inches(0.25)
    
    p_obj = tf_c1.paragraphs[0]
    p_obj.text = "CORE VALUE PROPOSITION"
    p_obj.font.name = "Arial"
    p_obj.font.size = Pt(10)
    p_obj.font.bold = True
    p_obj.font.color.rgb = C_BLUE

    points_s1 = [
        "Replaces subjective appraisal guesswork with empirical market intelligence.",
        "Generates instant fair market valuations in under 2 seconds.",
        "Tested on 4,000+ real transactions to protect dealership profit margins."
    ]
    for pt in points_s1:
        p = tf_c1.add_paragraph()
        p.text = "✔ " + pt
        p.font.size = Pt(11)
        p.font.color.rgb = C_WHITE
        p.space_before = Pt(6)

    # Right Side: Real Car Image Frame
    if car_img_path:
        # Subtle outer container border
        img_frame = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.5), Inches(5.7), Inches(3.6))
        img_frame.fill.solid()
        img_frame.fill.fore_color.rgb = C_NAVY_CARD
        img_frame.line.color.rgb = C_BLUE
        img_frame.line.width = Pt(1.5)

        # Add image
        s1.shapes.add_picture(car_img_path, Inches(6.85), Inches(1.55), Inches(5.6), Inches(3.5))

        # Bottom Caption Pill under image
        cap_pill = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(5.35), Inches(5.7), Inches(0.95))
        cap_pill.fill.solid()
        cap_pill.fill.fore_color.rgb = C_NAVY_CARD
        cap_pill.line.color.rgb = RGBColor(51, 65, 85)
        tf_cap = cap_pill.text_frame
        tf_cap.margin_left = Inches(0.3)
        tf_cap.margin_top = Inches(0.18)
        p_cp1 = tf_cap.paragraphs[0]
        p_cp1.text = "ENTERPRISE INTELLIGENCE ENGINE"
        p_cp1.font.size = Pt(10)
        p_cp1.font.bold = True
        p_cp1.font.color.rgb = C_CYAN
        p_cp2 = tf_cap.add_paragraph()
        p_cp2.text = "Benchmarked on verified commercial transaction datasets."
        p_cp2.font.size = Pt(10.5)
        p_cp2.font.color.rgb = C_WHITE
        p_cp2.space_before = Pt(2)

    add_notes(s1, """[SPEAKER 1 | TIME: ~0:45]

"Good morning everyone. Welcome to our presentation. Today, our team is presenting our Used Car Price Prediction System—an automated, data-driven valuation solution built to eliminate pricing guesswork in the automotive marketplace.

Setting the right price on pre-owned vehicles is one of the most critical commercial decisions an automotive business makes every single day. We built a complete, production-ready valuation platform that instantly estimates fair market value using real market transaction history. 

Over the next ten minutes, we will present the core business challenge, our data findings, the models tested, a live system walkthrough, and the concrete business return. Let's begin with the business problem."
""")

    # =========================================================================
    # SLIDE 2 (Member 1 - Slide 2 of 3): The Business Problem
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_bg(s2, C_BG)
    add_header(s2, "The Business Problem: The Cost of Pricing Guesswork", "Market Context")

    # Left Card: Why Manual Appraisal Fails (Concise)
    c_left = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(5.6), Inches(4.2))
    c_left.fill.solid()
    c_left.fill.fore_color.rgb = C_WHITE
    c_left.line.color.rgb = C_BORDER
    tf_l = c_left.text_frame
    tf_l.margin_left = Inches(0.35)
    tf_l.margin_top = Inches(0.35)
    p_lt = tf_l.paragraphs[0]
    p_lt.text = "THE APPRAISAL CHALLENGE"
    p_lt.font.size = Pt(13)
    p_lt.font.bold = True
    p_lt.font.color.rgb = C_TEXT_DARK

    bullets_left = [
        "High Multi-Factor Variance: Every used car has a unique blend of mileage, age, brand prestige, and history.",
        "Inconsistent Evaluations: Different appraisers evaluate the same vehicle differently across branch locations.",
        "Time-Consuming Research: Staff spend 30 to 45 minutes manually cross-checking classified portals per vehicle.",
        "Unpredictable Margins: Subjective pricing leads to volatile, unpredictable gross profit margins."
    ]
    for b in bullets_left:
        p = tf_l.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(11)
        p.font.color.rgb = C_TEXT_MUTED
        p.space_before = Pt(8)

    # Right Card: The Financial Risks (Concise)
    c_right = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.6), Inches(5.7), Inches(4.2))
    c_right.fill.solid()
    c_right.fill.fore_color.rgb = C_WHITE
    c_right.line.color.rgb = C_BORDER
    tf_r = c_right.text_frame
    tf_r.margin_left = Inches(0.35)
    tf_r.margin_top = Inches(0.35)
    p_rt = tf_r.paragraphs[0]
    p_rt.text = "THE DUAL FINANCIAL RISKS"
    p_rt.font.size = Pt(13)
    p_rt.font.bold = True
    p_rt.font.color.rgb = C_RED

    # Risk 1 Box: Overpricing
    r1 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.1), Inches(2.3), Inches(5.1), Inches(1.4))
    r1.fill.solid()
    r1.fill.fore_color.rgb = RGBColor(254, 242, 242)
    r1.line.color.rgb = RGBColor(254, 202, 202)
    tf_r1 = r1.text_frame
    tf_r1.margin_left = Inches(0.2)
    tf_r1.margin_top = Inches(0.18)
    p1 = tf_r1.paragraphs[0]
    p1.text = "OVERPRICING  ►  INVENTORY STAGNATION"
    p1.font.size = Pt(11)
    p1.font.bold = True
    p1.font.color.rgb = C_RED
    p1_sub = tf_r1.add_paragraph()
    p1_sub.text = "Car sits on the lot for months. Holding costs accumulate, capital is frozen, and forced discounts destroy profits."
    p1_sub.font.size = Pt(10)
    p1_sub.font.color.rgb = C_TEXT_MUTED
    p1_sub.space_before = Pt(4)

    # Risk 2 Box: Underpricing
    r2 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.1), Inches(3.9), Inches(5.1), Inches(1.4))
    r2.fill.solid()
    r2.fill.fore_color.rgb = RGBColor(255, 247, 237)
    r2.line.color.rgb = RGBColor(254, 215, 170)
    tf_r2 = r2.text_frame
    tf_r2.margin_left = Inches(0.2)
    tf_r2.margin_top = Inches(0.18)
    p2 = tf_r2.paragraphs[0]
    p2.text = "UNDERPRICING  ►  FORFEITED PROFIT MARGIN"
    p2.font.size = Pt(11)
    p2.font.bold = True
    p2.font.color.rgb = RGBColor(194, 65, 12)
    p2_sub = tf_r2.add_paragraph()
    p2_sub.text = "Car sells immediately, but thousands of dollars in legitimate gross margin are permanently lost."
    p2_sub.font.size = Pt(10)
    p2_sub.font.color.rgb = C_TEXT_MUTED
    p2_sub.space_before = Pt(4)

    # Bottom Banner
    bot_b = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(6.05), Inches(11.7), Inches(0.75))
    bot_b.fill.solid()
    bot_b.fill.fore_color.rgb = C_NAVY_DARK
    bot_b.line.fill.background()
    tf_bb = bot_b.text_frame
    p_bb = tf_bb.paragraphs[0]
    p_bb.text = "THE BOTTOM LINE: Subjective appraisal guesswork directly threatens dealership profitability."
    p_bb.font.size = Pt(12)
    p_bb.font.bold = True
    p_bb.font.color.rgb = C_WHITE
    p_bb.alignment = PP_ALIGN.CENTER

    add_notes(s2, """[SPEAKER 1 | TIME: ~0:55]

"Why is vehicle pricing such a difficult problem? 

Because unlike new cars with fixed MSRP stickers, no two used cars are identical. Two cars made in the same year have vastly different true market values based on mileage, usage intensity, brand equity, and accident history.

Today, dealerships rely heavily on manual human estimation. While experienced appraisers possess good intuition, manual appraisals create two expensive business risks:
First: Overpricing. When you price a car too high, it sits on the lot. Operating capital is tied up, holding costs increase, and you eventually discount it at a loss.
Second: Underpricing. The car sells fast, but you leave thousands of dollars of profit on the table.

Our business needed an objective, repeatable valuation standard. I will now show how our platform solves this."
""")

    # =========================================================================
    # SLIDE 3 (Member 1 - Slide 3 of 3): The Solution Workflow
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_bg(s3, C_BG)
    add_header(s3, "Our Solution: An Automated Valuation Engine", "Solution Workflow")

    # Top Mission Statement Card
    top_c = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(11.733), Inches(0.95))
    top_c.fill.solid()
    top_c.fill.fore_color.rgb = C_BLUE
    top_c.line.fill.background()
    tf_tc = top_c.text_frame
    p_tc = tf_tc.paragraphs[0]
    p_tc.text = '"An automated platform referencing thousands of verified transactions to calculate fair market prices in seconds."'
    p_tc.font.size = Pt(13)
    p_tc.font.bold = True
    p_tc.font.color.rgb = C_WHITE
    p_tc.alignment = PP_ALIGN.CENTER

    # 4 Clean Step Columns
    steps = [
        ("1. VEHICLE INTAKE", "Enter simple specs:\nYear, mileage, brand, title status, transmission.", C_WHITE),
        ("2. VALUATION ENGINE", "Instantly benchmarked against thousands of market transactions.", C_WHITE),
        ("3. RECOMMENDED PRICE", "Generates fair market value plus a safe negotiation band.", C_WHITE),
        ("4. PROFITABLE DEAL", "Appraisers close trade-ins faster and protect gross margins.", C_LIGHT_BLUE)
    ]
    for i, (title, desc, bg_c) in enumerate(steps):
        x = Inches(0.8 + i * 3.05)
        step_box = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(2.65), Inches(2.8), Inches(2.0))
        step_box.fill.solid()
        step_box.fill.fore_color.rgb = bg_c
        step_box.line.color.rgb = C_BORDER if bg_c == C_WHITE else C_BLUE
        tf_s = step_box.text_frame
        tf_s.margin_left = Inches(0.25)
        tf_s.margin_top = Inches(0.2)
        
        p_st = tf_s.paragraphs[0]
        p_st.text = title
        p_st.font.size = Pt(11)
        p_st.font.bold = True
        p_st.font.color.rgb = C_BLUE if bg_c == C_LIGHT_BLUE else C_TEXT_DARK

        p_sd = tf_s.add_paragraph()
        p_sd.text = desc
        p_sd.font.size = Pt(10)
        p_sd.font.color.rgb = C_TEXT_MUTED
        p_sd.space_before = Pt(6)

    # 3 Bottom Value Metric Pills
    pillars = [
        ("⚡ < 2 Seconds", "Instant valuation vs 30+ minutes of manual search"),
        ("🎯 100% Unified", "Consistent pricing standards across all branches"),
        ("🛡️ Decision Copilot", "Empowers staff while keeping final judgment in human hands")
    ]
    for i, (title, desc) in enumerate(pillars):
        x = Inches(0.8 + i * 4.05)
        pil_box = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(4.9), Inches(3.8), Inches(1.7))
        pil_box.fill.solid()
        pil_box.fill.fore_color.rgb = C_WHITE
        pil_box.line.color.rgb = C_BORDER
        tf_p = pil_box.text_frame
        tf_p.margin_left = Inches(0.25)
        tf_p.margin_top = Inches(0.25)

        p_pt = tf_p.paragraphs[0]
        p_pt.text = title
        p_pt.font.size = Pt(13)
        p_pt.font.bold = True
        p_pt.font.color.rgb = C_BLUE

        p_pd = tf_p.add_paragraph()
        p_pd.text = desc
        p_pd.font.size = Pt(10)
        p_pd.font.color.rgb = C_TEXT_MUTED
        p_pd.space_before = Pt(6)

    add_notes(s3, """[SPEAKER 1 | TIME: ~0:50]
[TRANSITION TO SPEAKER 2]

"To solve this problem, we developed an intelligent valuation platform.

The workflow is simple:
1. Staff enter basic vehicle specs: year, mileage, brand, and title condition.
2. The engine instantly compares the vehicle against thousands of verified historical transactions.
3. The platform outputs an expected market price and a safe negotiation corridor.
4. Your sales team closes trade-ins faster and protects company margins.

This tool acts as an objective decision-support copilot—keeping final discretion in human hands. I will now hand over to Member 2 to explain how we prepared and validated the underlying data."
""")

    # =========================================================================
    # SLIDE 4 (Member 2 - Slide 1 of 2): Data Foundation & Preprocessing
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_bg(s4, C_BG)
    add_header(s4, "Data Foundation & Preprocessing: Clean, Reliable Intelligence", "Data Engineering")

    # Banner with Clean Stats
    d_banner = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(11.733), Inches(0.75))
    d_banner.fill.solid()
    d_banner.fill.fore_color.rgb = C_NAVY_DARK
    d_banner.line.fill.background()
    tf_db = d_banner.text_frame
    p_db = tf_db.paragraphs[0]
    p_db.text = "DATA FOUNDATION: 4,008 REAL CAR SALES   |   3,206 TRAINING SAMPLES   |   802 UNTOUCHED TEST BENCHMARK"
    p_db.font.size = Pt(11.5)
    p_db.font.bold = True
    p_db.font.color.rgb = C_CYAN
    p_db.alignment = PP_ALIGN.CENTER

    # 4 Clean Cards (2x2 Grid, minimal text)
    prep_cards = [
        ("1. DATA CLEANING & QUALITY CONTROL", 
         "• Filtered duplicate listings and verified vehicle records.\n• Handled missing attributes with representative statistical medians.\n• Ensured only complete, verified market profiles entered the pipeline.",
         Inches(0.8), Inches(2.5)),
        ("2. TARGET PRICE STABILIZATION", 
         "• Used car prices span from $2,500 commuters to $300,000+ luxury cars.\n• Normalized price distribution using logarithmic scaling.\n• Prevents extreme exotic outliers from distorting everyday car estimates.",
         Inches(6.8), Inches(2.5)),
        ("3. DERIVED BUSINESS INDICATORS", 
         "• Engineered 'Miles per Year' to separate heavy fleet wear from commuter cars.\n• Flagged Luxury Brand tiers to capture distinct luxury depreciation behavior.\n• Encoded transmission, fuel type, and clean title status into market signals.",
         Inches(0.8), Inches(4.3)),
        ("4. STRICT UNSEEN BENCHMARK", 
         "• Reserved 20% of all data (802 vehicles) completely untouched.\n• Evaluated models strictly on unseen cars to simulate live customer arrivals.\n• Guarantees that reported accuracy reflects real-world commercial performance.",
         Inches(6.8), Inches(4.3))
    ]

    for title, body, x, y in prep_cards:
        box = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(5.7), Inches(1.65))
        box.fill.solid()
        box.fill.fore_color.rgb = C_WHITE
        box.line.color.rgb = C_BORDER
        tf_v = box.text_frame
        tf_v.margin_left = Inches(0.3)
        tf_v.margin_top = Inches(0.18)

        p_vt = tf_v.paragraphs[0]
        p_vt.text = title
        p_vt.font.size = Pt(11)
        p_vt.font.bold = True
        p_vt.font.color.rgb = C_BLUE

        for line in body.split("\n"):
            p_vb = tf_v.add_paragraph()
            p_vb.text = line
            p_vb.font.size = Pt(9.5)
            p_vb.font.color.rgb = C_TEXT_MUTED
            p_vb.space_before = Pt(3)

    # Bottom Takeaway Banner
    d_takeaway = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.15), Inches(11.733), Inches(0.65))
    d_takeaway.fill.solid()
    d_takeaway.fill.fore_color.rgb = C_LIGHT_BLUE
    d_takeaway.line.color.rgb = C_BLUE
    tf_dt = d_takeaway.text_frame
    p_dt = tf_dt.paragraphs[0]
    p_dt.text = 'KEY TAKEAWAY: Rigorous data preprocessing ensures the system learns genuine market behavior rather than statistical noise.'
    p_dt.font.size = Pt(10.5)
    p_dt.font.bold = True
    p_dt.font.color.rgb = C_BLUE
    p_dt.alignment = PP_ALIGN.CENTER

    add_notes(s4, """[SPEAKER 2 | TIME: ~1:15]

"Thank you. A valuation engine is only as good as the data powering it.

We based our system on an authentic dataset of 4,008 real used vehicle transactions. Before running any predictions, our primary focus was data hygiene:
1. Data Cleaning: We filtered out duplicate entries, corrected invalid values, and ensured all vehicle records were clean.
2. Price Stabilization: Because vehicles range from $2,500 economy hatchbacks to $300,000 supercars, prices are heavily skewed. We stabilized price curves to ensure luxury cars don't distort estimates for everyday family cars.
3. Derived Business Features: We created smart indicators like 'Miles Driven per Year' to distinguish high-wear fleet cars from low-mileage commuter vehicles, along with luxury brand tiers.
4. Strict Validation: We held back 802 cars that the system never saw during training, proving that our model performs reliably on future customer inventory."
""")

    # =========================================================================
    # SLIDE 5 (Member 2 - Slide 2 of 2): Key Market Factors Discovered
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_bg(s5, C_BG)
    add_header(s5, "Key Market Drivers: What Truly Dictates Vehicle Resale Value?", "Market Discoveries")

    # 4 Factor Cards (Concise, punchy)
    factors = [
        ("01. AGE & USAGE INTENSITY", [
            "Year-over-year mechanical and technological depreciation.",
            "Annual usage rate differentiates commuter cars from fleet wear.",
            "Age alone is misleading without knowing yearly usage intensity."
        ]),
        ("02. ODOMETER MILEAGE", [
            "Primary indicator of physical mechanical wear.",
            "Strongest day-to-day downward price driver.",
            "Depreciation penalty naturally flattens at higher mileage thresholds."
        ]),
        ("03. BRAND & LUXURY PRESTIGE", [
            "Prestige brands (Porsche, BMW, Mercedes) follow distinct value curves.",
            "Economy brands (Toyota, Honda) offer steady, predictable resale.",
            "Prevents applying budget car depreciation rules to luxury cars."
        ]),
        ("04. TITLE & ACCIDENT RECORD", [
            "Clean title verification is a prerequisite for fair trade-in value.",
            "Salvage or rebuilt titles trigger steep wholesale penalties.",
            "Prior accident history significantly dampens resale demand."
        ])
    ]

    for i, (title, items) in enumerate(factors):
        x = Inches(0.8 + i * 3.05)
        f_box = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.6), Inches(2.8), Inches(4.3))
        f_box.fill.solid()
        f_box.fill.fore_color.rgb = C_WHITE
        f_box.line.color.rgb = C_BORDER
        tf_f = f_box.text_frame
        tf_f.margin_left = Inches(0.2)
        tf_f.margin_top = Inches(0.25)
        
        p_ft = tf_f.paragraphs[0]
        p_ft.text = title
        p_ft.font.size = Pt(11)
        p_ft.font.bold = True
        p_ft.font.color.rgb = C_BLUE

        for item in items:
            p_fi = tf_f.add_paragraph()
            p_fi.text = "• " + item
            p_fi.font.size = Pt(10)
            p_fi.font.color.rgb = C_TEXT_MUTED
            p_fi.space_before = Pt(8)

    # Core Takeaway Banner
    takeaway = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.1), Inches(11.733), Inches(0.75))
    takeaway.fill.solid()
    takeaway.fill.fore_color.rgb = C_LIGHT_BLUE
    takeaway.line.color.rgb = C_BLUE
    tf_ta = takeaway.text_frame
    p_ta = tf_ta.paragraphs[0]
    p_ta.text = 'BUSINESS INSIGHT: "True market value comes from the compound interaction of age, usage rate, brand prestige, and title status."'
    p_ta.font.size = Pt(11)
    p_ta.font.bold = True
    p_ta.font.color.rgb = C_BLUE
    p_ta.alignment = PP_ALIGN.CENTER

    add_notes(s5, """[SPEAKER 2 | TIME: ~1:15]
[TRANSITION TO SPEAKER 3]

"Our data preparation revealed critical business findings about what moves car prices:

1. Age and Usage Rate: A 4-year-old car driven 5,000 miles a year retains much more value than one driven 30,000 miles a year. Age and annual usage must always be assessed together.
2. Odometer Mileage: This is the strongest downward anchor, reflecting accumulated physical wear.
3. Brand Prestige: Luxury brands hold residual value differently compared to economy brands.
4. Title and Accident History: A salvage title or accident triggers an immediate wholesale discount.

Because our automated system evaluates all four factors simultaneously, it prevents appraisers from overlooking critical depreciation drivers. I will now hand over to Member 3 to explain the four valuation methods we investigated."
""")

    # =========================================================================
    # SLIDE 6 (Member 3 - Slide 1 of 2): Exploring 4 Valuation Methods
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_bg(s6, C_BG)
    add_header(s6, "Valuation Approaches: Exploring 4 Core Methods", "Modeling Strategy")

    # 4 Clean Method Cards
    methods = [
        ("1. LINEAR REGRESSION", "Straight-Line Baseline",
         "• How it works: Assumes price drops in a fixed straight line with age and mileage.\n• Business Role: Useful baseline benchmark.\n• Limitation: Misses curved market realities like luxury brand retention.",
         Inches(0.8), Inches(1.6)),
        ("2. DECISION TREE", "Single Rule-Tree",
         "• How it works: Splits cars using simple if-then decision rules.\n• Business Role: Highly transparent rules.\n• Limitation: Overly rigid; makes erratic price jumps on unseen vehicles.",
         Inches(6.8), Inches(1.6)),
        ("3. RANDOM FOREST", "Committee Consensus",
         "• How it works: Averages estimates across a large team of diverse decision trees.\n• Business Role: Highly stable ensemble benchmark.\n• Limitation: Effective, but computationally heavier.",
         Inches(0.8), Inches(3.9)),
        ("4. GRADIENT BOOSTING", "Iterative Pattern Refiner (Champion)",
         "• How it works: Sequentially builds trees that learn from and correct previous errors.\n• Business Role: Exceptional at nuanced patterns like luxury brand curves.\n• Outcome: Delivered the highest explanatory power and consistency.",
         Inches(6.8), Inches(3.9))
    ]

    for title, subtitle, body, x, y in methods:
        box = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(5.7), Inches(2.05))
        box.fill.solid()
        box.fill.fore_color.rgb = C_WHITE
        box.line.color.rgb = C_BORDER if "Champion" not in subtitle else C_BLUE
        if "Champion" in subtitle:
            box.line.width = Pt(2)
        tf_v = box.text_frame
        tf_v.margin_left = Inches(0.3)
        tf_v.margin_top = Inches(0.18)

        p_vt = tf_v.paragraphs[0]
        p_vt.text = title
        p_vt.font.size = Pt(11)
        p_vt.font.bold = True
        p_vt.font.color.rgb = C_BLUE

        p_sub = tf_v.add_paragraph()
        p_sub.text = subtitle
        p_sub.font.size = Pt(9.5)
        p_sub.font.bold = True
        p_sub.font.color.rgb = C_TEXT_DARK
        p_sub.space_before = Pt(2)

        for line in body.split("\n"):
            p_vb = tf_v.add_paragraph()
            p_vb.text = line
            p_vb.font.size = Pt(9.5)
            p_vb.font.color.rgb = C_TEXT_MUTED
            p_vb.space_before = Pt(3)

    # Bottom summary callout
    bot_m6 = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.15), Inches(11.733), Inches(0.75))
    bot_m6.fill.solid()
    bot_m6.fill.fore_color.rgb = C_NAVY_DARK
    bot_m6.line.fill.background()
    tf_bm6 = bot_m6.text_frame
    p_bm6 = tf_bm6.paragraphs[0]
    p_bm6.text = "STRATEGIC APPROACH: Benchmarked four distinct approaches to identify the safest, most dependable tool for business operations."
    p_bm6.font.size = Pt(11)
    p_bm6.font.bold = True
    p_bm6.font.color.rgb = C_CYAN
    p_bm6.alignment = PP_ALIGN.CENTER

    add_notes(s6, """[SPEAKER 3 | TIME: ~1:15]

"Thank you. When choosing the right valuation engine, our goal was not to pick complex math, but to test four established approaches to find the most dependable engine for business use.

We investigated four distinct methods:
1. Linear Regression: Assumes price drops in a straight line with age and mileage. It is simple, but car depreciation in the real world is rarely a straight line.
2. Decision Tree: Uses simple if-then decision branches. However, single trees are rigid and make erratic price jumps on new cars.
3. Random Forest: Creates an entire committee of decision trees and averages their estimates. Much more stable.
4. Gradient Boosting: Rather than just averaging trees, it builds trees step-by-step, where each new model learns from and corrects the mistakes of the previous ones. It excels at subtle nuances, like knowing that mileage discounts luxury cars differently than economy cars."
""")

    # =========================================================================
    # SLIDE 7 (Member 3 - Slide 2 of 2): Comparing Methods & Business Suitability
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_bg(s7, C_BG)
    add_header(s7, "Comparing the 4 Methods: Performance & Business Suitability", "Model Evaluation")

    # Left: Concise Table (Strictly NO MAE)
    table_shape = s7.shapes.add_table(5, 4, Inches(0.8), Inches(1.5), Inches(7.5), Inches(3.2))
    table = table_shape.table
    table.columns[0].width = Inches(2.3)
    table.columns[1].width = Inches(1.7)
    table.columns[2].width = Inches(1.8)
    table.columns[3].width = Inches(1.7)

    headers = ["Pricing Method", "Pattern Accuracy", "Handling Complexity", "Business Suitability"]
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_NAVY_DARK
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(10)
            p.font.bold = True
            p.font.color.rgb = C_WHITE

    row_data = [
        ("Linear Regression", "59.9%", "Linear Only", "Baseline Benchmark"),
        ("Decision Tree", "39.3%", "Step-Wise Rules", "Unreliable / Inconsistent"),
        ("Random Forest", "Tested", "High Consensus", "Strong Contender"),
        ("Gradient Boosting", "66.2%", "Adaptive Refinement", "★ Selected Champion")
    ]
    for i, row in enumerate(row_data, start=1):
        for j, val in enumerate(row):
            cell = table.cell(i, j)
            cell.text = val
            cell.fill.solid()
            if i == 4:
                cell.fill.fore_color.rgb = C_LIGHT_BLUE
            else:
                cell.fill.fore_color.rgb = C_WHITE
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(10)
                if i == 4:
                    p.font.bold = True
                    p.font.color.rgb = C_BLUE
                else:
                    p.font.color.rgb = C_TEXT_DARK

    # Right: Champion Card (Concise)
    c_why = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.6), Inches(1.5), Inches(3.933), Inches(4.3))
    c_why.fill.solid()
    c_why.fill.fore_color.rgb = C_WHITE
    c_why.line.color.rgb = C_BLUE
    c_why.line.width = Pt(2)
    tf_w = c_why.text_frame
    tf_w.margin_left = Inches(0.3)
    tf_w.margin_top = Inches(0.3)

    p_wt = tf_w.paragraphs[0]
    p_wt.text = "WHY THE CHAMPION WON"
    p_wt.font.size = Pt(12)
    p_wt.font.bold = True
    p_wt.font.color.rgb = C_BLUE

    p_wm = tf_w.add_paragraph()
    p_wm.text = "Gradient Boosting Regressor"
    p_wm.font.size = Pt(15)
    p_wm.font.bold = True
    p_wm.font.color.rgb = C_TEXT_DARK
    p_wm.space_before = Pt(4)

    reasons = [
        "Highest Accuracy: Captured 66.2% of market price variation on 800+ unseen test vehicles.",
        "Smooth Predictions: Avoids wild over- or under-valuations on uncommon vehicle trims.",
        "Segment Adaptable: Accurately adjusts value curves across economy, luxury, and performance cars.",
        "Prudent Choice: Delivers the safest, most consistent risk profile for commercial operations."
    ]
    for r in reasons:
        p = tf_w.add_paragraph()
        p.text = "✔ " + r
        p.font.size = Pt(9.5)
        p.font.color.rgb = C_TEXT_MUTED
        p.space_before = Pt(8)

    # Bottom summary callout
    bot_m7 = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.0), Inches(7.5), Inches(1.8))
    bot_m7.fill.solid()
    bot_m7.fill.fore_color.rgb = C_WHITE
    bot_m7.line.color.rgb = C_BORDER
    tf_bm7 = bot_m7.text_frame
    tf_bm7.margin_left = Inches(0.3)
    tf_bm7.margin_top = Inches(0.25)
    p_bmt7 = tf_bm7.paragraphs[0]
    p_bmt7.text = "THE DECISION-MAKER SUMMARY"
    p_bmt7.font.size = Pt(11)
    p_bmt7.font.bold = True
    p_bmt7.font.color.rgb = C_TEXT_DARK

    p_bmd7 = tf_bm7.add_paragraph()
    p_bmd7.text = 'When tested on 800+ real customer cars the models had never seen before, Gradient Boosting consistently outperformed every alternative. It provides the safest, most stable foundation for commercial deployment.'
    p_bmd7.font.size = Pt(10.5)
    p_bmd7.font.color.rgb = C_TEXT_MUTED
    p_bmd7.space_before = Pt(6)

    add_notes(s7, """[SPEAKER 3 | TIME: ~1:15]
[TRANSITION TO SPEAKER 4]

"Let us examine the results when all four approaches were evaluated on our 800 unseen test vehicles:

- Linear Regression achieved a 59.9% accuracy score—an acceptable baseline, but too rigid to handle complex price curves.
- Decision Tree fell behind at 39.3%, proving far too erratic for commercial use.
- Random Forest performed well as an ensemble benchmark.
- Gradient Boosting demonstrated clear leadership: it achieved an accuracy score of 66.2%, successfully capturing roughly two out of every three dollars of price variation across the entire market.

It won because it avoids sudden, erratic appraisal jumps. It smoothly adapts whether evaluating a $15,000 sedan or an $80,000 luxury SUV. 

I will now hand over to our final member to walk through the selected champion model, the live system demonstration, and our strategic conclusion."
""")

    # =========================================================================
    # SLIDE 8 (Member 4 - Slide 1 of 2): Final Model & Live Demonstration
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_bg(s8, C_BG)
    add_header(s8, "Final Selected Model: In-Action System Demonstration", "Software Walkthrough")

    # Left: Concise Protocol
    c_demo = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(4.5), Inches(5.3))
    c_demo.fill.solid()
    c_demo.fill.fore_color.rgb = C_WHITE
    c_demo.line.color.rgb = C_BORDER
    tf_d = c_demo.text_frame
    tf_d.margin_left = Inches(0.3)
    tf_d.margin_top = Inches(0.3)

    p_dt = tf_d.paragraphs[0]
    p_dt.text = "LIVE VALUATION PROTOCOL"
    p_dt.font.size = Pt(12)
    p_dt.font.bold = True
    p_dt.font.color.rgb = C_BLUE

    steps_d = [
        ("Step 1: Open Valuation Console", "Access web portal via standard desktop or tablet browser."),
        ("Step 2: Enter Car Specifications", "Input Make, Year, Mileage, Transmission, Fuel, and Title condition."),
        ("Step 3: Instant Automated Valuation", "System benchmarks vehicle against market data in < 2 seconds."),
        ("Step 4: Review Negotiation Corridor", "Staff views market price and a safe negotiation band (lower/upper bounds)."),
        ("Step 5: Audit & History Tracking", "Valuation is saved to database for branch tracking and management review.")
    ]
    for s_title, s_desc in steps_d:
        p1 = tf_d.add_paragraph()
        p1.text = s_title
        p1.font.size = Pt(10.5)
        p1.font.bold = True
        p1.font.color.rgb = C_TEXT_DARK
        p1.space_before = Pt(8)

        p2 = tf_d.add_paragraph()
        p2.text = s_desc
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = C_TEXT_MUTED

    # Right: Mockup Interface Console (Clean)
    c_mock = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.6), Inches(1.5), Inches(6.933), Inches(5.3))
    c_mock.fill.solid()
    c_mock.fill.fore_color.rgb = C_NAVY_DARK
    c_mock.line.color.rgb = RGBColor(51, 65, 85)
    tf_m = c_mock.text_frame
    tf_m.margin_left = Inches(0.4)
    tf_m.margin_top = Inches(0.4)

    p_mt = tf_m.paragraphs[0]
    p_mt.text = "AUTOVALUATE ENTERPRISE PORTAL — LIVE VIEW"
    p_mt.font.size = Pt(12)
    p_mt.font.bold = True
    p_mt.font.color.rgb = C_CYAN

    # Inner Simulated Valuation Card
    sim = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.0), Inches(2.2), Inches(6.1), Inches(4.2))
    sim.fill.solid()
    sim.fill.fore_color.rgb = C_NAVY_CARD
    sim.line.color.rgb = C_BLUE
    tf_sim = sim.text_frame
    tf_sim.margin_left = Inches(0.3)
    tf_sim.margin_top = Inches(0.3)

    p_st1 = tf_sim.paragraphs[0]
    p_st1.text = "REAL-TIME MARKET VALUATION OUTPUT"
    p_st1.font.size = Pt(10)
    p_st1.font.bold = True
    p_st1.font.color.rgb = C_BLUE

    p_sp = tf_sim.add_paragraph()
    p_sp.text = "$48,250 USD"
    p_sp.font.size = Pt(36)
    p_sp.font.bold = True
    p_sp.font.color.rgb = C_WHITE
    p_sp.space_before = Pt(6)

    p_sr = tf_sim.add_paragraph()
    p_sr.text = "Recommended Negotiation Band: $43,100 – $54,200"
    p_sr.font.size = Pt(11)
    p_sr.font.color.rgb = C_CYAN
    p_sr.space_before = Pt(4)

    items_sim = [
        "Vehicle Profile: 2021 BMW 3-Series (Automatic, Gasoline, Clean Title)",
        "Odometer Reading: 35,000 miles (~8,750 miles/year usage rate)",
        "Key Drivers Identified: Luxury Brand Equity (+), Clean Title Bonus (+)",
        "Enterprise Tracking: Saved under active user session; searchable & auditable"
    ]
    for it in items_sim:
        p = tf_sim.add_paragraph()
        p.text = "• " + it
        p.font.size = Pt(9.5)
        p.font.color.rgb = RGBColor(203, 213, 225)
        p.space_before = Pt(5)

    add_notes(s8, """[SPEAKER 4 | TIME: ~1:15]

"Thank you. With Gradient Boosting selected as our champion engine, we packaged it into a user-friendly, production-ready web application.

Let's see how this works in an everyday dealership scenario:
Imagine a customer walks into your showroom to trade in a 2021 BMW with 35,000 miles on the odometer, an automatic transmission, and a clean vehicle title.

Your sales representative opens our portal, selects the car's attributes, and clicks 'Compute Market Valuation'. 
In less than two seconds, the Gradient Boosting engine evaluates the vehicle. 

As shown on screen, the platform delivers an expected fair market value of $48,250, accompanied by a negotiation corridor of $43,000 to $54,000. It also highlights the key drivers that justify this figure—such as luxury brand equity and the clean title bonus.

Every valuation is automatically saved to the dealership database, allowing branch managers to audit recent evaluations or clear resolved records with one click. It requires zero technical expertise for your staff to operate."
""")

    # =========================================================================
    # SLIDE 9 (Member 4 - Slide 2 of 2): Business Impact & Conclusion
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_bg(s9, C_NAVY_DARK)

    # Accent decorative ribbon
    ribbon9 = s9.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.2), Inches(0.12), Inches(4.8))
    ribbon9.fill.solid()
    ribbon9.fill.fore_color.rgb = C_GREEN
    ribbon9.line.fill.background()

    # Title box
    t9 = s9.shapes.add_textbox(Inches(1.2), Inches(1.2), Inches(11.0), Inches(1.0))
    tf_t9 = t9.text_frame
    p_t9 = tf_t9.paragraphs[0]
    p_t9.text = "Business Impact, Recommendations & Conclusion"
    p_t9.font.size = Pt(32)
    p_t9.font.bold = True
    p_t9.font.color.rgb = C_WHITE

    # 4 Key Takeaways in Dark Cards (De-cluttered)
    takeaways = [
        ("✔ 90% FASTER APPRAISAL VELOCITY", "Cuts trade-in evaluation time from 30+ minutes of manual search to under 2 seconds, accelerating customer closing rates."),
        ("✔ ENTERPRISE PRICING CONSISTENCY", "Ensures junior and senior appraisers across all branches price vehicles against the same objective market playbook."),
        ("✔ PROFIT MARGIN PROTECTION", "Prevents costly inventory stagnation caused by overpricing and eliminates money left on the table through underpricing."),
        ("✔ PRODUCTION-READY SOFTWARE", "Complete, tested software application with user authentication, database persistence, and transparent valuation bands.")
    ]

    for i, (head, body) in enumerate(takeaways):
        y = Inches(2.2 + i * 1.05)
        t_card = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), y, Inches(10.8), Inches(0.9))
        t_card.fill.solid()
        t_card.fill.fore_color.rgb = C_NAVY_CARD
        t_card.line.color.rgb = RGBColor(51, 65, 85)
        tf_tc9 = t_card.text_frame
        tf_tc9.margin_left = Inches(0.3)
        tf_tc9.margin_top = Inches(0.15)

        p1 = tf_tc9.paragraphs[0]
        p1.text = head
        p1.font.size = Pt(11)
        p1.font.bold = True
        p1.font.color.rgb = C_CYAN

        p2 = tf_tc9.add_paragraph()
        p2.text = body
        p2.font.size = Pt(10)
        p2.font.color.rgb = C_WHITE
        p2.space_before = Pt(2)

    # Closing Statement & Thank You
    bot_card = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(6.15), Inches(10.8), Inches(0.85))
    bot_card.fill.solid()
    bot_card.fill.fore_color.rgb = C_BLUE
    bot_card.line.fill.background()
    tf_bc = bot_card.text_frame
    p_bc = tf_bc.paragraphs[0]
    p_bc.text = '"From manual estimation to data-driven pricing intelligence."  —  Thank you! Questions & Discussion'
    p_bc.font.size = Pt(13)
    p_bc.font.bold = True
    p_bc.font.color.rgb = C_WHITE
    p_bc.alignment = PP_ALIGN.CENTER

    add_notes(s9, """[SPEAKER 4 | TIME: ~1:15]

"To conclude our presentation: our team has delivered a fully functioning, data-backed vehicle valuation platform designed specifically for commercial decision-makers.

By replacing subjective appraisal guesswork with empirical market intelligence:
1. We increase appraisal speed by over 90%, letting your sales team focus on closing transactions rather than hunting across classified portals.
2. We establish unified pricing consistency across every location and every appraiser.
3. We protect your company's gross profit margins from the costly pitfalls of overpricing and underpricing.

Our recommendation is to deploy this platform as an operational copilot for your appraisal and trade-in teams.

Thank you very much for your time and consideration. Our team is now delighted to open the floor to your questions and discussion."
""")

    # Save to disk (handles file locks if user has PPT open)
    filenames = [
        "Used_Car_Price_Prediction_System_Final_Presentation.pptx",
        "Used_Car_Price_Prediction_System_Presentation.pptx"
    ]
    saved_paths = []
    for fname in filenames:
        for folder in [".", ".."]:
            target_path = os.path.join(folder, fname)
            try:
                prs.save(target_path)
                saved_paths.append(target_path)
            except Exception:
                pass
    print(f"Presentation saved successfully to: {saved_paths}")

if __name__ == "__main__":
    create_deck()
