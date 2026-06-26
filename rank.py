import os
import json
import csv
import re
import argparse
from datetime import datetime
import numpy as np

# Standard library import of SentenceTransformer
from sentence_transformers import SentenceTransformer

# Consulting firms list (disqualifiers for lifers)
CONSULTING_FIRMS = {
    'tcs', 'tata consultancy services', 'infosys', 'wipro', 'accenture',
    'cognizant', 'capgemini', 'hcl', 'tech mahindra', 'l&t', 'larsen & toubro', 'mindtree'
}

# Reference date for activity calculation (current local time is late June 2026)
REF_DATE = datetime(2026, 6, 24)

def is_honeypot(c):
    """
    Returns True if the candidate has impossible or contradictory data (honeypots).
    """
    signals = c.get('redrob_signals', {})
    profile = c.get('profile', {})
    history = c.get('career_history', [])
    skills = c.get('skills', [])
    
    # 1. Last active date before signup date
    signup_s = signals.get('signup_date')
    last_act_s = signals.get('last_active_date')
    if signup_s and last_act_s:
        try:
            signup_dt = datetime.strptime(signup_s, "%Y-%m-%d")
            last_act_dt = datetime.strptime(last_act_s, "%Y-%m-%d")
            if last_act_dt < signup_dt:
                return True
        except ValueError:
            pass
            
    # 2. Skill duration contradiction (expert/advanced with 0 duration)
    for s in skills:
        if s.get('proficiency') == 'expert' and s.get('duration_months', -1) == 0:
            return True
            
    # 3. Job duration exceeds total years of experience (with small buffer)
    years_exp = profile.get('years_of_experience', 0)
    for job in history:
        dur_months = job.get('duration_months', 0)
        if dur_months > (years_exp + 1.5) * 12:
            return True
            
    # 4. Calendar start/end date vs duration mismatch
    for job in history:
        dur_months = job.get('duration_months', 0)
        start_s = job.get('start_date')
        end_s = job.get('end_date')
        if start_s:
            try:
                start_dt = datetime.strptime(start_s, "%Y-%m-%d")
                end_dt = datetime.strptime(end_s, "%Y-%m-%d") if end_s else REF_DATE
                diff_months = (end_dt.year - start_dt.year) * 12 + (end_dt.month - start_dt.month)
                if dur_months > diff_months + 12:  # Work duration exceeds calendar difference by over a year
                    return True
            except ValueError:
                pass
                
    # 5. Company founding year vs job start date or duration
    for job in history:
        desc = job.get('description', '').lower()
        dur_months = job.get('duration_months', 0)
        founding_match = re.search(r'founded\s+in\s+(\d{4})|established\s+in\s+(\d{4})|started\s+in\s+(\d{4})|inc\.\s+since\s+(\d{4})', desc)
        if founding_match:
            year_group = [g for g in founding_match.groups() if g]
            if year_group:
                founding_year = int(year_group[0])
                start_s = job.get('start_date')
                if start_s:
                    try:
                        start_year = datetime.strptime(start_s, "%Y-%m-%d").year
                        if start_year < founding_year:
                            return True
                        # If worked more months than the company has existed since founding to REF_DATE (2026)
                        max_possible_months = (REF_DATE.year - founding_year) * 12 + 6
                        if dur_months > max_possible_months + 12:
                            return True
                    except ValueError:
                        pass
                        
    return False

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        return REF_DATE

def coarse_filter(c):
    """
    Coarse filter to weed out completely irrelevant candidates quickly before embedding.
    We target candidates with >= 4 years of exp, exclude consulting lifers, ensure they have
    a tech title, check for specific AI/ML/NLP/Search keywords, and require at least one
    structured core AI/ML/Search skill.
    """
    profile = c.get('profile', {})
    skills = c.get('skills', [])
    history = c.get('career_history', [])
    
    # 1. Experience cutoff: must be at least 4 years
    years_exp = profile.get('years_of_experience', 0)
    if years_exp < 4.0:
        return False
        
    # 2. Exclude consulting firm lifers
    has_product_exp = False
    has_any_history = False
    for job in history:
        comp = job.get('company', '').lower()
        if comp:
            has_any_history = True
            is_consulting = any(firm in comp for firm in CONSULTING_FIRMS)
            if not is_consulting:
                has_product_exp = True
                break
    if has_any_history and not has_product_exp:
        return False  # Disqualify consulting firm lifers
        
    # 3. Ensure they have a tech title
    title = profile.get('current_title', '').lower()
    tech_title_words = {'engineer', 'scientist', 'developer', 'programmer', 'architect', 'lead', 'founder', 'head', 'specialist', 'expert', 'member'}
    if not any(w in title for w in tech_title_words):
        return False
        
    # 4. Disqualify keyword-stuffer non-tech fields (like plain HR, Graphic Designer, Accountant, Support)
    non_tech_roles = {'marketing', 'hr', 'recruiter', 'accountant', 'graphic', 'designer',
                      'support', 'sales', 'operations', 'civil', 'mechanical', 'finance'}
    if any(role in title for role in non_tech_roles):
        return False
            
    # 5. Core AI/ML/Search keyword checks: headline/summary must have at least some relevant words
    summary = profile.get('summary', '').lower()
    headline = profile.get('headline', '').lower()
    text_to_check = f"{title} {summary} {headline}".lower()
    
    # Extract exact words
    words = set(re.findall(r'\b[a-z]{2,}\b', text_to_check))
    interest_words = {'ai', 'ml', 'nlp', 'llm', 'rag', 'retrieval', 'search', 'embedding', 
                      'recommend', 'recommendation', 'vector', 'rank', 'ranking', 'mlops', 
                      'finetune', 'finetuning'}
                      
    has_interest = False
    if interest_words.intersection(words):
        has_interest = True
    elif "machine learning" in text_to_check or "deep learning" in text_to_check or "fine tuning" in text_to_check or "fine-tuning" in text_to_check:
        has_interest = True
        
    if not has_interest:
        return False
        
    # 6. Ensure they have at least one structured core AI/ML/Search skill in their profile
    core_skills = {
        'nlp', 'llm', 'rag', 'vector database', 'retrieval', 'ranking',
        'faiss', 'fine-tuning', 'mlops', 'pinecone', 'weaviate', 'milvus', 'qdrant',
        'machine learning', 'deep learning'
    }
    has_core_skill = False
    for s in skills:
        s_name = s.get('name', '').lower()
        # Ensure it has non-zero duration to filter out keyword stuffers
        if s.get('duration_months', 0) > 0 and any(cs in s_name for cs in core_skills):
            has_core_skill = True
            break
            
    if not has_core_skill:
        return False
        
    return True

def get_experience_score(exp):
    # Ideal range: 5 to 9 years
    if 5.0 <= exp <= 9.0:
        return 1.0
    elif 4.0 <= exp < 5.0 or 9.0 < exp <= 10.0:
        return 0.85
    elif 3.0 <= exp < 4.0 or 10.0 < exp <= 12.0:
        # Penalize slightly outside target band but still relevant
        return 0.65
    elif exp > 12.0:
        return 0.4
    else:
        return 0.1

def get_title_score(title):
    t = title.lower()
    if any(w in t for w in ['founding', 'lead', 'senior']) and any(w in t for w in ['ai', 'ml', 'nlp', 'retrieval', 'search', 'recommend']):
        return 1.0
    elif any(w in t for w in ['ai engineer', 'ml engineer', 'nlp engineer', 'applied ml', 'search engineer', 'retrieval engineer']):
        return 0.95
    elif any(w in t for w in ['data scientist', 'machine learning engineer']):
        return 0.9
    elif any(w in t for w in ['backend engineer', 'software engineer', 'data engineer', 'systems engineer']):
        return 0.75
    elif any(w in t for w in ['manager', 'lead']) and any(w in t for w in ['software', 'engineering', 'tech']):
        return 0.7
    else:
        return 0.3

def get_skill_score(skills):
    core_skills = {
        'nlp', 'llm', 'rag', 'vector database', 'search', 'retrieval', 'ranking',
        'faiss', 'fine-tuning', 'python', 'spark', 'mlops', 'pinecone', 'weaviate',
        'milvus', 'qdrant', 'opensearch', 'elasticsearch', 'pytorch', 'tensorflow'
    }
    
    score = 0.0
    valid_skills_count = 0
    for s in skills:
        name = s.get('name', '').lower()
        dur = s.get('duration_months', 0)
        prof = s.get('proficiency', '').lower()
        
        # Skip if 0 duration
        if dur == 0:
            continue
            
        # Match core skills
        is_core = any(cs in name for cs in core_skills)
        if is_core:
            valid_skills_count += 1
            # Add points based on proficiency
            prof_val = {'expert': 1.0, 'advanced': 0.8, 'intermediate': 0.6, 'beginner': 0.3}.get(prof, 0.4)
            score += prof_val
            
    # Normalize by core skills count (capped at 8 for a full score)
    if valid_skills_count == 0:
        return 0.0
    return min(1.0, (score / 5.0) + 0.1 * min(valid_skills_count, 3))

def get_behavioral_score(signals):
    score = 1.0
    
    # 1. Profile completeness
    completeness = signals.get('profile_completeness_score', 100)
    if completeness < 50:
        score *= 0.8
    elif completeness >= 80:
        score *= 1.05
        
    # 2. Activity / Last active
    last_act_s = signals.get('last_active_date')
    if last_act_s:
        last_act_dt = parse_date(last_act_s)
        days_inactive = (REF_DATE - last_act_dt).days
        if days_inactive <= 15:
            score *= 1.05
        elif days_inactive <= 45:
            score *= 0.95
        elif days_inactive <= 90:
            score *= 0.8
        elif days_inactive <= 180:
            score *= 0.6
        else:
            score *= 0.25  # Inactive lifer
            
    # 3. Recruiter response rate
    resp_rate = signals.get('recruiter_response_rate', 1.0)
    if resp_rate < 0.2:
        score *= 0.4
    elif resp_rate < 0.5:
        score *= 0.75
    elif resp_rate >= 0.8:
        score *= 1.05
        
    # 4. Open to work flag
    if signals.get('open_to_work_flag', False):
        score *= 1.1
    else:
        score *= 0.95
        
    # 5. Notice period days (prefer sub-30 days)
    notice = signals.get('notice_period_days', 60)
    if notice <= 30:
        score *= 1.05
    elif notice <= 60:
        score *= 1.0
    elif notice <= 90:
        score *= 0.85
    else:
        score *= 0.55  # long notice period
        
    return score

def get_location_score(profile, signals):
    loc = profile.get('location', '').lower()
    country = profile.get('country', '').lower()
    relocate = signals.get('willing_to_relocate', False)
    
    # Redrob JD prefers Pune/Noida, Delhi NCR, Hyderabad, Bangalore, Chennai, Mumbai
    tier_1_cities = {'noida', 'pune', 'delhi', 'ncr', 'gurgaon', 'hyderabad', 'bangalore', 'chennai', 'mumbai'}
    
    is_pune_noida = 'pune' in loc or 'noida' in loc
    is_tier_1 = any(c in loc for c in tier_1_cities)
    
    if is_pune_noida:
        return 1.0
    elif is_tier_1 and relocate:
        return 0.95
    elif is_tier_1 and not relocate:
        return 0.75
    elif relocate:
        return 0.85
    else:
        return 0.4

def generate_reasoning(c, rank, score):
    profile = c.get('profile', {})
    signals = c.get('redrob_signals', {})
    skills = c.get('skills', [])
    
    exp = profile.get('years_of_experience', 0)
    title = profile.get('current_title', '')
    loc = profile.get('location', '')
    notice = signals.get('notice_period_days', 60)
    resp_rate = int(signals.get('recruiter_response_rate', 0.5) * 100)
    
    # Filter for matching core AI/ML skills
    core_skills = {
        'nlp', 'llm', 'rag', 'vector database', 'search', 'retrieval', 'ranking',
        'faiss', 'fine-tuning', 'mlops', 'pinecone', 'weaviate', 'milvus', 'qdrant',
        'opensearch', 'elasticsearch', 'machine learning', 'deep learning', 'pytorch', 'tensorflow',
        'scikit-learn', 'pandas', 'numpy', 'python', 'spark'
    }
    matching_skills = []
    for s in skills:
        s_name = s.get('name', '')
        if any(cs in s_name.lower() for cs in core_skills) and s.get('duration_months', 0) > 0:
            matching_skills.append(s_name)
            
    if matching_skills:
        skills_s = ", ".join(matching_skills[:3])
    else:
        skill_names = [s.get('name') for s in skills if s.get('duration_months', 0) > 0][:3]
        skills_s = ", ".join(skill_names) if skill_names else "applied ML"
    
    reasons = []
    
    # Part 1: Experience & Title
    reasons.append(f"{title} with {exp:.1f} years of experience.")
    
    # Part 2: Skills and Location
    reasons.append(f"Strong match for JD core skills like {skills_s}. Located in {loc}.")
    
    # Part 3: Behavioral Signal / Notice Period / Warnings
    if notice <= 30:
        reasons.append(f"Highly active (response rate {resp_rate}%) and available immediately (notice period {notice} days).")
    else:
        reasons.append(f"Active job seeker (response rate {resp_rate}%) with a notice period of {notice} days.")
        
    return " ".join(reasons)


def main():
    parser = argparse.ArgumentParser(description="HireMind AI Candidate Ranking")
    parser.add_argument("--candidates", required=True, help="Path to candidates.jsonl file")
    parser.add_argument("--out", required=True, help="Path to write submission.csv")
    args = parser.parse_args()
    
    print(f"Loading local SentenceTransformer model from './embedding_model'...")
    local_model_path = os.path.join(os.path.dirname(__file__), "embedding_model")
    model = SentenceTransformer(local_model_path)
    
    # Job Description embedding query string
    jd_query = (
        "Senior AI Engineer founding team ML systems embeddings retrieval ranking LLMs fine-tuning search recommendation NLP"
    )
    jd_embedding = model.encode(jd_query, convert_to_numpy=True)
    
    print("Streaming and filtering candidates...")
    candidates = []
    count = 0
    filtered_count = 0
    
    # Stream the file to conserve RAM and keep it fast
    with open(args.candidates, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            count += 1
            
            c = json.loads(line)
            
            # Step 1: Honeypot check (hard exclude)
            if is_honeypot(c):
                continue
                
            # Step 2: Coarse filter
            if not coarse_filter(c):
                continue
                
            filtered_count += 1
            candidates.append(c)
            
    print(f"Total candidates scanned: {count}")
    print(f"Candidates remaining after filters: {filtered_count}")
    
    if filtered_count == 0:
        print("Warning: No candidates survived filtering!")
        return
        
    # Generate texts to embed for survivors
    print("Generating embeddings for filtered candidates...")
    texts_to_embed = []
    for c in candidates:
        profile = c.get('profile', {})
        skills = c.get('skills', [])
        skills_text = ", ".join([s.get('name', '') for s in skills if s.get('duration_months', 0) > 0])
        text = f"Title: {profile.get('current_title', '')}\nHeadline: {profile.get('headline', '')}\nSummary: {profile.get('summary', '')}\nSkills: {skills_text}"
        texts_to_embed.append(text)
        
    # Run batch embed
    candidate_embeddings = model.encode(texts_to_embed, convert_to_numpy=True, batch_size=64, show_progress_bar=True)
    
    # Compute similarity matrix
    norms_c = np.linalg.norm(candidate_embeddings, axis=1)
    norm_jd = np.linalg.norm(jd_embedding)
    similarities = np.dot(candidate_embeddings, jd_embedding) / (norms_c * norm_jd)
    
    print("Calculating final relevance scores...")
    candidate_scores = []
    for idx, c in enumerate(candidates):
        profile = c.get('profile', {})
        signals = c.get('redrob_signals', {})
        
        # Calculate sub-scores
        exp_score = get_experience_score(profile.get('years_of_experience', 0))
        title_score = get_title_score(profile.get('current_title', ''))
        skill_score = get_skill_score(c.get('skills', []))
        
        # Scale semantic similarity to [0.0, 1.0]
        sim = float(similarities[idx])
        sim_score = np.clip((sim - 0.2) / 0.5, 0.0, 1.0)
        
        # Calculate basic fit score
        basic_fit = 0.3 * exp_score + 0.3 * title_score + 0.2 * skill_score + 0.2 * sim_score
        
        # Apply modifiers
        behavior_modifier = get_behavioral_score(signals)
        location_modifier = get_location_score(profile, signals)
        
        final_score = basic_fit * behavior_modifier * location_modifier
        
        candidate_scores.append({
            "candidate_id": c["candidate_id"],
            "score": float(final_score),
            "candidate": c
        })
        
    # Sort candidates
    # Sort criteria: score descending, then candidate_id ascending for tie-break
    candidate_scores.sort(key=lambda x: (-x["score"], x["candidate_id"]))
    
    # Write top 100 to CSV
    top_100 = candidate_scores[:100]
    
    # Ensure scores are monotonically non-increasing (which sorting guarantees, but we should format them nicely)
    print(f"Writing top 100 ranked candidates to {args.out}...")
    with open(args.out, "w", encoding="utf-8", newline="") as out_f:
        writer = csv.writer(out_f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        
        for rank_idx, cs in enumerate(top_100):
            rank = rank_idx + 1
            cid = cs["candidate_id"]
            # Round score to 4 decimal places
            score = round(cs["score"], 4)
            reasoning = generate_reasoning(cs["candidate"], rank, score)
            writer.writerow([cid, rank, f"{score:.4f}", reasoning])
            
    print("Ranking successfully completed!")

if __name__ == "__main__":
    main()
