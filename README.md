# 🌐 AI Web Scraper

A powerful web scraping tool that combines Selenium automation with Google Gemini AI to extract and analyze website content intelligently.

## ✨ Features

- **🚀 Smart Web Scraping**: Uses Selenium WebDriver to handle dynamic content and JavaScript-heavy websites
- **🧠 AI-Powered Extraction**: Leverages Google Gemini 1.5 Flash to intelligently extract specific information from scraped content
- **💾 Intelligent Caching**: Automatically caches API responses to reduce costs and improve performance
- **⚡ Rate Limiting**: Built-in quota protection to stay within API limits
- **📊 Progress Tracking**: Real-time progress updates with detailed statistics
- **💾 Export Results**: Download extracted data as text files
- **Clean & Simple Interface**: Optimized settings pre-configured for best performance, no complex configuration options to confuse users, streamlined workflow: scrape → describe → extract → download

## 🛠️ Requirements

- Python 3.10
- Google Gemini API Key
- Chrome/Chromium browser (automatically handled)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/kagrawal284/AI_Web_Scraper
cd AI_Web_Scraper
```

### 2. Set up virtual environment(optional but recommended)

```bash
conda create -n venv_scraper python=3.10
conda activate venv_scraper
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create a .env file and add the following

```bash
GOOGLE_API_KEY=your_google_api_key

```

> ### Steps to Create `GOOGLE_API_KEY`
>
> - Go to [https://ai.google.dev/gemini-api/docs/api-key](https://ai.google.dev/gemini-api/docs/api-key)
> - Click on **Get API key** and then **Create API Key**

### 5. Run the app locally

```bash
streamlit run main.py
```

### 6. Public url of app

- Go to [https://ai-scrapy.streamlit.app/](https://ai-scrapy.streamlit.app/)

### 7. Demonstration link

- Go to [demo-ai-web-scraper](https://drive.google.com/file/d/1HXkd2KAJW4iD2RaIfBY3MEVto7rxLlUm/view?usp=sharing)
