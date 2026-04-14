import os
import json
from flask import Flask, render_template, request, Response, stream_with_context
from agents import run_search_agent, run_reader_agent, writer_chain, critic_chain, clean_output
from pipeline import extract_urls, invoke_with_retry

app = Flask(__name__)


# SSE helpers

def sse(event: str, data: dict) -> str:
    """Format a Server-Sent Event string."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


# Streaming pipeline generator 

def run_pipeline_streaming(topic: str):
    try:
        # 1. Search
        yield sse("status", {"step": "search", "message": "🔍 Searching the web..."})

        search_content = run_search_agent(topic)
        yield sse("search_done", {"content": search_content})

        #  2. Reader 
        yield sse("status", {"step": "reader", "message": "📄 Scraping sources..."})

        urls = extract_urls(search_content)
        scraped_content = run_reader_agent(urls)
        yield sse("reader_done", {"content": scraped_content})

        # 3. Writer
        yield sse("status", {"step": "writer", "message": "✍️ Writing research report..."})

        research_combined = (
            f"## Search Results\n\n{search_content}\n\n"
            f"## Scraped Page Content\n\n{scraped_content}"
        )
        raw_report = invoke_with_retry(
            writer_chain,
            {"topic": topic, "research": research_combined},
        )
        report = clean_output(raw_report)
        yield sse("report_done", {"content": report})

        # 4. Critic
        yield sse("status", {"step": "critic", "message": "🧐 Running editorial review..."})

        raw_critique = invoke_with_retry(critic_chain, {"report": report})
        critique = clean_output(raw_critique)
        yield sse("critique_done", {"content": critique})

        #  Done
        yield sse("done", {"message": "Pipeline complete."})

    except Exception as e:
        yield sse("error", {"message": str(e)})


#  Routes 

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/run")
def run():
    topic = request.args.get("topic", "").strip()
    if not topic:
        return Response(
            sse("error", {"message": "No topic provided."}),
            mimetype="text/event-stream",
        )

    return Response(
        stream_with_context(run_pipeline_streaming(topic)),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


#Entry point



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
