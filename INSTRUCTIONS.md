# 🧭 LoRA the Explorer - Setup Instructions

## 📦 **Complete Toolkit Ready!**

LoRA the Explorer is a comprehensive FLUX LoRA manipulation toolkit with an intuitive GUI interface:

```
lora-the-explorer/
├── 🧭 lora_algebra_gui.py    # Quick GUI launcher
├── 📚 README.md              # Complete documentation
├── ⚙️  requirements.txt       # Dependencies
├── 🏗️  setup.py              # Installation script
├── 🛠️  install.py             # Automatic installer
├── 📄 LICENSE                # MIT license
├── 🔧 lora_algebra/          # Main package
│   ├── core.py              # LoRA processing engine
│   ├── operations.py        # Subtract, merge, layer operations
│   ├── analysis.py          # Compatibility prediction
│   ├── utils.py             # Helper functions
│   ├── gui.py               # Full Gradio interface
│   └── lora_cache.py        # Path management system
└── 🔗 sd-scripts/           # Kohya sd-scripts integration
```

## 🚀 **Quick Start**

### **Option 1: Automatic Installation (Recommended)**
```bash
# Clone and install everything automatically
git clone https://github.com/shootthesound/lora-the-explorer.git
cd lora-the-explorer
python install.py
```

The installer will:
- ✅ Create virtual environment
- ✅ Download sd-scripts with FLUX support (pinned to stable commit)
- ✅ Apply FLUX metadata compatibility fixes
- ✅ Install all dependencies
- ✅ Create launcher scripts

### **Option 2: Launch GUI Directly**
```bash
cd lora-the-explorer
python lora_algebra_gui.py
```

## 🎯 **Features Overview**

### **📖 About LoRA the Explorer**
Overview and getting started:
- Community project focus and development philosophy
- Feature summary and navigation guide
- Demo examples with layer merging showcase
- Credits and support information

### **🔺 LoRA Subtraction**
Remove conflicts between LoRAs:
- Perfect for cleaning style LoRAs that change faces
- Create character-neutral styles
- Fix interference between LoRAs
- Sweet spot formula: 85% of normal usage strength

### **➕ LoRA Merging**
Traditional LoRA combination:
- Add two LoRAs together with custom weights
- Auto-detects incompatibilities and enables concat mode
- Works with LoRAs from different training tools
- Enhanced error handling with helpful suggestions

### **🔀 Layer Based LoRA Merging** 
Surgically combine specific layers:
- **Face A + Style B**: Character face + artistic style
- **Facial Priority**: All facial layers from one LoRA
- **Complement Split**: Early/late layer combinations
- **Fix Overtrained**: Replace bad layers with good ones

### **🎯 Layer Targeting**
Selectively mute FLUX layers:
- **Facial Layers (7,12,16,20)**: Remove face details, keep costume/style
- **Aggressive Mode**: Maximum facial identity removal  
- **Custom Selection**: Choose from 38 available layers
- **Perfect for**: Character costumes without faces, universal LoRAs

### **🔍 LoRA MetaViewer**
Technical validation and metadata viewing:
- Check rank, alpha, base model compatibility
- Predict potential conflicts and suggest optimal strengths
- Browse and analyze existing LoRAs
- View complete LoRA metadata in readable format
- Double-click file selection from analysis results

### **🏷️ LoRA MetaEditor**
Direct metadata editing with full control:
- Edit any metadata field in raw JSON format
- Fix training tool compatibility issues (wrong network modules, base models)
- Repair corrupted or incorrect metadata
- Universal metadata management for LoRAs from any source
- In-place editing with full user responsibility
- Cross-tool compatibility fixes and custom metadata management

### **📁 LoRA Paths**
Streamlined workflow management:
- Recursive LoRA directory scanning with caching
- Autocomplete for all path inputs (50 results, starts after 1 character)
- Default output directory settings that persist across sessions
- Smart file discovery and persistent settings

## 💡 **Key Use Cases**

### **Character Costume Extraction**
- **Gandalf costume, no Ian McKellen face**
- **Wonder Woman outfit, no Gal Gadot face**
- **Anime character clothes, no specific face**

### **Style LoRA Cleaning**
- Remove face changes from artistic styles
- Create face-neutral lighting/composition LoRAs
- Fix style LoRAs that interfere with character LoRAs

### **Advanced Combinations**
- Mix facial features from one LoRA with style from another
- Create hybrid concepts using selective layers
- Rescue partially corrupted or overtrained LoRAs

### **Cross-Tool Compatibility Fixes**
- Merge LoRAs from different training tools seamlessly
- Fix metadata issues preventing LoRA combinations
- Handle layer-merged LoRAs with mixed dimensions
- Repair LoRAs with incorrect network modules

### **Advanced Metadata Management**
- **LoRA MetaViewer**: View and analyze complete LoRA metadata
- **LoRA MetaEditor**: Edit any metadata field directly
- **Automatic fixes**: Wrong network modules (networks.lora → networks.lora_flux)
- **Repair capabilities**: Correct base model info, add training details
- **Privacy tools**: Clean sensitive information from metadata
- **Cross-tool support**: Fix LoRAs from any training tool

## 🛠️ **Getting Started Workflow**

1. **Setup Paths**
   - Use "LoRA Paths" tab to scan your directory
   - Set default output directory
   - All paths now have autocomplete

2. **Start Simple**
   - Try basic LoRA subtraction first
   - Use compatibility analysis to understand your LoRAs
   - Experiment with preset layer combinations

3. **Advanced Techniques**
   - Layer targeting for face/style separation
   - Surgical layer merging for custom combinations
   - Use analysis results to optimize parameters

## 📤 **Sharing Your Tool**

### **GitHub Repository Setup**
```bash
cd lora-the-explorer
git init
git add .
git commit -m "Initial release: LoRA the Explorer

🧭 Advanced FLUX LoRA manipulation toolkit featuring:
- LoRA subtraction for compatibility fixes
- Layer targeting for facial/style control  
- Surgical layer merging capabilities
- Comprehensive analysis and compatibility tools
- Intuitive GUI interface for all skill levels
- Built for the community - completely free to use

Perfect for:
- Removing face changes from style LoRAs
- Creating character costumes without faces
- Fixing LoRA interference issues
- Advanced layer-based combinations"

git remote add origin https://github.com/shootthesound/lora-the-explorer.git
git branch -M main
git push -u origin main
```

### **Community Sharing**
- **Reddit**: r/StableDiffusion, r/LocalLLaMA
- **CivitAI**: Share results and techniques
- **Discord**: AI art communities
- **GitHub**: Open source collaboration

## 🌟 **What Makes This Special**

### **🆕 Innovation**
- **First comprehensive GUI** for FLUX layer manipulation
- **Mathematical approach** to LoRA compatibility
- **Layer-specific targeting** with 38-layer granularity
- **Integrated workflow** from analysis to final output

### **🎯 Practical Impact**
- **Solves real problems** - face interference, unusable LoRAs
- **Saves time** - no more manual trial and error
- **Enables new workflows** - character + style combinations
- **Community benefit** - completely free and open

### **🔬 Technical Excellence**
- **Robust error handling** and validation
- **Performance optimized** for large LoRAs
- **Professional UI/UX** with helpful guides
- **Extensible architecture** for future features

## 🤝 **Community & Support**

### **Free to Use**
LoRA the Explorer is completely free. If you find it useful, you can support development at:
**☕ [buymeacoffee.com/loratheexplorer](https://buymeacoffee.com/loratheexplorer)**

Recurring supporters get early access to test builds.

### **Feedback Welcome**
- **Bug reports**: Help improve stability
- **Feature requests**: Shape future development  
- **Usage examples**: Share your results
- **Technical feedback**: Optimize performance

### **Contributing**
- **GUI improvements**: Better user experience
- **Layer research**: Understanding FLUX architecture
- **Performance**: Faster processing
- **Documentation**: Better guides and examples

## 🎉 **Ready to Launch!**

Your toolkit is complete and ready for the community. LoRA the Explorer provides professional-grade LoRA manipulation tools that solve real problems for FLUX users.

**Key strengths:**
- ✅ **Comprehensive feature set** covering all major use cases
- ✅ **Professional presentation** with clear documentation
- ✅ **Community focus** - free and feedback-driven
- ✅ **Easy installation** with automatic setup
- ✅ **Intuitive GUI interface** for ease of use

---

**🧭 Ready to explore the world of LoRA possibilities!** 🚀