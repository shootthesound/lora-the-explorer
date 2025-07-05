"""
Gradio GUI for LoRA the Explorer operations
"""

import gradio as gr
import os
from typing import Optional
from .operations import subtract_loras, merge_loras, analyze_lora, target_lora_layers, selective_layer_merge
from .analysis import predict_compatibility
from .utils import find_lora_files, get_recent_loras, validate_lora_path
from .lora_cache import lora_cache

def create_gui(sd_scripts_path: Optional[str] = None) -> gr.Blocks:
    """Create the main LoRA the Explorer GUI
    
    Args:
        sd_scripts_path: Custom path to sd-scripts directory
        
    Returns:
        Gradio Blocks interface
    """
    
    # CSS styling
    css = """
    .operation-section { 
        border: 2px solid #e0e0e0; 
        border-radius: 8px; 
        padding: 15px; 
        margin: 10px 0; 
    }
    .success { color: #28a745; font-weight: bold; }
    .error { color: #dc3545; font-weight: bold; }
    .warning { color: #ffc107; font-weight: bold; }
    .info { color: #17a2b8; }
    .title { 
        text-align: center; 
        color: #2c3e50; 
        font-size: 2.5em; 
        margin-bottom: 0.5em; 
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .subtitle {
        text-align: center;
        color: #7f8c8d;
        font-size: 1.2em;
        margin-bottom: 2em;
    }
    
    /* Layer selection styling for A/B checkboxes - only when checked */
    .source-a-checkbox input[type="checkbox"]:checked {
        accent-color: #007bff !important;
        background-color: #007bff !important;
        border-color: #007bff !important;
    }
    
    .source-a-checkbox:has(input[type="checkbox"]:checked) {
        background-color: rgba(0, 123, 255, 0.2) !important;
        border: 1px solid rgba(0, 123, 255, 0.5) !important;
        border-radius: 4px !important;
        padding: 4px !important;
    }
    
    .source-a-checkbox:has(input[type="checkbox"]:checked) label {
        color: #007bff !important;
        font-weight: bold !important;
    }
    
    .source-b-checkbox input[type="checkbox"]:checked {
        accent-color: #dc3545 !important;
        background-color: #dc3545 !important;
        border-color: #dc3545 !important;
    }
    
    .source-b-checkbox:has(input[type="checkbox"]:checked) {
        background-color: rgba(220, 53, 69, 0.2) !important;
        border: 1px solid rgba(220, 53, 69, 0.5) !important;
        border-radius: 4px !important;
        padding: 4px !important;
    }
    
    .source-b-checkbox:has(input[type="checkbox"]:checked) label {
        color: #dc3545 !important;
        font-weight: bold !important;
    }
    
    /* Drag and drop styling */
    input[data-testid="textbox"]:focus {
        outline: 2px solid #2196f3 !important;
        outline-offset: 2px !important;
    }
    
    .drag-over {
        background-color: #e3f2fd !important;
        border-color: #2196f3 !important;
        border-width: 2px !important;
        border-style: dashed !important;
    }
    
    /* Autocomplete dropdown styling */
    .autocomplete-dropdown {
        margin-top: -10px !important;
        border: 1px solid #ddd !important;
        border-radius: 4px !important;
        background-color: #fff !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15) !important;
        max-height: 200px !important;
        overflow-y: auto !important;
    }
    
    .autocomplete-dropdown .svelte-select-list {
        max-height: 180px !important;
    }
    """
    
    with gr.Blocks(title="LoRA the Explorer", css=css, theme=gr.themes.Soft()) as demo:
        
        # Header
        gr.HTML("""
        <div class="title">🧭 LoRA the Explorer</div>
        <div class="subtitle">Advanced FLUX LoRA Manipulation Toolkit</div>
        """)
        
        with gr.Tabs() as tabs:
            
            # About Tab
            with gr.TabItem("ℹ️ About"):
                gr.Markdown("""
                ## LoRA the Explorer
                
                This tool provides various LoRA manipulation techniques including subtraction, merging, targeted layer merging between LoRAs, layer targeting for zeroing and analysis. It's designed to help you create compatible LoRAs and experiment with different combination approaches.
                """)
                
                with gr.Row():
                    with gr.Column(scale=2):
                        gr.Markdown("""
                ### What You Can Do:
                - **LoRA Subtraction**: Remove conflicts between LoRAs
                - **LoRA Merging**: Combine LoRAs with control over relative strengths.
                - **Layer-Based Merging**: Surgically combine specific layers from different LoRAs
                - **Layer Targeting**: Selectively mute facial or style layers
                - **LoRA MetaViewer**: Direct metadata viewing for LoRAs.
                - **LoRA MetaEditor**: Direct metadata editing for fixing Loras and customization (power users)
                - **Path Management**: Smart autocomplete and persistent settings
                - **New features in active development**
                
                ### Community Project
                I'm building this for the community and welcome your feedback, suggestions, and bug reports. The goal is to make LoRA manipulation more accessible and experimental for the many who are less comfortbale with CLI based tools or GUIs aimed at experts.
                
                ### Free to Use
                This tool is completely free. If you find it useful and want to support development, you can do so at:
                
                **☕ [buymeacoffee.com/loratheexplorer](https://buymeacoffee.com/loratheexplorer)**
                
                **Re-occuring supporters get early access to test new features as milestones arise in devlopment.**
                
                ### Getting Started
                1. **Set up paths**: Use the "LoRA Paths" tab to scan your LoRA directory for autocomplete, and choose your default save directory
                2. **Experiment**: Try different operations - each tab has usage guides and presets
                3. **Start simple**: Begin with basic merging or subtraction or trying advanced layer techniques. My tip is to find a great style lora and merge a character into it with face layers.
                
                ### Feedback Welcome
                Found a bug? Have a feature request? Want to share results? All feedback helps improve the tool for everyone. 
                
                **📧 Email**: pneill@gmail.com  
                **⭐ GitHub**: [github.com/shootthesound/lora-the-explorer](https://github.com/shootthesound/lora-the-explorer)
                
                ### Credits
                LoRA the Explorer relies on [sd-scripts by kohya-ss](https://github.com/kohya-ss/sd-scripts) for core LoRA processing functionality. Our installer automatically downloads the sd3 branch with FLUX support. Special thanks to kohya-ss and the sd-scripts community for this essential toolkit.
                
                **Demo Image LoRAs:**
                - [Eurasian Golden Oriole](https://civitai.green/models/1668493/eurasian-golden-oriole?modelVersionId=1888520) by hloveex30w126 on CivitAI
                - [Fantasy LoRA](https://civitai.green/models/789313?modelVersionId=1287297) by ArsMachina on CivitAI
                        """)
                    
                    with gr.Column(scale=1):
                        gr.Image(
                            value="demo.jpg",
                            label="Example: Bird character in fantasy armor",
                            show_label=False,
                            interactive=False,
                            width=400,
                            height=400,
                            elem_classes=["demo-image"]
                        )
                        gr.Markdown("""
                        <p style="text-align: center; color: #666; font-size: 0.9em; margin-top: 10px;">
                        Created using layer-based LoRA merging.<BR>See Loras merged in Credits at bottom of page.
                        </p>
                        """)
                        
                        # Method screenshot button and toggle
                        method_button = gr.Button("Tap here to see screenshot of settings used", size="sm", variant="secondary")
                        
                        method_image = gr.Image(
                            value="method.jpg",
                            label="Layer Merging Settings Used - Screenshot showing layer selections and parameters",
                            interactive=False,
                            show_label=True,
                            visible=False
                        )
            
            # LoRA Subtraction Tab
            with gr.TabItem("🔺 LoRA Subtraction"):
                gr.Markdown("""
                ### LoRA Compatibility tool
                
                **Subtract one LoRA from another to help remove conflicts and create compatible versions.**
                
                **Perfect for:**
                - Removing face changes from style LoRAs
                - Creating character-neutral styles  
                - Fixing LoRA interference issues
                - Can be useful pre layer merging as a possible approach to improve performance
                - As always experimentig is key
                """)
                
                with gr.Row():
                    with gr.Column():
                        with gr.Group(elem_classes="operation-section"):
                            gr.Markdown("#### LoRA A (To Keep)")
                            with gr.Row():
                                subtract_lora_a = gr.Textbox(
                                    label="LoRA A Path",
                                    placeholder="Path to the LoRA you want to preserve",
                                    lines=1,
                                    scale=4
                                )
                                subtract_lora_a_browse = gr.Button("📁", scale=1, min_width=40)
                            subtract_lora_a_dropdown = gr.Dropdown(
                                choices=[],
                                visible=False,
                                allow_custom_value=True,
                                label="📝 Click to select:",
                                show_label=True,
                                elem_classes=["autocomplete-dropdown"]
                            )
                            subtract_strength_a = gr.Slider(
                                label="LoRA A Strength",
                                minimum=0.1,
                                maximum=2.0,
                                value=1.0,
                                step=0.1
                            )
                        
                        with gr.Group(elem_classes="operation-section"):
                            gr.Markdown("#### LoRA B (To Subtract)")
                            with gr.Row():
                                subtract_lora_b = gr.Textbox(
                                    label="LoRA B Path", 
                                    placeholder="Path to the LoRA to subtract/remove",
                                    lines=1,
                                    scale=4
                                )
                                subtract_lora_b_browse = gr.Button("📁", scale=1, min_width=40)
                            subtract_lora_b_dropdown = gr.Dropdown(
                                choices=[],
                                visible=False,
                                allow_custom_value=True,
                                label="📝 Click to select:",
                                show_label=True,
                                elem_classes=["autocomplete-dropdown"]
                            )
                            subtract_strength_b = gr.Slider(
                                label="LoRA B Strength",
                                minimum=0.1,
                                maximum=2.0,
                                value=0.7,
                                step=0.1,
                                info="Recommended: ~85-90% of normal usage strength"
                            )
                        
                        with gr.Group(elem_classes="operation-section"):
                            gr.Markdown("#### Output Settings")
                            subtract_output = gr.Textbox(
                                label="Output Path",
                                placeholder=f"{lora_cache.get_default_output_path()}/cleaned_lora.safetensors",
                                value=f"{lora_cache.get_default_output_path()}/difference.safetensors"
                            )
                            
                            subtract_button = gr.Button(
                                "🔺 Extract Difference (A - B)", 
                                variant="primary",
                                size="lg"
                            )
                    
                    with gr.Column():
                        gr.Markdown("#### 💡 How to Use")
                        gr.Markdown("""
                        **Example: Clean a style LoRA that changes faces**
                        
                        1. **LoRA A**: Your style LoRA (e.g., `anime_style.safetensors`)
                        2. **LoRA B**: A character/face LoRA (e.g., `face_lora.safetensors`)
                        3. **Strength B**: Set to ~0.7 if you normally use face LoRA at 0.8
                        4. **Result**: Style LoRA without face interference
                        
                        **The Sweet Spot Formula:**
                        ```
                        Subtract Strength = Normal Usage × 0.85
                        ```
                        """)
                        
                        compatibility_check = gr.Button("🔍 Check Compatibility", variant="secondary")
                        compatibility_result = gr.Textbox(
                            label="Compatibility Analysis",
                            lines=8,
                            interactive=False
                        )
                
                subtract_result = gr.Textbox(
                    label="Operation Result",
                    lines=5,
                    interactive=False
                )
            
            # LoRA Merging Tab  
            with gr.TabItem("➕ LoRA Merging"):
                gr.Markdown("""
                ### Traditional LoRA Combination
                
                **Add two LoRAs together with custom weights.**
                
                Example usage: merging two loras trained on a given subject at 1.0 strength each can create a very effective lora when used at 0.4 strength at runtime.
                
                This is one technique of many to experiment with.
                """)
                
                with gr.Row():
                    with gr.Column():
                        with gr.Group(elem_classes="operation-section"):
                            gr.Markdown("#### LoRA A")
                            with gr.Row():
                                merge_lora_a = gr.Textbox(
                                    label="LoRA A Path",
                                    placeholder="Path to first LoRA",
                                    lines=1,
                                    scale=4
                                )
                                merge_lora_a_browse = gr.Button("📁", scale=1, min_width=40)
                            merge_lora_a_dropdown = gr.Dropdown(
                                choices=[],
                                visible=False,
                                allow_custom_value=True,
                                label="📝 Click to select:",
                                show_label=True,
                                elem_classes=["autocomplete-dropdown"]
                            )
                            merge_strength_a = gr.Slider(
                                label="LoRA A Strength",
                                minimum=0.1,
                                maximum=2.0,
                                value=1.0,
                                step=0.1,
                                interactive=True
                            )
                        
                        with gr.Group(elem_classes="operation-section"):
                            gr.Markdown("#### LoRA B")
                            with gr.Row():
                                merge_lora_b = gr.Textbox(
                                    label="LoRA B Path",
                                    placeholder="Path to second LoRA", 
                                    lines=1,
                                    scale=4
                                )
                                merge_lora_b_browse = gr.Button("📁", scale=1, min_width=40)
                            merge_lora_b_dropdown = gr.Dropdown(
                                choices=[],
                                visible=False,
                                allow_custom_value=True,
                                label="📝 Click to select:",
                                show_label=True,
                                elem_classes=["autocomplete-dropdown"]
                            )
                            merge_strength_b = gr.Slider(
                                label="LoRA B Strength",
                                minimum=0.1,
                                maximum=2.0,
                                value=1.0,
                                step=0.1,
                                interactive=True
                            )
                        
                        with gr.Group(elem_classes="operation-section"):
                            gr.Markdown("#### Output Settings")
                            merge_output = gr.Textbox(
                                label="Output Path",
                                placeholder=f"{lora_cache.get_default_output_path()}/merged_lora.safetensors",
                                value=f"{lora_cache.get_default_output_path()}/merged.safetensors"
                            )
                            merge_concat = gr.Checkbox(
                                label="Use Concat Mode",
                                value=False,
                                info="If enabled, allows loras of differnt Rank to merge (it will auto turn it on if this is detected), but LoRA will be bigger and sometimes you **may need to use much higher strengths for the LoRA in your generation environment** - experiment!"
                            )
                            
                            merge_button = gr.Button(
                                "➕ Merge LoRAs (A + B)",
                                variant="primary", 
                                size="lg"
                            )
                    
                    with gr.Column():
                        gr.Markdown("#### Recent LoRAs")
                        recent_loras_display = gr.Textbox(
                            label="Recently Modified LoRAs",
                            lines=10,
                            interactive=False,
                            value="Click 'Refresh' to load recent LoRAs",
                            max_lines=10
                        )
                        refresh_recent = gr.Button("🔄 Refresh Recent LoRAs")
                
                merge_result = gr.Textbox(
                    label="Operation Result",
                    lines=5,
                    interactive=False
                )
            
            # Layer Based LoRA Merging Tab
            with gr.TabItem("🔀 Layer Based LoRA Merging"):
                gr.Markdown("""
                ### Surgical LoRA Layer Merging
                
                **Selectively combine specific layers from two LoRAs to create the perfect hybrid.**
                
                **Key Features:**
                - Cherry-pick layers from each LoRA independently
                - Perfect character + style combinations  
                - Fix overtrained LoRAs by mixing clean layers
                - Create unique hybrid concepts
                """)
                
                with gr.Row():
                    with gr.Column():
                        with gr.Group(elem_classes="operation-section"):
                            gr.Markdown("#### Source LoRAs")
                            with gr.Row():
                                merge_lora_a_path = gr.Textbox(
                                    label="LoRA A Path",
                                    placeholder="Path to first source LoRA",
                                    lines=1,
                                    scale=4
                                )
                                merge_lora_a_path_browse = gr.Button("📁", scale=1, min_width=40)
                            merge_lora_a_path_dropdown = gr.Dropdown(
                                choices=[],
                                visible=False,
                                allow_custom_value=True,
                                label="📝 Click to select:",
                                show_label=True,
                                elem_classes=["autocomplete-dropdown"]
                            )
                            layer_merge_strength_a = gr.Slider(
                                label="LoRA A Strength",
                                minimum=0.0,
                                maximum=2.0,
                                value=1.0,
                                step=0.1,
                                info="Overall power multiplier for all layers from LoRA A"
                            )
                            with gr.Row():
                                merge_lora_b_path = gr.Textbox(
                                    label="LoRA B Path", 
                                    placeholder="Path to second source LoRA",
                                    lines=1,
                                    scale=4
                                )
                                merge_lora_b_path_browse = gr.Button("📁", scale=1, min_width=40)
                            merge_lora_b_path_dropdown = gr.Dropdown(
                                choices=[],
                                visible=False,
                                allow_custom_value=True,
                                label="📝 Click to select:",
                                show_label=True,
                                elem_classes=["autocomplete-dropdown"]
                            )
                            layer_merge_strength_b = gr.Slider(
                                label="LoRA B Strength", 
                                minimum=0.0,
                                maximum=2.0,
                                value=1.0,
                                step=0.1,
                                info="Overall power multiplier for all layers from LoRA B"
                            )
                            
                            gr.Markdown("#### Quick Select Presets")
                            with gr.Row():
                                merge_preset_face_style_btn = gr.Button("👤🎨 Face A + Style B", variant="secondary", size="sm")
                                merge_preset_facial_priority_btn = gr.Button("👤🔥 Facial Priority A + Style B", variant="secondary", size="sm")
                            with gr.Row():
                                merge_preset_complement_btn = gr.Button("⚖️ Complement Split", variant="secondary", size="sm")
                                merge_preset_clear_btn = gr.Button("❌ Clear All", variant="secondary", size="sm")
                                merge_preset_invert_btn = gr.Button("🔄 Swap A↔B", variant="secondary", size="sm")
                            
                            gr.Markdown("#### Layer Selection")
                            gr.Markdown("🔵 **Blue** = From LoRA A  |  🔴 **Red** = From LoRA B  |  ⚪ **Unchecked** = Exclude")
                            
                            # Create dual layer selection interface
                            with gr.Accordion("📋 Layer Source Selection (38 total)", open=False):
                                
                                # Text Encoder Layers (0-11)
                                with gr.Group():
                                    gr.Markdown("**Text Encoder Layers (0-11)**")
                                    merge_te_layers_a = {}
                                    merge_te_layers_b = {}
                                    for row_start in range(0, 12, 6):  # 6 per row for dual selection
                                        with gr.Row():
                                            for i in range(row_start, min(row_start + 6, 12)):
                                                with gr.Column(scale=1):
                                                    gr.Markdown(f"**TE{i}**")
                                                    merge_te_layers_a[i] = gr.Checkbox(
                                                        label="A", 
                                                        value=False,
                                                        elem_classes=["source-a-checkbox"]
                                                    )
                                                    merge_te_layers_b[i] = gr.Checkbox(
                                                        label="B",
                                                        value=False, 
                                                        elem_classes=["source-b-checkbox"]
                                                    )
                                
                                # UNet Double Block Layers (0-19)
                                with gr.Group():
                                    gr.Markdown("**UNet Double Block Layers (0-19)**")
                                    merge_double_layers_a = {}
                                    merge_double_layers_b = {}
                                    for row_start in range(0, 20, 5):  # 5 per row for dual selection
                                        with gr.Row():
                                            for i in range(row_start, min(row_start + 5, 20)):
                                                with gr.Column(scale=1):
                                                    gr.Markdown(f"**DB{i}**")
                                                    merge_double_layers_a[i] = gr.Checkbox(
                                                        label="A",
                                                        value=False,
                                                        elem_classes=["source-a-checkbox"]
                                                    )
                                                    merge_double_layers_b[i] = gr.Checkbox(
                                                        label="B",
                                                        value=False,
                                                        elem_classes=["source-b-checkbox"] 
                                                    )
                                
                                # UNet Single Block Layers (0-37)
                                with gr.Group():
                                    gr.Markdown("**UNet Single Block Layers (0-37)**")
                                    merge_single_layers_a = {}
                                    merge_single_layers_b = {}
                                    for row_start in range(0, 38, 5):  # 5 per row for dual selection
                                        with gr.Row():
                                            for i in range(row_start, min(row_start + 5, 38)):
                                                with gr.Column(scale=1):
                                                    gr.Markdown(f"**SB{i}**")
                                                    merge_single_layers_a[i] = gr.Checkbox(
                                                        label="A",
                                                        value=False,
                                                        elem_classes=["source-a-checkbox"]
                                                    )
                                                    merge_single_layers_b[i] = gr.Checkbox(
                                                        label="B", 
                                                        value=False,
                                                        elem_classes=["source-b-checkbox"]
                                                    )
                        
                        with gr.Group(elem_classes="operation-section"):
                            gr.Markdown("#### Output Settings")
                            merge_output_name = gr.Textbox(
                                label="Output Path",
                                placeholder=f"{lora_cache.get_default_output_path()}/hybrid_lora.safetensors",
                                value=f"{lora_cache.get_default_output_path()}/layer_merged.safetensors"
                            )
                            
                            merge_layer_button = gr.Button(
                                "🔀 Merge Selected Layers",
                                variant="primary",
                                size="lg"
                            )
                    
                    with gr.Column():
                        gr.Markdown("#### 💡 Use Cases & Strategies")
                        gr.Markdown("""
                        **👤🎨 Face A + Style B:**
                        - Standard facial layers (7,12,16,20) from character LoRA
                        - Style layers from artistic LoRA
                        - Perfect for clean, well-trained LoRAs
                        
                        **👤🔥 Facial Priority A + Style B:**
                        - ALL potential facial layers (4,7,8,12,15,16,19,20) from A
                        - Remaining layers from B for style
                        - Perfect for overtrained LoRAs with facial bleed
                        
                        **⚖️ Complement Split:**
                        - Early layers (0-18) from LoRA A
                        - Late layers (19-37) from LoRA B
                        - Structure from A, details from B
                        
                        **🔧 Fix Overtrained LoRAs:**
                        - Clean layers from good LoRA
                        - Fill problematic layers from better source
                        - Rescue partially corrupted LoRAs
                        
                        **🎭 Hybrid Concepts:**
                        - Mix two character LoRAs selectively
                        - Combine different training approaches
                        - Create unique style blends
                        
                        **⚡ Strength Control:**
                        - Boost facial features: A=1.2, B=1.0
                        - Tone down overpowering style: A=1.0, B=0.8
                        - Dramatic effects: Both above 1.0
                        - Subtle blending: Both below 1.0
                        
                        **⚠️ Conflict Detection:**
                        - Cannot select same layer from both A and B
                        - Preview shows layer assignments and strengths
                        - Validation before merge
                        """)
                        
                        merge_layer_preview = gr.Textbox(
                            label="Layer Assignment Preview",
                            lines=8,
                            interactive=False,
                            value="Select layers to see preview"
                        )
                
                merge_layer_result = gr.Textbox(
                    label="Operation Result",
                    lines=5,
                    interactive=False
                )
            
            # Layer Targeting Tab
            with gr.TabItem("🎯 Layer Targeting"):
                gr.Markdown("""
                ### FLUX Layer muting
                
                **Selectively mute facial (or style) layers in a single LoRA to preserve one while removing the other.**

                The agressive otpion removes data from more layers. If likeness of a subject beyond that persists, its likely down to spillover in training (possible overtraining), but you will at least be able to reduce the likeness to allow other LoRAs have greater effect in tandem.
                
                **Target Layers:**
                - **Layers 7 & 20**: Primary facial structure and details
                - **Layers 12 & 16**: Secondary facial features (optional)
                - **Layers 7,12,16,20**: Apart from facial details, these layers often hold lighting style information which can be useful to target for non-facial loras.


                """)
                
                with gr.Row():
                    with gr.Column():
                        with gr.Group(elem_classes="operation-section"):
                            gr.Markdown("#### Input LoRA")
                            with gr.Row():
                                target_lora_path = gr.Textbox(
                                    label="LoRA File Path",
                                    placeholder="Path to the LoRA you want to modify",
                                    lines=1,
                                    scale=4
                                )
                                target_lora_path_browse = gr.Button("📁", scale=1, min_width=40)
                            target_lora_path_dropdown = gr.Dropdown(
                                choices=[],
                                visible=False,
                                allow_custom_value=True,
                                label="📝 Click to select:",
                                show_label=True,
                                elem_classes=["autocomplete-dropdown"]
                            )
                            
                            gr.Markdown("#### Quick Select Presets")
                            with gr.Row():
                                preset_facial_btn = gr.Button("🎯 Facial Layers (7,12,16,20)", variant="secondary", size="sm")
                                preset_style_btn = gr.Button("🎨 Style Layers (Non-Facial)", variant="secondary", size="sm")
                                preset_aggressive_btn = gr.Button("🔥 Aggressive (4,7,8,12,15,16,19,20)", variant="secondary", size="sm")
                            with gr.Row():
                                preset_clear_btn = gr.Button("❌ Clear All", variant="secondary", size="sm")
                                preset_invert_btn = gr.Button("🔄 Invert Selection", variant="secondary", size="sm")
                            
                            gr.Markdown("#### Layer Selection")
                            
                            # Create dynamic layer checkboxes
                            with gr.Accordion("📋 All Layers (38 total)", open=False):
                                
                                # Text Encoder Layers (0-11)
                                with gr.Group():
                                    gr.Markdown("**Text Encoder Layers (0-11)**")
                                    te_layers = {}
                                    with gr.Row():
                                        for i in range(0, 12):
                                            te_layers[i] = gr.Checkbox(
                                                label=f"TE{i}",
                                                value=(i in [7]),  # Default: only layer 7
                                                scale=1
                                            )
                                
                                # UNet Double Block Layers (0-19) 
                                with gr.Group():
                                    gr.Markdown("**UNet Double Block Layers (0-19)**")
                                    double_layers = {}
                                    with gr.Row():
                                        for i in range(0, 20):
                                            double_layers[i] = gr.Checkbox(
                                                label=f"DB{i}",
                                                value=(i in [7, 12, 16]),  # Default facial layers
                                                scale=1
                                            )
                                
                                # UNet Single Block Layers (0-37)
                                with gr.Group():
                                    gr.Markdown("**UNet Single Block Layers (0-37)**")
                                    single_layers = {}
                                    for row_start in range(0, 38, 10):  # 10 per row
                                        with gr.Row():
                                            for i in range(row_start, min(row_start + 10, 38)):
                                                single_layers[i] = gr.Checkbox(
                                                    label=f"SB{i}",
                                                    value=(i in [7, 12, 16, 20]),  # Default facial layers
                                                    scale=1
                                                )
                        
                        with gr.Group(elem_classes="operation-section"):
                            gr.Markdown("#### Output Settings")
                            target_output_name = gr.Textbox(
                                label="Output Path", 
                                placeholder=f"{lora_cache.get_default_output_path()}/modified_lora.safetensors",
                                value=f"{lora_cache.get_default_output_path()}/face_muted.safetensors"
                            )
                            
                            target_button = gr.Button(
                                "🎯 Apply Layer Targeting",
                                variant="primary",
                                size="lg"
                            )
                    
                    with gr.Column():
                        gr.Markdown("#### 💡 Use Cases & Presets")
                        gr.Markdown("""
                        **🎯 Facial Layers (7,12,16,20):**
                        - Remove face while keeping style/costume
                        - Standard approach for character LoRAs
                        
                        **🎨 Style Layers (Non-Facial):**
                        - Preserve artistic style, lighting, composition
                        - Removes facial features from art style LoRAs
                        - Best for creating face-neutral artistic LoRAs
                        
                        **🔥 Aggressive (4,7,8,12,15,16,19,20):**
                        - Maximum facial identity removal
                        - For heavily overtrained LoRAs
                        - When faces "bleed" into other layers
                        
                        **🔄 Invert Selection:**
                        - Flip current selection instantly
                        - Useful for experimenting with opposite layer sets
                        
                        **Perfect Applications:**
                        - 🧙 Character style separation (Gandalf costume, no Ian McKellen face)
                        - 🎨 Art style cleaning (artistic techniques, no artist's face)  
                        - 👤 Universal character LoRAs (clothing/poses, no face changes)
                        - 🖼️ Remove styling from face LoRAs (keep face, remove artistic style/effects)
                        - ⚡ Clean face LoRAs for maximum flexibility (remove face data from non-facial layers to prevent style interference)
                        """)
                        
                        layer_preview = gr.Textbox(
                            label="Selected Layers to Mute",
                            lines=8,
                            interactive=False,
                            value="Layers 7, 20 will be muted"
                        )
                
                target_result = gr.Textbox(
                    label="Operation Result",
                    lines=5,
                    interactive=False
                )
                
            # Analysis Tab
            with gr.TabItem("🔍 LoRA MetaViewer"):
                gr.Markdown("""
                ### LoRA MetaViewer
                
                **Analyze LoRA files to understand their characteristics and predict compatibility.**
                """)
                
                with gr.Row():
                    with gr.Column():
                        with gr.Row():
                            analyze_path = gr.Textbox(
                                label="LoRA File Path",
                                placeholder="Path to LoRA file to analyze",
                                lines=1,
                                scale=4
                            )
                            analyze_path_browse = gr.Button("📁", scale=1, min_width=40)
                        analyze_path_dropdown = gr.Dropdown(
                            choices=[],
                            visible=False,
                            allow_custom_value=True,
                            label="📝 Click to select:",
                            show_label=True,
                            elem_classes=["autocomplete-dropdown"]
                        )
                        analyze_button = gr.Button(
                            "🔍 Analyze LoRA",
                            variant="primary"
                        )
                    
                    with gr.Column():
                        browse_directory = gr.Textbox(
                            label="Browse Directory",
                            placeholder="Directory to search for LoRAs",
                            value=lora_cache.get_default_output_path(),
                            lines=1
                        )
                        browse_button = gr.Button("📁 Find LoRA Files")
                
                with gr.Row():
                    with gr.Column():
                        analysis_result = gr.JSON(
                            label="LoRA MetaViewer Results",
                            visible=True
                        )
                    
                    with gr.Column():
                        found_files = gr.Textbox(
                            label="Found LoRA Files (Double-click to select)",
                            lines=15,
                            interactive=True,
                            info="Double-click on a line to use that LoRA for analysis",
                            max_lines=15
                        )
            

            # LoRA MetaEditor Tab
            with gr.TabItem("🏷️ LoRA MetaEditor"):
                gr.Markdown("""
                ### LoRA Metadata Editor
                
                **⚠️ WARNING: You are editing LoRA metadata directly!**
                - **Ensure you have backups before proceeding**
                - **Incorrect metadata can break your LoRA**
                - **You are responsible for any changes made** 
                - **Edit at your own risk!**
                
                This tool allows complete freedom to edit any metadata field in your LoRA files.
                """)
                
                with gr.Row():
                    with gr.Column():
                        with gr.Group(elem_classes="operation-section"):
                            gr.Markdown("#### Select LoRA File")
                            with gr.Row():
                                metaedit_lora_path = gr.Textbox(
                                    label="LoRA File Path",
                                    placeholder="Path to LoRA file to edit",
                                    lines=1,
                                    scale=4
                                )
                                metaedit_lora_browse = gr.Button("📁", scale=1, min_width=40)
                            metaedit_lora_dropdown = gr.Dropdown(
                                choices=[],
                                visible=False,
                                allow_custom_value=True,
                                label="📝 Click to select:",
                                show_label=True,
                                elem_classes=["autocomplete-dropdown"]
                            )
                            
                            metaedit_load_button = gr.Button("📂 Load Metadata", variant="primary")
                    
                    with gr.Column():
                        with gr.Group(elem_classes="operation-section"):
                            gr.Markdown("#### Metadata Editor")
                            metaedit_metadata = gr.Code(
                                label="Raw Metadata (JSON format)",
                                language="json",
                                lines=20,
                                interactive=True,
                                value="// Click 'Load Metadata' to see LoRA metadata here..."
                            )
                            
                            metaedit_save_button = gr.Button("💾 Save Changes", variant="secondary")
                            
                            metaedit_result = gr.Textbox(
                                label="Result",
                                lines=3,
                                interactive=False
                            )

             # LoRA Paths Tab
            with gr.TabItem("📁 LoRA Paths"):
                gr.Markdown("""
                ### LoRA Path Scanner
                
                **Scan directories for LoRA files to enable autocomplete in all path inputs.**
                """)
                
                with gr.Row():
                    with gr.Column():
                        with gr.Row():
                            scan_directory = gr.Textbox(
                                label="Base Directory",
                                placeholder="Path to directory containing LoRAs",
                                value=lora_cache.scan_directory or ".",
                                scale=4
                            )
                            scan_directory_browse = gr.Button("📁", scale=1, min_width=40)
                        
                        with gr.Row():
                            default_output_path = gr.Textbox(
                                label="Default Output Directory",
                                placeholder="Default directory for all output files",
                                value=lora_cache.get_default_output_path(),
                                scale=4
                            )
                            default_output_browse = gr.Button("📁", scale=1, min_width=40)
                        
                        with gr.Row():
                            scan_button = gr.Button("🔍 Scan LoRAs", variant="primary")
                            rescan_button = gr.Button("🔄 Rescan", variant="secondary")
                            save_settings_button = gr.Button("💾 Save Settings", variant="secondary")
                        
                        # Auto-scan on startup
                        auto_scan_success, auto_scan_message = lora_cache.auto_scan_on_startup()
                        cache_info = lora_cache.get_cache_info()
                        
                        if auto_scan_success:
                            initial_status = f"🔄 Auto-scan completed!\n{auto_scan_message}\n\n✅ Autocomplete ready for all path inputs"
                        elif cache_info['has_data']:
                            initial_status = f"✅ {cache_info['total_loras']} LoRAs loaded from cache\n\n✅ Autocomplete ready for all path inputs" 
                        else:
                            initial_status = "Ready to scan - Click 'Scan LoRAs' to begin"
                        
                        scan_status = gr.Textbox(
                            label="Scan Status",
                            lines=6,
                            interactive=False,
                            value=initial_status
                        )
            
        # Event Handlers
        def handle_subtract(lora_a, lora_b, strength_a, strength_b, output):
            try:
                # Validate inputs
                valid_a, msg_a = validate_lora_path(lora_a)
                if not valid_a:
                    return f"❌ LoRA A: {msg_a}"
                
                valid_b, msg_b = validate_lora_path(lora_b)
                if not valid_b:
                    return f"❌ LoRA B: {msg_b}"
                
                if not output:
                    return "❌ Please specify an output path"
                
                # Fix FLUX metadata if needed
                metadata_fixes_applied = []
                temp_files_to_cleanup = []
                
                try:
                    # Extract metadata from both LoRAs (same as analysis tab)
                    from .operations import analyze_lora
                    analysis_a = analyze_lora(lora_a, sd_scripts_path)
                    analysis_b = analyze_lora(lora_b, sd_scripts_path)
                    metadata_a = analysis_a.get('metadata', {})
                    metadata_b = analysis_b.get('metadata', {})
                    
                    # Check for layer-merged LoRAs (informational - subtract always uses concat)
                    has_layer_merged = 'lora_algebra_merge_type' in metadata_a or 'lora_algebra_merge_type' in metadata_b
                    
                    # Check and fix FLUX metadata if needed
                    def needs_network_fix(metadata):
                        is_flux = (
                            'flux' in metadata.get('modelspec.architecture', '').lower() or
                            metadata.get('ss_base_model_version', '') == 'flux1'
                        )
                        wrong_module = metadata.get('ss_network_module', '') == 'networks.lora'
                        return is_flux and wrong_module
                    
                    def create_fixed_lora(lora_path, metadata):
                        import tempfile
                        from safetensors import safe_open
                        from safetensors.torch import save_file
                        
                        # Create temp file
                        temp_fd, temp_path = tempfile.mkstemp(suffix='.safetensors')
                        os.close(temp_fd)
                        
                        # Load original LoRA
                        with safe_open(lora_path, framework="pt", device="cpu") as f:
                            state_dict = {key: f.get_tensor(key) for key in f.keys()}
                            original_metadata = dict(f.metadata()) if f.metadata() else {}
                        
                        # Fix metadata
                        fixed_metadata = original_metadata.copy()
                        fixed_metadata['ss_network_module'] = 'networks.lora_flux'
                        
                        # Save with fixed metadata
                        save_file(state_dict, temp_path, metadata=fixed_metadata)
                        return temp_path
                    
                    # Fix LoRA A if needed
                    if needs_network_fix(metadata_a):
                        lora_a = create_fixed_lora(lora_a, metadata_a)
                        temp_files_to_cleanup.append(lora_a)
                        metadata_fixes_applied.append("A")
                    
                    # Fix LoRA B if needed  
                    if needs_network_fix(metadata_b):
                        lora_b = create_fixed_lora(lora_b, metadata_b)
                        temp_files_to_cleanup.append(lora_b)
                        metadata_fixes_applied.append("B")
                        
                except Exception as e:
                    # If we can't process metadata, proceed with original files
                    print(f"Warning: Could not process metadata: {e}")
                    pass
                
                # Create output directory
                os.makedirs(os.path.dirname(output), exist_ok=True)
                
                # Perform subtraction (always use concat mode for best compatibility)
                try:
                    success, message = subtract_loras(
                        lora_a, lora_b, output, 
                        strength_a, strength_b, True, 
                        sd_scripts_path
                    )
                    
                    # Clean up temp files
                    for temp_file in temp_files_to_cleanup:
                        try:
                            os.unlink(temp_file)
                        except:
                            pass
                    
                    if success:
                        result_message = f"✅ {message}"
                        
                        if metadata_fixes_applied:
                            fixed_loras = " & ".join(metadata_fixes_applied)
                            result_message += f"\n\n🔧 Auto-fixed FLUX metadata for LoRA {fixed_loras} (networks.lora → networks.lora_flux)"
                        
                        return result_message
                    else:
                        # Enhanced error message with helpful suggestions
                        error_msg = f"❌ Error during subtraction: {message}"
                        if "shape mismatch" in message.lower() or "different dims" in message.lower() or "incompatible" in message.lower():
                            error_msg += "\n\n💡 This likely failed due to incompatibilities between the LoRAs."
                            error_msg += "\n   Try using different LoRAs or check that both are compatible FLUX LoRAs."
                            if has_layer_merged:
                                error_msg += "\n   (Layer-merged LoRA detected - these can sometimes have compatibility issues)"
                        return error_msg
                        
                except Exception as subtract_error:
                    # Clean up temp files even on error
                    for temp_file in temp_files_to_cleanup:
                        try:
                            os.unlink(temp_file)
                        except:
                            pass
                    raise subtract_error
                    
            except Exception as e:
                return f"❌ Error: {str(e)}"
        
        def handle_merge(lora_a, lora_b, strength_a, strength_b, output, use_concat):
            try:
                # Debug logging
                print(f"🎚️ GUI DEBUG: Received strength values - A: {strength_a} (type: {type(strength_a)}), B: {strength_b} (type: {type(strength_b)})")
                
                # Ensure strengths are floats
                strength_a = float(strength_a)
                strength_b = float(strength_b)
                
                print(f"🎚️ GUI DEBUG: After conversion - A: {strength_a}, B: {strength_b}")
                
                # Validate inputs
                valid_a, msg_a = validate_lora_path(lora_a)
                if not valid_a:
                    return f"❌ LoRA A: {msg_a}"
                
                valid_b, msg_b = validate_lora_path(lora_b)
                if not valid_b:
                    return f"❌ LoRA B: {msg_b}"
                
                if not output:
                    return "❌ Please specify an output path"
                
                # Check if concat mode should be automatically enabled and fix FLUX metadata
                auto_concat_enabled = False
                metadata_fixes_applied = []
                temp_files_to_cleanup = []
                
                try:
                    # Extract metadata from both LoRAs (same as analysis tab)
                    from .operations import analyze_lora
                    analysis_a = analyze_lora(lora_a, sd_scripts_path)
                    analysis_b = analyze_lora(lora_b, sd_scripts_path)
                    metadata_a = analysis_a.get('metadata', {})
                    metadata_b = analysis_b.get('metadata', {})
                    
                    # Check ranks and dimension complexity for auto-concat
                    auto_concat_reason = None
                    if not use_concat:
                        # Helper functions for dimension analysis
                        def extract_primary_rank(metadata):
                            # Try multiple possible keys for rank/dimension info
                            for key in ['network_dim', 'ss_network_dim', 'dim']:
                                if key in metadata:
                                    value = metadata[key]
                                    if isinstance(value, (list, tuple)) and len(value) > 0:
                                        return value[0]  # Use first rank for comparison
                                    elif isinstance(value, (int, float)):
                                        return int(value)
                                    elif isinstance(value, str):
                                        # Handle string representations like "[4]" or "4"
                                        try:
                                            if value.startswith('[') and value.endswith(']'):
                                                # Parse list format like "[4]" or "[4, 8]"
                                                import ast
                                                parsed = ast.literal_eval(value)
                                                if isinstance(parsed, list) and len(parsed) > 0:
                                                    return parsed[0]
                                            else:
                                                # Parse simple number
                                                return int(float(value))
                                        except:
                                            continue
                            
                            # Default fallback
                            return 32
                        
                        def has_mixed_dimensions(metadata):
                            # Check for mixed dimensions in any dimension field
                            for key in ['network_dim', 'ss_network_dim', 'dim']:
                                if key in metadata:
                                    dim_str = str(metadata[key])
                                    if '[' in dim_str and ',' in dim_str:
                                        return True
                            return False
                        
                        rank_a = extract_primary_rank(metadata_a)
                        rank_b = extract_primary_rank(metadata_b)
                        mixed_a = has_mixed_dimensions(metadata_a)
                        mixed_b = has_mixed_dimensions(metadata_b)
                        
                        # Check for rank differences
                        if rank_a != rank_b:
                            use_concat = True
                            auto_concat_enabled = True
                            auto_concat_reason = f"different ranks ({rank_a} vs {rank_b})"
                        
                        # Check for mixed dimension complexity differences
                        elif mixed_a != mixed_b:
                            use_concat = True
                            auto_concat_enabled = True
                            complexity_a = "mixed" if mixed_a else "uniform"
                            complexity_b = "mixed" if mixed_b else "uniform"
                            auto_concat_reason = f"different dimension structures ({complexity_a} vs {complexity_b})"
                        
                        # Check for layer-merged LoRAs (always need concat mode)
                        elif 'lora_algebra_merge_type' in metadata_a or 'lora_algebra_merge_type' in metadata_b:
                            use_concat = True
                            auto_concat_enabled = True
                            auto_concat_reason = "layer-merged LoRA detected"
                    
                    # Check and fix FLUX metadata if needed
                    def needs_network_fix(metadata):
                        is_flux = (
                            'flux' in metadata.get('modelspec.architecture', '').lower() or
                            metadata.get('ss_base_model_version', '') == 'flux1'
                        )
                        wrong_module = metadata.get('ss_network_module', '') == 'networks.lora'
                        return is_flux and wrong_module
                    
                    def create_fixed_lora(lora_path, metadata):
                        import tempfile
                        import shutil
                        from safetensors import safe_open
                        from safetensors.torch import save_file
                        
                        # Create temp file
                        temp_fd, temp_path = tempfile.mkstemp(suffix='.safetensors')
                        os.close(temp_fd)
                        
                        # Load original LoRA
                        with safe_open(lora_path, framework="pt", device="cpu") as f:
                            state_dict = {key: f.get_tensor(key) for key in f.keys()}
                            original_metadata = dict(f.metadata()) if f.metadata() else {}
                        
                        # Fix metadata
                        fixed_metadata = original_metadata.copy()
                        fixed_metadata['ss_network_module'] = 'networks.lora_flux'
                        
                        # Save with fixed metadata
                        save_file(state_dict, temp_path, metadata=fixed_metadata)
                        return temp_path
                    
                    # Fix LoRA A if needed
                    if needs_network_fix(metadata_a):
                        lora_a = create_fixed_lora(lora_a, metadata_a)
                        temp_files_to_cleanup.append(lora_a)
                        metadata_fixes_applied.append("A")
                    
                    # Fix LoRA B if needed  
                    if needs_network_fix(metadata_b):
                        lora_b = create_fixed_lora(lora_b, metadata_b)
                        temp_files_to_cleanup.append(lora_b)
                        metadata_fixes_applied.append("B")
                        
                except Exception as e:
                    # If we can't process metadata, proceed with original files
                    print(f"Warning: Could not process metadata: {e}")
                    pass
                
                # Create output directory
                os.makedirs(os.path.dirname(output), exist_ok=True)
                
                # Perform merge
                try:
                    success, message = merge_loras(
                        lora_a, lora_b, output,
                        strength_a, strength_b, use_concat,
                        sd_scripts_path
                    )
                    
                    # Clean up temp files
                    for temp_file in temp_files_to_cleanup:
                        try:
                            os.unlink(temp_file)
                        except:
                            pass
                    
                    if success:
                        result_message = f"✅ {message}"
                        
                        if auto_concat_enabled and auto_concat_reason:
                            result_message += f"\n\n⚡ Auto-enabled concat mode due to architecture differnces between the LoRAs"
                        
                        if metadata_fixes_applied:
                            fixed_loras = " & ".join(metadata_fixes_applied)
                            result_message += f"\n\n🔧 Auto-fixed FLUX metadata for LoRA {fixed_loras} (networks.lora → networks.lora_flux)"
                        
                        return result_message
                    else:
                        # Enhanced error message with helpful suggestions
                        error_msg = f"❌ Error during merge: {message}"
                        error_msg += "\n\n💡 This likely failed due to incompatibilities between the LoRAs."
                        error_msg += "\n   Try enabling concat mode, or use the MetaViewer tab to be sure both are Flux LoRAs."
                        return error_msg
                        
                except Exception as merge_error:
                    # Clean up temp files even on error
                    for temp_file in temp_files_to_cleanup:
                        try:
                            os.unlink(temp_file)
                        except:
                            pass
                    raise merge_error
                    
            except Exception as e:
                return f"❌ Error: {str(e)}"
        
        def handle_analyze(path):
            try:
                valid, msg = validate_lora_path(path)
                if not valid:
                    return {"error": msg}
                
                result = analyze_lora(path, sd_scripts_path)
                return result
                
            except Exception as e:
                return {"error": str(e)}
        
        def handle_compatibility_check(lora_a, lora_b):
            try:
                valid_a, msg_a = validate_lora_path(lora_a)
                if not valid_a:
                    return f"❌ LoRA A: {msg_a}"
                
                valid_b, msg_b = validate_lora_path(lora_b)
                if not valid_b:
                    return f"❌ LoRA B: {msg_b}"
                
                result = predict_compatibility(lora_a, lora_b)
                
                output = f"🔍 Compatibility Analysis\n\n"
                output += f"⚠️ This analysis is a guide to catch common technical issues only.\n"
                output += f"It checks: rank differences, alpha mismatches, base model compatibility, and training efficiency.\n\n"
                output += f"Status: {result['status']}\n"
                output += f"Confidence: {result['confidence']:.1%}\n\n"
                
                output += "Issues:\n"
                for issue in result['issues']:
                    output += f"• {issue}\n"
                
                output += "\nRecommendations:\n"
                for rec in result['recommendations']:
                    output += f"• {rec}\n"
                
                if 'suggested_strengths' in result:
                    output += f"\nSuggested Strengths:\n"
                    output += f"• LoRA A: {result['suggested_strengths']['lora_a']:.1f}\n"
                    output += f"• LoRA B: {result['suggested_strengths']['lora_b']:.1f}\n"
                
                return output
                
            except Exception as e:
                return f"❌ Error analyzing compatibility: {str(e)}"
        
        def handle_browse_files(directory):
            try:
                if not os.path.exists(directory):
                    return "❌ Directory not found"
                
                files = find_lora_files(directory, recursive=True)
                if not files:
                    return "No LoRA files found in directory"
                
                output = f"Found {len(files)} LoRA files:\n\n"
                for file_path in files[:20]:  # Limit to first 20
                    rel_path = os.path.relpath(file_path, directory)
                    file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                    output += f"{file_path}\n"
                
                if len(files) > 20:
                    output += f"\n... and {len(files) - 20} more files"
                
                return output
                
            except Exception as e:
                return f"❌ Error browsing files: {str(e)}"
        
        def handle_refresh_recent():
            try:
                # Look in common directories
                directories = ["output", "outputs", "."]
                recent_files = []
                
                for directory in directories:
                    if os.path.exists(directory):
                        recent_files.extend(get_recent_loras(directory, limit=5))
                
                if not recent_files:
                    return "No recent LoRA files found"
                
                output = "Recent LoRA files:\n\n"
                for path, name, mod_time in recent_files[:10]:
                    import datetime
                    mod_date = datetime.datetime.fromtimestamp(mod_time)
                    output += f"• {name}\n  {path}\n  Modified: {mod_date.strftime('%Y-%m-%d %H:%M')}\n\n"
                
                return output
                
            except Exception as e:
                return f"❌ Error loading recent files: {str(e)}"
        
        def handle_file_browse():
            """Open file browser for LoRA selection"""
            try:
                import tkinter as tk
                from tkinter import filedialog
                
                # Hide the root window
                root = tk.Tk()
                root.withdraw()
                
                # Open file dialog
                file_path = filedialog.askopenfilename(
                    title="Select LoRA File",
                    filetypes=[
                        ("LoRA files", "*.safetensors *.ckpt *.pt"),
                        ("SafeTensors", "*.safetensors"), 
                        ("All files", "*.*")
                    ],
                    initialdir="."
                )
                
                root.destroy()
                
                return file_path if file_path else ""
                
            except Exception as e:
                print(f"File browser error: {e}")
                return ""
        
        def handle_file_upload(file):
            """Handle file upload and return the file path"""
            if file is not None:
                return file.name
            return ""
        
        def handle_scan_loras(directory):
            """Scan directory for LoRA files and update cache"""
            if not directory:
                return "❌ Please provide a directory path"
            
            success, message = lora_cache.scan_directory_for_loras(directory)
            
            if success:
                cache_info = lora_cache.get_cache_info()
                return f"✅ {message}\n\nCache updated with {cache_info['total_loras']} LoRA files"
            else:
                return f"❌ {message}"
        
        def handle_rescan_loras():
            """Rescan the current directory"""
            cache_info = lora_cache.get_cache_info()
            if not cache_info['scan_directory']:
                return "❌ No directory set. Please scan a directory first."
            
            return handle_scan_loras(cache_info['scan_directory'])
        
        def handle_directory_browse():
            """Browse for directory using file dialog"""
            try:
                import tkinter as tk
                from tkinter import filedialog
                
                root = tk.Tk()
                root.withdraw()
                
                directory = filedialog.askdirectory(
                    title="Select LoRA Directory",
                    initialdir="."
                )
                
                root.destroy()
                
                return directory if directory else ""
            except Exception as e:
                print(f"Directory browser error: {e}")
                return ""
        
        def handle_output_directory_browse():
            """Browse for output directory using file dialog"""
            try:
                import tkinter as tk
                from tkinter import filedialog
                
                root = tk.Tk()
                root.withdraw()
                
                directory = filedialog.askdirectory(
                    title="Select Default Output Directory",
                    initialdir=lora_cache.get_default_output_path()
                )
                
                root.destroy()
                
                return directory if directory else ""
            except Exception as e:
                print(f"Output directory browser error: {e}")
                return ""
        
        def handle_save_settings(output_path):
            """Save the output path settings"""
            if output_path:
                lora_cache.set_default_output_path(output_path)
                return "✅ Settings saved! Default output path updated."
            return "❌ Please provide an output path"
        
        def handle_autocomplete(query):
            """Handle autocomplete for path textboxes"""
            if not query or len(query) < 1:
                return gr.Dropdown(choices=[], visible=False, label="📝 Click to select:")
            
            # Check if any LoRAs are cached
            if not lora_cache.lora_paths:
                return gr.Dropdown(choices=[], visible=False, label="💡 Set up LoRA scan directory in LoRA Paths tab first")
            
            matches = lora_cache.get_matching_loras(query)
            
            if matches:
                if len(matches) >= 50:
                    label = f"📝 {len(matches)} matches found (limited to 50) - Click to select:"
                else:
                    label = f"📝 {len(matches)} matches found - Click to select:"
                return gr.Dropdown(choices=matches, visible=True, label=label, value=None)
            else:
                return gr.Dropdown(choices=[], visible=False, label="❌ No matches found")
        
        def handle_dropdown_select(selected_path, dropdown_value):
            """Handle selection from autocomplete dropdown"""
            if dropdown_value and dropdown_value != selected_path:
                return dropdown_value, gr.Dropdown(visible=False)
            return gr.update(), gr.update()
        
        def handle_found_files_click(found_files_text):
            """Handle click on found files to extract the clicked path"""
            if not found_files_text:
                return ""
            
            # Parse the text to extract file paths
            lines = found_files_text.strip().split('\n')
            for line in lines:
                line = line.strip()
                # Skip empty lines and header lines
                if not line or line.startswith('Found') or line.startswith('❌') or line.startswith('...'):
                    continue
                # Check if this line looks like a file path
                if line.endswith('.safetensors') or line.endswith('.ckpt') or line.endswith('.pt'):
                    return line
            
            return ""
        
        def handle_layer_targeting(lora_path, output_name, *layer_selections):
            try:
                print(f"🎯 BROWSER LOG: Starting layer targeting operation")
                print(f"📁 Input LoRA: {lora_path}")
                print(f"📝 Output name: {output_name}")
                
                # Validate inputs
                if not lora_path:
                    print("❌ BROWSER LOG: No LoRA path provided")
                    return "❌ Please provide a LoRA file path"
                
                if not os.path.exists(lora_path):
                    print(f"❌ BROWSER LOG: File not found: {lora_path}")
                    return f"❌ LoRA file not found: {lora_path}"
                
                if not output_name:
                    print("❌ BROWSER LOG: No output name provided")
                    return "❌ Please provide an output filename"
                
                # Build list of layers to mute from dynamic selections
                mute_layers = []
                
                # Process all layer selections (TE: 0-11, Double: 0-19, Single: 0-37)
                layer_idx = 0
                
                # Text Encoder layers (0-11)
                for i in range(12):
                    if layer_idx < len(layer_selections) and layer_selections[layer_idx]:
                        mute_layers.append(i)
                    layer_idx += 1
                
                # UNet Double Block layers (0-19) 
                for i in range(20):
                    if layer_idx < len(layer_selections) and layer_selections[layer_idx]:
                        mute_layers.append(i)
                    layer_idx += 1
                
                # UNet Single Block layers (0-37)
                for i in range(38):
                    if layer_idx < len(layer_selections) and layer_selections[layer_idx]:
                        mute_layers.append(i)
                    layer_idx += 1
                
                print(f"🎯 BROWSER LOG: Layers to mute: {mute_layers}")
                
                if not mute_layers:
                    print("❌ BROWSER LOG: No layers selected")
                    return "❌ Please select at least one layer to mute"
                
                # Use output path directly (now it's a full path, not just filename)
                output_path = output_name
                if not output_path.endswith('.safetensors'):
                    output_path += '.safetensors'
                
                print(f"💾 BROWSER LOG: Output path: {output_path}")
                print(f"🚀 BROWSER LOG: Starting layer targeting operation...")
                
                # Perform layer targeting
                success, message = target_lora_layers(
                    lora_path, output_path, mute_layers, sd_scripts_path
                )
                
                if success:
                    print(f"✅ BROWSER LOG: Layer targeting completed successfully!")
                    return f"✅ {message}"
                else:
                    print(f"❌ BROWSER LOG: Layer targeting failed: {message}")
                    return f"❌ {message}"
                    
            except Exception as e:
                print(f"💥 BROWSER LOG: Exception in layer targeting: {str(e)}")
                return f"❌ Error: {str(e)}"
        
        def update_layer_preview(*layer_selections):
            """Update the preview of selected layers"""
            selected = []
            layer_idx = 0
            
            # Text Encoder layers (0-11)
            for i in range(12):
                if layer_idx < len(layer_selections) and layer_selections[layer_idx]:
                    selected.append(f"TE{i}")
                layer_idx += 1
            
            # UNet Double Block layers (0-19)
            for i in range(20):
                if layer_idx < len(layer_selections) and layer_selections[layer_idx]:
                    selected.append(f"DB{i}")
                layer_idx += 1
            
            # UNet Single Block layers (0-37)
            for i in range(38):
                if layer_idx < len(layer_selections) and layer_selections[layer_idx]:
                    selected.append(f"SB{i}")
                layer_idx += 1
            
            if not selected:
                return "No layers selected"
            
            preview = f"Will mute {len(selected)} layer(s):\\n\\n"
            preview += ", ".join(selected)
            
            return preview
        
        def preset_facial_layers():
            """Set facial layer preset (7,12,16,20)"""
            updates = {}
            
            # Reset all to False first
            for i in range(12):  # TE layers
                updates[te_layers[i]] = False
            for i in range(20):  # Double layers  
                updates[double_layers[i]] = False
            for i in range(38):  # Single layers
                updates[single_layers[i]] = False
            
            # Set facial layers to True
            updates[te_layers[7]] = True
            updates[double_layers[7]] = True
            updates[double_layers[12]] = True  
            updates[double_layers[16]] = True
            updates[single_layers[7]] = True
            updates[single_layers[12]] = True
            updates[single_layers[16]] = True
            updates[single_layers[20]] = True
            
            return list(updates.values())
        
        def preset_aggressive_layers():
            """Set aggressive layer preset (4,7,8,12,15,16,19,20)"""
            updates = {}
            
            # Reset all to False first
            for i in range(12):  # TE layers
                updates[te_layers[i]] = False
            for i in range(20):  # Double layers
                updates[double_layers[i]] = False  
            for i in range(38):  # Single layers
                updates[single_layers[i]] = False
            
            # Set aggressive layers to True
            aggressive_layers = [4, 7, 8, 12, 15, 16, 19, 20]
            
            for layer in aggressive_layers:
                if layer < 12:  # TE layer
                    updates[te_layers[layer]] = True
                if layer < 20:  # Double layer
                    updates[double_layers[layer]] = True
                if layer < 38:  # Single layer
                    updates[single_layers[layer]] = True
            
            return list(updates.values())
        
        def preset_style_layers():
            """Set style layer preset (excludes facial layers, focuses on artistic style)"""
            updates = {}
            
            # Reset all to False first
            for i in range(12):  # TE layers
                updates[te_layers[i]] = False
            for i in range(20):  # Double layers
                updates[double_layers[i]] = False
            for i in range(38):  # Single layers
                updates[single_layers[i]] = False
            
            # Style layers based on research:
            # - Early layers (0-6): Basic structure and composition
            # - Middle layers (excluding facial 7,12,16,20): Artistic style, texture, lighting  
            # - Late layers (21-37): Fine details, artistic refinement
            
            # Text Encoder style layers (avoid 7 which is facial)
            style_te_layers = [0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 11]
            for layer in style_te_layers:
                updates[te_layers[layer]] = True
            
            # Double Block style layers (avoid 7,12,16 which are facial)
            style_double_layers = [0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 13, 14, 15, 17, 18, 19]
            for layer in style_double_layers:
                updates[double_layers[layer]] = True
            
            # Single Block style layers (avoid 7,12,16,20 which are facial)
            style_single_layers = [0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 13, 14, 15, 17, 18, 19, 
                                  21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37]
            for layer in style_single_layers:
                updates[single_layers[layer]] = True
            
            return list(updates.values())
        
        def preset_invert_selection():
            """Invert current layer selections"""
            # This function will be called with current selections as input
            # It will be handled differently in the event handler
            pass
        
        def invert_current_selection(*current_selections):
            """Invert the current layer selections"""
            return [not selection for selection in current_selections]
        
        def preset_clear_all():
            """Clear all layer selections"""
            updates = []
            
            # Set all to False
            for i in range(12):  # TE layers
                updates.append(False)
            for i in range(20):  # Double layers
                updates.append(False)
            for i in range(38):  # Single layers
                updates.append(False)
            
            return updates
        
        # Layer-based merging functions
        def handle_layer_merge(lora_a_path, lora_b_path, strength_a, strength_b, output_name, *layer_selections):
            """Handle selective layer merging from two LoRAs"""
            try:
                print(f"🔀 BROWSER LOG: Starting layer-based merge operation")
                print(f"📁 LoRA A: {lora_a_path} (strength: {strength_a})")
                print(f"📁 LoRA B: {lora_b_path} (strength: {strength_b})")
                print(f"📝 Output name: {output_name}")
                
                # Validate inputs
                if not lora_a_path or not lora_b_path:
                    return "❌ Please provide paths for both LoRAs"
                
                if not os.path.exists(lora_a_path):
                    return f"❌ LoRA A file not found: {lora_a_path}"
                
                if not os.path.exists(lora_b_path):
                    return f"❌ LoRA B file not found: {lora_b_path}"
                
                if not output_name:
                    return "❌ Please provide an output filename"
                
                # Parse layer selections (A and B selections are interleaved)
                layer_selections_a = []
                layer_selections_b = []
                
                # Extract A and B selections (they're interleaved in the input)
                for i in range(0, len(layer_selections), 2):
                    if i < len(layer_selections):
                        layer_selections_a.append(layer_selections[i])
                    if i + 1 < len(layer_selections):
                        layer_selections_b.append(layer_selections[i + 1])
                
                # Build layer assignments
                layers_from_a = []
                layers_from_b = []
                conflicts = []
                
                layer_idx = 0
                
                # Process TE layers (0-11)
                for i in range(12):
                    if layer_idx < len(layer_selections_a) and layer_idx < len(layer_selections_b):
                        from_a = layer_selections_a[layer_idx]
                        from_b = layer_selections_b[layer_idx]
                        
                        if from_a and from_b:
                            conflicts.append(f"TE{i}")
                        elif from_a:
                            layers_from_a.append(i)
                        elif from_b:
                            layers_from_b.append(i)
                    layer_idx += 1
                
                # Process Double Block layers (0-19)
                for i in range(20):
                    if layer_idx < len(layer_selections_a) and layer_idx < len(layer_selections_b):
                        from_a = layer_selections_a[layer_idx]
                        from_b = layer_selections_b[layer_idx]
                        
                        if from_a and from_b:
                            conflicts.append(f"DB{i}")
                        elif from_a:
                            layers_from_a.append(i)
                        elif from_b:
                            layers_from_b.append(i)
                    layer_idx += 1
                
                # Process Single Block layers (0-37)
                for i in range(38):
                    if layer_idx < len(layer_selections_a) and layer_idx < len(layer_selections_b):
                        from_a = layer_selections_a[layer_idx]
                        from_b = layer_selections_b[layer_idx]
                        
                        if from_a and from_b:
                            conflicts.append(f"SB{i}")
                        elif from_a:
                            layers_from_a.append(i)
                        elif from_b:
                            layers_from_b.append(i)
                    layer_idx += 1
                
                # Check for conflicts
                if conflicts:
                    return f"❌ Layer conflicts detected! Cannot select same layer from both LoRAs: {', '.join(conflicts)}"
                
                # Check if any layers selected
                if not layers_from_a and not layers_from_b:
                    return "❌ Please select at least one layer from either LoRA A or B"
                
                print(f"🔀 BROWSER LOG: Layers from A: {layers_from_a}")
                print(f"🔀 BROWSER LOG: Layers from B: {layers_from_b}")
                
                # Use output path directly (now it's a full path, not just filename)
                output_path = output_name
                if not output_path.endswith('.safetensors'):
                    output_path += '.safetensors'
                
                # Perform the selective merge
                success, message = selective_layer_merge(
                    lora_a_path, lora_b_path, output_path, 
                    layers_from_a, layers_from_b, strength_a, strength_b
                )
                
                if success:
                    print(f"✅ BROWSER LOG: Layer merge completed successfully!")
                    return f"✅ {message}"
                else:
                    print(f"❌ BROWSER LOG: Layer merge failed: {message}")
                    return f"❌ {message}"
                    
            except Exception as e:
                print(f"💥 BROWSER LOG: Exception in layer merge: {str(e)}")
                return f"❌ Error: {str(e)}"
        
        def update_merge_layer_preview(strength_a, strength_b, *layer_selections):
            """Update preview of layer assignments for merging"""
            try:
                # Parse A and B selections (interleaved)
                layer_selections_a = []
                layer_selections_b = []
                
                for i in range(0, len(layer_selections), 2):
                    if i < len(layer_selections):
                        layer_selections_a.append(layer_selections[i])
                    if i + 1 < len(layer_selections):
                        layer_selections_b.append(layer_selections[i + 1])
                
                layers_a = []
                layers_b = []
                conflicts = []
                layer_idx = 0
                
                # Process all layer types
                layer_types = [
                    ("TE", 12),    # Text Encoder 0-11
                    ("DB", 20),    # Double Block 0-19  
                    ("SB", 38)     # Single Block 0-37
                ]
                
                for prefix, count in layer_types:
                    for i in range(count):
                        if layer_idx < len(layer_selections_a) and layer_idx < len(layer_selections_b):
                            from_a = layer_selections_a[layer_idx]
                            from_b = layer_selections_b[layer_idx]
                            
                            if from_a and from_b:
                                conflicts.append(f"{prefix}{i}")
                            elif from_a:
                                layers_a.append(f"{prefix}{i}")
                            elif from_b:
                                layers_b.append(f"{prefix}{i}")
                        layer_idx += 1
                
                preview = ""
                
                if conflicts:
                    preview += f"⚠️ CONFLICTS: {', '.join(conflicts)}\\n\\n"
                
                if layers_a:
                    preview += f"🔵 From LoRA A @ {strength_a}x ({len(layers_a)} layers):\\n"
                    preview += f"{', '.join(layers_a)}\\n\\n"
                
                if layers_b:
                    preview += f"🔴 From LoRA B @ {strength_b}x ({len(layers_b)} layers):\\n"
                    preview += f"{', '.join(layers_b)}\\n\\n"
                
                if not layers_a and not layers_b:
                    preview = "No layers selected"
                elif not conflicts:
                    total_layers = len(layers_a) + len(layers_b)
                    preview += f"✅ Ready to merge {total_layers} layers total\\n"
                    preview += f"⚡ Strengths: A={strength_a}x, B={strength_b}x"
                
                return preview
                
            except Exception as e:
                return f"Error updating preview: {str(e)}"
        
        # Merge preset functions
        def merge_preset_face_style():
            """Face A + Style B preset"""
            updates = []
            
            # TE layers: Face from A (layer 7), rest from B
            for i in range(12):
                updates.append(i == 7)  # A
                updates.append(i != 7)  # B
            
            # Double layers: Face from A (7,12,16), style from B
            facial_double = [7, 12, 16]
            for i in range(20):
                updates.append(i in facial_double)  # A
                updates.append(i not in facial_double)  # B
            
            # Single layers: Face from A (7,12,16,20), style from B  
            facial_single = [7, 12, 16, 20]
            for i in range(38):
                updates.append(i in facial_single)  # A
                updates.append(i not in facial_single)  # B
            
            return updates
        
        def merge_preset_facial_priority():
            """Facial Priority A + Style B preset (aggressive facial capture)"""
            updates = []
            
            # Aggressive facial layers: 4, 7, 8, 12, 15, 16, 19, 20
            aggressive_facial = [4, 7, 8, 12, 15, 16, 19, 20]
            
            # TE layers: Aggressive facial from A, rest from B
            for i in range(12):
                updates.append(i in aggressive_facial)  # A
                updates.append(i not in aggressive_facial)  # B
            
            # Double layers: Aggressive facial from A, style from B
            for i in range(20):
                updates.append(i in aggressive_facial)  # A
                updates.append(i not in aggressive_facial)  # B
            
            # Single layers: Aggressive facial from A, style from B  
            for i in range(38):
                updates.append(i in aggressive_facial)  # A
                updates.append(i not in aggressive_facial)  # B
            
            return updates
        
        def merge_preset_complement():
            """Complement split: Early A + Late B"""
            updates = []
            
            # TE layers: First half A, second half B
            for i in range(12):
                updates.append(i < 6)   # A
                updates.append(i >= 6)  # B
            
            # Double layers: First half A, second half B
            for i in range(20):
                updates.append(i < 10)   # A
                updates.append(i >= 10)  # B
            
            # Single layers: First half A, second half B
            for i in range(38):
                updates.append(i < 19)   # A
                updates.append(i >= 19)  # B
            
            return updates
        
        def merge_preset_clear():
            """Clear all merge selections"""
            updates = []
            
            # Clear all A and B selections
            total_checkboxes = (12 + 20 + 38) * 2  # Each layer has A and B checkbox
            for i in range(total_checkboxes):
                updates.append(False)
            
            return updates
        
        def merge_preset_swap_ab():
            """Swap A and B selections"""
            # This will be handled by taking current selections and swapping them
            pass
        
        def swap_merge_selections(*current_selections):
            """Swap A and B selections in merge interface"""
            updates = []
            
            # Swap A and B selections (they're interleaved)
            for i in range(0, len(current_selections), 2):
                if i + 1 < len(current_selections):
                    # Swap A and B
                    updates.append(current_selections[i + 1])  # B -> A
                    updates.append(current_selections[i])      # A -> B
                else:
                    updates.append(current_selections[i])
            
            return updates
        
        # Wire up event handlers
        subtract_button.click(
            fn=handle_subtract,
            inputs=[subtract_lora_a, subtract_lora_b, subtract_strength_a, 
                   subtract_strength_b, subtract_output],
            outputs=subtract_result
        )
        
        merge_button.click(
            fn=handle_merge,
            inputs=[merge_lora_a, merge_lora_b, merge_strength_a,
                   merge_strength_b, merge_output, merge_concat],
            outputs=merge_result
        )
        
        analyze_button.click(
            fn=handle_analyze,
            inputs=analyze_path,
            outputs=analysis_result
        )
        
        compatibility_check.click(
            fn=handle_compatibility_check,
            inputs=[subtract_lora_a, subtract_lora_b],
            outputs=compatibility_result
        )
        
        browse_button.click(
            fn=handle_browse_files,
            inputs=browse_directory,
            outputs=found_files
        )
        
        found_files.select(
            fn=handle_found_files_click,
            inputs=found_files,
            outputs=analyze_path
        )
        
        refresh_recent.click(
            fn=handle_refresh_recent,
            outputs=recent_loras_display
        )
        
        # File browser event handlers
        subtract_lora_a_browse.click(
            fn=handle_file_browse,
            outputs=subtract_lora_a
        )
        
        subtract_lora_b_browse.click(
            fn=handle_file_browse,
            outputs=subtract_lora_b
        )
        
        merge_lora_a_browse.click(
            fn=handle_file_browse,
            outputs=merge_lora_a
        )
        
        merge_lora_b_browse.click(
            fn=handle_file_browse,
            outputs=merge_lora_b
        )
        
        analyze_path_browse.click(
            fn=handle_file_browse,
            outputs=analyze_path
        )
        
        merge_lora_a_path_browse.click(
            fn=handle_file_browse,
            outputs=merge_lora_a_path
        )
        
        merge_lora_b_path_browse.click(
            fn=handle_file_browse,
            outputs=merge_lora_b_path
        )
        
        target_lora_path_browse.click(
            fn=handle_file_browse,
            outputs=target_lora_path
        )
        
        # LoRA scanning event handlers
        scan_directory_browse.click(
            fn=handle_directory_browse,
            outputs=scan_directory
        )
        
        scan_button.click(
            fn=handle_scan_loras,
            inputs=scan_directory,
            outputs=scan_status
        )
        
        rescan_button.click(
            fn=handle_rescan_loras,
            outputs=scan_status
        )
        
        default_output_browse.click(
            fn=handle_output_directory_browse,
            outputs=default_output_path
        )
        
        save_settings_button.click(
            fn=handle_save_settings,
            inputs=default_output_path,
            outputs=scan_status
        )
        
        # Autocomplete event handlers for all path textboxes
        subtract_lora_a.change(
            fn=handle_autocomplete,
            inputs=subtract_lora_a,
            outputs=subtract_lora_a_dropdown
        )
        
        subtract_lora_a_dropdown.change(
            fn=handle_dropdown_select,
            inputs=[subtract_lora_a, subtract_lora_a_dropdown],
            outputs=[subtract_lora_a, subtract_lora_a_dropdown]
        )
        
        subtract_lora_b.change(
            fn=handle_autocomplete,
            inputs=subtract_lora_b,
            outputs=subtract_lora_b_dropdown
        )
        
        subtract_lora_b_dropdown.change(
            fn=handle_dropdown_select,
            inputs=[subtract_lora_b, subtract_lora_b_dropdown],
            outputs=[subtract_lora_b, subtract_lora_b_dropdown]
        )
        
        merge_lora_a.change(
            fn=handle_autocomplete,
            inputs=merge_lora_a,
            outputs=merge_lora_a_dropdown
        )
        
        merge_lora_a_dropdown.change(
            fn=handle_dropdown_select,
            inputs=[merge_lora_a, merge_lora_a_dropdown],
            outputs=[merge_lora_a, merge_lora_a_dropdown]
        )
        
        merge_lora_b.change(
            fn=handle_autocomplete,
            inputs=merge_lora_b,
            outputs=merge_lora_b_dropdown
        )
        
        merge_lora_b_dropdown.change(
            fn=handle_dropdown_select,
            inputs=[merge_lora_b, merge_lora_b_dropdown],
            outputs=[merge_lora_b, merge_lora_b_dropdown]
        )
        
        analyze_path.change(
            fn=handle_autocomplete,
            inputs=analyze_path,
            outputs=analyze_path_dropdown
        )
        
        analyze_path_dropdown.change(
            fn=handle_dropdown_select,
            inputs=[analyze_path, analyze_path_dropdown],
            outputs=[analyze_path, analyze_path_dropdown]
        )
        
        merge_lora_a_path.change(
            fn=handle_autocomplete,
            inputs=merge_lora_a_path,
            outputs=merge_lora_a_path_dropdown
        )
        
        merge_lora_a_path_dropdown.change(
            fn=handle_dropdown_select,
            inputs=[merge_lora_a_path, merge_lora_a_path_dropdown],
            outputs=[merge_lora_a_path, merge_lora_a_path_dropdown]
        )
        
        merge_lora_b_path.change(
            fn=handle_autocomplete,
            inputs=merge_lora_b_path,
            outputs=merge_lora_b_path_dropdown
        )
        
        merge_lora_b_path_dropdown.change(
            fn=handle_dropdown_select,
            inputs=[merge_lora_b_path, merge_lora_b_path_dropdown],
            outputs=[merge_lora_b_path, merge_lora_b_path_dropdown]
        )
        
        target_lora_path.change(
            fn=handle_autocomplete,
            inputs=target_lora_path,
            outputs=target_lora_path_dropdown
        )
        
        target_lora_path_dropdown.change(
            fn=handle_dropdown_select,
            inputs=[target_lora_path, target_lora_path_dropdown],
            outputs=[target_lora_path, target_lora_path_dropdown]
        )
        
        # Collect all layer checkboxes in order for targeting
        all_layer_checkboxes = []
        all_layer_checkboxes.extend([te_layers[i] for i in range(12)])      # TE layers 0-11
        all_layer_checkboxes.extend([double_layers[i] for i in range(20)])  # Double layers 0-19  
        all_layer_checkboxes.extend([single_layers[i] for i in range(38)])  # Single layers 0-37
        
        # Collect all merge layer checkboxes (A and B interleaved)
        all_merge_checkboxes = []
        for i in range(12):  # TE layers
            all_merge_checkboxes.extend([merge_te_layers_a[i], merge_te_layers_b[i]])
        for i in range(20):  # Double layers
            all_merge_checkboxes.extend([merge_double_layers_a[i], merge_double_layers_b[i]])
        for i in range(38):  # Single layers
            all_merge_checkboxes.extend([merge_single_layers_a[i], merge_single_layers_b[i]])
        
        # Layer targeting event handlers
        target_button.click(
            fn=handle_layer_targeting,
            inputs=[target_lora_path, target_output_name] + all_layer_checkboxes,
            outputs=target_result
        )
        
        # Preset button handlers
        preset_facial_btn.click(
            fn=preset_facial_layers,
            outputs=all_layer_checkboxes
        )
        
        preset_style_btn.click(
            fn=preset_style_layers,
            outputs=all_layer_checkboxes
        )
        
        preset_aggressive_btn.click(
            fn=preset_aggressive_layers,
            outputs=all_layer_checkboxes
        )
        
        preset_clear_btn.click(
            fn=preset_clear_all,
            outputs=all_layer_checkboxes
        )
        
        preset_invert_btn.click(
            fn=invert_current_selection,
            inputs=all_layer_checkboxes,
            outputs=all_layer_checkboxes
        )
        
        # Layer-based merge event handlers
        merge_layer_button.click(
            fn=handle_layer_merge,
            inputs=[merge_lora_a_path, merge_lora_b_path, layer_merge_strength_a, layer_merge_strength_b, merge_output_name] + all_merge_checkboxes,
            outputs=merge_layer_result
        )
        
        # Merge preset handlers
        merge_preset_face_style_btn.click(
            fn=merge_preset_face_style,
            outputs=all_merge_checkboxes
        )
        
        merge_preset_facial_priority_btn.click(
            fn=merge_preset_facial_priority,
            outputs=all_merge_checkboxes
        )
        
        merge_preset_complement_btn.click(
            fn=merge_preset_complement,
            outputs=all_merge_checkboxes
        )
        
        merge_preset_clear_btn.click(
            fn=merge_preset_clear,
            outputs=all_merge_checkboxes
        )
        
        merge_preset_invert_btn.click(
            fn=swap_merge_selections,
            inputs=all_merge_checkboxes,
            outputs=all_merge_checkboxes
        )
        
        # Update merge preview when any checkbox or strength changes
        merge_inputs = [layer_merge_strength_a, layer_merge_strength_b] + all_merge_checkboxes
        
        for checkbox in all_merge_checkboxes:
            checkbox.change(
                fn=update_merge_layer_preview,
                inputs=merge_inputs,
                outputs=merge_layer_preview
            )
        
        # Also update preview when strength sliders change
        layer_merge_strength_a.change(
            fn=update_merge_layer_preview,
            inputs=merge_inputs,
            outputs=merge_layer_preview
        )
        
        layer_merge_strength_b.change(
            fn=update_merge_layer_preview,
            inputs=merge_inputs,
            outputs=merge_layer_preview
        )
        
        # Update layer preview when any checkbox changes
        for checkbox in all_layer_checkboxes:
            checkbox.change(
                fn=update_layer_preview,
                inputs=all_layer_checkboxes,
                outputs=layer_preview
            )
        
        # MetaEditor Event Handlers
        def handle_metaedit_load(lora_path):
            """Load metadata from LoRA file for editing"""
            try:
                valid, msg = validate_lora_path(lora_path)
                if not valid:
                    return "", f"❌ {msg}"
                
                # Load full analysis like the analysis tab
                analysis = analyze_lora(lora_path, sd_scripts_path)
                if 'error' in analysis:
                    return "", f"❌ {analysis['error']}"
                
                # Get raw metadata and format as JSON
                metadata = analysis.get('metadata', {})
                import json
                formatted_metadata = json.dumps(metadata, indent=2, ensure_ascii=False)
                
                return formatted_metadata, f"✅ Loaded metadata from: {lora_path}"
                
            except Exception as e:
                return "", f"❌ Error loading metadata: {str(e)}"
        
        def handle_metaedit_save(lora_path, metadata_json):
            """Save edited metadata back to LoRA file"""
            try:
                valid, msg = validate_lora_path(lora_path)
                if not valid:
                    return f"❌ {msg}"
                
                if not metadata_json.strip():
                    return "❌ No metadata to save"
                
                # Parse JSON metadata
                import json
                try:
                    new_metadata = json.loads(metadata_json)
                except json.JSONDecodeError as e:
                    return f"❌ Invalid JSON format: {str(e)}"
                
                # Load the LoRA file
                from safetensors import safe_open
                from safetensors.torch import save_file
                import tempfile
                import shutil
                
                # Load tensors into memory first
                state_dict = {}
                with safe_open(lora_path, framework="pt", device="cpu") as f:
                    for key in f.keys():
                        state_dict[key] = f.get_tensor(key).clone()
                # File is now properly closed
                
                # Create temporary file to avoid file locking issues
                temp_fd, temp_path = tempfile.mkstemp(suffix='.safetensors')
                os.close(temp_fd)
                
                try:
                    # Save to temp file with new metadata
                    save_file(state_dict, temp_path, metadata=new_metadata)
                    
                    # Replace original file with temp file
                    shutil.move(temp_path, lora_path)
                except Exception as e:
                    # Clean up temp file on error
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
                    raise e
                
                return f"✅ Successfully saved metadata to: {lora_path}"
                
            except Exception as e:
                return f"❌ Error saving metadata: {str(e)}"
        
        # MetaEditor event bindings
        metaedit_lora_path.change(
            fn=handle_autocomplete,
            inputs=metaedit_lora_path,
            outputs=metaedit_lora_dropdown
        )
        
        metaedit_lora_dropdown.change(
            fn=handle_dropdown_select,
            inputs=[metaedit_lora_path, metaedit_lora_dropdown],
            outputs=[metaedit_lora_path, metaedit_lora_dropdown]
        )
        
        metaedit_lora_browse.click(
            fn=handle_file_browse,
            outputs=metaedit_lora_path
        )
        
        metaedit_load_button.click(
            fn=handle_metaedit_load,
            inputs=metaedit_lora_path,
            outputs=[metaedit_metadata, metaedit_result]
        )
        
        metaedit_save_button.click(
            fn=handle_metaedit_save,
            inputs=[metaedit_lora_path, metaedit_metadata],
            outputs=metaedit_result
        )
        
        # Method screenshot toggle
        def toggle_method_image(current_visible):
            return gr.Image(visible=not current_visible)
        
        method_button.click(
            fn=lambda: gr.Image(visible=True),
            outputs=method_image
        )
        
        # Load recent files on startup
        demo.load(fn=handle_refresh_recent, outputs=recent_loras_display)
    
    return demo

def launch_gui(sd_scripts_path: Optional[str] = None, **kwargs):
    """Launch the LoRA the Explorer GUI
    
    Args:
        sd_scripts_path: Custom path to sd-scripts directory
        **kwargs: Additional arguments for demo.launch()
    """
    demo = create_gui(sd_scripts_path)
    
    # Default launch settings
    launch_args = {
        "debug": True,
        "show_error": True,
        "share": False,
        "inbrowser": True
    }
    launch_args.update(kwargs)
    
    demo.launch(**launch_args)

if __name__ == "__main__":
    launch_gui()