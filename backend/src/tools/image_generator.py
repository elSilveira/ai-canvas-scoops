"""Image generation tool using Stability AI with Ultra endpoint for best quality."""

# Primary import - use Ultra for best quality
from .image_generator_ultra import ImageGeneratorUltraTool

# Keep original for fallback
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple

import src.settings


class ImageGeneratorTool:
    """Image generation tool with automatic fallback from Ultra to Core."""

    def __init__(self):
        """Initialize with Ultra as primary, Core as fallback."""
        if not src.settings.STABILITY_AI_KEY:
            raise ValueError(
                "Stability AI API key not found. Please set STABILITY_AI_KEY environment variable."
            )

        # Try Ultra first
        try:
            self.ultra_generator = ImageGeneratorUltraTool()
            self.has_ultra = True
        except Exception:
            self.has_ultra = False

        # Core fallback setup
        self.api_key = src.settings.STABILITY_AI_KEY
        self.base_url = "https://api.stability.ai/v2beta/stable-image/generate/core"

    def generate_ice_cream_image(
        self,
        ingredients: list[str],
        scoops: int = 2,
        save_to_root: bool = True,
        filename_prefix: str = "icecream",
    ) -> Tuple[Optional[str], Optional[str], bool]:
        """
        Generate an ice cream image with automatic Ultra → Core fallback.

        Args:
            ingredients: List of ice cream ingredients
            scoops: Number of scoops
            save_to_root: Whether to save image to project root
            filename_prefix: Prefix for saved filename

        Returns:
            Tuple of (image_url, local_file_path, success)
        """
        # Try Ultra first for best quality
        if self.has_ultra:
            try:
                print("🚀 Attempting Ultra generation for maximum quality...")
                return self.ultra_generator.generate_ice_cream_image(
                    ingredients=ingredients,
                    scoops=scoops,
                    save_to_root=save_to_root,
                    filename_prefix=filename_prefix,
                    width=2048,
                    height=2048,
                )
            except Exception as e:
                print(f"⚠️ Ultra generation failed: {e}")
                print("🔄 Falling back to Core endpoint...")

        # Fallback to Core endpoint
        return self._generate_with_core(
            ingredients, scoops, save_to_root, filename_prefix
        )

    def _generate_with_core(
        self,
        ingredients: list[str],
        scoops: int,
        save_to_root: bool,
        filename_prefix: str,
    ) -> Tuple[Optional[str], Optional[str], bool]:
        """Generate image using Core endpoint as fallback."""
        try:
            # Create a detailed prompt for ice cream
            prompt = self._create_natural_language_prompt(ingredients, scoops)

            print(f"🎨 Generated prompt: {prompt}")

            # Make request to Stability AI Core
            headers = {"authorization": f"Bearer {self.api_key}", "accept": "image/*"}

            files = {"none": ""}

            data = {"prompt": prompt, "output_format": "png", "aspect_ratio": "1:1"}

            response = requests.post(
                self.base_url, headers=headers, files=files, data=data
            )

            if response.status_code == 200:
                local_path = None
                image_url = None

                if save_to_root:
                    # Save image to project root
                    local_path = self._save_image_from_response(
                        response.content, filename_prefix
                    )
                    image_url = f"file://{local_path}"
                    print(f"🖼️ Stability AI Core image saved to: {local_path}")
                else:
                    # For non-save mode, we'd need to host the image somewhere
                    # For now, save it and return file URL
                    local_path = self._save_image_from_response(
                        response.content, filename_prefix
                    )
                    image_url = f"file://{local_path}"

                return image_url, local_path, True
            else:
                error_info = (
                    response.json() if response.content else {"error": "Unknown error"}
                )
                raise Exception(
                    f"Stability AI Core error {response.status_code}: {error_info}"
                )

        except Exception as e:
            print(f"❌ Stability AI Core image generation failed: {e}")
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
        try:
            # Create a detailed prompt for ice cream
            prompt = self._create_natural_language_prompt(ingredients, scoops)

            print(f"🎨 Generated prompt: {prompt}")

            # Make request to Stability AI
            headers = {"authorization": f"Bearer {self.api_key}", "accept": "image/*"}

            files = {"none": ""}

            data = {"prompt": prompt, "output_format": "png", "aspect_ratio": "1:1"}

            response = requests.post(
                self.base_url, headers=headers, files=files, data=data
            )

            if response.status_code == 200:
                local_path = None
                image_url = None

                if save_to_root:
                    # Save image to project root
                    local_path = self._save_image_from_response(
                        response.content, filename_prefix
                    )
                    image_url = f"file://{local_path}"
                    print(f"🖼️ Stability AI image saved to: {local_path}")
                else:
                    # For non-save mode, we'd need to host the image somewhere
                    # For now, save it and return file URL
                    local_path = self._save_image_from_response(
                        response.content, filename_prefix
                    )
                    image_url = f"file://{local_path}"

                return image_url, local_path, True
            else:
                error_info = (
                    response.json() if response.content else {"error": "Unknown error"}
                )
                raise Exception(
                    f"Stability AI error {response.status_code}: {error_info}"
                )

        except Exception as e:
            print(f"❌ Stability AI image generation failed: {e}")
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

    def _create_natural_language_prompt(
        self, ingredients: list[str], scoops: int
    ) -> str:
        """Create a natural language prompt for Stability AI."""
        # Classify ingredients into flavors and toppings
        flavors = []
        toppings = []

        # Common flavor keywords
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
            "caramel",
            "butterscotch",
            "rocky road",
            "neapolitan",
            "rainbow",
            "tutti frutti",
        ]

        # Common topping keywords
        topping_keywords = [
            "sauce",
            "syrup",
            "sprinkles",
            "chips",
            "chunks",
            "nuts",
            "berries",
            "fruit",
            "whipped",
            "fudge",
            "drizzle",
            "crumble",
            "wafer",
            "cone",
            "candies",
            "gummy",
            "marshmallow",
            "graham",
            "oreo",
            "brownie",
            "cherry",
        ]

        for ingredient in ingredients:
            ingredient_lower = ingredient.lower()
            is_flavor = False
            is_topping = False

            # Check for flavor keywords
            for keyword in flavor_keywords:
                if keyword in ingredient_lower:
                    flavors.append(ingredient)
                    is_flavor = True
                    break

            # If not identified as flavor, check for topping keywords
            if not is_flavor:
                for keyword in topping_keywords:
                    if keyword in ingredient_lower:
                        toppings.append(ingredient)
                        is_topping = True
                        break

            # If still not categorized, assume it's a flavor
            if not is_flavor and not is_topping:
                flavors.append(ingredient)

        # Build the prompt
        if scoops == 1:
            base_text = "A single scoop of ice cream"
        elif scoops == 2:
            base_text = "Two scoops of ice cream"
        else:
            base_text = f"{scoops} scoops of ice cream"

        # Add flavors
        if flavors:
            flavor_text = ", ".join(flavors[:3])  # Limit to 3 flavors for clarity
            base_text += f" with {flavor_text}"

        # Add toppings
        if toppings:
            topping_text = ", ".join(toppings[:3])  # Limit to 3 toppings
            base_text += f" topped with {topping_text}"

        # Determine serving style
        if scoops <= 2:
            container = "in a waffle cone"
        else:
            container = "served in a bowl"

        # Final prompt
        prompt = (
            f"Professional food photography of {base_text}, {container}. "
            f"Photorealistic, high-quality image with soft lighting, clean background, "
            f"appetizing presentation, slightly melting texture. Studio lighting with "
            f"soft shadows. Commercial food photography style."
        )

        return prompt

    def _save_image_from_response(
        self, image_content: bytes, filename_prefix: str
    ) -> str:
        """Save image data from response content to project root."""
        # Get project root directory (2 levels up from this file)
        project_root = Path(__file__).resolve().parents[2]

        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_stability_{timestamp}.png"
        file_path = project_root / filename

        # Save image content directly
        with open(file_path, "wb") as f:
            f.write(image_content)

        print(f"🖼️ Stability AI image saved to: {file_path}")
        return str(file_path)


# Convenience function for easy integration
def generate_ice_cream_image(
    ingredients: list[str], scoops: int = 2, save_to_root: bool = True
) -> Tuple[Optional[str], Optional[str], bool]:
    """
    Convenience function for image generation.

    Returns:
        Tuple of (image_url, local_file_path, success)
    """
    generator = ImageGeneratorTool()
    return generator.generate_ice_cream_image(
        ingredients=ingredients, scoops=scoops, save_to_root=save_to_root
    )
