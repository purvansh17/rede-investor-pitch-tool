import streamlit as st
from google import genai
from google.genai import types

# Set GEMINI_API_KEY in the environment before starting Streamlit.
client = genai.Client(api_key="AQ.Ab8RN6LR56EGrbYD2-J_utcq41EzD0sVOq_sO5xldGebUF92HA")


st.set_page_config(page_title="NYU REDE - Deal Screener", layout="centered")

st.title("🏢 REDE : Deal Screener")
st.markdown("Submit your preliminary deal metrics below. The AI will audit your math, check for syllabus rule violations, and prepare you for LP pushback.")

# --- THE FORM ---
with st.form("deal_form"):
    st.subheader("1. Property Details")
    col1, col2 = st.columns(2)
    address = col1.text_input("Property Address (City, State)", value="Astoria, NY")
    prop_type = col2.selectbox("Property Type", ["Residential (Multifamily)", "Office", "Retail", "Industrial"])
    year_built = st.number_input("Year Built", min_value=1800, max_value=2026, value=1931)

    st.subheader("2. Deal Financials")
    col3, col4 = st.columns(2)
    purchase_price = col3.number_input("Purchase Price ($)", min_value=0, value=2995000)
    reno_cost = col4.number_input("Renovation/CapEx Cost ($)", min_value=0, value=320000)
    year_1_noi = st.number_input("Projected Year 1 NOI ($)", min_value=0, value=264648)

    st.subheader("3. Capital Stack & Waterfall")
    col5, col6 = st.columns(2)
    loan_amount = col5.number_input("Loan Amount ($)", min_value=0, value=2618000)
    developer_equity = col6.number_input("Developer Equity ($)", min_value=0, value=262000)
    investor_equity = st.number_input("LP Investor Equity ($)", min_value=0, value=611000)
    
    submitted = st.form_submit_button("Analyze My Deal")

# --- THE AI LOGIC ---
if submitted:
    with st.spinner("Auditing deal parameters against course rubrics..."):
        
        # Package the inputs into a clean string for the AI
        deal_data = f"""
        Property: {address} ({prop_type}), Built {year_built}
        Purchase Price: ${purchase_price} | Reno Cost: ${reno_cost}
        Year 1 NOI: ${year_1_noi}
        Capital Stack: Loan ${loan_amount}, Developer Equity ${developer_equity}, Investor Equity ${investor_equity}
        """

        # The "Secret Sauce" Prompt
        system_prompt = """
        You are a Private Equity Investor and Grader for Professor Chernoff's NYU Real Estate course.
        Review the provided deal data strictly based on these course rules:
        1. Deal size should be between $500k and $8M.
        2. No ground-up construction (if reno costs exceed purchase price, flag it).
        3. If it's a NY Residential property built before 1974, explicitly warn them about the HSTPA 2019 Rent Stabilization laws.
        4. Standard course assumption is a maximum 75% LTV mortgage.
        
        Output your response clearly with these exactly headers:
        ### Course Rule Checks
        [Pass/Fail based on the rules]
        
        ### The Math Audit
        [Calculate total cost, going-in cap rate, LTV, and check if Loan + Equity = Total Cost. Be direct if math is wrong.]

        -- Note: Make sure to format your response in Markdown for clarity. Use bullet points, bolding, and headings as appropriate. Especially remember using the dollar sign messes up with Markdown formatting, so make sure it is formatted properly.
        """

        # additional questions
        
        # ### Investor Pushback (Pitch Prep)
        # [Ask 2 tough, specific questions about their deal that a shark investor would ask.]

        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(
                            text=f"{system_prompt}\n\nDeal data to review:\n{deal_data}"
                        )
                    ],
                ),
                config=types.GenerateContentConfig(temperature=0.2),
            )
            
            st.success("Analysis Complete! ✨")
            st.markdown(response.text)
            
        except Exception as e:
            st.error(f"Error communicating with AI: {e}")