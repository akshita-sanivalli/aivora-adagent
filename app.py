
import io
import textwrap
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from google import genai

st.set_page_config(page_title="Aivora | AdAgent", page_icon="🚀", layout="wide")

st.title("🚀 Aivora AdAgent")
st.caption("Your AI-powered end-to-end marketing campaign engine")

with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input(
        "Gemini API key",
        type="password",
        help="Your key is used for this session. Never share it publicly."
    )
    st.caption("AI calls require a valid API key and internet access.")

    st.divider()
    st.markdown("**Your AI agents**")
    st.write("✍️ Creative Agent")
    st.write("🎯 Strategy Agent")
    st.write("📊 Optimization Agent")

st.subheader("1. Describe your campaign")

with st.form("campaign_form"):
    product = st.text_input(
        "Product or brand",
        placeholder="e.g. EcoSip reusable water bottles"
    )
    description = st.text_area(
        "What are you promoting?",
        placeholder="Describe the product, its benefits and what makes it different."
    )

    col1, col2 = st.columns(2)
    with col1:
        audience = st.text_input(
            "Target audience",
            "College students aged 18–25"
        )
        goal = st.selectbox(
            "Campaign goal",
            ["Brand awareness", "Website traffic", "Sales",
             "Product launch", "Engagement"]
        )
    with col2:
        budget = st.number_input(
            "Total budget (₹)",
            min_value=500,
            max_value=10000000,
            value=5000,
            step=500
        )
        platforms = st.multiselect(
            "Marketing channels",
            ["Instagram", "YouTube", "LinkedIn", "Facebook"],
            default=["Instagram", "YouTube"]
        )

    submitted = st.form_submit_button(
        "✨ Generate my campaign",
        type="primary",
        use_container_width=True
    )


def ask_agent(client, role, instructions, context):
    prompt = f"""
You are the {role} in AdAgent, an AI marketing system.

YOUR RESPONSIBILITY:
{instructions}

CAMPAIGN INFORMATION:
{context}

IMPORTANT RULES:
1. Use only product facts explicitly provided by the user.
2. Never invent product features, materials, certifications,
   prices, discounts, guarantees, customer reviews, or test results.
3. If important information is missing, do not guess.
4. Clearly identify assumptions and estimates.
5. Keep the output practical, specific, and easy to understand.
6. Make recommendations appropriate to the stated target audience.
7. Do not claim that an advertisement was published.
8. Do not claim that real campaign metrics were collected.
9. If metrics are provided as simulated data, treat them as examples,
   not verified real-world results.

Give a useful response appropriate to your assigned agent role.
"""

    interaction = client.interactions.create(
        model="gemini-3.8-flash",
        input=prompt
    )

    return interaction.output_text or "The agent returned an empty response."


def make_poster(product_name, tagline):
    image = Image.new("RGB", (1080, 1080), "#172554")
    draw = ImageDraw.Draw(image)

    # Decorative shapes
    draw.ellipse((700, -120, 1200, 380), fill="#7c3aed")
    draw.ellipse((-180, 700, 350, 1230), fill="#0891b2")
    draw.rounded_rectangle(
        (70, 70, 1010, 1010),
        radius=38,
        outline="#c4b5fd",
        width=4
    )

    try:
        title_font = ImageFont.truetype("arial.ttf", 76)
        body_font = ImageFont.truetype("arial.ttf", 38)
        small_font = ImageFont.truetype("arial.ttf", 28)
    except OSError:
        title_font = ImageFont.load_default()
        body_font = title_font
        small_font = title_font

    draw.text((105, 125), "INTRODUCING", font=small_font, fill="#a5f3fc")

    title_lines = textwrap.wrap(product_name.upper(), width=18)[:3]
    y = 270
    for line in title_lines:
        draw.text((100, y), line, font=title_font, fill="white")
        y += 100

    tagline_lines = textwrap.wrap(tagline, width=38)[:4]
    y += 35
    for line in tagline_lines:
        draw.text((105, y), line, font=body_font, fill="#ddd6fe")
        y += 55

    draw.rounded_rectangle(
        (105, 820, 490, 905),
        radius=22,
        fill="#7c3aed"
    )
    draw.text((145, 840), "DISCOVER MORE", font=small_font, fill="white")
    draw.text(
        (105, 950),
        "AI-GENERATED CONCEPT • AIVORA",
        font=small_font,
        fill="#a5f3fc"
    )

    output = io.BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


if submitted:
    if not product.strip() or not description.strip():
        st.error("Enter your product name and description first.")
    elif not api_key.strip():
        st.error(
            "Enter your Gemini API key in the sidebar to generate "
            "a real AI campaign."
        )
    elif not platforms:
        st.error("Select at least one marketing channel.")
    else:
        context = f"""
Product: {product}
Description: {description}
Target audience: {audience}
Campaign goal: {goal}
Budget in INR: {budget}
Selected platforms: {", ".join(platforms)}
"""

        try:
            client = genai.Client(api_key=api_key)

            with st.spinner("Agent 1 is creating your campaign..."):
                creative = ask_agent(
                    client,
                    "Creative Agent",
                    "Create platform-specific ad headlines, captions, "
                    "calls to action and a short poster tagline. "
                    "Label each platform's content clearly.",
                    context
                )

            with st.spinner("Agent 2 is planning distribution..."):
                strategy = ask_agent(
                    client,
                    "Strategy and Scheduling Agent",
                    "Use the creative campaign as input. Recommend "
                    "channel allocation, audience fit, a 7-day posting "
                    "calendar with suggested local times, and a budget "
                    "split totalling the supplied budget. Explain that "
                    "timing suggestions are hypotheses, not measured "
                    "audience peak times.",
                    context + "\nCreative Agent output:\n" + creative
                )

            with st.spinner("Agent 3 is preparing optimization..."):
                optimization = ask_agent(
                    client,
                    "Performance and Optimization Agent",
                    "Prepare a measurement plan for impressions, clicks, "
                    "CTR, engagement and comment sentiment. Give an "
                    "example of how you would optimize a campaign. "
                    "Clearly label all sample metrics as simulated; "
                    "no actual campaign data is available yet.",
                    context + "\nCreative output:\n" + creative
                    + "\nStrategy output:\n" + strategy
                )

            st.session_state["campaign"] = {
                "product": product,
                "creative": creative,
                "strategy": strategy,
                "optimization": optimization,
                "context": context
            }
            st.success("Your three-agent campaign workflow completed!")

        except Exception as error:
            st.error("The AI request failed.")
            st.code(f"{type(error).__name__}: {error}")


campaign = st.session_state.get("campaign")


if campaign:
    st.divider()
    st.subheader(f"2. Your campaign: {campaign['product']}")

    tab1, tab2, tab3, tab4 = st.tabs([
        "✍️ Creative",
        "🎯 Strategy",
        "📊 Analytics",
        "🖼️ Poster"
    ])

    with tab1:
        st.markdown(campaign["creative"])
        st.download_button(
            "Download creative copy",
            campaign["creative"],
            file_name="adagent_creative.txt"
        )

    with tab2:
        st.markdown(campaign["strategy"])
        st.download_button(
            "Download campaign plan",
            campaign["strategy"],
            file_name="adagent_strategy.txt"
        )

    with tab3:
        st.warning(
            "DEMO DATA ONLY — these are simulated figures, "
            "not results from real published advertisements."
        )

        st.markdown("### Campaign Performance Simulator")

        impressions = st.number_input(
            "Impressions",
            min_value=0,
            max_value=10000000,
            value=12400,
            step=100
        )

        clicks = st.number_input(
            "Clicks",
            min_value=0,
            max_value=10000000,
            value=620,
            step=10
        )

        engagements = st.number_input(
            "Engagements",
            min_value=0,
            max_value=10000000,
            value=595,
            step=10
        )

        ctr = (clicks / impressions * 100) if impressions else 0
        engagement_rate = (
            engagements / impressions * 100
            if impressions else 0
        )

        a, b, c, d = st.columns(4)
        a.metric("Impressions", f"{impressions:,}")
        b.metric("Clicks", f"{clicks:,}")
        c.metric("CTR", f"{ctr:.2f}%")
        d.metric("Engagement rate", f"{engagement_rate:.2f}%")

        st.markdown("### Optimization Agent")

        if impressions == 0:
            st.info("Add impressions to analyse campaign performance.")
        elif clicks == 0:
            st.info(
                "No clicks in this simulated example. "
                "Test a clearer call to action and a more relevant audience."
            )
        elif ctr < 2:
            st.info(
                "Simulated CTR is below 2%. Test different headlines, "
                "creative designs, and audience targeting."
            )
        else:
            st.success(
                "Simulated CTR is at least 2%. Compare alternative "
                "creatives to see whether performance can improve further."
            )

        st.caption(
            "CTR = clicks divided by impressions × 100. "
            "Recommendations use illustrative thresholds, not "
            "industry-wide benchmarks."
        )

    with tab4:
        poster_path = "ecosip_poster.png"

        try:
            with open(poster_path, "rb") as file:
                poster = file.read()

            st.image(
                poster,
                caption="EcoSip promotional poster concept",
                use_container_width=True
            )

            st.download_button(
                "Download campaign poster (PNG)",
                data=poster,
                file_name="adagent_poster.png",
                mime="image/png"
            )

        except FileNotFoundError:
            st.warning(
                "Poster file not found. Place ecosip_poster.png "
                "in the same folder as app.py."
            )

st.divider()
st.caption(
    "Aivora AdAgent | AI-generated recommendations. "
    "Publishing integrations and live analytics are not yet connected."
)
