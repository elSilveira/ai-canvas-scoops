"""Advanced image generation tool using Stability AI Ultra endpoint with specification-based prompts."""

import random
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, Dict, Any
from io import BytesIO
from PIL import Image

import src.settings


class ImageGeneratorUltraTool:
    """Advanced image generation tool using Stability AI Ultra endpoint."""

    def __init__(self):
        """Initialize the image generator with Stability AI Ultra."""
        if not src.settings.STABILITY_AI_KEY:
            raise ValueError(
                "Stability AI API key not found. Please set STABILITY_AI_KEY environment variable."
            )

        self.api_key = src.settings.STABILITY_AI_KEY
        self.ultra_url = "https://api.stability.ai/v2beta/stable-image/generate/ultra"

    def generate_ice_cream_image(
        self,
        ingredients: list[str],
        scoops: int = 2,
        save_to_root: bool = True,
        filename_prefix: str = "icecream",
        width: int = 2048,
        height: int = 2048,
        generate_variations: bool = False,
    ) -> Tuple[Optional[str], Optional[str], bool]:
        """
        Generate an ice cream image based on ingredients using Stability AI Ultra.

        Args:
            ingredients: List of ice cream ingredients
            scoops: Number of scoops
            save_to_root: Whether to save image to project root
            filename_prefix: Prefix for saved filename
            width: Output image width
            height: Output image height
            generate_variations: Whether to generate multiple variations

        Returns:
            Tuple of (image_url, local_file_path, success)
        """
        try:
            # Create specification from ingredients
            spec = self._create_ice_cream_spec(ingredients, scoops, width, height)

            print("🎯 Generated specification:")
            print(
                f"  Subject: {spec['subject']['type']} with {spec['subject']['scoops']} scoops"
            )
            print(f"  Flavors: {', '.join(spec['subject']['flavors'])}")
            print(f"  Toppings: {', '.join(spec['subject']['toppings'])}")

            if generate_variations:
                # Generate two variations
                filepaths = self._generate_two_images(
                    spec, filename_prefix, save_to_root
                )
                if filepaths:
                    primary_path = filepaths[0]
                    image_url = f"file://{primary_path}" if save_to_root else None
                    return image_url, primary_path, True
            else:
                # Generate single image
                image_bytes = self._call_ultra(spec)

                if save_to_root:
                    local_path = self._save_image_from_bytes(
                        image_bytes, filename_prefix, spec
                    )
                    image_url = f"file://{local_path}"
                    print(f"🖼️ Stability AI Ultra image saved to: {local_path}")
                    return image_url, local_path, True

            return None, None, False

        except Exception as e:
            print(f"❌ Stability AI Ultra image generation failed: {e}")
            print("🔄 Falling back to mock image generation...")

            # Fallback to mock generation
            try:
                from src.tools.mock_image_generator import MockImageGeneratorTool

                mock_generator = MockImageGeneratorTool()
                return mock_generator.generate_ice_cream_image(
                    ingredients, scoops, save_to_root, filename_prefix
                )
            except Exception as mock_error:
                print(f"❌ Mock generation also failed: {mock_error}")
                return None, None, False

    def _create_ice_cream_spec(
        self, ingredients: list[str], scoops: int, width: int, height: int
    ) -> Dict[str, Any]:
        """Create a detailed specification for ice cream image generation with proper stacking logic."""

        # Analyze ingredients with proper ordering
        flavors, ordered_toppings = self._analyze_ingredients(ingredients)

        # Handle empty cone case (0 flavors/scoops)
        if scoops == 0 or not flavors:
            return self._create_empty_cone_spec(width, height)

        # Ensure we don't exceed the number of requested scoops
        available_flavors = flavors[:scoops] if len(flavors) >= scoops else flavors

        # Create ordered scoop description for stacking
        stacked_scoops = self._create_stacking_description(available_flavors, scoops)

        # Determine container based on scoops - ALWAYS use waffle cone (MANDATORY)
        container = "waffle_cone"  # MANDATORY: Always use waffle cone

        if scoops == 1:
            state = "perfectly_formed"
        elif scoops <= 3:
            state = "slightly_melting"
        else:
            state = "creamy_soft"

        # Create comprehensive specification
        spec = {
            "version": "1.0",
            "task": "generate_image",
            "subject": {
                "type": "ice_cream_dessert",
                "scoops": scoops,
                "flavors": available_flavors,
                "stacking_order": stacked_scoops,
                "container": container,
                "toppings": ordered_toppings[:4],  # Limit to 4 toppings
                "topping_application": "liquid_first_then_solid",
                "state": state,
            },
            "look": {
                "style": "photorealistic",
                "lighting": "soft_diffused_front",
                "surface_detail": "high",
                "color_palette": self._get_color_palette(
                    available_flavors, ordered_toppings
                ),
            },
            "composition": {
                "framing": "centered",
                "shot": "close_up" if scoops <= 2 else "medium_shot",
                "angle": "eye_level",
                "negative_space": "ample",
            },
            "camera": {"focal_length_mm": 50 if scoops <= 2 else 85, "aperture_f": 2.8},
            "background": {
                "type": "solid_color",
                "color": "#F8F9FA",  # Clean light background
            },
            "output": {
                "aspect_ratio": "1:1",
                "width": width,
                "height": height,
                "format": "png",
                "seed": random.randint(1, 4294967294),
            },
            "negative_prompt": [
                "hands",
                "text",
                "logos",
                "watermarks",
                "multiple_cones",
                "multiple_waffle_cones",
                "two_cones",
                "three_cones",
                "several_cones",
                "many_cones",
                "separate_cones",
                "individual_cones",
                "multiple_ice_creams",
                "side_by_side_cones",
                "deformed_ice_cream",
                "plastic_or_cartoon_style",
                "artificial_colors",
                "oversaturated",
                "mixed_scoops",
                "unstacked_scoops",
                "floating_scoops",
                "bowl",
                "cup",
                "sugar_cone",
                "plain_cone",
                "cake_cone",
                "paper_cup",
                "glass_bowl",
                "ceramic_bowl",
                "plastic_container",
                "toppings_between_scoops",
                "sauce_between_layers",
                "sprinkles_between_scoops",
                "layered_toppings",
                "mixed_layers",
                "toppings_in_middle",
            ],
            "constraints": {
                "brand_safe": True,
                "no_background_clutter": True,
                "proper_stacking": True,
            },
        }

        return spec

    def _create_empty_cone_spec(self, width: int, height: int) -> Dict[str, Any]:
        """Create specification for empty cone when no flavors are provided."""
        spec = {
            "version": "1.0",
            "task": "generate_image",
            "subject": {
                "type": "empty_ice_cream_cone",
                "scoops": 0,
                "flavors": [],
                "container": "waffle_cone",
                "toppings": [],
                "state": "empty_clean",
            },
            "look": {
                "style": "photorealistic",
                "lighting": "soft_diffused_front",
                "surface_detail": "high",
                "color_palette": ["#D2B48C", "#F5DEB3", "#FAEBD7"],  # Cone colors
            },
            "composition": {
                "framing": "centered",
                "shot": "close_up",
                "angle": "slight_angle",
                "negative_space": "ample",
            },
            "camera": {"focal_length_mm": 50, "aperture_f": 2.8},
            "background": {"type": "solid_color", "color": "#F8F9FA"},
            "output": {
                "aspect_ratio": "1:1",
                "width": width,
                "height": height,
                "format": "png",
                "seed": random.randint(1, 4294967294),
            },
            "negative_prompt": [
                "ice_cream",
                "ice cream",
                "scoops",
                "scoop",
                "melting",
                "toppings",
                "sauce",
                "sprinkles",
                "chips",
                "any_food_items",
                "dessert_toppings",
                "sweet_toppings",
                "frozen_dessert",
                "dairy_products",
                "cream",
                "vanilla",
                "chocolate",
                "strawberry",
                "flavors",
                "hands",
                "text",
                "logos",
                "watermarks",
                "deformed_cone",
                "filled_cone",
                "topped_cone",
            ],
            "constraints": {
                "brand_safe": True,
                "no_background_clutter": True,
                "empty_cone_only": True,
            },
        }
        return spec

    def _create_stacking_description(self, flavors: list[str], scoops: int) -> str:
        """Create a description of how scoops should be stacked in order."""
        if scoops == 0 or not flavors:
            return "no_scoops"

        if scoops == 1:
            return f"single scoop of {flavors[0]} on top"

        # Build stacking description from bottom to top
        stack_parts = []

        for i in range(min(scoops, len(flavors))):
            if i == 0:
                stack_parts.append(f"bottom scoop: {flavors[i]}")
            elif i == scoops - 1:
                stack_parts.append(f"top scoop: {flavors[i]}")
            else:
                stack_parts.append(f"middle scoop {i}: {flavors[i]}")

        # If we have more scoops than flavors, repeat the last flavor
        if scoops > len(flavors):
            remaining_scoops = scoops - len(flavors)
            last_flavor = flavors[-1] if flavors else "vanilla ice cream"
            for i in range(remaining_scoops):
                stack_parts.append(f"additional scoop: {last_flavor}")

        return " stacked with ".join(stack_parts)

    def _analyze_ingredients(
        self, ingredients: list[str]
    ) -> Tuple[list[str], list[str]]:
        """Analyze ingredients and categorize into flavors and toppings with proper ordering."""
        flavors = []
        liquid_toppings = []
        solid_toppings = []

        # Enhanced flavor keywords - more specific matches
        flavor_keywords = [
            "ice cream",
            "gelato",
            "sorbet",
            "frozen yogurt",
            "vanilla",
            "chocolate",
            "strawberry",
            "mint",
            "pistachio",
            "cookie",
            "butterscotch",
            "rocky road",
            "neapolitan",
            "rainbow",
            "tutti frutti",
            "custard",
            "sherbet",
        ]

        # Liquid toppings (applied first)
        liquid_topping_keywords = [
            "sauce",
            "syrup",
            "drizzle",
            "fudge",
            "caramel sauce",
            "chocolate sauce",
            "strawberry sauce",
            "hot fudge",
            "butterscotch sauce",
            "whipped cream",
        ]

        # Solid toppings (applied second)
        solid_topping_keywords = [
            "sprinkles",
            "chips",
            "chunks",
            "nuts",
            "berries",
            "fruit",
            "crumble",
            "wafer",
            "candies",
            "gummy",
            "marshmallow",
            "graham",
            "oreo",
            "brownie",
            "cherry",
            "jimmies",
            "confetti",
            "coconut",
        ]

        for ingredient in ingredients:
            ingredient_lower = ingredient.lower()
            is_categorized = False

            # Check for liquid toppings FIRST
            for keyword in liquid_topping_keywords:
                if keyword in ingredient_lower:
                    liquid_toppings.append(ingredient)
                    is_categorized = True
                    break

            # Then check for solid toppings
            if not is_categorized:
                for keyword in solid_topping_keywords:
                    if keyword in ingredient_lower:
                        solid_toppings.append(ingredient)
                        is_categorized = True
                        break

            # Finally check for flavor keywords if not already categorized
            if not is_categorized:
                # Special case: if it contains "ice cream" but also topping words, it's a flavor
                if "ice cream" in ingredient_lower:
                    flavors.append(ingredient)
                    is_categorized = True
                else:
                    for keyword in flavor_keywords:
                        if keyword in ingredient_lower:
                            flavors.append(ingredient)
                            is_categorized = True
                            break

            # Default to flavor if uncategorized
            if not is_categorized:
                flavors.append(ingredient)

        # Combine toppings in proper order: liquids first, then solids
        ordered_toppings = liquid_toppings + solid_toppings

        return flavors, ordered_toppings

    def _get_color_palette(self, flavors: list[str], toppings: list[str]) -> list[str]:
        """Generate appropriate color palette based on flavors and toppings."""
        # Base palette for ice cream
        palette = ["#F7F3E9", "#FFFFFF", "#FFF8DC"]  # Cream, white, beige

        # Add flavor-specific colors
        for flavor in flavors:
            flavor_lower = flavor.lower()
            if "chocolate" in flavor_lower:
                palette.append("#8B4513")
            elif "strawberry" in flavor_lower:
                palette.append("#FFB6C1")
            elif "mint" in flavor_lower:
                palette.append("#98FB98")
            elif "caramel" in flavor_lower:
                palette.append("#C57A40")
            elif "pistachio" in flavor_lower:
                palette.append("#93C572")

        # Add topping-specific colors
        for topping in toppings:
            topping_lower = topping.lower()
            if "chocolate" in topping_lower:
                palette.append("#3A2B1A")
            elif "sprinkles" in topping_lower:
                palette.extend(["#FF6B6B", "#4ECDC4", "#FFE66D"])

        return palette[:6]  # Limit to 6 colors

    def _prompt_from_spec(self, spec: Dict[str, Any]) -> str:
        """Convert specification to detailed prompt with proper stacking and topping order."""
        s = spec["subject"]
        look = spec["look"]
        c = spec["composition"]
        cam = spec["camera"]
        bg = spec["background"]

        # Handle empty cone case
        if s["scoops"] == 0 or s["type"] == "empty_ice_cream_cone":
            prompt_parts = [
                "Photorealistic EMPTY waffle ice cream cone with NO ice cream scoops, completely EMPTY and unused.",
                "ABSOLUTELY NO ice cream, NO scoops, NO toppings, NO food items whatsoever.",
                "Just a clean, empty, pristine waffle cone standing alone.",
                "IMPORTANT: The cone must be completely EMPTY with NO ice cream inside or on top.",
                f"Framing: {c['framing']}, {c['shot']}, angle {c['angle']}, negative space {c['negative_space']}.",
                f"Lighting: {look['lighting']}. Surface detail: {look['surface_detail']}.",
                f"Color palette: {', '.join(look.get('color_palette', []))}.",
                f"Background: {bg['type']} {bg.get('color', '#FFFFFF')}.",
                f"Camera feel: {cam['focal_length_mm']}mm, f/{cam['aperture_f']}.",
            ]
        else:
            # Build complete stacking description with toppings placement
            if "stacking_order" in s and s["stacking_order"] != "no_scoops":
                scoop_description = f"Ice cream with {s['stacking_order']} in a WAFFLE CONE (textured waffle pattern cone)"
            else:
                scoop_description = f"{s['scoops']} scoop(s) of {', '.join(s['flavors'])} stacked in a WAFFLE CONE (textured waffle pattern cone)"

            # Build comprehensive structure description
            if s.get("toppings"):
                if s.get("topping_application") == "liquid_first_then_solid":
                    structure_description = f"Complete structure from bottom to top: waffle cone base → {scoop_description} → toppings applied ON TOP of all scoops in this order: {', '.join(s['toppings'])} (liquid sauces first, then solid toppings on the very top)."
                else:
                    structure_description = f"Complete structure: waffle cone base → {scoop_description} → toppings ON TOP: {', '.join(s['toppings'])}."
            else:
                structure_description = (
                    f"Structure: waffle cone base → {scoop_description} (no toppings)."
                )

            prompt_parts = [
                f"Photorealistic {s['type'].replace('_', ' ')} with perfect layer structure.",
                "SINGLE waffle cone only - exactly ONE cone with ALL scoops stacked on top.",
                structure_description,
                "MANDATORY: Must be served in a waffle cone with visible waffle texture pattern.",
                "CRITICAL: Only ONE cone in the entire image - all scoops must be stacked on this single cone.",
                "IMPORTANT: All toppings must be placed ON TOP of the highest scoop, never between scoops.",
                f"State: {s['state']}. Perfect stacking with no floating or mixed scoops, toppings only on the very top.",
                f"Framing: {c['framing']}, {c['shot']}, angle {c['angle']}, negative space {c['negative_space']}.",
                f"Lighting: {look['lighting']}. Surface detail: {look['surface_detail']}.",
                f"Color palette: {', '.join(look.get('color_palette', []))}.",
                f"Background: {bg['type']} {bg.get('color', '#FFFFFF')}.",
                f"Camera feel: {cam['focal_length_mm']}mm, f/{cam['aperture_f']}.",
            ]

        return " ".join(prompt_parts)

    def _aspect_from_spec(self, spec: Dict[str, Any]) -> str:
        """Extract aspect ratio from spec."""
        allowed = {"1:1", "16:9", "21:9", "3:2", "2:3", "4:5", "5:4", "9:16", "9:21"}
        ar = spec.get("output", {}).get("aspect_ratio", "1:1")
        return ar if ar in allowed else "1:1"

    def _seed_from_spec(self, spec: Dict[str, Any]) -> int:
        """Extract seed from spec."""
        s = spec.get("output", {}).get("seed")
        return int(s) if isinstance(s, int) and 0 <= s <= 4294967294 else 0

    def _call_ultra(self, spec: Dict[str, Any], prompt_variation: str = "") -> bytes:
        """Make API call to Stability AI Ultra endpoint."""
        prompt = self._prompt_from_spec(spec)
        if prompt_variation:
            prompt += f" {prompt_variation}"

        negative = ", ".join(spec.get("negative_prompt", []))
        aspect_ratio = self._aspect_from_spec(spec)
        output_format = spec.get("output", {}).get("format", "png").lower()
        seed = self._seed_from_spec(spec)

        print(f"🎨 Generated prompt: {prompt}")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "image/*",
        }

        # Multipart form data
        form = {
            "prompt": (None, prompt),
            "negative_prompt": (None, negative) if negative else None,
            "aspect_ratio": (None, aspect_ratio),
            "output_format": (None, output_format),
            "seed": (None, str(seed)),
            "style_preset": (None, "photographic"),
        }

        # Remove None values
        form = {k: v for k, v in form.items() if v is not None}

        response = requests.post(
            self.ultra_url, headers=headers, files=form, timeout=120
        )

        if response.status_code != 200:
            try:
                error_json = response.json()
                raise RuntimeError(
                    f"Stability API error {response.status_code}: {error_json}"
                )
            except Exception:
                raise RuntimeError(
                    f"Stability API error {response.status_code}: {response.text[:200]}"
                )

        return response.content

    def _generate_two_images(
        self, spec: Dict[str, Any], filename_prefix: str, save_to_root: bool
    ) -> Optional[list[str]]:
        """Generate two image variations."""
        try:
            # Generate first image
            img1 = self._call_ultra(spec)

            # Create second spec with different seed and variation
            spec2 = {**spec}
            spec2.setdefault("output", {})["seed"] = random.randint(1, 4294967294)
            img2 = self._call_ultra(
                spec2, "Subtle variation in drizzle pattern and sprinkle distribution."
            )

            # Save both images
            if save_to_root:
                path1 = self._save_image_from_bytes(
                    img1, f"{filename_prefix}_var1", spec
                )
                path2 = self._save_image_from_bytes(
                    img2, f"{filename_prefix}_var2", spec
                )
                return [path1, path2]

            return None

        except Exception as e:
            print(f"❌ Failed to generate image variations: {e}")
            return None

    def _save_image_from_bytes(
        self, image_bytes: bytes, filename_prefix: str, spec: Dict[str, Any]
    ) -> str:
        """Save image bytes to file with optional upscaling."""
        # Optional upscaling
        image_bytes = self._upscale_if_requested(image_bytes, spec)

        # Get project root directory
        project_root = Path(__file__).resolve().parents[2]

        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fmt = spec.get("output", {}).get("format", "png").lower()
        filename = f"{filename_prefix}_ultra_{timestamp}.{fmt}"
        file_path = project_root / filename

        # Save image
        with open(file_path, "wb") as f:
            f.write(image_bytes)

        print(f"🖼️ Stability AI Ultra image saved to: {file_path}")
        return str(file_path)

    def _upscale_if_requested(self, img_bytes: bytes, spec: Dict[str, Any]) -> bytes:
        """Upscale image if specific dimensions are requested."""
        out = spec.get("output", {})
        w, h = out.get("width"), out.get("height")
        fmt = out.get("format", "png").lower()

        if w and h:
            try:
                img = Image.open(BytesIO(img_bytes))
                if (img.width, img.height) != (w, h):
                    img = img.resize((w, h), Image.LANCZOS)
                    buf = BytesIO()
                    img.save(buf, format="PNG" if fmt == "png" else "JPEG")
                    return buf.getvalue()
            except Exception as e:
                print(f"⚠️ Upscaling failed, using original: {e}")

        return img_bytes


# Convenience function for easy integration
def generate_ice_cream_image_ultra(
    ingredients: list[str],
    scoops: int = 2,
    save_to_root: bool = True,
    width: int = 2048,
    height: int = 2048,
    generate_variations: bool = False,
) -> Tuple[Optional[str], Optional[str], bool]:
    """
    Convenience function for ultra image generation.

    Returns:
        Tuple of (image_url, local_file_path, success)
    """
    generator = ImageGeneratorUltraTool()
    return generator.generate_ice_cream_image(
        ingredients=ingredients,
        scoops=scoops,
        save_to_root=save_to_root,
        width=width,
        height=height,
        generate_variations=generate_variations,
    )
