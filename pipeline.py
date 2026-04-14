import re
import time
from rich import print
from agents import run_search_agent, run_reader_agent, writer_chain, critic_chain, clean_output


# Helpers

def extract_urls(text: str) -> list[str]:
    """Extract valid, scrapeable HTTP/HTTPS URLs from text."""
    raw = re.findall(r"https?://[^\s\n,\]\)\"'<>]+", text)
    blacklist = [
        "youtube.com", "youtu.be", "twitter.com", "x.com",
        "instagram.com", "facebook.com", "tiktok.com",
        "reddit.com", "msn.com/en-in/video",
    ]
    seen, unique = set(), []
    for url in raw:
        url = url.rstrip(".,;)")  # strip trailing punctuation
        if url not in seen and not any(b in url for b in blacklist):
            seen.add(url)
            unique.append(url)
    return unique


def invoke_with_retry(fn, inputs: dict, retries: int = 3, delay: int = 45):
    """Retry a callable on rate-limit errors with exponential-ish backoff."""
    for attempt in range(retries):
        try:
            return fn(inputs) if callable(fn) else fn.invoke(inputs)
        except Exception as e:
            err = str(e)
            if "429" in err or "RESOURCE_EXHAUSTED" in err or "rate" in err.lower():
                wait = delay * (attempt + 1)
                print(f"[yellow]Rate limited. Retrying in {wait}s (attempt {attempt+1}/{retries})...[/yellow]")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Max retries exceeded due to rate limiting.")


# Pipeline

def run_research_pipeline(topic: str) -> dict:
    state = {}

    # 1. Search
    print(f"\n[bold green]► Stage 1: Search Agent[/bold green]")
    state["search_result"] = run_search_agent(topic)
    print(state["search_result"])

    # 2. Reader
    print(f"\n[bold green]► Stage 2: Reader Agent[/bold green]")
    urls = extract_urls(state["search_result"])
    print(f"  Scraping {min(len(urls), 3)} URLs: {urls[:3]}")
    state["scraped_result"] = run_reader_agent(urls)
    print(state["scraped_result"][:800] + "..." if len(state["scraped_result"]) > 800 else state["scraped_result"])

    # 3. Writer
    print(f"\n[bold green]► Stage 3: Writer Chain[/bold green]")
    research_combined = (
        f"## Search Results\n\n{state['search_result']}\n\n"
        f"## Scraped Page Content\n\n{state['scraped_result']}"
    )
    raw_report = invoke_with_retry(
        writer_chain,
        {"topic": topic, "research": research_combined},
    )
    state["report"] = clean_output(raw_report)
    print(state["report"])

    # 4. Critic 
    print(f"\n[bold green]► Stage 4: Critic Chain[/bold green]")
    raw_critique = invoke_with_retry(critic_chain, {"report": state["report"]})
    state["critique"] = clean_output(raw_critique)
    print(state["critique"])

    return state


if __name__ == "__main__":
    topic = input("\nEnter a research topic: ").strip()
    if topic:
        run_research_pipeline(topic)
