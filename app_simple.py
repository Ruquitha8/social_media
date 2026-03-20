"""
Streamlit App for Social Media Content Generator
Intelligent conversation-based: LLM extracts product info naturally → generates content pack.
Uses LangChain memory for context-aware conversation.
"""

import streamlit as st
import json
from datetime import datetime

from config_simple import (
    APP_TITLE,
    APP_ICON,
    PLATFORMS,
    TONES,
    CONTENT_TYPES,
)
from llm_handler_simple import LLMHandler
from image_handler_simple import ImageHandler
from conversation_manager import IntelligentConversationManager


# =======================
# PAGE CONFIG
# =======================
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
)

# =======================
# SIDEBAR CONFIGURATION
# =======================
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Platform selection (can be changed during conversation)
    selected_platform = st.selectbox(
        "📱 Target Platform",
        options=list(PLATFORMS.keys()),
        help="Select primary platform for content generation"
    )
    
    # Image generation count
    num_images = st.slider(
        "🖼️ Number of Images to Generate",
        min_value=0,
        max_value=5,
        value=1,
        help="0 = No images, 1-5 = Number of variations to create"
    )
    
    st.divider()
    st.info(
        f"**Selected Platform:** `{selected_platform.upper()}`\n\n"
        f"**Image Count:** {num_images} image(s)"
    )

# =======================
# SESSION STATE
# =======================
if "llm" not in st.session_state:
    try:
        st.session_state.llm = LLMHandler()
        st.session_state.img = ImageHandler()
        st.session_state.conversation_manager = IntelligentConversationManager()
    except Exception as e:
        st.error(f"❌ Failed to initialize: {e}")
        st.stop()

if "conversation" not in st.session_state:
    st.session_state.conversation = []

if "generated_content" not in st.session_state:
    st.session_state.generated_content = None

if "content_ready" not in st.session_state:
    st.session_state.content_ready = False

if "selected_platform" not in st.session_state:
    st.session_state.selected_platform = None

if "num_images" not in st.session_state:
    st.session_state.num_images = 1

# =======================
# INTELLIGENT CONVERSATION LOGIC
# =======================
def process_user_message(user_input: str):
    """Process user message through intelligent conversation manager."""
    if not user_input or not user_input.strip():
        return

    manager = st.session_state.conversation_manager

    # Add user message to conversation display
    st.session_state.conversation.append({"role": "user", "message": user_input})

    # Generate intelligent bot response (extracts info + asks smart follow-ups)
    bot_response = manager.generate_intelligent_response(user_input)

    # Add bot response to conversation display
    st.session_state.conversation.append({"role": "bot", "message": bot_response})

    # Check if ready to generate
    if manager.is_ready_to_generate():
        st.session_state.content_ready = True

    st.rerun()


def generate_content_pack():
    """Generate full content pack from extracted product info."""
    manager = st.session_state.conversation_manager
    info = manager.get_product_info()

    if not all([info["name"], info["description"], info["platform"], info["tone"], info["content_type"]]):
        st.error("❌ Missing product information. Please complete the conversation.")
        return

    try:
        with st.spinner("🔄 Generating content pack..."):
            # Generate post content for selected platform
            result = st.session_state.llm.generate_post(
                product_name=info["name"],
                product_description=info["description"],
                platform=info["platform"],
                tone=info["tone"],
                content_type=info["content_type"],
            )

            st.session_state.generated_content = {
                "timestamp": datetime.now().isoformat(),
                "platform": info["platform"],
                "product": info["name"],
                "tone": info["tone"],
                "content_type": info["content_type"],
                "num_images_requested": st.session_state.num_images,
                **result,
            }

            # Generate images if requested
            images = []
            image_paths = []
            if st.session_state.num_images > 0:
                try:
                    img_prompt = f"{info['description']} - {info['tone']} tone"
                    # generate_product_image returns a list of PIL Images
                    images = st.session_state.img.generate_product_image(
                        product_name=info["name"],
                        product_description=img_prompt,
                        num_images=st.session_state.num_images,
                    )

                    # Save images to disk so they are JSON-serializable and downloadable
                    from pathlib import Path
                    out_dir = Path("outputs")
                    out_dir.mkdir(exist_ok=True)
                    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                    for idx, im in enumerate(images):
                        filename = f"{info['name'].replace(' ', '_')}_{ts}_{idx+1}.png"
                        path = out_dir / filename
                        try:
                            im.save(path)
                            image_paths.append(str(path))
                        except Exception as e:
                            print(f"⚠️  Could not save image {idx}: {e}")

                    if image_paths:
                        st.session_state.generated_content["image_paths"] = image_paths
                        st.session_state.generated_content["image_prompt"] = img_prompt
                        st.session_state.generated_content["num_images_generated"] = len(image_paths)
                except Exception as e:
                    st.error(f"IMAGE ERROR: {e}")
                    raise e

            image_status = f"✅ {len(images)} image(s) generated" if images else "⏭️ No images requested"

            st.session_state.conversation.append(
                {
                    "role": "bot",
                    "message": f"🎉 **Content pack generated for {info['platform'].upper()}!**\n\n"
                    f"✅ Caption + Hashtags + Ad Copy + Description\n\n"
                    f"📸 {image_status}\n\n"
                    f"Check the right panel to see all content!",
                }
            )

            st.rerun()

    except Exception as e:
        st.error(f"❌ Error generating content: {e}")
        st.session_state.conversation.append(
            {"role": "bot", "message": f"❌ Error: {e}"}
        )


# =======================
# MAIN PAGE LAYOUT
# =======================
def main():
    """Main app layout with intelligent conversation."""
    st.title(APP_TITLE)
    st.markdown("*Have a natural conversation to generate optimized social media content*")

    col_left, col_right = st.columns([1, 2])

    # =======================
    # LEFT: INTELLIGENT CONVERSATION
    # =======================
    with col_left:
        st.header("💬 Smart Chat")
        st.markdown("*Just chat naturally! I'll extract product info & generate content.*")

        # Display conversation history
        conv_container = st.container()
        with conv_container:
            if st.session_state.conversation:
                for msg in st.session_state.conversation:
                    if msg["role"] == "user":
                        st.write(f"👤 **You**: {msg['message']}")
                    elif msg["role"] == "bot":
                        st.write(f"🤖 **Bot**: {msg['message']}")
            else:
                # Initial greeting
                st.info("👋 **Hey there!** Tell me about your product and I'll help you create amazing social media content. Just chat naturally!")

        st.divider()

        # User input
        user_input = st.text_input(
            "Your message:",
            placeholder="Tell me about your product, platform, desired tone, etc...",
            key="user_input",
        )

        if st.button("📤 Send", key="send_btn", use_container_width=True):
            if user_input:
                process_user_message(user_input)

        st.divider()

        # Show collection status in a better format
        manager = st.session_state.conversation_manager
        info = manager.get_product_info()

        st.subheader("📊 Collection Status")
        
        # Create a nice status display
        status_items = [
            ("Product Name", info["name"]),
            ("Description", info["description"][:30] + "..." if info["description"] and len(info["description"]) > 30 else info["description"]),
            ("Platform", info["platform"]),
            ("Tone", info["tone"]),
            ("Content Type", info["content_type"]),
        ]
        
        # Use columns for compact display
        for label, value in status_items:
            col1, col2 = st.columns([1, 2])
            with col1:
                st.write(f"**{label}:**")
            with col2:
                if value:
                    st.write(f"✅ `{value}`")
                else:
                    st.write("⏳ *Waiting...*")

        st.divider()

        # Generate button (enabled when all info collected)
        if st.session_state.content_ready or manager.is_ready_to_generate():
            st.session_state.content_ready = True
            if st.button("🚀 Generate Content Pack", use_container_width=True, type="primary"):
                generate_content_pack()
        else:
            st.button("🚀 Generate Content Pack", use_container_width=True, disabled=True)

        # Clear button
        if st.button("🔄 Start Over", use_container_width=True):
            st.session_state.conversation = []
            st.session_state.generated_content = None
            st.session_state.content_ready = False
            st.session_state.conversation_manager = IntelligentConversationManager()
            st.rerun()

    # =======================
    # RIGHT: GENERATED CONTENT
    # =======================
    with col_right:
        st.header("✨ Generated Content")

        if st.session_state.generated_content:
            content = st.session_state.generated_content

            # Header info
            st.info(
                f"📱 **{content['platform'].upper()}** | "
                f"🎯 **{content['tone']}** | "
                f"📝 **{content['content_type']}**"
            )

            # Generated Images (if available)
            if content.get("image_paths"):
                st.subheader(f"🖼️ Generated Images ({len(content.get('image_paths', []))})")
                cols_img = st.columns(min(len(content.get("image_paths", [])), 3))
                for idx, image_path in enumerate(content.get("image_paths", [])):
                    with cols_img[idx % len(cols_img)]:
                        # image_path is a filesystem path to the saved image
                        st.image(image_path, width="stretch")
                        st.caption(f"Variant {idx + 1}")
                st.caption(f"📸 Prompt: {content.get('image_prompt', 'AI generated')}")
                st.divider()

            # Caption
            st.subheader("📝 Caption")
            st.text_area(
                "Post Caption",
                value=content.get("caption", ""),
                height=120,
                disabled=True,
                key="caption_display",
            )

            # Copy caption button
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📋 Copy Caption", key="copy_caption", use_container_width=True):
                    st.success("✅ Copied to clipboard!")
            with col2:
                if st.button("📝 Edit Caption", key="edit_caption", use_container_width=True):
                    st.write("*(Edit feature coming soon)*")

            st.divider()

            # Hashtags
            st.subheader("#️⃣ Hashtags")
            hashtags_list = content.get("hashtags", [])
            if hashtags_list:
                hashtags_str = " ".join([f"#{h}" for h in hashtags_list])
                st.text_area(
                    "Hashtags",
                    value=hashtags_str,
                    height=80,
                    disabled=True,
                    key="hashtags_display",
                )
                if st.button("📋 Copy Hashtags", key="copy_hashtags", use_container_width=True):
                    st.success("✅ Copied!")
            else:
                st.write("No hashtags generated")

            st.divider()

            # Ad Copy
            st.subheader("🎯 Ad Copy")
            st.text_area(
                "Ad Copy",
                value=content.get("ad_copy", ""),
                height=80,
                disabled=True,
                key="ad_copy_display",
            )

            if st.button("📋 Copy Ad Copy", key="copy_ad", use_container_width=True):
                st.success("✅ Copied!")

            st.divider()

            # Description
            st.subheader("📖 Description")
            st.text_area(
                "Product Description",
                value=content.get("description", ""),
                height=100,
                disabled=True,
                key="description_display",
            )

            st.divider()

            # Download as JSON - make a JSON-serializable copy
            serializable = {}
            from PIL import Image as PILImage
            for k, v in content.items():
                # Skip heavy/non-serializable image objects (we saved paths under image_paths)
                if isinstance(v, PILImage.Image):
                    # already saved to disk earlier; prefer paths
                    continue
                try:
                    json.dumps(v)
                    serializable[k] = v
                except TypeError:
                    serializable[k] = str(v)

            json_str = json.dumps(serializable, indent=2)
            st.download_button(
                label="📥 Download as JSON",
                data=json_str,
                file_name=f"content_{content['platform']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True,
            )

        else:
            if st.session_state.content_ready:
                st.info("👈 Click **Generate Content Pack** to see your content here!")
            else:
                st.info("👈 Have a natural conversation on the left to provide product details, then generate content!")


if __name__ == "__main__":
    main()

