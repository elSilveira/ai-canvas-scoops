import asyncio
import aiosqlite
from src.settings import DB_FILE


async def migrate_and_mock():
    print(f"Loading database from {DB_FILE}")
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("DROP TABLE IF EXISTS inventory")
        await db.commit()

        await db.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
            ingredient    TEXT PRIMARY KEY,           -- name of the ingredient
            description   TEXT,                       -- short description
            used_on       TEXT NOT NULL DEFAULT '[]', -- JSON array of recipe names
            allergies     TEXT NOT NULL DEFAULT '[]', -- JSON array of allergy tags
            quantity      TEXT,                       -- purchase pack size / unit (e.g., "5 kg bag", "946 ml bottle")
            cost_min      REAL,                       -- per-portion cost (min for ranges)
            cost_max      REAL,                       -- per-portion cost (max for ranges; equal to min if fixed)
            inventory     INTEGER NOT NULL DEFAULT 0, -- number of packs on hand (mocked values later)
            CHECK (json_valid(used_on)),
            CHECK (json_valid(allergies)),
            CHECK (inventory >= 0),
            CHECK (cost_min IS NULL OR cost_min >= 0),
            CHECK (cost_max IS NULL OR cost_max >= 0),
            CHECK (cost_min IS NULL OR cost_max IS NULL OR cost_max >= cost_min)
            )
        """)
        await db.commit()

        await db.execute("""
            INSERT INTO inventory (
               ingredient, description, used_on, allergies, quantity, cost_min, cost_max, inventory
            ) VALUES
            -- 1
            ('Vanilla extract',
            'Pure vanilla extract for base flavoring',
            '["Vanilla (Superman)","Stevia-sweetened vanilla (Spock)"]',
            '["alcohol"]',
            '946 ml bottle',
            0.25, 0.25, 7),

            -- 2
            ('Rum flavoring (extract)',
            'Rum flavor/extract to soak raisins',
            '["Rum raisin (Indiana Jones)"]',
            '["alcohol"]',
            '473 ml bottle',
            NULL, NULL, 3),

            -- 3
            ('Raisins',
            'Seedless raisins for rum-raisin mix-in',
            '["Rum raisin (Indiana Jones)"]',
            '["sulfites"]',
            '5 kg bag',
            NULL, NULL, 4),

            -- 4
            ('Lemons (fresh)',
            'Juice + zest for bright sorbet',
            '["Lemon sorbet (Mary Poppins)"]',
            '["citrus"]',
            '5 kg case (~35 pcs)',
            0.15, 0.15, 2),

            -- 5
            ('Mint leaves (fresh)',
            'Fresh mint for infusion or garnish',
            '["Mint (Elsa)"]',
            '[]',
            '250 g clamshell',
            0.10, 0.10, 6),

            -- 6
            ('Mint extract',
            'Alternative to fresh leaves',
            '["Mint (Elsa)"]',
            '["alcohol"]',
            '473 ml bottle',
            0.10, 0.10, 2),

            -- 7
            ('Dark chocolate (70%+ callets)',
            'Premium dark chocolate for shavings/chunks and sauces',
            '["Dark chocolate (Iron Man)","Chocolate chips (Willy Wonka)","Silky chocolate mousse ribbon (James Bond)","Rich chocolate sauce (Vianne Rocher)"]',
            '["milk","soy","caffeine"]',
            '5 kg box',
            0.50, 0.50, 3),

            -- 8
            ('Mascarpone',
            'Soft Italian cheese for tiramisu swirl',
            '["Tiramisu swirl (Holly Golightly)"]',
            '["dairy"]',
            '2 kg tub',
            0.40, 0.55, 5),

            -- 9
            ('Cocoa powder (unsweetened)',
            'For tiramisu drizzle and chocolate sauce',
            '["Tiramisu swirl (Holly Golightly)","Rich chocolate sauce (Vianne Rocher)"]',
            '["caffeine"]',
            '1 kg bag',
            0.10, 0.10, 8),

            -- 10
            ('Espresso beans',
            'Pulled as espresso for tiramisu drizzle',
            '["Tiramisu swirl (Holly Golightly)"]',
            '["caffeine"]',
            '5 kg bag',
            0.10, 0.15, 2),

            -- 11
            ('Hazelnuts (roasted)',
            'Crunchy nut mix-in',
            '["Hazelnuts (Scrat)"]',
            '["tree_nuts"]',
            '2 kg bag',
            0.40, 0.50, 5),

            -- 12
            ('Oreo-style sandwich cookies',
            'Crushed cookie chunks',
            '["Oreo cookie chunks (Cookie Monster)"]',
            '["gluten","soy","milk"]',
            '4.5 kg case',
            0.25, 0.25, 2),

            -- 13
            ('Chocolate chips (semi-sweet)',
            'Small chips for texture',
            '["Chocolate chips (Willy Wonka)"]',
            '["milk","soy"]',
            '10 kg bag',
            0.20, 0.30, 1),

            -- 14
            ('Heavy cream (35-40%)',
            'For whipped cream, mousse, and caramel',
            '["Whipped cream (Donkey)","Silky chocolate mousse ribbon (James Bond)","Sea-salt caramel drizzle (Jack Sparrow)"]',
            '["dairy"]',
            '12x1 L case',
            NULL, NULL, 4),

            -- 15
            ('Granulated sugar',
            'Base sweetener; sauces and sorbet',
            '["Lemon sorbet (Mary Poppins)","Rich chocolate sauce (Vianne Rocher)","Sea-salt caramel drizzle (Jack Sparrow)","Silky chocolate mousse ribbon (James Bond)"]',
            '[]',
            '25 kg sack',
            NULL, NULL, 3),

            -- 16
            ('Eggs (pasteurized)',
            'For safe chocolate mousse',
            '["Silky chocolate mousse ribbon (James Bond)"]',
            '["egg"]',
            '180-egg case',
            NULL, NULL, 1),

            -- 17
            ('Pineapple (fresh or canned)',
            'Chunks for topping',
            '["Pineapple pieces (Moana)"]',
            '[]',
            '12 kg fresh case or 6x3 kg cans',
            0.25, 0.25, 3),

            -- 18
            ('Butter (unsalted)',
            'For sea-salt caramel',
            '["Sea-salt caramel drizzle (Jack Sparrow)"]',
            '["dairy"]',
            '5 kg block',
            NULL, NULL, 2),

            -- 19
            ('Sea salt flakes',
            'Finishing salt for caramel',
            '["Sea-salt caramel drizzle (Jack Sparrow)"]',
            '[]',
            '1 kg box',
            0.01, 0.01, 6),

            -- 20
            ('Mini marshmallows',
            'Soft topping',
            '["Mini marshmallows (Stay Puft)"]',
            '["gelatin"]',
            '2 kg bag',
            0.15, 0.15, 4),

            -- 21
            ('Coconut milk (full-fat)',
            'Dairy-free base option',
            '["Coconut milk base (Po)"]',
            '["coconut","tree_nuts"]',
            '12x400 ml cans',
            0.40, 0.50, 5),

            -- 22
            ('Stevia packets',
            'Non-sugar sweetener for vanilla swap',
            '["Stevia-sweetened vanilla (Spock)"]',
            '[]',
            'Box (200 pkts)',
            0.15, 0.15, 2),

            -- 23
            ('Sunflower seed butter',
            'Nut-free butter swirl',
            '["Sunflower seed butter swirl (Spider-Man)"]',
            '["sunflower_seed"]',
            '2 kg tub',
            0.35, 0.40, 3);

        """)
        await db.commit()


async def init_db():
    await asyncio.gather(migrate_and_mock())
