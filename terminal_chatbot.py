"""
Clean Terminal Marketing Chatbot
(Text-Only Version)
"""

import json
from datetime import datetime
from pathlib import Path

from llm_handler_simple import LLMHandler


# ==========================================
# SMART SEQUENTIAL CHATBOT
# ==========================================

class SmartChatbot:

    def __init__(self):
        self.product_info = {
            "name": None,
            "description": None,
            "platform": None,
            "tone": None,
            "content_type": None,
            "target_audience": None,
            "cta": None,
        }

    def next_question(self):
        for key, value in self.product_info.items():
            if value is None:
                if key == "name":
                    return "What is your product name?"
                elif key == "description":
                    return "Describe your product and its benefits."
                elif key == "platform":
                    return "Which platform? (Instagram / Facebook / LinkedIn)"
                elif key == "tone":
                    return "What tone do you prefer? (Professional / Casual / Energetic)"
                elif key == "content_type":
                    return "Content type? (Promotional / Educational)"
                elif key == "target_audience":
                    return "Who is your target audience?"
                elif key == "cta":
                    return "Any specific call-to-action?"
        return None

    def extract_info(self, text):
        text = text.strip()

        for key, value in self.product_info.items():
            if value is None:
                self.product_info[key] = text
                return

    def is_ready(self):
        return all(value is not None for value in self.product_info.values())


# ==========================================
# MAIN CHATBOT LOGIC
# ==========================================

print("\n🚀 AI Marketing Chatbot Starting...\n")

try:
    llm = LLMHandler()
    bot = SmartChatbot()
except Exception as e:
    print(f"❌ Initialization failed: {e}")
    exit()

print("✅ Ready!\n")
print("💬 Let's build your content step by step.")
print("Type 'generate' when ready or 'exit' to quit.\n")


def generate_content():
    info = bot.product_info

    print("\n🔄 Generating content...\n")

    result = llm.generate_post(
        product_name=info["name"],
        product_description=info["description"],
        platform=info["platform"],
        tone=info["tone"],
        content_type=info["content_type"],
    )

    print("=" * 60)
    print("📝 CAPTION:\n")
    print(result.get("caption", ""))

    print("\n#️⃣ HASHTAGS:\n")
    print(" ".join([f"#{h}" for h in result.get("hashtags", [])]))

    print("\n🎯 AD COPY:\n")
    print(result.get("ad_copy", ""))

    print("\n📖 DESCRIPTION:\n")
    print(result.get("description", ""))
    print("=" * 60)

    # Save JSON
    save = input("\n💾 Save as JSON? (y/n): ").strip().lower()
    if save == "y":
        out_dir = Path("outputs")
        out_dir.mkdir(exist_ok=True)
        filename = f"content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        path = out_dir / filename

        with open(path, "w") as f:
            json.dump(result, f, indent=2)

        print(f"✅ Saved to {path}\n")


# ==========================================
# CHAT LOOP
# ==========================================

while True:

    if not bot.is_ready():
        question = bot.next_question()
        print(f"\n🤖 {question}")

    user_input = input("👤 You: ").strip()

    if user_input.lower() == "exit":
        print("👋 Goodbye!")
        break

    if user_input.lower() == "generate":
        if bot.is_ready():
            generate_content()
        else:
            print("❌ Still missing information.")
        continue

    bot.extract_info(user_input)