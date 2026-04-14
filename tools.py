from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information. Returns structured markdown results."""
    results = tavily.search(query=query, max_results=5)
    out = ["## Search Results\n"]

    for i, r in enumerate(results["results"], 1):
        title   = r.get("title", "Untitled").strip()
        url     = r.get("url", "").strip()
        snippet = r.get("content", "")[:600].strip()

        out.append(
            f"### {i}. {title}\n"
            f"**Source:** [{url}]({url})\n\n"
            f"{snippet}\n"
        )

    return "\n---\n".join(out)


@tool
def scrape_website(url: str) -> str:
    """Scrape clean structured content from a URL. Returns title, headings, and body text."""
    if not url.startswith("http"):
        return "**Error:** Invalid URL — must start with `http` or `https`."

    try:
        res = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0 (compatible; ResearchBot/1.0)"},
        )
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        # Remove noise
        for tag in soup(["script", "style", "nav", "footer", "aside", "form", "iframe"]):
            tag.decompose()

        title    = soup.title.string.strip() if soup.title else "No title"
        headings = [h.get_text(strip=True) for h in soup.find_all(["h1", "h2", "h3"])[:8]]
        paragraphs = [
            p.get_text(strip=True)
            for p in soup.find_all("p")
            if len(p.get_text(strip=True)) > 60
        ]
        body = "\n\n".join(paragraphs[:25])

        heading_md = "\n".join(f"- {h}" for h in headings) if headings else "_None found_"

        return (
            f"## {title}\n\n"
            f"**Key Sections:**\n{heading_md}\n\n"
            f"**Content:**\n\n{body[:4000]}"
        )

    except Exception as e:
        return f"**Scrape failed:** `{str(e)}`"