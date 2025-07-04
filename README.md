# LoRA the Explorer - for advanced FLUX LoRA manipulation

![LoRA the Explorer Banner](https://img.shields.io/badge/LoRA-the%20Explorer-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

This tool provides various FLUX LoRA manipulation techniques including subtraction, merging, layer targeting, and analysis. It's designed to help you create compatible LoRAs and experiment with different combination approaches.

## What You Can Do:

- **LoRA Subtraction**: Remove conflicts between LoRAs
- **Traditional Merging**: Combine LoRAs with custom weights (auto-detects incompatibilities)
- **Layer-Based Merging**: Surgically combine specific layers from different LoRAs
- **Layer Targeting**: Selectively mute facial or style layers
- **LoRA MetaEditor**: Direct metadata editing for any LoRA file
- **LoRA MetaViewer**: Examine LoRA characteristics, metadata, and compatibility
- **LoRA MetaEditor**: Direct metadata editing for fixing and customizing LoRAs
- **Universal Compatibility**: Works with LoRAs from any training tool (AI-Toolkit, FluxGym, sd-scripts)
- **Automatic Fixes**: Auto-detects and resolves common compatibility issues

## 🛠️ Installation

### Automatic Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/shootthesound/lora-the-explorer.git
cd lora-the-explorer

# Run the installer
python install.py

or

Double click on windows_install.bat
```

This will:
- ✅ Create a Python virtual environment
- ✅ Download and set up sd-scripts (sd3 branch with Flux support, pinned to stable commit)
- ✅ Apply compatibility fixes for FLUX LoRA metadata
- ✅ Install all dependencies
- ✅ Create launcher scripts

### Quick Launch
```bash
# Windows: Double-click start_gui.bat
# Unix/macOS: ./start_gui.sh
# Or manually:
python lora_algebra_gui.py
```

## 🎮 Getting Started

1. **Set up paths**: Use the "LoRA Paths" tab to scan your LoRA directory for autocomplete, and choose your default save directory
2. **Experiment**: Try different operations - each tab has usage guides and presets
3. **Start simple**: Begin with basic merging or subtraction or trying advanced layer techniques. My tip is to find a great style lora and merge a character into it with face layers.

## 🎯 Key Features

### LoRA Subtraction
Remove unwanted influences from LoRAs:
```
Style_LoRA - Character_LoRA = Clean_Style_LoRA
```
Perfect for removing face changes from style LoRAs and creating character-neutral styles.

### Layer Targeting (FLUX)
Selectively mute specific layers in FLUX LoRAs:
- **Facial Layers (7,12,16,20)**: Remove face details while keeping style/costume
- **Aggressive Mode**: Maximum facial identity removal
- **Custom Selection**: Choose any combination of available layers

Perfect for extracting character costumes without faces (like Gandalf costume without Ian McKellen's face).

### Layer-Based Merging
Surgically combine layers from different LoRAs:
- **Face A + Style B**: Facial layers from character LoRA, style from artistic LoRA
- **Facial Priority**: All potential facial layers from one LoRA
- **Complement Split**: Early layers from one LoRA, late layers from another
- **Fix Overtrained LoRAs**: Replace problematic layers with clean ones

### LoRA MetaViewer & Analysis
Technical validation and metadata viewing:
- Check rank, alpha, base model compatibility
- Predict potential conflicts and suggest optimal strengths
- Browse and analyze existing LoRAs
- View complete LoRA metadata in readable format
- Double-click file selection from analysis results

*Note: This analysis is a guide to catch common technical issues only. It checks: rank differences, alpha mismatches, base model compatibility, and training efficiency.*

### Path Management
Streamlined workflow:
- Recursive LoRA directory scanning with autocomplete for all path inputs
- Default output directory settings that persist across sessions
- Double-click file selection in analysis results

### Universal Compatibility
Automatic fixes for cross-tool compatibility:
- **Auto-detects incompatible LoRAs** and enables concat mode when needed
- **Fixes FLUX metadata issues** (networks.lora → networks.lora_flux) automatically
- **Handles mixed-dimension LoRAs** from layer merging operations
- **Works with any training tool**: AI-Toolkit, FluxGym, sd-scripts, kohya-ss
- **Enhanced error messages** with helpful suggestions when edge cases occur

### LoRA MetaEditor
Direct metadata editing with full control:
- **Edit any metadata field** in raw JSON format
- **Fix common issues**: Wrong network modules, incorrect base models, missing fields
- **In-place editing**: Modifies original file (ensure you have backups!)
- **Full user responsibility**: No safety nets - edit at your own risk
- **Universal metadata repair** for LoRAs from any source
- **Cross-tool compatibility fixes**: Repair LoRAs from different training tools
- **Custom metadata management**: Add training details, tags, or remove sensitive info

## 💡 Use Cases

### Style LoRA Cleaning
Use the LoRA Subtraction tab to remove face changes from style LoRAs:
1. Load your style LoRA as "LoRA A" 
2. Load a character/face LoRA as "LoRA B"
3. Set strength B to ~0.7 (85% of normal usage)
4. Output a clean style LoRA that won't change faces

### Character Costume Extraction
- **Gandalf costume, no Ian McKellen face**: Mute facial layers (7,12,16,20)

### Cross-Tool LoRA Compatibility
Fix LoRAs that won't merge due to different training tools:
1. **Auto-detection**: Tool automatically detects and fixes metadata issues
2. **Manual fixes**: Use LoRA MetaEditor to fix network modules manually
3. **Mixed dimensions**: Layer-merged LoRAs automatically trigger concat mode
4. **Universal merging**: Combine LoRAs from AI-Toolkit, FluxGym, sd-scripts seamlessly

### Metadata Repair & Customization
Use the LoRA MetaEditor for advanced metadata management:
1. **Fix training tool bugs**: Correct wrong network modules or base model info
2. **Add missing information**: Training details, base model versions, custom tags
3. **Remove sensitive data**: Clean out unwanted metadata fields
4. **Standardize collections**: Ensure consistent metadata across your LoRA library

⚠️ **MetaEditor Safety**: Always backup your LoRAs before editing metadata. Incorrect changes can break your LoRAs permanently.
- **Wonder Woman outfit, no Gal Gadot face**: Use layer targeting
- **Anime character clothes, no specific face**: Create universal character LoRAs

### Advanced Combinations
- Mix facial features from one LoRA with style from another using layer-based merging
- Create hybrid concepts using selective layers
- Rescue partially corrupted or overtrained LoRAs

## 📊 FLUX Layer Architecture

LoRA the Explorer works with FLUX's layer architecture:
- **Text Encoder (0-11)**: 12 layers
- **Double Blocks (0-19)**: 20 layers  
- **Single Blocks (0-37)**: 38 layers

**Known layer functions:**
- **Layers 7 & 20**: Primary facial structure and details
- **Layers 12 & 16**: Secondary facial features
- **Other layers**: Style, composition, lighting (experimental)

## 💡 Tips & Best Practices

### Subtraction Sweet Spot
```
Optimal_Subtraction_Strength = Normal_Usage_Strength × 0.85
```

### Layer Targeting Strategy
- Start with preset combinations (facial, style, aggressive)
- Experiment with individual layers for fine control
- Use preview to see selected layers before applying

## 🌟 Community Project

I'm building this for the community and welcome your feedback, suggestions, and bug reports. The goal is to make LoRA manipulation more accessible and experimental for the many who are less comfortable with very CLI based tools.

### Free to Use
This tool is completely free. If you find it useful and want to support development, you can do so at:

**☕ [buymeacoffee.com/loratheexplorer](https://buymeacoffee.com/loratheexplorer)**

Re-occurring supporters get early access to test new features as milestones arise in development.

### Feedback Welcome
Found a bug? Have a feature request? Want to share results? All feedback helps improve the tool for everyone. Emails to pneill@gmail.com.

## 🤝 Contributing

We welcome contributions! Areas for improvement:
- GUI enhancements and user experience
- Advanced layer analysis research
- Performance optimizations
- Documentation improvements
- Testing with different LoRA types
- New preset combinations for layer targeting

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

This tool is free to use, modify, and distribute. The goal is to make LoRA manipulation more accessible to everyone.

## 🙏 Credits & Dependencies

### sd-scripts Integration
LoRA the Explorer relies on [sd-scripts by kohya-ss](https://github.com/kohya-ss/sd-scripts) for the core LoRA processing functionality. Our installer automatically downloads the sd3 branch which includes FLUX support.

**sd-scripts provides:**
- FLUX LoRA manipulation capabilities
- SafeTensors file handling
- Core mathematical operations for LoRA algebra

Special thanks to kohya-ss and the sd-scripts community for creating and maintaining this essential toolkit.

## 🔬 Technical Notes

### Mathematical Foundation
LoRAs modify model weights as: `W_new = W_original + α(BA)`

Subtraction operation: `LoRA_A - LoRA_B = A₁B₁ - A₂B₂`

This removes overlapping parameter modifications while preserving unique characteristics.

### Performance
- **Processing Speed**: ~2-5 seconds per operation
- **Memory Usage**: ~2GB RAM for large LoRAs
- **Compatibility**: Works with safetensors, ckpt, and pt formats
- **Quality**: No degradation when using optimal parameters

---

**⭐ Star the repository at [github.com/shootthesound/lora-the-explorer](https://github.com/shootthesound/lora-the-explorer) if LoRA the Explorer helps with your LoRA workflow!**