import google.generativeai as genai
import os
import time
import hashlib
import json
from datetime import datetime, timedelta
from typing import List, Callable, Optional


class GeminiParser:
    def __init__(self, cache_dir="gemini_cache", cache_duration_hours=24, rate_limit_delay=4):
        """
        Initialize Gemini Parser with caching and rate limiting

        Args:
            cache_dir: Directory to store cached results
            cache_duration_hours: How long to keep cached results
            rate_limit_delay: Seconds to wait between API calls (4s = 15 calls/minute)
        """
        self.cache_dir = cache_dir
        self.cache_duration = timedelta(hours=cache_duration_hours)
        self.rate_limit_delay = rate_limit_delay
        self.last_api_call = 0

        # Create cache directory
        os.makedirs(cache_dir, exist_ok=True)

        # Configure Gemini
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

        print(
            f"🧠 Gemini Parser initialized with {rate_limit_delay}s rate limit")

    def _get_cache_key(self, content: str, parse_description: str) -> str:
        """Generate unique cache key for content + query combination"""
        combined = f"{content}|{parse_description}"
        return hashlib.md5(combined.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> str:
        """Get cache file path"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")

    def _is_cache_valid(self, cache_path: str) -> bool:
        """Check if cached result is still valid"""
        if not os.path.exists(cache_path):
            return False

        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)

            cached_time = datetime.fromisoformat(cached_data['timestamp'])
            return datetime.now() - cached_time < self.cache_duration
        except:
            return False

    def _load_from_cache(self, cache_key: str) -> Optional[str]:
        """Load result from cache if valid"""
        cache_path = self._get_cache_path(cache_key)

        if self._is_cache_valid(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                    print(f"📖 Cache HIT for chunk {cache_key[:8]}...")
                    return cached_data['result']
            except Exception as e:
                print(f"⚠️ Error reading cache: {e}")

        return None

    def _save_to_cache(self, cache_key: str, result: str):
        """Save result to cache"""
        cache_path = self._get_cache_path(cache_key)

        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'cache_key': cache_key,
                'result': result
            }

            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)

            print(f"💾 Cached result for chunk {cache_key[:8]}...")
        except Exception as e:
            print(f"⚠️ Error saving to cache: {e}")

    def _enforce_rate_limit(self):
        """Enforce rate limiting between API calls"""
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call

        if time_since_last_call < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last_call
            print(f"⏳ Rate limiting: waiting {sleep_time:.1f} seconds...")
            time.sleep(sleep_time)

        self.last_api_call = time.time()

    def _handle_quota_error(self, error_msg: str, attempt: int) -> int:
        """Handle quota exceeded errors with exponential backoff"""
        if "429" in str(error_msg) or "quota" in str(error_msg).lower():
            # Exponential backoff: 60s, 120s, 240s, 300s (max 5 minutes)
            wait_time = min(60 * (2 ** attempt), 300)
            print(
                f"🚨 Quota exceeded! Waiting {wait_time} seconds before retry (attempt {attempt + 1})")
            time.sleep(wait_time)
            return attempt + 1
        else:
            raise Exception(error_msg)

    def create_parsing_prompt(self, content: str, parse_description: str) -> str:
        """Create an optimized prompt for content parsing"""
        return f"""You are an expert data extractor. Your task is to extract information from the following content:

{content}

Please carefully follow these instructions:

1. **Objective**: Extract exactly what is described below:
    **{parse_description}**

2. **Output Format**:
    - If the description or question specifies a format (e.g., list, markdown table, plain text), deliver the output in that format.
    - If the format request is mentioned in a conversational way (like "show me in a table"), still deliver in that format.
    - Do not include any extra explanation, commentary, or notes.

3. **No Duplicates**: Only show each unique item once. Remove any duplicate entries.

4. **Understanding User Intent**: If the format is not explicitly mentioned in the description but is requested in the question, respect that format.

5. **No Additional Text**: Your response must contain only the extracted information in the requested format.

6. **No Match Found**: If no matching information is found, return an empty string ('')"""

    def process_single_chunk(self, chunk: str, parse_description: str, max_retries: int = 3) -> str:
        """Process a single chunk with caching and error handling"""
        cache_key = self._get_cache_key(chunk, parse_description)

        # Try to load from cache first
        cached_result = self._load_from_cache(cache_key)
        if cached_result is not None:
            return cached_result

        # Cache miss - need to call API
        print(f"❌ Cache MISS - calling Gemini API...")

        attempt = 0
        while attempt <= max_retries:
            try:
                # Enforce rate limiting
                self._enforce_rate_limit()

                # Create prompt and call Gemini
                prompt = self.create_parsing_prompt(chunk, parse_description)

                start_time = time.time()
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1,
                        top_p=0.8,
                        top_k=20,
                        max_output_tokens=2048,
                    )
                )

                processing_time = time.time() - start_time
                print(f"✅ API call completed in {processing_time:.2f} seconds")

                # Extract and cache result
                if response.text and response.text.strip():
                    result = response.text.strip()
                    self._save_to_cache(cache_key, result)
                    return result
                else:
                    return ""

            except Exception as e:
                error_msg = str(e)
                print(f"❌ Error on attempt {attempt + 1}: {error_msg}")

                # Handle quota errors with exponential backoff
                if "429" in error_msg or "quota" in error_msg.lower():
                    if attempt < max_retries:
                        attempt = self._handle_quota_error(error_msg, attempt)
                        continue
                    else:
                        # Max retries reached
                        error_result = f"❌ Max retries reached due to quota limits. Please wait and try again later."
                        print(error_result)
                        return error_result
                else:
                    # Non-quota error
                    if attempt < max_retries:
                        print(
                            f"⚠️ Retrying in 5 seconds... (attempt {attempt + 2})")
                        time.sleep(5)
                        attempt += 1
                    else:
                        error_result = f"Error: {error_msg}"
                        print(error_result)
                        return error_result

        return "❌ Failed to process chunk after multiple attempts"

    def get_cache_stats(self) -> dict:
        """Get cache statistics"""
        cache_files = [f for f in os.listdir(
            self.cache_dir) if f.endswith('.json')]
        total_size = sum(os.path.getsize(os.path.join(
            self.cache_dir, f)) for f in cache_files)

        return {
            'cached_chunks': len(cache_files),
            'cache_size_mb': round(total_size / (1024 * 1024), 2),
            'cache_dir': self.cache_dir
        }

    def clear_old_cache(self, older_than_hours: int = 48):
        """Clear cache files older than specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
        cleared = 0

        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.cache_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getctime(filepath))

                if file_time < cutoff_time:
                    os.remove(filepath)
                    cleared += 1

        print(
            f"🧹 Cleared {cleared} old cache files (older than {older_than_hours}h)")


def configure_gemini():
    """Legacy function for backward compatibility"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set")

    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')


def create_parsing_prompt(content: str, parse_description: str) -> str:
    """Legacy function for backward compatibility"""
    parser = GeminiParser()
    return parser.create_parsing_prompt(content, parse_description)


def parse_with_gemini(
    dom_chunks: List[str],
    parse_description: str,
    progress_callback: Optional[Callable[[int, int, str], None]] = None
) -> str:
    """
    Enhanced parse function with smart caching and quota handling

    Args:
        dom_chunks: List of content chunks to process
        parse_description: Description of what to extract
        progress_callback: Optional callback for progress updates

    Returns:
        Combined parsed results as string
    """
    try:
        # Initialize parser with caching
        # 5 seconds = 12 calls/minute (safe buffer)
        parser = GeminiParser(rate_limit_delay=5)

        # Show cache stats
        stats = parser.get_cache_stats()
        print(
            f"📊 Cache stats: {stats['cached_chunks']} cached chunks, {stats['cache_size_mb']} MB")

        parsed_results = []
        total_chunks = len(dom_chunks)
        api_calls_made = 0
        cache_hits = 0

        print(f"🚀 Processing {total_chunks} chunks with smart caching...")

        for i, chunk in enumerate(dom_chunks, start=1):
            try:
                print(
                    f"\n📦 Processing chunk {i}/{total_chunks} (length: {len(chunk)})")

                # Update progress if callback provided
                if progress_callback:
                    progress_callback(i, total_chunks, f"Processing chunk {i}")

                # Process chunk with caching
                result = parser.process_single_chunk(chunk, parse_description)

                # Track if this was cached or a fresh API call
                if "Cache HIT" in str(result) or parser._load_from_cache(parser._get_cache_key(chunk, parse_description)):
                    cache_hits += 1
                else:
                    api_calls_made += 1

                # Add result if not empty and not an error
                if result and result.strip() and not result.startswith("❌"):
                    if "no relevant information found" not in result.lower():
                        parsed_results.append(
                            f"--- From Section {i} ---\n{result}")
                elif result.startswith("❌"):
                    # Handle quota limit errors gracefully
                    print(f"⚠️ Chunk {i} failed due to quota limits")
                    if "Max retries reached" in result:
                        # Stop processing if we've hit quota limits
                        print("🛑 Stopping processing due to quota limits")
                        parsed_results.append(
                            f"--- Processing stopped at section {i} due to quota limits ---")
                        break

            except Exception as e:
                print(f"❌ Error processing chunk {i}: {e}")
                continue

        # Summary
        print(f"\n📊 Processing Summary:")
        print(f"   Total chunks: {total_chunks}")
        print(f"   Cache hits: {cache_hits}")
        print(f"   API calls made: {api_calls_made}")
        print(f"   Quota efficiency: {(cache_hits/total_chunks)*100:.1f}%")

        # Combine results
        if parsed_results:
            combined_result = "\n\n".join(parsed_results)
            print(
                f"🎉 Parsing completed! Total results length: {len(combined_result)}")
            return combined_result
        else:
            return "Sorry, I couldn't find any relevant information for your query due to API quota limits. Please try again later or upgrade your plan."

    except Exception as e:
        print(f"❌ Error in parse_with_gemini: {e}")
        return f"Error: {str(e)}. Please check your Google API key and quota limits."


def test_gemini_connection():
    """Test if Gemini is properly configured and working"""
    try:
        parser = GeminiParser()
        response = parser.model.generate_content(
            "Say 'Hello from Gemini!' and nothing else.")
        return True, response.text.strip()
    except Exception as e:
        return False, str(e)
