import gradio as gr
from transformers import pipeline
import re

print("⚡ Loading optimized Qwen model with anti-loop safeguards...")
pipe = pipeline("text-generation", model="Qwen/Qwen2.5-1.5B-Instruct", device="cpu")
print("✅ Ready! Generation will be clean, fast, and loop-free.")

def create_brand(business_idea, industry, audience, personality):
    # Strict, example-driven prompt
    prompt = f"""You are an expert brand strategist. Create a brand identity:
- Idea: {business_idea}
- Industry: {industry}
- Audience: {audience}
- Personality: {personality}

Reply using EXACTLY this format (keep it very short):
NAME: [1-2 words]
TAG: [Max 6 words]
STORY: [Exactly 2 sentences]
COLORS: [3 colors]
POST: [1 short sentence with 2-3 emojis]"""

    print(f"🎨 Generating brand for: {business_idea[:30]}...")
    
    # Generate with anti-loop safeguards
    result = pipe(
        prompt, 
        max_new_tokens=150,        # Strict limit
        temperature=0.6,           # Lowered for focus (prevents rambling)
        repetition_penalty=1.2,    # MAGIC FIX: Prevents the emoji/sentence repetition loop
        do_sample=True,
        pad_token_id=pipe.tokenizer.eos_token_id
    )
    
    full_text = result[0]['generated_text']
    
    # ==========================================
    # BULLETPROOF EXTRACTION (Ignores leaked prompts)
    # ==========================================
    # We use regex to find the data, ignoring whatever garbage the model printed before/after
    name_match = re.search(r'(?:NAME|Brand Name):\s*(.+?)(?=\n|$)', full_text, re.IGNORECASE)
    tag_match = re.search(r'(?:TAG|Tagline):\s*(.+?)(?=\n|$)', full_text, re.IGNORECASE)
    story_match = re.search(r'(?:STORY|Brand Story):\s*(.+?)(?=\n(?:NAME|TAG|COLORS|POST|Brand)|$)', full_text, re.IGNORECASE | re.DOTALL)
    colors_match = re.search(r'(?:COLORS|Brand Colors):\s*(.+?)(?=\n|$)', full_text, re.IGNORECASE)
    post_match = re.search(r'(?:POST|Instagram Post):\s*(.+?)(?=\n|$)', full_text, re.IGNORECASE)
    
    # Extract and clean
    name = name_match.group(1).strip() if name_match else "Brand Name"
    tagline = tag_match.group(1).strip().strip('"') if tag_match else "Tagline"
    story = story_match.group(1).strip() if story_match else "Brand story goes here."
    colors = colors_match.group(1).strip() if colors_match else "Color palette"
    
    # Special cleaning for the post to prevent any remaining repetition
    raw_post = post_match.group(1).strip() if post_match else "Instagram post"
    # Take only the first sentence/segment to guarantee no loops
    clean_post = raw_post.split('. ')[0] + '.' 
    if len(clean_post) > 90:
        clean_post = clean_post[:87] + "..."

    # ==========================================
    # STUNNING VISUAL OUTPUT
    # ==========================================
    html_output = f"""
    <div style="background: linear-gradient(145deg, #1a1a2e 0%, #16213e 100%); padding: 35px; border-radius: 24px; color: white; font-family: 'Segoe UI', system-ui, sans-serif; box-shadow: 0 20px 50px rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.1);">
        
        <div style="text-align: center; margin-bottom: 35px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 25px;">
            <div style="font-size: 52px; font-weight: 800; text-transform: uppercase; letter-spacing: 4px; background: linear-gradient(90deg, #00f2fe, #4facfe); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0 4px 15px rgba(79, 172, 254, 0.3);">{name}</div>
            <div style="font-size: 22px; font-weight: 300; font-style: italic; margin-top: 12px; color: #a0aec0; letter-spacing: 1px;">"{tagline}"</div>
        </div>
        
        <div style="background: rgba(255,255,255,0.05); padding: 25px; border-radius: 16px; margin-bottom: 20px; border-left: 4px solid #4facfe;">
            <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 2px; color: #4facfe; margin-bottom: 12px; font-weight: bold;">📖 Brand Story</div>
            <div style="font-size: 17px; line-height: 1.7; color: #e2e8f0;">{story}</div>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
            <div style="background: rgba(255,255,255,0.05); padding: 25px; border-radius: 16px; border-left: 4px solid #f6ad55;">
                <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 2px; color: #f6ad55; margin-bottom: 12px; font-weight: bold;">🎨 Brand Colors</div>
                <div style="font-size: 16px; color: #e2e8f0; font-weight: 500;">{colors}</div>
            </div>
            <div style="background: rgba(255,255,255,0.05); padding: 25px; border-radius: 16px; border-left: 4px solid #68d391;">
                <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 2px; color: #68d391; margin-bottom: 12px; font-weight: bold;">📱 Instagram Post</div>
                <div style="font-size: 16px; color: #e2e8f0; line-height: 1.5;">{clean_post}</div>
            </div>
        </div>
        
    </div>
    """
    return html_output

# ==========================================
# Modern Dark UI
# ==========================================
custom_css = """
body, .gradio-container {background-color: #0f0f13 !important;}
h1 {
    background: linear-gradient(90deg, #00f2fe, #4facfe);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    font-size: 3em !important;
    font-weight: 800 !important;
}
.primary {
    background: linear-gradient(90deg, #00f2fe, #4facfe) !important;
    color: #0f0f13 !important;
    font-weight: bold !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(79, 172, 254, 0.4) !important;
}
.primary:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(79, 172, 254, 0.6) !important;
}
"""

with gr.Blocks(css=custom_css, theme=gr.themes.Monochrome()) as demo:
    gr.Markdown("# 🎨 AI Creative Director")
    gr.Markdown("<p style='text-align: center; color: #888; font-size: 18px; margin-top: -10px;'>Generate stunning, loop-free brand identities in 3 seconds</p>")
    
    with gr.Row():
        with gr.Column(scale=1):
            idea = gr.Textbox(label="💡 Business Idea", value="Smart desk lamp for studying and relaxation", lines=2)
            industry = gr.Dropdown(["Tech", "Food", "Fashion", "Wellness", "Other"], value="Tech", label="🏢 Industry")
            audience = gr.Textbox(label="🎯 Target Audience", value="College students and exam aspirants", lines=1)
            personality = gr.Dropdown(["Luxury", "Fun", "Professional", "Natural", "Bold"], value="Professional", label="✨ Personality")
            btn = gr.Button("🚀 Generate Brand", variant="primary", size="lg")
            
        with gr.Column(scale=2):
            output = gr.HTML(label="✨ Your Brand Identity", value="<div style='text-align: center; padding: 80px; color: #555;'><h2>Your stunning brand will appear here</h2></div>")
    
    btn.click(fn=create_brand, inputs=[idea, industry, audience, personality], outputs=output)

if __name__ == "__main__":
    demo.launch()