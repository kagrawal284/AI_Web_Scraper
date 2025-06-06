import streamlit as st
import os
from dotenv import load_dotenv
from scrape import (scrape_website,
                    extract_body_content,
                    clean_body_content,
                    split_dom_content)

from parse_gemini import parse_with_gemini, GeminiParser

# Load environment variables from .env file
load_dotenv()

# Configure Streamlit page
st.set_page_config(page_title="AI Web Scraper", page_icon="🌐", layout="wide")

st.title("🌐 AI Web Scraper")
st.markdown("*Powered by Google Gemini 1.5 Flash*")

# Check for API key from .env file
api_key = os.getenv("GOOGLE_API_KEY")

# Check for API key and show status
if api_key:
    print(" API Key loaded from .env file!")
else:
    st.error("❌ API Key not found!")
    print("API Key not found!")
    st.markdown("""
    **To fix this:**
    1. Create a `.env` file in your project folder
    2. Add this line: `GOOGLE_API_KEY=your_actual_api_key_here`
    3. Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
    4. Restart the app
    """)
    st.stop()  # Stop the app if no API key

# Main interface
col1, col2 = st.columns([2, 1])

with col1:
    url = st.text_input("🔗 Enter a website URL:",
                        placeholder="https://example.com")

with col2:
    st.write(" ")  # Add some spacing
    st.write("")  # Add some spacing
    scrape_button = st.button(
        "🚀 Scrape Site", type="primary", use_container_width=True)

if scrape_button and url:
    if not api_key:
        st.error("❌ Please check your .env file and restart the app!")
    else:
        with st.spinner("🔍 Scraping the website..."):
            try:
                result = scrape_website(url)

                if result:
                    body_content = extract_body_content(result, url)
                    cleaned_content = clean_body_content(body_content)

                    st.session_state.dom_content = cleaned_content
                    st.session_state.scraped_url = url

                    # Show scraping stats
                    print("Raw HTML", f"{len(result):,} chars")

                    print("Cleaned Content", f"{len(cleaned_content):,} chars")

                    chunks = len(split_dom_content(cleaned_content))
                    print("Processing Chunks", chunks)

                    st.success(f"✅ Successfully scraped: {url}")

                    # Cache info for this content
                    try:
                        parser = GeminiParser()
                        # Count how many chunks might be cached
                        test_chunks = split_dom_content(cleaned_content)
                        cached_count = 0
                        for chunk in test_chunks:
                            cache_key = parser._get_cache_key(chunk, "test")
                            if parser._load_from_cache(cache_key):
                                cached_count += 1

                        if cached_count > 0:
                            cache_efficiency = (
                                cached_count / len(test_chunks)) * 100
                            st.info(
                                f"🎯 Cache efficiency for this content: {cache_efficiency:.1f}% ({cached_count}/{len(test_chunks)} chunks cached)")
                    except:
                        pass

                    with st.expander("👀 View Scraped Content", expanded=False):
                        st.text_area(
                            "DOM Content", cleaned_content, height=300)

                else:
                    st.error(
                        "❌ Failed to scrape the website. Please check the URL and try again.")

            except Exception as e:
                st.error(f"❌ Error scraping website: {str(e)}")

# Parsing section
if "dom_content" in st.session_state:
    st.divider()
    st.header("🤖 Parse Content with AI")

    col1, col2 = st.columns([3, 1])

    with col1:
        parse_description = st.text_area(
            "📝 What do you want to extract?",
            placeholder="e.g., Extract all the urls along with their text from the webpage, print them out in the form of table ...",
            height=100
        )

    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        parse_button = st.button(
            "🔍 Parse Content", type="primary", use_container_width=True)
        
    rate_limit = 5

    if parse_button and parse_description:
        if not api_key:
            st.error("❌ Please check your .env file and restart the app!")
        else:
            try:

                dom_chunks = split_dom_content(
                    st.session_state.dom_content)  
                parser = GeminiParser(rate_limit_delay=rate_limit)  

                # Pre-analysis: check cache efficiency
                cached_count = 0
                for chunk in dom_chunks:
                    cache_key = parser._get_cache_key(chunk, parse_description)
                    if parser._load_from_cache(cache_key):
                        cached_count += 1

                cache_efficiency = (
                    cached_count / len(dom_chunks)) * 100 if dom_chunks else 0
                estimated_api_calls = len(dom_chunks) - cached_count
                estimated_time = estimated_api_calls * rate_limit

                st.metric(
                    "⏰ Est. Time", f"{estimated_time//60:.0f}m {estimated_time%60:.0f}s")

                # Progress tracking
                progress_bar = st.progress(0)
                status_container = st.container()
                results_container = st.container()

                def update_progress(current, total, chunk_result=""):
                    progress = current / total
                    progress_bar.progress(progress)

                    # Update status with cache info
                    cache_hits = sum(1 for i, chunk in enumerate(dom_chunks[:current])
                                     if parser._load_from_cache(parser._get_cache_key(chunk, parse_description)))
                    api_calls = current - cache_hits

                with st.spinner("🧠 AI is analyzing the content..."):
                    parsed_result = parse_with_gemini(
                        dom_chunks, parse_description, update_progress)

                progress_bar.progress(1.0)

                # Final status update
                final_cache_hits = sum(1 for chunk in dom_chunks
                                       if parser._load_from_cache(parser._get_cache_key(chunk, parse_description)))
                final_api_calls = len(dom_chunks) - final_cache_hits

                status_container.success(f"✅ Parsing completed!")

                # Display results
                with results_container:
                    st.subheader("📋 Extracted Information")

                    if parsed_result and parsed_result.strip():
                        # Check if results were truncated due to quota limits
                        if "quota limits" in parsed_result.lower() or "max retries reached" in parsed_result.lower():
                            st.warning(
                                "⚠️ Processing was stopped due to API quota limits. Results may be incomplete.")
                            st.info(
                                "💡 Try again later or consider upgrading your Google API plan.")
                        elif "sorry" not in parsed_result.lower():
                            st.success("🎉 Results extracted successfully!")

                        st.markdown("### Results:")
                        st.write(parsed_result)

                        # Download option
                        st.download_button(
                            label="💾 Download Results",
                            data=parsed_result,
                            file_name=f"scraped_data_{st.session_state.scraped_url.replace('https://', '').replace('/', '_')}.txt",
                            mime="text/plain"
                        )

                        # Show processing stats
                        with st.expander("📊 Processing Statistics", expanded=False):
                            st.write(f"**Total Chunks:** {len(dom_chunks)}")
                            st.write(f"**Cache Hits:** {final_cache_hits}")
                            st.write(f"**API Calls Made:** {final_api_calls}")
                            st.write(
                                f"**Cache Efficiency:** {(final_cache_hits/len(dom_chunks)*100):.1f}%")
                            st.write(
                                f"**Rate Limit:** {rate_limit} seconds between calls")

                            if final_api_calls > 0:
                                st.write(
                                    f"**Quota Usage:** ~{final_api_calls} requests from your daily limit")
                    else:
                        st.warning(
                            "⚠️ No relevant information found for your query. Try a different description.")

            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "quota" in error_msg.lower():
                    st.error("🚨 API Quota Exceeded!")
                    st.info("""
                    **What happened:** You've hit the free tier limit of 15 requests per minute.
                    
                    **Solutions:**
                    1. **Wait 1-2 minutes** and try again
                    2. **Use smaller chunks** (reduce chunk size in Advanced Options)
                    3. **Increase rate limit** to 8-10 seconds between calls
                    4. **Upgrade your plan** at https://ai.google.dev/pricing
                    5. The app will **automatically cache results** to avoid repeat API calls
                    """)
                else:
                    st.error(f"❌ Error during parsing: {error_msg}")
                    st.info(
                        "💡 Make sure your Google API Key is valid and you have credits available.")

    elif parse_button and not parse_description:
        st.warning(
            "⚠️ Please describe what you want to extract from the content.")


