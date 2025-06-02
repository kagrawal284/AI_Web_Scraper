# import selenium.webdriver as webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
# from webdriver_manager.chrome import ChromeDriverManager
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin
# import re
# import time


# def scrape_website(website):
#     """
#     Scrape website content using Selenium and return HTML
#     Now uses WebDriverManager for automatic ChromeDriver management
#     """
#     print("🚀 Launching Chrome Browser...")

#     # Chrome options for better performance
#     options = webdriver.ChromeOptions()
#     options.add_argument("--headless")  # Run without GUI
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--disable-extensions")
#     options.add_argument("--disable-logging")
#     options.add_argument("--log-level=3")  # Suppress logs
#     options.add_argument("--disable-web-security")
#     options.add_argument("--disable-features=VizDisplayCompositor")

#     # Use WebDriverManager to automatically handle ChromeDriver
#     try:
#         driver = webdriver.Chrome(
#             service=Service(ChromeDriverManager().install()),
#             options=options
#         )
#     except Exception as e:
#         print(f"❌ Error setting up ChromeDriver: {e}")
#         return ""

#     # Set timeouts to prevent infinite hanging
#     driver.set_page_load_timeout(30)
#     driver.implicitly_wait(10)

#     try:
#         print(f"🌐 Navigating to: {website}")
#         driver.get(website)
#         print("📄 Page loaded...")

#         # Wait for page to be fully loaded
#         WebDriverWait(driver, 15).until(
#             lambda driver: driver.execute_script(
#                 "return document.readyState") == "complete"
#         )
#         print("✅ Page fully rendered...")

#         html = driver.page_source
#         print(f"📊 HTML content length: {len(html):,} characters")
#         return html

#     except Exception as e:
#         print(f"❌ Error scraping website: {e}")
#         return ""

#     finally:
#         print("🔄 Closing browser...")
#         try:
#             driver.quit()
#             print("✅ Browser closed successfully")
#         except Exception as e:
#             print(f"⚠️ Error closing browser: {e}")


# def extract_body_content(html_content, base_url=""):
#     """Extract body content from HTML - FIXED: Process images BEFORE links"""
#     if not html_content:
#         return ""

#     soup = BeautifulSoup(html_content, "html.parser")

#     # Extract title from head section
#     title_tag = soup.find('title')
#     page_title = title_tag.get_text().strip() if title_tag else "No title found"

#     # Extract body content
#     body_content = soup.body
#     if body_content:
#         # Count images and links before processing
#         links_found = body_content.find_all('a')
#         images_found = body_content.find_all('img')
#         print(f"🔍 DEBUG: Found {len(links_found)} links and {len(images_found)} images")
        
#         # CRITICAL FIX: Process images FIRST, before links
#         # This prevents images nested in links from being removed
#         for i, img in enumerate(images_found):
#             img_src = img.get('src', '')
#             img_alt = img.get('alt', '')

#             # Convert relative URLs to absolute URLs
#             if img_src and base_url:
#                 img_src = urljoin(base_url, img_src)

#             marker = f"[IMAGE: {img_alt} -> {img_src}]"
#             print(f"🖼️ DEBUG: Image {i+1}: {marker}")
            
#             # Replace this specific image with its marker
#             img.replace_with(marker)

#         # NOW process hyperlinks (after images are already replaced)
#         # Re-find links since the DOM may have changed
#         current_links = body_content.find_all('a')
#         print(f"🔍 DEBUG: After processing images, found {len(current_links)} links to process")
        
#         for i, link in enumerate(current_links):
#             link_href = link.get('href', '')
#             link_text = link.get_text().strip()

#             # Convert relative URLs to absolute URLs
#             if link_href and base_url:
#                 link_href = urljoin(base_url, link_href)

#             marker = f"[LINK: {link_text} -> {link_href}]"
#             print(f"🔗 DEBUG: Link {i+1}: {marker}")
            
#             # Replace this specific link with its marker
#             link.replace_with(marker)

#         # Get the text content directly
#         body_html = body_content.get_text(separator="\n")
        
#         # Debug: Check if markers are preserved
#         link_count = body_html.count('[LINK:')
#         image_count = body_html.count('[IMAGE:')
#         print(f"📊 DEBUG: After processing - {link_count} LINK markers, {image_count} IMAGE markers")
        
#     else:
#         body_html = ""
#         print("⚠️ DEBUG: No body content found!")

#     # Combine title with body content
#     combined_content = f"PAGE TITLE: {page_title}\n\nBODY CONTENT:\n{body_html}"
#     return combined_content


# def clean_body_content(body_content):
#     """Clean body content by removing scripts, styles and extra whitespace - SIMPLIFIED since we now get text directly"""
#     if not body_content:
#         return ""

#     print("🧹 DEBUG: Starting clean_body_content")
    
#     # Check if this is the new format with title
#     if body_content.startswith("PAGE TITLE:"):
#         # Split the title and body parts
#         parts = body_content.split("BODY CONTENT:\n", 1)
#         title_part = parts[0]  # Keep the title part as-is
#         text_part = parts[1] if len(parts) > 1 else ""

#         if text_part:
#             print(f"📝 DEBUG: Text part length: {len(text_part)}")
            
#             # Count markers
#             link_count = text_part.count('[LINK:')
#             image_count = text_part.count('[IMAGE:')
#             print(f"🔍 DEBUG: Found {link_count} LINK markers and {image_count} IMAGE markers")

#             # Clean up whitespace only
#             lines = [line.strip() for line in text_part.splitlines() if line.strip()]
#             cleaned_text = "\n".join(lines)
            
#             # Final check
#             final_link_count = cleaned_text.count('[LINK:')
#             final_image_count = cleaned_text.count('[IMAGE:')
#             print(f"🎯 DEBUG: Final result - {final_link_count} LINK markers, {final_image_count} IMAGE markers")

#             # Combine title with cleaned content
#             result = f"{title_part}\n\n{cleaned_text}"
#             return result
#         else:
#             return title_part
#     else:
#         # Original cleaning method for backward compatibility
#         soup = BeautifulSoup(body_content, "html.parser")

#         # Remove script and style elements
#         for script_or_style in soup(["script", "style"]):
#             script_or_style.extract()

#         # Remove comments
#         from bs4 import Comment
#         comments = soup.findAll(text=lambda text: isinstance(text, Comment))
#         for comment in comments:
#             comment.extract()

#         # Get text content
#         cleaned_content = soup.get_text(separator="\n")

#         # Clean up whitespace
#         lines = [line.strip()
#                  for line in cleaned_content.splitlines() if line.strip()]
#         cleaned_content = "\n".join(lines)

#         return cleaned_content


# def split_dom_content(dom_content, max_length=8000):
#     """
#     Split DOM content into chunks for processing
#     Increased chunk size for better context with Gemini
#     """
#     if not dom_content:
#         return []

#     chunks = [
#         dom_content[i: i + max_length]
#         for i in range(0, len(dom_content), max_length)
#     ]
    
#     # Debug: Check each chunk for markers
#     for i, chunk in enumerate(chunks):
#         link_count = chunk.count('[LINK:')
#         image_count = chunk.count('[IMAGE:')
#         print(f"📦 DEBUG: Chunk {i+1} has {link_count} LINK markers and {image_count} IMAGE markers")
    
#     return chunks


# import selenium.webdriver as webdriver
# from selenium.webdriver.chrome.service import Service  as ChromeService
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
# from webdriver_manager.chrome import ChromeDriverManager
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin
# import re
# import time


# def scrape_website(website):
#     """
#     Scrape website content using Selenium and return HTML
#     Now uses WebDriverManager for automatic ChromeDriver management
#     """
#     print("🚀 Launching Chrome Browser...")

#     # Chrome options for better performance
#     options = webdriver.ChromeOptions()
#     options.add_argument("--headless")  # Run without GUI
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--disable-extensions")
#     options.add_argument("--disable-logging")
#     options.add_argument("--log-level=3")  # Suppress logs
#     options.add_argument("--disable-web-security")
#     options.add_argument("--disable-features=VizDisplayCompositor")

#     # Use WebDriverManager to automatically handle ChromeDriver
#     try:
#         driver = webdriver.Chrome(
#             service = ChromeService(ChromeDriverManager().install()),
#             options=options
#         )
#     except Exception as e:
#         print(f"❌ Error setting up ChromeDriver: {e}")
#         return ""

#     # Set timeouts to prevent infinite hanging
#     driver.set_page_load_timeout(30)
#     driver.implicitly_wait(10)

#     try:
#         print(f"🌐 Navigating to: {website}")
#         driver.get(website)
#         print("📄 Page loaded...")

#         # Wait for page to be fully loaded
#         WebDriverWait(driver, 15).until(
#             lambda driver: driver.execute_script(
#                 "return document.readyState") == "complete"
#         )
#         print("✅ Page fully rendered...")

#         html = driver.page_source
#         print(f"📊 HTML content length: {len(html):,} characters")
#         return html

#     except Exception as e:
#         print(f"❌ Error scraping website: {e}")
#         return ""

#     finally:
#         print("🔄 Closing browser...")
#         try:
#             driver.quit()
#             print("✅ Browser closed successfully")
#         except Exception as e:
#             print(f"⚠️ Error closing browser: {e}")


# def extract_body_content(html_content, base_url=""):
#     """Extract body content from HTML - FIXED: Process images BEFORE links"""
#     if not html_content:
#         return ""

#     soup = BeautifulSoup(html_content, "html.parser")

#     # Extract title from head section
#     title_tag = soup.find('title')
#     page_title = title_tag.get_text().strip() if title_tag else "No title found"

#     # Extract body content
#     body_content = soup.body
#     if body_content:
#         # Count images and links before processing
#         links_found = body_content.find_all('a')
#         images_found = body_content.find_all('img')
#         print(f"🔍 DEBUG: Found {len(links_found)} links and {len(images_found)} images")
        
#         # CRITICAL FIX: Process images FIRST, before links
#         # This prevents images nested in links from being removed
#         for i, img in enumerate(images_found):
#             img_src = img.get('src', '')
#             img_alt = img.get('alt', '')

#             # Convert relative URLs to absolute URLs
#             if img_src and base_url:
#                 img_src = urljoin(base_url, img_src)

#             marker = f"🖼️ IMAGE_ASSET: {img_alt} | Source: {img_src}"
#             print(f"🖼️ DEBUG: Image {i+1}: {marker}")
            
#             # Replace this specific image with its marker
#             img.replace_with(marker)

#         # NOW process hyperlinks (after images are already replaced)
#         # Re-find links since the DOM may have changed
#         current_links = body_content.find_all('a')
#         print(f"🔍 DEBUG: After processing images, found {len(current_links)} links to process")
        
#         for i, link in enumerate(current_links):
#             link_href = link.get('href', '')
#             link_text = link.get_text().strip()
            
#             # Handle empty link text
#             if not link_text:
#                 link_text = "NO_TEXT"

#             # Convert relative URLs to absolute URLs
#             if link_href and base_url:
#                 link_href = urljoin(base_url, link_href)

#             marker = f"[HYPERLINK: {link_text} -> {link_href}]"
#             print(f"🔗 DEBUG: Link {i+1}: {marker}")
            
#             # Replace this specific link with its marker
#             link.replace_with(marker)

#         # Get the text content directly
#         body_html = body_content.get_text(separator="\n")
        
#         # Debug: Check if markers are preserved
#         link_count = body_html.count('[HYPERLINK:')
#         image_count = body_html.count('🖼️ IMAGE_ASSET:')
#         print(f"📊 DEBUG: After processing - {link_count} HYPERLINK markers, {image_count} IMAGE markers")
        
#     else:
#         body_html = ""
#         print("⚠️ DEBUG: No body content found!")

#     # Combine title with body content
#     combined_content = f"PAGE TITLE: {page_title}\n\nBODY CONTENT:\n{body_html}"
#     return combined_content


# def clean_body_content(body_content):
#     """Clean body content by removing scripts, styles and extra whitespace - SIMPLIFIED since we now get text directly"""
#     if not body_content:
#         return ""

#     print("🧹 DEBUG: Starting clean_body_content")
    
#     # Check if this is the new format with title
#     if body_content.startswith("PAGE TITLE:"):
#         # Split the title and body parts
#         parts = body_content.split("BODY CONTENT:\n", 1)
#         title_part = parts[0]  # Keep the title part as-is
#         text_part = parts[1] if len(parts) > 1 else ""

#         if text_part:
#             print(f"📝 DEBUG: Text part length: {len(text_part)}")
            
#             # Count markers
#             link_count = text_part.count('[HYPERLINK:')
#             image_count = text_part.count('🖼️ IMAGE_ASSET:')
#             print(f"🔍 DEBUG: Found {link_count} HYPERLINK markers and {image_count} IMAGE markers")

#             # Clean up whitespace only
#             lines = [line.strip() for line in text_part.splitlines() if line.strip()]
#             cleaned_text = "\n".join(lines)
            
#             # Final check
#             final_link_count = cleaned_text.count('[HYPERLINK:')
#             final_image_count = cleaned_text.count('🖼️ IMAGE_ASSET:')
#             print(f"🎯 DEBUG: Final result - {final_link_count} HYPERLINK markers, {final_image_count} IMAGE markers")

#             # Combine title with cleaned content
#             result = f"{title_part}\n\n{cleaned_text}"
#             return result
#         else:
#             return title_part
#     else:
#         # Original cleaning method for backward compatibility
#         soup = BeautifulSoup(body_content, "html.parser")

#         # Remove script and style elements
#         for script_or_style in soup(["script", "style"]):
#             script_or_style.extract()

#         # Remove comments
#         from bs4 import Comment
#         comments = soup.findAll(text=lambda text: isinstance(text, Comment))
#         for comment in comments:
#             comment.extract()

#         # Get text content
#         cleaned_content = soup.get_text(separator="\n")

#         # Clean up whitespace
#         lines = [line.strip()
#                  for line in cleaned_content.splitlines() if line.strip()]
#         cleaned_content = "\n".join(lines)

#         return cleaned_content


# def split_dom_content(dom_content, max_length=8000):
#     """
#     Split DOM content into chunks for processing
#     Increased chunk size for better context with Gemini
#     """
#     if not dom_content:
#         return []

#     chunks = [
#         dom_content[i: i + max_length]
#         for i in range(0, len(dom_content), max_length)
#     ]
    
#     # Debug: Check each chunk for markers
#     for i, chunk in enumerate(chunks):
#         link_count = chunk.count('[HYPERLINK:')
#         image_count = chunk.count('🖼️ IMAGE_ASSET:')
#         print(f"📦 DEBUG: Chunk {i+1} has {link_count} HYPERLINK markers and {image_count} IMAGE markers")
    
#     return chunks


import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import streamlit as st
import os
import re
import time


def setup_chrome_driver():
    """Setup Chrome driver for both local and Streamlit Cloud environments"""
    try:
        st.write("🚀 Setting up Chrome Browser...")
        
        # Chrome options for headless mode - optimized for Chrome 137
        options = Options()
        
        # Check if we're running locally (Windows) or on cloud (Linux)
        import platform
        is_local = platform.system() == "Windows"
        
        if is_local:
            # More conservative options for local Windows Chrome 137
            options.add_argument('--headless')  # Use old headless for stability
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-logging')
            options.add_argument('--log-level=3')
            options.add_argument('--window-size=1920,1080')
            # Remove problematic options for local
        else:
            # More aggressive options for Linux/Cloud
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-logging')
            options.add_argument('--log-level=3')
            options.add_argument('--disable-web-security')
            options.add_argument('--disable-features=VizDisplayCompositor')
            options.add_argument('--remote-debugging-port=9222')
            options.add_argument('--disable-background-timer-throttling')
            options.add_argument('--disable-background-networking')
            options.add_argument('--disable-backgrounding-occluded-windows')
            options.add_argument('--disable-renderer-backgrounding')
            options.add_argument('--disable-features=TranslateUI')
            options.add_argument('--disable-ipc-flooding-protection')
            options.add_argument('--single-process')
            options.add_argument('--disable-setuid-sandbox')
            options.add_argument('--window-size=1920,1080')
        
        # Check if we're running locally (Windows) or on Streamlit Cloud (Linux)
        import platform
        is_local = platform.system() == "Windows"
        
        if is_local:
            st.write("🖥️ Local Windows environment detected")
            # For local development - use WebDriverManager
            try:
                st.write("🔄 Using WebDriverManager for local development...")
                from webdriver_manager.chrome import ChromeDriverManager
                
                # Don't set binary location for local Windows
                service = ChromeService(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
                st.write("✅ Success with WebDriverManager!")
                return driver
            except Exception as e:
                st.error(f"❌ WebDriverManager failed: {e}")
                return None
        else:
            st.write("☁️ Streamlit Cloud (Linux) environment detected")
            # For Streamlit Cloud - use system packages
            
            # Debug: Check what's actually installed
            st.write("🔍 Checking installed browsers and drivers...")
            
            # Check browser paths
            browser_paths = [
                '/usr/bin/chromium',
                '/usr/bin/chromium-browser', 
                '/usr/bin/google-chrome',
                '/usr/bin/google-chrome-stable'
            ]
            
            available_browser = None
            for path in browser_paths:
                if os.path.exists(path):
                    st.write(f"✅ Found browser: {path}")
                    available_browser = path
                    break
                else:
                    st.write(f"❌ Not found: {path}")
            
            # Check driver paths  
            driver_paths = [
                '/usr/bin/chromedriver',
                '/usr/bin/chromium-driver'
            ]
            
            available_driver = None
            for path in driver_paths:
                if os.path.exists(path):
                    st.write(f"✅ Found driver: {path}")
                    available_driver = path
                    break
                else:
                    st.write(f"❌ Not found: {path}")
            
            # Try to get versions
            if available_browser:
                try:
                    import subprocess
                    result = subprocess.run([available_browser, '--version'], 
                                          capture_output=True, text=True, timeout=5)
                    st.write(f"**Browser version:** {result.stdout.strip()}")
                except:
                    st.write("**Browser version:** Could not determine")
                    
            if available_driver:
                try:
                    import subprocess
                    result = subprocess.run([available_driver, '--version'], 
                                          capture_output=True, text=True, timeout=5)
                    st.write(f"**Driver version:** {result.stdout.strip()}")
                except:
                    st.write("**Driver version:** Could not determine")
            
            # Try to use what we found
            if available_browser and available_driver:
                st.write(f"🚀 Attempting to use: {available_browser} + {available_driver}")
                options.binary_location = available_browser
                
                try:
                    service = ChromeService(available_driver)
                    driver = webdriver.Chrome(service=service, options=options)
                    st.write(f"✅ Success! Using {available_browser} + {available_driver}")
                    return driver
                except Exception as e:
                    st.write(f"❌ Failed: {str(e)[:200]}...")
            
            # If system packages don't work, try WebDriverManager as fallback
            try:
                st.write("🔄 Fallback: Trying WebDriverManager on Linux...")
                from webdriver_manager.chrome import ChromeDriverManager
                
                # Remove binary location for WebDriverManager
                options.binary_location = None
                service = ChromeService(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
                st.write("✅ Success with WebDriverManager fallback!")
                return driver
            except Exception as e:
                st.error(f"❌ All attempts failed: {e}")
                return None
                
    except Exception as e:
        st.error(f"❌ Error setting up Chrome options: {e}")
        return None

def scrape_website(website):
    """
    Scrape website content using Selenium - Fixed for Streamlit Cloud
    """
    st.write("🚀 Launching Chrome Browser...")

    # Setup Chrome driver
    driver = setup_chrome_driver()
    if not driver:
        return ""

    # Set timeouts to prevent infinite hanging
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(10)

    try:
        st.write(f"🌐 Navigating to: {website}")
        driver.get(website)
        st.write("📄 Page loaded...")

        # Wait for page to be fully loaded
        WebDriverWait(driver, 15).until(
            lambda driver: driver.execute_script(
                "return document.readyState") == "complete"
        )
        st.write("✅ Page fully rendered...")

        html = driver.page_source
        st.write(f"📊 HTML content length: {len(html):,} characters")
        return html

    except Exception as e:
        st.error(f"❌ Error scraping website: {e}")
        return ""

    finally:
        st.write("🔄 Closing browser...")
        try:
            driver.quit()
            st.write("✅ Browser closed successfully")
        except Exception as e:
            st.warning(f"⚠️ Error closing browser: {e}")


def extract_body_content(html_content, base_url=""):
    """Extract body content from HTML - FIXED: Process images BEFORE links"""
    if not html_content:
        return ""

    soup = BeautifulSoup(html_content, "html.parser")

    # Extract title from head section
    title_tag = soup.find('title')
    page_title = title_tag.get_text().strip() if title_tag else "No title found"

    # Extract body content
    body_content = soup.body
    if body_content:
        # Count images and links before processing
        links_found = body_content.find_all('a')
        images_found = body_content.find_all('img')
        print(f"🔍 DEBUG: Found {len(links_found)} links and {len(images_found)} images")
        
        # CRITICAL FIX: Process images FIRST, before links
        # This prevents images nested in links from being removed
        for i, img in enumerate(images_found):
            img_src = img.get('src', '')
            img_alt = img.get('alt', '')

            # Convert relative URLs to absolute URLs
            if img_src and base_url:
                img_src = urljoin(base_url, img_src)

            marker = f"🖼️ IMAGE_ASSET: {img_alt} | Source: {img_src}"
            print(f"🖼️ DEBUG: Image {i+1}: {marker}")
            
            # Replace this specific image with its marker
            img.replace_with(marker)

        # NOW process hyperlinks (after images are already replaced)
        # Re-find links since the DOM may have changed
        current_links = body_content.find_all('a')
        print(f"🔍 DEBUG: After processing images, found {len(current_links)} links to process")
        
        for i, link in enumerate(current_links):
            link_href = link.get('href', '')
            link_text = link.get_text().strip()
            
            # Handle empty link text
            if not link_text:
                link_text = "NO_TEXT"

            # Convert relative URLs to absolute URLs
            if link_href and base_url:
                link_href = urljoin(base_url, link_href)

            marker = f"[HYPERLINK: {link_text} -> {link_href}]"
            print(f"🔗 DEBUG: Link {i+1}: {marker}")
            
            # Replace this specific link with its marker
            link.replace_with(marker)

        # Get the text content directly
        body_html = body_content.get_text(separator="\n")
        
        # Debug: Check if markers are preserved
        link_count = body_html.count('[HYPERLINK:')
        image_count = body_html.count('🖼️ IMAGE_ASSET:')
        print(f"📊 DEBUG: After processing - {link_count} HYPERLINK markers, {image_count} IMAGE markers")
        
    else:
        body_html = ""
        print("⚠️ DEBUG: No body content found!")

    # Combine title with body content
    combined_content = f"PAGE TITLE: {page_title}\n\nBODY CONTENT:\n{body_html}"
    return combined_content


def clean_body_content(body_content):
    """Clean body content by removing scripts, styles and extra whitespace - SIMPLIFIED since we now get text directly"""
    if not body_content:
        return ""

    print("🧹 DEBUG: Starting clean_body_content")
    
    # Check if this is the new format with title
    if body_content.startswith("PAGE TITLE:"):
        # Split the title and body parts
        parts = body_content.split("BODY CONTENT:\n", 1)
        title_part = parts[0]  # Keep the title part as-is
        text_part = parts[1] if len(parts) > 1 else ""

        if text_part:
            print(f"📝 DEBUG: Text part length: {len(text_part)}")
            
            # Count markers
            link_count = text_part.count('[HYPERLINK:')
            image_count = text_part.count('🖼️ IMAGE_ASSET:')
            print(f"🔍 DEBUG: Found {link_count} HYPERLINK markers and {image_count} IMAGE markers")

            # Clean up whitespace only
            lines = [line.strip() for line in text_part.splitlines() if line.strip()]
            cleaned_text = "\n".join(lines)
            
            # Final check
            final_link_count = cleaned_text.count('[HYPERLINK:')
            final_image_count = cleaned_text.count('🖼️ IMAGE_ASSET:')
            print(f"🎯 DEBUG: Final result - {final_link_count} HYPERLINK markers, {final_image_count} IMAGE markers")

            # Combine title with cleaned content
            result = f"{title_part}\n\n{cleaned_text}"
            return result
        else:
            return title_part
    else:
        # Original cleaning method for backward compatibility
        soup = BeautifulSoup(body_content, "html.parser")

        # Remove script and style elements
        for script_or_style in soup(["script", "style"]):
            script_or_style.extract()

        # Remove comments
        from bs4 import Comment
        comments = soup.findAll(text=lambda text: isinstance(text, Comment))
        for comment in comments:
            comment.extract()

        # Get text content
        cleaned_content = soup.get_text(separator="\n")

        # Clean up whitespace
        lines = [line.strip()
                 for line in cleaned_content.splitlines() if line.strip()]
        cleaned_content = "\n".join(lines)

        return cleaned_content


def split_dom_content(dom_content, max_length=8000):
    """
    Split DOM content into chunks for processing
    Increased chunk size for better context with Gemini
    """
    if not dom_content:
        return []

    chunks = [
        dom_content[i: i + max_length]
        for i in range(0, len(dom_content), max_length)
    ]
    
    # Debug: Check each chunk for markers
    for i, chunk in enumerate(chunks):
        link_count = chunk.count('[HYPERLINK:')
        image_count = chunk.count('🖼️ IMAGE_ASSET:')
        print(f"📦 DEBUG: Chunk {i+1} has {link_count} HYPERLINK markers and {image_count} IMAGE markers")
    
    return chunks