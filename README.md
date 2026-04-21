# GEO & SEO Hybrid Content Writer Skill

> An AI Agent Skill designed to transform a target SEO keyword into a fully-optimized Markdown blog post and a premium, responsive HTML landing page using Generative Engine Optimization (GEO) principles.

## 🚀 What is this?
This repository contains an AI *Skill Profile* (`SKILL.md`). It is a highly-structured prompt designed to be loaded into AI coding assistants and agents (such as **Claude Code, Cursor, OpenClaw, GitHub Copilot, etc.**).

By giving your AI assistant access to this skill, you upgrade it into a **Top-tier SEO Copywriter + Elite Frontend Developer**, capable of generating "double-threat" content that ranks on traditional search engines (Google) AND AI engines (Perplexity, SearchGPT).

## 💡 How to use this Skill

### 1. Run the Keyword Distiller (Optional but Recommended)
This repo contains the `distiller/` directory which acts as the data-engine.
```bash
cd distiller
python install.py
python run.py "your keyword"
```
The distiller will crawl DuckDuckGo, analyze the top 10 competitors, and generate a cognitive-level content strategy inside `output/`.

### 2. Load the Writer Skill into your AI
Copy this folder into your workspace or point your AI assistant (Cursor / Claude) to the `SKILL.md` file located in the root of this repo.

### 3. Trigger the Workflow
In your AI chat/terminal, type:
> *"Load geo-hybrid-content-writer skill and write content for [YOUR_KEYWORD]"*

### 4. Provide Strategy Context (Prerequisite)
This writing agent performs best when it reads a *Content Strategy*. 
- If you used the `distiller/run.py` script above, make sure the `<keyword>_content_strategy.skill/SKILL.md` file is present in your workspace.
- If you do not have one, you can paste 2-3 competitor articles into the chat and say: *"Analyze these competitors and execute the GEO content writer skill based on them."*

### 5. What you get from the AI
The AI will automatically output:
1. `_blog.md`: A 1500+ word, highly structured Markdown article optimized with Cognitive Beliefs and E-E-A-T signals.
2. `_landing/index.html`: A high-converting HTML landing page maintaining 1:1 content fidelity from the MD file.
3. `_landing/styles.css`: Premium Glassmorphism & dark-mode styling.
4. `_landing/script.js`: Scroll-intersection micro-animations.

## 🎯 The "Hybrid" Moat (SEO + GEO)
This workflow ensures you survive the search transition:
- **Traditional SEO (Googlebot):** Strictly semantic HTML tags, proper length, and keyword phrase mapping.
- **Generative Engine Optimization (GEO):** Content is packed with a *Cognitive Layer* and *E-E-A-T stats*, inducing LLM-based search engines to extract your points as citations and verified answers.
