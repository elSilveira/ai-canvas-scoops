"""Mock image generator for fallback when Stability AI is unavailable."""

import random
from typing import Optional, Dict, Any


class MockImageGeneratorTool:
    """Mock image generator that provides placeholder images for development/fallback."""

    def __init__(self):
        """Initialize mock generator with placeholder image URLs."""
        self.placeholder_images = [
            "https://via.placeholder.com/512x512/FFB6C1/FFFFFF?text=🍦+Ice+Cream",
            "https://via.placeholder.com/512x512/87CEEB/FFFFFF?text=🍨+Delicious",
            "https://via.placeholder.com/512x512/DDA0DD/FFFFFF?text=🧁+Sweet",
            "https://via.placeholder.com/512x512/F0E68C/FFFFFF?text=🍯+Tasty",
            "https://via.placeholder.com/512x512/98FB98/FFFFFF?text=🌟+Amazing",
        ]

    async def generate_ice_cream_image(
        self,
        selections: list[str],
        player_name: str = "Player",
        style: str = "realistic",
        size: str = "512x512",
    ) -> Dict[str, Any]:
        """
        Generate a mock ice cream image response.

        Args:
            selections: List of player selections
            player_name: Name of the player
            style: Image style (ignored in mock)
            size: Image size (ignored in mock)

        Returns:
            Dict with success status and mock image URL
        """
        try:
            # Select a random placeholder image
            mock_image_url = random.choice(self.placeholder_images)

            # Customize based on selections if available
            if selections:
                primary_selection = selections[0] if selections else "Classic"
                # Create a more personalized placeholder
                mock_image_url = f"https://via.placeholder.com/512x512/FFB6C1/FFFFFF?text=🍦+{primary_selection}+for+{player_name}"

            return {
                "success": True,
                "image_url": mock_image_url,
                "metadata": {
                    "generator": "mock",
                    "player_name": player_name,
                    "selections": selections,
                    "note": "This is a placeholder image. Configure STABILITY_AI_KEY for real image generation.",
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Mock image generation failed: {str(e)}",
            }

    def generate_ice_cream_image(
        self,
        ingredients: list[str],
        scoops: int = 2,
        save_to_root: bool = False,
        filename_prefix: str = "icecream",
    ) -> tuple[Optional[str], Optional[str], bool]:
        """
        Synchronous version for backward compatibility with existing code.

        Returns:
            Tuple of (image_url, file_path, success)
        """
        try:
            # Generate mock URL based on ingredients
            ingredient_text = "+".join(ingredients[:2]) if ingredients else "Ice+Cream"
            mock_url = f"https://via.placeholder.com/512x512/FFB6C1/FFFFFF?text=🍦+{ingredient_text}"

            return mock_url, None, True

        except Exception:
            return None, None, False
