import json
import csv
import os

def main():
    base_dir = r"c:\Users\rmk spandanaa\Downloads\India Runs"
    candidates_file = os.path.join(base_dir, "[PUB] India_runs_data_and_ai_challenge", "[PUB] India_runs_data_and_ai_challenge", "India_runs_data_and_ai_challenge", "candidates.jsonl")
    submission_file = os.path.join(base_dir, "submission.csv")
    output_html = os.path.join(base_dir, "dashboard.html")
    
    if not os.path.exists(submission_file):
        print(f"Error: {submission_file} does not exist. Run rank.py first.")
        return
        
    print("Loading top 100 ranks and reasoning from submission.csv...")
    ranks = {}
    with open(submission_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader) # skip header
        for row in reader:
            if row:
                cid, rank, score, reasoning = row
                ranks[cid] = {
                    "rank": int(rank),
                    "score": float(score),
                    "reasoning": reasoning
                }
                
    print("Streaming candidates.jsonl to extract full details...")
    top_candidates = [None] * 100 # Preallocate to maintain sorting by rank
    
    with open(candidates_file, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            c = json.loads(line)
            cid = c["candidate_id"]
            if cid in ranks:
                rank_info = ranks[cid]
                # Combine original candidate data with rank, score, and reasoning
                c["rank"] = rank_info["rank"]
                c["score"] = rank_info["score"]
                c["reasoning"] = rank_info["reasoning"]
                
                # Insert at correct index (rank is 1-indexed)
                top_candidates[rank_info["rank"] - 1] = c
                
    # Filter out any None values in case some IDs weren't found
    top_candidates = [tc for tc in top_candidates if tc is not None]
    print(f"Loaded full profiles for {len(top_candidates)} candidates.")
    
    # HTML + CSS + JS Template
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HireMind AI - Recruiter Intelligence Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-base: #0B0F19;
            --bg-surface: rgba(17, 24, 39, 0.7);
            --bg-surface-hover: rgba(31, 41, 55, 0.8);
            --border-color: rgba(255, 255, 255, 0.08);
            --accent-primary: #8B5CF6; /* Purple */
            --accent-secondary: #06B6D4; /* Cyan */
            --text-primary: #F3F4F6;
            --text-secondary: #9CA3AF;
            --text-muted: #6B7280;
            --success: #10B981;
            --warning: #F59E0B;
            --danger: #EF4444;
            --glow-color: rgba(139, 92, 246, 0.15);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Plus Jakarta Sans', sans-serif;
            scrollbar-width: thin;
            scrollbar-color: var(--border-color) transparent;
        }

        body {
            background-color: var(--bg-base);
            background-image: 
                radial-gradient(at 0% 0%, rgba(139, 92, 246, 0.12) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(6, 182, 212, 0.08) 0px, transparent 50%);
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
        }

        header {
            background: rgba(11, 15, 25, 0.8);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border-color);
            padding: 1.25rem 2rem;
            position: sticky;
            top: 0;
            z-index: 100;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo-container {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .logo-icon {
            width: 2.25rem;
            height: 2.25rem;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            border-radius: 0.75rem;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-family: 'Outfit', sans-serif;
            color: white;
            box-shadow: 0 0 15px rgba(139, 92, 246, 0.4);
        }

        .logo-text {
            font-family: 'Outfit', sans-serif;
            font-size: 1.5rem;
            font-weight: 800;
            letter-spacing: -0.5px;
            background: linear-gradient(to right, #FFFFFF, #D1D5DB);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .logo-tag {
            font-size: 0.7rem;
            background: rgba(139, 92, 246, 0.15);
            color: #C084FC;
            padding: 0.2rem 0.5rem;
            border-radius: 0.5rem;
            border: 1px solid rgba(139, 92, 246, 0.3);
            font-weight: 600;
        }

        .jd-badge {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border-color);
            padding: 0.5rem 1rem;
            border-radius: 0.75rem;
            font-size: 0.85rem;
            color: var(--text-secondary);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .jd-badge strong {
            color: var(--accent-secondary);
        }

        .main-container {
            display: flex;
            flex: 1;
            padding: 1.5rem 2rem;
            gap: 1.5rem;
            height: calc(100vh - 70px);
            overflow: hidden;
        }

        /* Sidebar / Controls Panel */
        .sidebar {
            width: 320px;
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 1rem;
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
            overflow-y: auto;
            backdrop-filter: blur(8px);
        }

        .section-title {
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--accent-secondary);
            font-weight: 700;
            margin-bottom: 0.5rem;
        }

        .slider-group {
            display: flex;
            flex-direction: column;
            gap: 0.85rem;
        }

        .slider-item {
            display: flex;
            flex-direction: column;
            gap: 0.4rem;
        }

        .slider-header {
            display: flex;
            justify-content: space-between;
            font-size: 0.85rem;
            font-weight: 500;
            color: var(--text-secondary);
        }

        .slider-val {
            color: var(--text-primary);
            font-weight: 600;
        }

        input[type="range"] {
            -webkit-appearance: none;
            width: 100%;
            height: 6px;
            background: rgba(255, 255, 255, 0.08);
            border-radius: 3px;
            outline: none;
        }

        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background: var(--accent-primary);
            cursor: pointer;
            box-shadow: 0 0 10px var(--accent-primary);
            transition: transform 0.1s;
        }

        input[type="range"]::-webkit-slider-thumb:hover {
            transform: scale(1.2);
        }

        .filter-group {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }

        .search-box {
            position: relative;
        }

        .search-input {
            width: 100%;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border-color);
            border-radius: 0.75rem;
            padding: 0.75rem 1rem 0.75rem 2.25rem;
            color: var(--text-primary);
            font-size: 0.85rem;
            outline: none;
            transition: border-color 0.2s, box-shadow 0.2s;
        }

        .search-input:focus {
            border-color: var(--accent-primary);
            box-shadow: 0 0 10px var(--glow-color);
        }

        .search-icon {
            position: absolute;
            left: 0.85rem;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-muted);
            font-size: 0.9rem;
        }

        .select-input {
            width: 100%;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border-color);
            border-radius: 0.75rem;
            padding: 0.75rem;
            color: var(--text-primary);
            font-size: 0.85rem;
            outline: none;
            cursor: pointer;
        }

        .select-input option {
            background-color: var(--bg-base);
            color: var(--text-primary);
        }

        .btn-apply {
            background: linear-gradient(135deg, var(--accent-primary), #6D28D9);
            color: white;
            border: none;
            border-radius: 0.75rem;
            padding: 0.75rem 1rem;
            font-weight: 600;
            font-size: 0.9rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 4px 12px rgba(139, 92, 246, 0.25);
        }

        .btn-apply:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 16px rgba(139, 92, 246, 0.35);
        }

        .btn-apply:active {
            transform: translateY(1px);
        }

        /* Candidates List View */
        .list-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 1rem;
            backdrop-filter: blur(8px);
            overflow: hidden;
        }

        .list-header {
            padding: 1.25rem 1.5rem;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .list-title {
            font-family: 'Outfit', sans-serif;
            font-size: 1.15rem;
            font-weight: 700;
            color: white;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .candidates-count {
            font-size: 0.75rem;
            background: rgba(255, 255, 255, 0.05);
            padding: 0.2rem 0.5rem;
            border-radius: 0.5rem;
            color: var(--text-secondary);
            border: 1px solid var(--border-color);
        }

        .list-scroll {
            flex: 1;
            overflow-y: auto;
            padding: 1rem 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }

        .candidate-card {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border-color);
            border-radius: 0.85rem;
            padding: 1.2rem;
            cursor: pointer;
            transition: transform 0.2s, border-color 0.2s, background-color 0.2s, box-shadow 0.2s;
            display: flex;
            gap: 1.2rem;
            align-items: center;
            position: relative;
        }

        .candidate-card:hover {
            transform: translateX(4px);
            border-color: rgba(6, 182, 212, 0.3);
            background-color: rgba(255, 255, 255, 0.03);
            box-shadow: 0 4px 15px rgba(6, 182, 212, 0.04);
        }

        .candidate-card.active {
            border-color: var(--accent-secondary);
            background-color: rgba(6, 182, 212, 0.04);
            box-shadow: 0 0 15px rgba(6, 182, 212, 0.08);
        }

        .rank-badge {
            width: 2.25rem;
            height: 2.25rem;
            border-radius: 0.6rem;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Outfit', sans-serif;
            font-size: 1rem;
            font-weight: 700;
            color: var(--text-secondary);
            flex-shrink: 0;
        }

        .candidate-card:nth-child(1) .rank-badge {
            background: linear-gradient(135deg, #F59E0B, #D97706);
            color: white;
            border: none;
            box-shadow: 0 0 10px rgba(245, 158, 11, 0.3);
        }

        .candidate-card:nth-child(2) .rank-badge {
            background: linear-gradient(135deg, #9CA3AF, #4B5563);
            color: white;
            border: none;
        }

        .candidate-card:nth-child(3) .rank-badge {
            background: linear-gradient(135deg, #B45309, #78350F);
            color: white;
            border: none;
        }

        .card-info {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 0.3rem;
            min-width: 0;
        }

        .card-name-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
        }

        .card-name {
            font-size: 1.05rem;
            font-weight: 600;
            color: white;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .card-score {
            font-family: 'Outfit', sans-serif;
            font-weight: 700;
            color: var(--accent-secondary);
            font-size: 0.95rem;
        }

        .card-title {
            font-size: 0.85rem;
            color: var(--accent-primary);
            font-weight: 600;
        }

        .card-exp {
            font-size: 0.8rem;
            color: var(--text-secondary);
        }

        .card-tags {
            display: flex;
            gap: 0.4rem;
            flex-wrap: wrap;
            margin-top: 0.4rem;
        }

        .card-tag {
            font-size: 0.7rem;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid var(--border-color);
            padding: 0.15rem 0.45rem;
            border-radius: 0.4rem;
            color: var(--text-secondary);
        }

        .card-tag.highlight {
            background: rgba(6, 182, 212, 0.15);
            color: #22D3EE;
            border-color: rgba(6, 182, 212, 0.3);
        }

        /* Detail Panel */
        .detail-panel {
            width: 480px;
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 1rem;
            display: flex;
            flex-direction: column;
            overflow-y: auto;
            backdrop-filter: blur(8px);
            padding: 1.75rem;
            gap: 1.5rem;
        }

        .detail-placeholder {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: var(--text-muted);
            text-align: center;
            gap: 1rem;
        }

        .placeholder-icon {
            font-size: 3rem;
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(6, 182, 212, 0.2));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .detail-header {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 1.25rem;
        }

        .detail-name-row {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }

        .detail-name {
            font-family: 'Outfit', sans-serif;
            font-size: 1.4rem;
            font-weight: 700;
            color: white;
        }

        .detail-meta-text {
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-top: 0.25rem;
        }

        .reasoning-box {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.08), rgba(6, 182, 212, 0.04));
            border: 1px solid rgba(139, 92, 246, 0.2);
            border-radius: 0.75rem;
            padding: 1rem;
            position: relative;
            box-shadow: inset 0 0 10px rgba(139, 92, 246, 0.05);
        }

        .reasoning-title {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #C084FC;
            font-weight: 700;
            margin-bottom: 0.35rem;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }

        .reasoning-text {
            font-size: 0.85rem;
            color: var(--text-primary);
            line-height: 1.45;
            font-style: italic;
        }

        .metric-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 0.75rem;
        }

        .metric-card {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border-color);
            border-radius: 0.75rem;
            padding: 0.85rem;
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }

        .metric-label {
            font-size: 0.75rem;
            color: var(--text-muted);
            font-weight: 500;
        }

        .metric-value {
            font-size: 1rem;
            font-weight: 600;
            color: var(--text-secondary);
        }

        .metric-value.highlight {
            color: var(--accent-secondary);
            font-family: 'Outfit', sans-serif;
            font-weight: 700;
        }

        .signals-title {
            font-size: 0.85rem;
            font-weight: 700;
            color: white;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 0.5rem;
            margin-top: 0.5rem;
        }

        .signals-list {
            display: flex;
            flex-direction: column;
            gap: 0.6rem;
        }

        .signal-row {
            display: flex;
            justify-content: space-between;
            font-size: 0.85rem;
        }

        .signal-label {
            color: var(--text-secondary);
        }

        .signal-val {
            color: var(--text-primary);
            font-weight: 600;
        }

        .signal-val.badge {
            background: rgba(16, 185, 129, 0.15);
            color: #34D399;
            border: 1px solid rgba(16, 185, 129, 0.3);
            padding: 0.05rem 0.4rem;
            border-radius: 0.35rem;
            font-size: 0.75rem;
        }

        .signal-val.badge.warning {
            background: rgba(245, 158, 11, 0.15);
            color: #FBBF24;
            border-color: rgba(245, 158, 11, 0.3);
        }

        .signal-val.badge.danger {
            background: rgba(239, 68, 68, 0.15);
            color: #F87171;
            border-color: rgba(239, 68, 68, 0.3);
        }

        .history-list {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .history-item {
            border-left: 2px solid var(--accent-primary);
            padding-left: 0.85rem;
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }

        .history-title-row {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }

        .history-title {
            font-size: 0.85rem;
            font-weight: 600;
            color: white;
        }

        .history-company {
            font-size: 0.8rem;
            color: var(--text-secondary);
        }

        .history-dates {
            font-size: 0.75rem;
            color: var(--text-muted);
        }

        .history-desc {
            font-size: 0.8rem;
            color: var(--text-secondary);
            line-height: 1.4;
            margin-top: 0.25rem;
        }

        /* Responsive */
        @media (max-width: 1024px) {
            .main-container {
                flex-direction: column;
                height: auto;
                overflow: visible;
            }
            .sidebar, .list-container, .detail-panel {
                width: 100%;
                height: auto;
                max-height: 500px;
            }
        }
    </style>
</head>
<body>
    <header>
        <div class="logo-container">
            <div class="logo-icon">HM</div>
            <div class="logo-text">HireMind AI</div>
            <div class="logo-tag">Ranking Engine</div>
        </div>
        <div style="display: flex; align-items: center; gap: 1rem;">
            <a href="upload.html" style="text-decoration: none; display: flex; align-items: center; gap: 0.5rem; background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary)); padding: 0.55rem 1.1rem; border-radius: 0.75rem; color: white; font-size: 0.85rem; font-weight: 600; box-shadow: 0 4px 12px rgba(139, 92, 246, 0.25); transition: all 0.2s; border: 1px solid rgba(255, 255, 255, 0.1);" onmouseover="this.style.transform='translateY(-1px)'; this.style.boxShadow='0 6px 16px rgba(139, 92, 246, 0.35)';" onmouseout="this.style.transform='none'; this.style.boxShadow='0 4px 12px rgba(139, 92, 246, 0.25)';">
                <span>📤</span> Upload Resumes
            </a>
            <div class="jd-badge">
                Target Job: <strong>Senior AI Engineer — Founding Team</strong>
            </div>
        </div>
    </header>

    <div class="main-container">
        <!-- Sidebar Controls -->
        <div class="sidebar">
            <div>
                <h3 class="section-title">Search & Filters</h3>
                <div class="filter-group">
                    <div class="search-box">
                        <span class="search-icon">🔍</span>
                        <input type="text" id="searchBar" class="search-input" placeholder="Search name, title, skill...">
                    </div>
                    <select id="locationFilter" class="select-input">
                        <option value="">All Locations</option>
                        <option value="noida">Noida / Noida preferred</option>
                        <option value="pune">Pune / Pune preferred</option>
                        <option value="willing">Willing to Relocate</option>
                    </select>
                    <select id="noticeFilter" class="select-input">
                        <option value="">All Notice Periods</option>
                        <option value="30">≤ 30 days (Immediate)</option>
                        <option value="60">≤ 60 days</option>
                    </select>
                </div>
            </div>

            <div>
                <h3 class="section-title">Re-Rank Weights</h3>
                <div class="slider-group">
                    <div class="slider-item">
                        <div class="slider-header">
                            <span>Semantic Cosine</span>
                            <span class="slider-val" id="valSemantic">35%</span>
                        </div>
                        <input type="range" id="wtSemantic" min="0" max="100" value="35">
                    </div>
                    <div class="slider-item">
                        <div class="slider-header">
                            <span>Experience Target</span>
                            <span class="slider-val" id="valExperience">25%</span>
                        </div>
                        <input type="range" id="wtExperience" min="0" max="100" value="25">
                    </div>
                    <div class="slider-item">
                        <div class="slider-header">
                            <span>Core Skill Match</span>
                            <span class="slider-val" id="valSkills">25%</span>
                        </div>
                        <input type="range" id="wtSkills" min="0" max="100" value="25">
                    </div>
                    <div class="slider-item">
                        <div class="slider-header">
                            <span>Behavior & Activity</span>
                            <span class="slider-val" id="valBehavior">15%</span>
                        </div>
                        <input type="range" id="wtBehavior" min="0" max="100" value="15">
                    </div>
                </div>
                <button id="reRankBtn" class="btn-apply" style="width: 100%; margin-top: 1.25rem;">
                    🔄 Recalculate & Re-Rank
                </button>
            </div>
        </div>

        <!-- Candidates List -->
        <div class="list-container">
            <div class="list-header">
                <h2 class="list-title">
                    Ranked Candidates
                    <span id="candidatesCount" class="candidates-count">100 Candidates</span>
                </h2>
            </div>
            <div class="list-scroll" id="candidatesList">
                <!-- Javascript fills this -->
            </div>
        </div>

        <!-- Detail Panel -->
        <div class="detail-panel" id="detailPanel">
            <div class="detail-placeholder">
                <div class="placeholder-icon">🤖</div>
                <h3>Select a Candidate</h3>
                <p>Click on any candidate card to inspect their full profile, career timeline, and behavioral scoring dashboard.</p>
            </div>
        </div>
    </div>

    <script>
        // Embed the compiled candidates dataset
        const candidatesData = DATA_PLACEHOLDER;

        // UI References
        const listContainer = document.getElementById('candidatesList');
        const detailPanel = document.getElementById('detailPanel');
        const searchBar = document.getElementById('searchBar');
        const locationFilter = document.getElementById('locationFilter');
        const noticeFilter = document.getElementById('noticeFilter');
        const countBadge = document.getElementById('candidatesCount');

        const wtSemantic = document.getElementById('wtSemantic');
        const wtExperience = document.getElementById('wtExperience');
        const wtSkills = document.getElementById('wtSkills');
        const wtBehavior = document.getElementById('wtBehavior');

        const valSemantic = document.getElementById('valSemantic');
        const valExperience = document.getElementById('valExperience');
        const valSkills = document.getElementById('valSkills');
        const valBehavior = document.getElementById('valBehavior');
        const reRankBtn = document.getElementById('reRankBtn');

        let selectedId = null;
        let activeCandidates = [...candidatesData];

        // Sliders updates
        const updateSliderVal = (slider, valElement) => {
            slider.addEventListener('input', () => {
                valElement.innerText = slider.value + '%';
            });
        };
        updateSliderVal(wtSemantic, valSemantic);
        updateSliderVal(wtExperience, valExperience);
        updateSliderVal(wtSkills, valSkills);
        updateSliderVal(wtBehavior, valBehavior);

        // Subscore Functions
        const getExpScore = (exp) => {
            if (5.0 <= exp && exp <= 9.0) return 1.0;
            if ((4.0 <= exp && exp < 5.0) || (9.0 < exp && exp <= 10.0)) return 0.85;
            if ((3.0 <= exp && exp < 4.0) || (10.0 < exp && exp <= 12.0)) return 0.65;
            if (exp > 12.0) return 0.4;
            return 0.1;
        };

        const getTitleScore = (title) => {
            const t = title.toLowerCase();
            if (t.includes('founding') || t.includes('lead') || t.includes('senior')) {
                if (t.includes('ai') || t.includes('ml') || t.includes('nlp') || t.includes('retrieval') || t.includes('search')) return 1.0;
            }
            if (t.includes('ai engineer') || t.includes('ml engineer') || t.includes('nlp engineer') || t.includes('search engineer') || t.includes('retrieval engineer')) return 0.95;
            if (t.includes('data scientist') || t.includes('machine learning engineer')) return 0.9;
            if (t.includes('backend') || t.includes('software') || t.includes('data engineer')) return 0.75;
            return 0.3;
        };

        const getSkillsScore = (skills) => {
            const core = ['nlp', 'llm', 'rag', 'vector database', 'search', 'retrieval', 'ranking', 'faiss', 'fine-tuning', 'mlops', 'pinecone', 'weaviate', 'milvus', 'qdrant', 'elasticsearch', 'pytorch', 'tensorflow'];
            let score = 0;
            let count = 0;
            skills.forEach(s => {
                const name = s.name.toLowerCase();
                if (s.duration_months > 0 && core.some(c => name.includes(c))) {
                    count++;
                    const profVal = { 'expert': 1.0, 'advanced': 0.8, 'intermediate': 0.6, 'beginner': 0.3 }[s.proficiency.toLowerCase()] || 0.4;
                    score += profVal;
                }
            });
            if (count === 0) return 0;
            return Math.min(1.0, (score / 5.0) + 0.1 * Math.min(count, 3));
        };

        const getBehaviorScore = (signals) => {
            let score = 1.0;
            if (signals.profile_completeness_score >= 80) score *= 1.05;
            else if (signals.profile_completeness_score < 50) score *= 0.8;

            const signup = new Date(signals.signup_date);
            const active = new Date(signals.last_active_date);
            const ref = new Date('2026-06-24');
            const diffDays = Math.floor((ref - active) / (1000 * 60 * 60 * 24));
            
            if (diffDays <= 15) score *= 1.05;
            else if (diffDays <= 45) score *= 0.95;
            else if (diffDays <= 90) score *= 0.8;
            else if (diffDays <= 180) score *= 0.6;
            else score *= 0.25;

            if (signals.recruiter_response_rate >= 0.8) score *= 1.05;
            else if (signals.recruiter_response_rate < 0.2) score *= 0.4;
            else if (signals.recruiter_response_rate < 0.5) score *= 0.75;

            if (signals.open_to_work_flag) score *= 1.1;
            else score *= 0.95;

            if (signals.notice_period_days <= 30) score *= 1.05;
            else if (signals.notice_period_days <= 90) score *= 0.85;
            else score *= 0.55;

            return score;
        };

        const getLocScore = (profile, signals) => {
            const loc = profile.location.toLowerCase();
            const relocate = signals.willing_to_relocate;
            const tier_1 = ['noida', 'pune', 'delhi', 'ncr', 'gurgaon', 'hyderabad', 'bangalore', 'chennai', 'mumbai'];
            
            if (loc.includes('noida') || loc.includes('pune')) return 1.0;
            if (tier_1.some(c => loc.includes(c))) return relocate ? 0.95 : 0.75;
            return relocate ? 0.85 : 0.4;
        };

        // Render functions
        const renderList = () => {
            listContainer.innerHTML = '';
            
            if (activeCandidates.length === 0) {
                listContainer.innerHTML = `
                    <div style="text-align: center; padding: 3rem 0; color: var(--text-muted);">
                        <p style="font-size: 1.5rem; margin-bottom: 0.5rem;">🔍 No Matches Found</p>
                        <p style="font-size: 0.85rem;">Try relaxing your search terms or filter constraints.</p>
                    </div>
                `;
                countBadge.innerText = '0 Matches';
                return;
            }

            countBadge.innerText = `${activeCandidates.length} Matches`;

            activeCandidates.forEach(c => {
                const card = document.createElement('div');
                card.className = `candidate-card ${selectedId === c.candidate_id ? 'active' : ''}`;
                card.onclick = () => selectCandidate(c.candidate_id);

                const topSkills = c.skills
                    .filter(s => s.duration_months > 0 && ['nlp', 'llm', 'rag', 'mlops', 'vector', 'search', 'milvus', 'weaviate', 'pinecone', 'qdrant', 'elasticsearch', 'pytorch', 'machine learning', 'deep learning'].some(cs => s.name.toLowerCase().includes(cs)))
                    .map(s => s.name)
                    .slice(0, 3);
                
                const skillsHtml = topSkills.map(s => `<span class="card-tag highlight">${s}</span>`).join('') || `<span class="card-tag">Python</span>`;

                card.innerHTML = `
                    <div class="rank-badge">${c.rank}</div>
                    <div class="card-info">
                        <div class="card-name-row">
                            <span class="card-name">${c.profile.anonymized_name}</span>
                            <span class="card-score">${c.score.toFixed(4)}</span>
                        </div>
                        <div class="card-title">${c.profile.current_title} @ ${c.profile.current_company}</div>
                        <div class="card-exp">${c.profile.years_of_experience.toFixed(1)} yrs exp • ${c.profile.location}</div>
                        <div class="card-tags">${skillsHtml}</div>
                    </div>
                `;
                listContainer.appendChild(card);
            });
        };

        const selectCandidate = (id) => {
            selectedId = id;
            
            // Re-render list to update active highlight class
            const cards = document.querySelectorAll('.candidate-card');
            activeCandidates.forEach((c, idx) => {
                if (c.candidate_id === id) {
                    cards[idx].classList.add('active');
                } else {
                    cards[idx].classList.remove('active');
                }
            });

            const c = candidatesData.find(cand => cand.candidate_id === id);
            if (!c) return;

            // Compute sub-scores for visual charts
            const expS = getExpScore(c.profile.years_of_experience);
            const titleS = getTitleScore(c.profile.current_title);
            const skillS = getSkillsScore(c.skills);
            const behS = getBehaviorScore(c.redrob_signals);
            const locS = getLocScore(c.profile, c.redrob_signals);

            const timelineHtml = c.career_history.map(job => `
                <div class="history-item">
                    <div class="history-title-row">
                        <span class="history-title">${job.title}</span>
                        <span class="history-dates">${job.start_date} - ${job.end_date || 'Present'}</span>
                    </div>
                    <div class="history-company">${job.company} (${job.company_size} employees)</div>
                    <p class="history-desc">${job.description}</p>
                </div>
            `).join('');

            const skillsListHtml = c.skills.map(s => `
                <div class="signal-row" style="padding: 0.2rem 0; border-bottom: 1px solid rgba(255,255,255,0.02)">
                    <span class="signal-label">${s.name} (${s.duration_months} mo)</span>
                    <span class="signal-val badge ${s.proficiency === 'expert' ? '' : s.proficiency === 'advanced' ? 'warning' : 'danger'}">${s.proficiency}</span>
                </div>
            `).join('');

            detailPanel.innerHTML = `
                <div class="detail-header">
                    <div class="detail-name-row">
                        <span class="detail-name">${c.profile.anonymized_name}</span>
                        <span class="logo-tag">Rank #${c.rank}</span>
                    </div>
                    <div class="card-title" style="font-size: 0.95rem;">${c.profile.current_title} @ ${c.profile.current_company}</div>
                    <div class="detail-meta-text">📍 ${c.profile.location}, ${c.profile.country} • 💼 ${c.profile.years_of_experience.toFixed(1)} Years of Experience</div>
                </div>

                <div class="reasoning-box">
                    <div class="reasoning-title">🪄 AI Engine Fit Reasoning</div>
                    <div class="reasoning-text">"${c.reasoning}"</div>
                </div>

                <h3 class="signals-title">Score Breakdown</h3>
                <div class="metric-grid">
                    <div class="metric-card">
                        <span class="metric-label">Weighted Score</span>
                        <span class="metric-value highlight">${c.score.toFixed(4)}</span>
                    </div>
                    <div class="metric-card">
                        <span class="metric-label">Exp Fit Score</span>
                        <span class="metric-value">${(expS * 100).toFixed(0)}%</span>
                    </div>
                    <div class="metric-card">
                        <span class="metric-label">Title Relevance</span>
                        <span class="metric-value">${(titleS * 100).toFixed(0)}%</span>
                    </div>
                    <div class="metric-card">
                        <span class="metric-label">Structured Skills</span>
                        <span class="metric-value">${(skillS * 100).toFixed(0)}%</span>
                    </div>
                </div>

                <h3 class="signals-title">Behavioral & Platform Signals</h3>
                <div class="signals-list">
                    <div class="signal-row">
                        <span class="signal-label">Profile Completeness</span>
                        <span class="signal-val">${c.redrob_signals.profile_completeness_score}%</span>
                    </div>
                    <div class="signal-row">
                        <span class="signal-label">Notice Period</span>
                        <span class="signal-val badge ${c.redrob_signals.notice_period_days <= 30 ? '' : c.redrob_signals.notice_period_days <= 60 ? 'warning' : 'danger'}">${c.redrob_signals.notice_period_days} Days</span>
                    </div>
                    <div class="signal-row">
                        <span class="signal-label">Recruiter Response Rate</span>
                        <span class="signal-val">${(c.redrob_signals.recruiter_response_rate * 100).toFixed(0)}%</span>
                    </div>
                    <div class="signal-row">
                        <span class="signal-label">Weekly Active Status</span>
                        <span class="signal-val badge">Active ${c.redrob_signals.last_active_date}</span>
                    </div>
                    <div class="signal-row">
                        <span class="signal-label">Expected Salary</span>
                        <span class="signal-val">₹${c.redrob_signals.expected_salary_range_inr_lpa.min} - ${c.redrob_signals.expected_salary_range_inr_lpa.max} LPA</span>
                    </div>
                    <div class="signal-row">
                        <span class="signal-label">Preferred Work Mode</span>
                        <span class="signal-val" style="text-transform: capitalize;">${c.redrob_signals.preferred_work_mode}</span>
                    </div>
                </div>

                <h3 class="signals-title">Skills Inventory</h3>
                <div class="signals-list" style="max-height: 180px; overflow-y: auto; padding-right: 0.25rem;">
                    ${skillsListHtml}
                </div>

                <h3 class="signals-title">Career Timeline</h3>
                <div class="history-list">
                    ${timelineHtml}
                </div>
            `;
        };

        // Re-ranking calculations in Javascript
        reRankBtn.onclick = () => {
            const wSemantic = parseFloat(wtSemantic.value) / 100;
            const wExperience = parseFloat(wtExperience.value) / 100;
            const wSkills = parseFloat(wtSkills.value) / 100;
            const wBehavior = parseFloat(wtBehavior.value) / 100;

            const sum = wSemantic + wExperience + wSkills + wBehavior;
            if (sum === 0) return;

            // Recalculate scores
            const rescores = candidatesData.map(c => {
                const expS = getExpScore(c.profile.years_of_experience);
                const titleS = getTitleScore(c.profile.current_title);
                const skillS = getSkillsScore(c.skills);
                
                // Estimate semantic similarity from current score
                const sim = c.score; 
                
                // Recalculate basic fit
                // Normalize sliders sum to 100%
                const normSemantic = wSemantic / sum;
                const normExperience = wExperience / sum;
                const normSkills = wSkills / sum;
                const normBehavior = wBehavior / sum;

                const basicFit = (normExperience * expS) + (normSkills * skillS) + (normSemantic * sim);
                
                const behaviorM = getBehaviorScore(c.redrob_signals);
                const locationM = getLocScore(c.profile, c.redrob_signals);

                // Final Score
                const newScore = basicFit * behaviorM * locationM;

                return {
                    ...c,
                    score: newScore
                };
            });

            // Sort candidates
            rescores.sort((a, b) => b.score - a.score);

            // Re-assign ranks
            rescores.forEach((c, idx) => {
                c.rank = idx + 1;
            });

            // Update candidate lists
            candidatesData.forEach(c => {
                const updated = rescores.find(r => r.candidate_id === c.candidate_id);
                if (updated) {
                    c.score = updated.score;
                    c.rank = updated.rank;
                }
            });

            filterAndRender();
        };

        // Filter and Search logic
        const filterAndRender = () => {
            const q = searchBar.value.toLowerCase();
            const locVal = locationFilter.value;
            const noticeVal = noticeFilter.value;

            activeCandidates = candidatesData.filter(c => {
                // Search match
                const matchName = c.profile.anonymized_name.toLowerCase().includes(q);
                const matchTitle = c.profile.current_title.toLowerCase().includes(q);
                const matchSkills = c.skills.some(s => s.name.toLowerCase().includes(q));
                
                const matchSearch = matchName || matchTitle || matchSkills;
                if (!matchSearch) return false;

                // Location match
                if (locVal === 'noida' && !c.profile.location.toLowerCase().includes('noida')) return false;
                if (locVal === 'pune' && !c.profile.location.toLowerCase().includes('pune')) return false;
                if (locVal === 'willing' && !c.redrob_signals.willing_to_relocate && !c.profile.location.toLowerCase().includes('noida') && !c.profile.location.toLowerCase().includes('pune')) return false;

                // Notice period match
                if (noticeVal && c.redrob_signals.notice_period_days > parseInt(noticeVal)) return false;

                return true;
            });

            // Re-sort current candidates by rank
            activeCandidates.sort((a, b) => a.rank - b.rank);

            renderList();
            
            // Re-open details panel for the first match or keep active selected
            if (activeCandidates.length > 0) {
                const currentActive = activeCandidates.find(c => c.candidate_id === selectedId);
                if (currentActive) {
                    selectCandidate(selectedId);
                } else {
                    selectCandidate(activeCandidates[0].candidate_id);
                }
            } else {
                detailPanel.innerHTML = `
                    <div class="detail-placeholder">
                        <div class="placeholder-icon">🤖</div>
                        <h3>No Candidate Selected</h3>
                        <p>No matches for current search criteria.</p>
                    </div>
                `;
            }
        };

        searchBar.oninput = filterAndRender;
        locationFilter.onchange = filterAndRender;
        noticeFilter.onchange = filterAndRender;

        // Initialize UI
        filterAndRender();
    </script>
</body>
</html>
"""
    
    # Replace placeholder with stringified JSON payload
    data_json = json.dumps(top_candidates, indent=2)
    rendered_html = html_template.replace("DATA_PLACEHOLDER", data_json)
    
    print(f"Writing self-contained recruiter dashboard to {output_html}...")
    with open(output_html, "w", encoding="utf-8") as out:
        out.write(rendered_html)
    print("Dashboard UI built successfully!")

if __name__ == "__main__":
    main()
