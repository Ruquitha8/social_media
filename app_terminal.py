"""
Terminal-based Social Media Content Generator
Conversation-driven intelligent content creation
"""

import json
from datetime import datetime
from pathlib import Path

from config_simple import PLATFORMS, TONES, CONTENT_TYPES
from llm_handler_simple import LLMHandler
from image_handler_simple import ImageHandler
from conversation_manager import IntelligentConversationManager


# ===============================
# INITIALIZATION
# ===============================
print("🚀 Initializing AI Social Media Generator...\n")

try:
    llm = LLMHandler()
    img = ImageHandler()
    manager = IntelligentConversationManager()
except Exception as e:
    print(f"❌ Initialization failed: {e}")
    exit()

print("✅ Ready!\n")
print("💬 Start chatting about your product.\nType 'generate' when ready.")
print("Type 'exit' to quit.\n")


# ===============================
# CONVERSATION LOOP
# ===============================
while True:
    user_input = input("👤 You: ")

    if user_input.lower() == "exit":
        print("👋 Goodbye!")
        break

    if user_input.lower() == "generate":
        if not manager.is_ready_to_generate():
            print("❌ Missing required information.")
            print("Please provide: Product Name, Description, Platform, Tone, Content Type.\n")
            continue

        info = manager.get_product_info()

        print("\n🔄 Generating content pack...\n")

        try:
            # Generate content
            result = llm.generate_post(
                product_name=info["name"],
                product_description=info["description"],
                platform=info["platform"],
                tone=info["tone"],
                content_type=info["content_type"],
            )

            output_data = {
                "timestamp": datetime.now().isoformat(),
                "platform": info["platform"],
                "product": info["name"],
                "tone": info["tone"],
                "content_type": info["content_type"],
                **result,
            }

            # ===============================
            # IMAGE GENERATION
            # ===============================
            num_images = int(input("🖼️ How many images to generate? (0-5): "))

            image_paths = []
            if num_images > 0:
                img_prompt = f"{info['description']} - {info['tone']} tone"
                images = img.generate_product_image(
                    product_name=info["name"],
                    product_description=img_prompt,
                    num_images=num_images,
                )

                out_dir = Path("outputs")
                out_dir.mkdir(exist_ok=True)
                ts = datetime.now().strftime('%Y%m%d_%H%M%S')

                for idx, im in enumerate(images):
                    filename = f"{info['name'].replace(' ', '_')}_{ts}_{idx+1}.png"
                    path = out_dir / filename
                    im.save(path)
                    image_paths.append(str(path))

                output_data["image_paths"] = image_paths
                output_data["image_prompt"] = img_prompt

                print(f"✅ {len(image_paths)} image(s) saved in /outputs\n")

            # ===============================
            # DISPLAY CONTENT
            # ===============================
            print("🎉 CONTENT PACK GENERATED\n")
            print("=====================================")
            print("📝 CAPTION:\n")
            print(result.get("caption", ""))
            print("\n-------------------------------------")

            print("#️⃣ HASHTAGS:\n")
            hashtags = result.get("hashtags", [])
            print(" ".join([f"#{h}" for h in hashtags]))
            print("\n-------------------------------------")

            print("🎯 AD COPY:\n")
            print(result.get("ad_copy", ""))
            print("\n-------------------------------------")

            print("📖 DESCRIPTION:\n")
            print(result.get("description", ""))
            print("\n=====================================\n")

            # ===============================
            # SAVE JSON
            # ===============================
            out_dir = Path("outputs")
            out_dir.mkdir(exist_ok=True)

            json_filename = f"content_{info['platform']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            json_path = out_dir / json_filename

            with open(json_path, "w") as f:
                json.dump(output_data, f, indent=2)

            print(f"📥 JSON saved at: {json_path}\n")

        except Exception as e:
            print(f"❌ Error generating content: {e}\n")

        continue

    # ===============================
    # NORMAL CHAT FLOW
    # ===============================
    bot_response = manager.generate_intelligent_response(user_input)
    print(f"\n🤖 Bot: {bot_response}\n")

    if manager.is_ready_to_generate():
        print("✅ All required info collected! Type 'generate' to create content.\n")