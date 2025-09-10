from typing import Any, Dict, List

from pydantic import BaseModel, Field
from pydantic_ai import Agent

import src.settings


class ImageInstructions(BaseModel):
    scoops: int
    flavors: List[str] = Field(default_factory=list)
    toppings: List[str] = Field(default_factory=list)

    def model_dump(self, **kwargs) -> Dict[str, Any]:
        return {
            "version": "1.0",
            "task": "generate_image",
            "subject": {
                "type": "ice_cream_cone",
                "scoops": self.scoops,
                "flavors": self.flavors,
                "container": "waffle_cone",
                "toppings": self.toppings,
                "state": "slightly_melting",
            },
            "look": {
                "style": "photorealistic",
                "lighting": "soft_diffused_front",
                "surface_detail": "high",
                "color_palette": ["#F7F3E9", "#C57A40", "#3A2B1A"],
            },
            "composition": {
                "framing": "centered",
                "shot": "close_up",
                "angle": "eye_level",
                "negative_space": "ample",
            },
            "camera": {"focal_length_mm": 50, "aperture_f": 2.8},
            "background": {"type": "solid_color", "color": "#F5F7FB"},
            "output": {
                "aspect_ratio": "1:1",
                "width": 2048,
                "height": 2048,
                "format": "png",
                "seed": 42,
            },
            "negative_prompt": [
                "hands",
                "text",
                "logos",
                "watermarks",
                "multiple_cones",
                "deformed_ice_cream",
                "plastic_or_cartoon_style",
            ],
            "constraints": {"brand_safe": True, "no_background_clutter": True},
        }


def get_image_generator_agent(instructions: ImageInstructions) -> Agent:
    return Agent(
        "openai:gpt-5",
        system_prompt=f"""
        You are in charge of generating high-quality images of ice cream cones based on detailed user instructions. Your goal is to create photorealistic images that accurately reflect the specified number of scoops, flavors, toppings, and container type, while adhering to the desired style, composition, and camera settings.
        ```
        {instructions.model_dump_json()}
        ```
        """,
    )


if __name__ == "__main__":
    instructions = ImageInstructions(
        scoops=3,
        flavors=["vanilla", "chocolate", "strawberry"],
        toppings=["sprinkles", "chocolate_syrup"],
    )
    print(instructions.model_dump_json())
    # response = get_image_generator_agent(instructions).run_sync(instructions)
    # print(response)  # This would be the generated image URL or data

    test = Agent(
        "openai:gpt-5",
        system_prompt="""
        What is the capital of France?
        """,
    )
    response = test.run_sync()
    print(response)
