
import io
import textwrap
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from google import genai
from concurrent.futures import ThreadPoolExecutor

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
    request = st.text_area(
        "What would you like AdAgent to help you market?",
        placeholder=(
            "Example: Promote my handmade jewellery business "
            "on Instagram, launch my college fest, advertise a "
            "food delivery app, promote a coaching service, or "
            "create a campaign for a new product."
        ),
        height=130
    )

    col1, col2 = st.columns(2)

    with col1:
        audience = st.text_input(
            "Target audience (optional)",
            placeholder="e.g. college students, working professionals"
        )

        goal = st.selectbox(
            "Campaign goal",
            [
                "Brand awareness",
                "Website traffic",
                "Sales or enquiries",
                "Product or service launch",
                "Event registrations",
                "App downloads",
                "Engagement",
                "Other"
            ]
        )

    with col2:
        budget = st.number_input(
            "Total budget (₹)",
            min_value=0,
            max_value=10000000,
            value=5000,
            step=500
        )

        platforms = st.multiselect(
            "Marketing channels (optional)",
            [
                "Instagram",
                "YouTube",
                "LinkedIn",
                "Facebook",
                "WhatsApp",
                "Email",
                "Website",
                "Other"
            ],
            default=["Instagram"]
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
        input=prompt,
        timeout=30
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
    if not request.strip():
        st.error(
            "Describe what you want AdAgent to help you market."
        )
    elif not api_key.strip():
        st.error(
            "Enter your Gemini API key in the sidebar to generate "
            "a real AI campaign."
        )
    else:
        audience_text = audience.strip() or "Not specified"
        platform_text = ", ".join(platforms) if platforms else "Recommend suitable channels"

        context = f"""
USER'S MARKETING REQUEST:
{request}

CAMPAIGN GOAL:
{goal}

TARGET AUDIENCE:
{audience_text}

TOTAL BUDGET IN INR:
₹{budget}

PREFERRED MARKETING CHANNELS:
{platform_text}

IMPORTANT INSTRUCTIONS:
- Adapt the campaign to the user's actual request.
- Support products, services, businesses, events, apps,
  personal brands, educational services and other legitimate
  marketing needs.
- Do not assume the request is about EcoSip or any particular
  brand unless the user explicitly says so.
- Do not invent product features, prices, discounts, testimonials,
  certifications, performance results or business claims.
- If important details are missing, state reasonable assumptions
  clearly instead of presenting them as verified facts.
- Make recommendations practical for the specified budget.
"""

        try:
            def run_agent(role, instructions):
                agent_client = genai.Client(api_key=api_key)
                return ask_agent(
                    agent_client,
                    role,
                    instructions,
                    context
                )

            with st.spinner(
                "All three AI agents are working simultaneously..."
            ):
                with ThreadPoolExecutor(max_workers=3) as executor:
                    creative_future = executor.submit(
                        run_agent,
                        "Creative Agent",
                        """
                        Create a concise marketing campaign for the user's
                        request. Include a campaign idea, three headlines,
                        two captions, calls to action, and a poster
                        headline and tagline. Adapt to the actual product,
                        service, event, app or business. Never invent
                        factual claims.
                        """
                    )

                    strategy_future = executor.submit(
                        run_agent,
                        "Marketing Strategy Agent",
                        """
                        Create a practical marketing plan with suitable
                        channels, target audience, a seven-day posting
                        calendar, budget allocation and three
                        recommendations. Ensure the budget allocation
                        matches the supplied budget. For zero budget,
                        recommend free promotional methods. Treat
                        suggested posting times as estimates.
                        """
                    )

                    optimization_future = executor.submit(
                        run_agent,
                        "Performance and Optimization Agent",
                        """
                        Create a measurement plan with three relevant
                        metrics, how to measure them, two improvement
                        experiments and a weekly review plan. Adapt
                        metrics to the campaign goal. Label example
                        numbers as simulated. Do not claim access to
                        real campaign data.
                        """
                    )

                    creative = creative_future.result()
                    strategy = strategy_future.result()
                    optimization = optimization_future.result()

            st.session_state["campaign"] = {
                "product": request,
                "creative": creative,
                "strategy": strategy,
                "optimization": optimization,
                "context": context
            }

            st.success(
                "Your three-agent marketing campaign is ready!"
            )

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
        st.subheader("Campaign Poster")

        campaign = st.session_state.get("campaign")

        if not campaign:
            st.info(
                "Generate a campaign first to create its poster."
            )
        else:
            poster_context = campaign.get("context", "")
            creative_text = campaign.get("creative", "")

            st.write(
                "Create poster content tailored to your campaign."
            )

            if st.button("✨ Generate Poster Content"):
                if not api_key.strip():
                    st.error("Enter your Gemini API key in the sidebar.")
                else:
                    try:
                        client = genai.Client(api_key=api_key)

                        with st.spinner(
                            "Creating your poster content..."
                        ):
                            poster_content = ask_agent(
                                client,
                                "Marketing Poster Designer",
                                """
                                Design the content and visual layout
                                for a promotional poster.

                                Return:
                                1. A short, attention-grabbing headline.
                                2. A supporting tagline.
                                3. Three short supporting points.
                                4. A clear call to action.
                                5. A visual concept, including suggested
                                   colors, imagery and layout.

                                Adapt everything to the user's actual
                                campaign. Do not assume it is EcoSip.
                                Never invent dates, prices, prizes,
                                features or other factual details.
                                Use placeholders for missing information.

                                Return a polished, easy-to-read design
                                brief. Do not claim this is an actual
                                rendered image.
                                """,
                                poster_context
                                + "\nCAMPAIGN CREATIVE:\n"
                                + creative_text
                            )

                        st.session_state["poster_content"] = (
                            poster_content
                        )

                    except Exception as error:
                        st.error("Poster content generation failed.")
                        st.code(
                            f"{type(error).__name__}: {error}"
                        )

            poster_content = st.session_state.get(
                "poster_content"
            )

            if poster_content:
                st.markdown(poster_content)

                st.download_button(
                    "Download poster content (.txt)",
                    data=poster_content,
                    file_name="adagent_poster_content.txt",
                    mime="text/plain"
                )

st.divider()
st.caption(
    "Aivora AdAgent | AI-generated recommendations. "
    "Publishing integrations and live analytics are not yet connected."
)
