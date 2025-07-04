# Fixed Files Directory

This directory contains corrected versions of sd-scripts files that have bugs affecting LoRA the Explorer.

## flux_merge_lora.py

**Issue:** The original file sets `ss_network_module` to `"networks.lora"` instead of `"networks.lora_flux"` for FLUX LoRAs.

**Impact:** This metadata mismatch prevents FLUX LoRAs created by LoRA the Explorer from merging with LoRAs created by other tools (like FluxGym) even when they have the same rank.

**Fix:** Line 550 changed from:
```python
metadata = train_util.build_minimum_network_metadata(str(False), base_model, "networks.lora", dims, alphas, None)
```
to:
```python
metadata = train_util.build_minimum_network_metadata(str(False), base_model, "networks.lora_flux", dims, alphas, None)
```

**Applied:** During installation, this corrected file is copied over the sd-scripts version.